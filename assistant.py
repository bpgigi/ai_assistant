import json
import llm_service
from rag.service import retrieve,build_rag_context,rewrite_query
class Assistant:
    def __init__(self,conversation):
        self.conversation = conversation
        self.prompt = ""
        self.load_prompt()
        self.last_sources = []
    def load_prompt(self):
        try:
            with open("prompt.json", "r", encoding="utf-8") as f:
                self.prompt = json.load(f)
        except FileNotFoundError:
            print("第一次使用，已创建好助手")
            with open("prompt.json", "w",encoding="utf-8") as f:
                self.prompt = "You are a helpful assistant"
                json.dump(self.prompt, f, ensure_ascii=False, indent=4)


    def ask_ai(self,question,use_rag = False):
        self.last_sources = []
        recent_messages = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in self.conversation.history[-10:]
        ]

        system_prompt = self.prompt
        user_content = question
        answer = None

        if use_rag:
            search_query = rewrite_query(question,recent_messages)
            results = retrieve(search_query)

            self.last_sources = results

            if not results:
                answer = "知识库中没有找到相关内容"
            else:
                context = build_rag_context(results)

                system_prompt = """
                你是一个知识库问答助手。
                只能根据提供的参考资料回答问题。
                如果资料不足以回答，就说：知识库中没有足够的信息。
                不要编造答案。
                """

                user_content = f"""
                参考资料：
                {context}
                
                用户问题：
                {question}
                """

        if answer is None:
            messages = [
                {
                    "role":"system",
                    "content":system_prompt
                }
            ] + recent_messages + [
                {
                    "role":"user",
                    "content":user_content
                }
            ]

            answer = llm_service.ask_question(messages)

        self.conversation.add_user_message(question)
        self.conversation.add_assistant_message(answer,sources=self.last_sources)

        return answer

    def set_prompt(self,prompt):
        self.prompt = prompt
        with open("prompt.json", "w", encoding="utf-8") as f:
            json.dump(self.prompt, f, ensure_ascii=False, indent=4)
