import json
import config
#from Conversation import Conversation
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
    def ask_ai(self):
        # question = input()
        question = input("What is the question:")
        # all_questions = question + str(self.history_dict)
        self.conversation.add_history(question,True)
        #messages = self.history_dict +
        recent_messages = self.conversation.history_dict[-11:]
        answer = config.ask_question(recent_messages)
        #answer = config.ask_question(self.history_dict)
        if answer is not None:
            print(answer)
            self.conversation.add_history(answer, False)
        else:
            print("AI 没有成功回答，请稍后重试。")
        #self.add_history(answer,False)
    def set_prompt(self,prompt):
        self.prompt = prompt
        with open("prompt.json", "w", encoding="utf-8") as f:
            json.dump(self.prompt, f, ensure_ascii=False, indent=4)
