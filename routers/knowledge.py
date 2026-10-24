from fastapi import APIRouter
from rag import service as rag_service
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"]
)


@router.get("/documents")
def get_documents():
    return rag_service.list_documents()


MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MiB
PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...)
):
    filename = file.filename

    # 1. 验证文件名
    if (
        not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or not filename.lower().endswith(".md")
    ):
        raise HTTPException(
            status_code=400,
            detail="只允许上传 .md 文件，且文件名不能包含路径"
        )

    # 2. 读取文件，限制大小
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="文件不能超过 2 MiB"
        )

    # 3. 检查是否为 UTF-8 文本
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Markdown 文件必须使用 UTF-8 编码"
        )

    chunks = rag_service.split_markdown(text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Markdown 文件没有可索引的内容"
        )
    # 4. 避免覆盖已有文件
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    file_path = KNOWLEDGE_DIR / filename
    source = file_path.relative_to(PROJECT_ROOT).as_posix()

    # 只允许创建新文件，禁止覆盖同名文件
    try:
        with file_path.open("xb") as f:
            f.write(content)

    except FileExistsError:
        raise HTTPException(
            status_code=409,
            detail="同名文件已存在"
        )

    # 保存成功后，开始索引
    try:
        chunk_count = rag_service.index_documents(
            chunks,
            source
        )

    except Exception:
        logger.exception(
            "知识库文件索引失败: %s",
            source
        )

        # 尝试清理本次上传来源的残留索引
        try:
            rag_service.delete_document(source)
        except Exception:
            logger.exception(
                "索引失败后的 ChromaDB 清理也失败: %s",
                source
            )

        # 清理本次创建的文件
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            logger.exception(
                "索引失败后的文件清理也失败: %s",
                source
            )

        raise HTTPException(
            status_code=500,
            detail="文档索引失败，请查看服务器日志"
        )

    return {
        "filename": filename,
        "source": source,
        "chunk_count": chunk_count,
        "saved": True
    }

@router.put("/documents")
async def update_document(file: UploadFile = File(...)):
    filename = file.filename

    # 1. 校验文件名
    if (
        not filename
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or not filename.lower().endswith(".md")
    ):
        raise HTTPException(400, "无效的 Markdown 文件名")

    file_path = KNOWLEDGE_DIR / filename

    # PUT 只能更新已存在的普通文件
    if file_path.is_symlink():
        raise HTTPException(400, "不允许更新符号链接")

    if not file_path.is_file():
        raise HTTPException(404, "要更新的文件不存在")

    # 2. 读取并验证新内容
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "文件不能超过 2 MiB")

    try:
        new_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "文件必须使用 UTF-8 编码")

    new_chunks = rag_service.split_markdown(new_text)

    if not new_chunks:
        raise HTTPException(400, "文档没有可索引的内容")

    source = file_path.relative_to(PROJECT_ROOT).as_posix()

    # 3. 保留原文件内容，用于失败恢复
    old_content = file_path.read_bytes()
    old_text = old_content.decode("utf-8")
    old_chunks = rag_service.split_markdown(old_text)

    temp_path = None
    index_started = False

    try:
        # 4. 先在同一目录创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=KNOWLEDGE_DIR,
            prefix=".update_",
            suffix=".tmp",
            delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(content)

        # 5. 更新向量索引
        index_started = True
        chunk_count = rag_service.index_documents(
            new_chunks, source
        )

        # 6. 索引成功后才替换原文件
        os.replace(temp_path, file_path)
        temp_path = None

    except Exception:
        logger.exception("更新知识库文档失败: %s", source)

        # 尽可能恢复旧索引
        if index_started:
            try:
                rag_service.index_documents(old_chunks, source)
            except Exception:
                logger.exception("恢复旧索引失败: %s", source)

        raise HTTPException(
            status_code=500,
            detail="文档更新失败，请检查服务器日志"
        )

    finally:
        # 清理没有完成替换的临时文件
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return {
        "filename": filename,
        "source": source,
        "chunk_count": chunk_count,
        "updated": True
    }
@router.delete("/documents")
def delete_document(source: str):
    deleted_count = rag_service.delete_document(source)

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="知识库中没有找到该来源"
        )

    return {
        "source": source,
        "deleted_chunks": deleted_count
    }

@router.delete("/documents/file")
def delete_document_file(source: str):
    # 只允许删除 knowledge/ 下的 Markdown 文件
    if (
        not source.startswith("knowledge/")
        or not source.endswith(".md")
    ):
        raise HTTPException(
            status_code=400,
            detail="只允许删除 knowledge 目录中的 Markdown 文件"
        )

    file_path = (PROJECT_ROOT / source).resolve()
    knowledge_root = KNOWLEDGE_DIR.resolve()

    # 阻止路径穿越
    if not file_path.is_relative_to(knowledge_root):
        raise HTTPException(
            status_code=400,
            detail="非法文件路径"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )

    # 规范化 source，保持与 ChromaDB 一致
    normalized_source = file_path.relative_to(
        PROJECT_ROOT
    ).as_posix()

    deleted_chunks = rag_service.delete_document(
        normalized_source
    )

    file_path.unlink()

    return {
        "source": normalized_source,
        "deleted_chunks": deleted_chunks,
        "file_deleted": True
    }