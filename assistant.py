import json
import llm_service
class Assistant:
    def __init__(self,conversation):
        self.conversation = conversation
        self.prompt = ""
        self.load_prompt()
    def load_prompt(self):
        try:
            with open("prompt.json", "r", encoding="utf-8") as f:
                self.prompt = json.load(f)
        except FileNotFoundError:
            print("第一次使用，已创建好助手")
            with open("prompt.json", "w",encoding="utf-8") as f:
                self.prompt = "You are a helpful assistant"
                json.dump(self.prompt, f, ensure_ascii=False, indent=4)

    def ask_ai(self,question):
        recent_messages = self.conversation.history[-10:]
        messages = [
            {
                "role":"system",
                "content":self.prompt
            }
        ] + recent_messages + [
            {
                "role":"user",
                "content":question
            }
        ]
        answer = llm_service.ask_question(messages)

        self.conversation.add_user_message(question)
        self.conversation.add_assistant_message(answer)
        return answer

    def set_prompt(self,prompt):
        self.prompt = prompt
        with open("prompt.json", "w", encoding="utf-8") as f:
            json.dump(self.prompt, f, ensure_ascii=False, indent=4)
