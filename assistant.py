import json
import config
from Conversation import Conversation
# class User:
#     def __init__(self):
#         #history_dict = {}->不行，必须加self
#
#         self.history_dict = [
#             {"role":"user","content":""}, #u1.history_dict[0]["content"]  偶数个
#             {"role":"assistant","content":""},
#         ]
#         #定义就加载数据
#         self.load_history()
#     def load_history(self):
#         try:
#             with open("history.json", "r", encoding="utf-8") as f:
#                 self.history_dict = json.load(f)
#         except FileNotFoundError:
#             print("没有数据文件")
#
#     # flag = True
#     # user1 = config.User("lll")
#     def add_history(self, s, flag):
#         if flag:
#             user_dict = {"role":"user","content":s}
#             # self.history_dict["user"].append(s)
#             self.history_dict.append(user_dict)
#         else:
#             assistant_dict = {"role":"assistant","content":s}
#             self.history_dict.append(assistant_dict)
#
#         with open("history.json", "w", encoding="utf-8") as f:
#             json.dump(self.history_dict, f, ensure_ascii=False, indent=4)
#     # def ask_ai(self):
#     #     # question = input()
#     #     question = input("What is the question:")
#     #     # all_questions = question + str(self.history_dict)
#     #     self.add_history(question, True)
#     #     #messages = self.history_dict +
#     #     recent_messages = self.history_dict[-11:]
#     #     answer = config.ask_question(recent_messages)
#     #     #answer = config.ask_question(self.history_dict)
#     #     if answer is not None:
#     #         print(answer)
#     #         self.add_history(answer, False)
#     #     else:
#     #         print("AI 没有成功回答，请稍后重试。")
#     #     #self.add_history(answer,False)
#     def check_history(self):
#         print(self.history_dict)
#         # choice = input("你想要哪个历史记录？你的问题->1,我的回答->2:")
#         # if choice == "1":
#         #     print(self.history_dict["user"])
#         # else:
#         #     print(self.history_dict["assistant"])
#     def delete_history(self):
#         # 清空直接空字典？
#         # self.history_dict = {"user": [], "assistant": []}
#         self.history_dict = [
#             # {"role": "user", "content": ""},  # u1.history_dict[0]["content"]  偶数个
#             # {"role": "assistant", "content": ""},
#         ]
#         with open("history.json", "w", encoding="utf-8") as f:
#             json.dump(self.history_dict, f, ensure_ascii=False, indent=4)
#     # def reset_ai(self):
#     #     pass
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
    #def lower_history(self):


# def print_hi():
#     print("="*5 + "AI学习助手" + "="*5)
#     print("1.向AI提问")
#     print("2.查看历史对话")
#     print("3.清空历史对话")
#     print("4.修改AI角色")
#     print("5.退出")
#     print("请选择：",end="")
#
# if __name__ == "__main__":
#     u1 = User()
#     # print(u1.history_dict)
#     # print(type(u1.history_dict))
#     # print(u1.history_dict[1]["content"])   #--->user class str
#     # print(type(u1.history_dict[1]["content"]))
#     # u1.history_dict[1]["content"] = "aaaa" #没有写进去json
#     # print(type(u1.history_dict["assistant"]))
#
#     # print(u1.history_dict[0])
#     # print(type(u1.history_dict[0]))
#     # print(u1.history_dict[1])
#     assist1 = Assistant()
#     print("="*20)
#     while True:
#         print_hi()
#         choice = input()
#         #while True:   --->死循环一直一个case执行
#         match choice:
#             case "1":
#                 # question = input("What is the question:")
#                 # config.ask_question(question)
#                 u1.ask_ai()
#             case "2":
#                 u1.check_history()
#             case "3":
#                 u1.delete_history()
#                 #break 选项里的函数报错才break
#             case "4":
#                 prompt = input("What is the prompt:")
#                 assist1.set_prompt(prompt)
#             case "5":
#                 break
