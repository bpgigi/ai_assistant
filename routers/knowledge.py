from fastapi import APIRouter
from rag import service as rag_service
from pathlib import Path
from fastapi import UploadFile, File, HTTPException


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

    # 4. 避免覆盖已有文件
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    file_path = KNOWLEDGE_DIR / filename

    try:
        with file_path.open("xb") as f:
            f.write(content)
    except FileExistsError:
        raise HTTPException(
            status_code=409,
            detail="同名文件已存在"
        )

    try:
        chunks = rag_service.split_markdown(text)

        source = file_path.relative_to(
            PROJECT_ROOT
        ).as_posix()

        chunk_count = rag_service.index_documents(
            chunks,
            source
        )

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    return {
        "filename": filename,
        "source": source,
        "chunk_count": chunk_count,
        "saved": True
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