import json
import os
from openai import OpenAI
import config
class User:
    def __init__(self):
        #history_dict = {}->不行，必须加self
        self.history_dict = {
            "user": [],
            "assistant": [],
        }
        #self.history_dict = { }
        #定义就加载数据
        self.load_history()
    def load_history(self):
        try:
            with open("history.json", "r", encoding="utf-8") as f:
                self.history_dict = json.load(f)
        except FileNotFoundError:
            print("没有数据文件")

    flag = True
    # user1 = config.User("lll")
    def add_history(self, s, flag):
        if flag:
            self.history_dict["user"].append(s)
        else:
            self.history_dict["assistant"].append(s)
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history_dict, f, ensure_ascii=False, indent=4)
    def ask_ai(self):
        print("你好！我是大笨猪，有什么可以帮你。")
        # question = input()
        question = input("What is the question:")
        answer = config.ask_question(question)
        self.add_history(question,True)

        self.add_history(answer,False)
        #print(answer)
    def check_history(self):
        with open("history.json", "r", encoding="utf-8") as f:
            history_dict = json.load(f)
            choice = input("你想要哪个历史记录？你的问题->1,我的回答->2:")
            if choice == "1":
                print(history_dict["user"])
            else:
                print(history_dict["assistant"])
    def delete_history(self):
        # 清空直接空字典？
        self.history_dict = {"user": [], "assistant": []}
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history_dict, f, ensure_ascii=False, indent=4)
    def reset_ai(self):
        pass
class Assistant:
    def __init__(self,str):
        self.promopt = str

def print_hi():
    print("="*5 + "AI学习助手" + "="*5)
    print("1.向AI提问")
    print("2.查看历史对话")
    print("3.清空历史对话")
    print("4.修改AI角色")
    print("5.退出")
    print("请选择：",end="")

if __name__ == "__main__":
    u1 = User()
    # print(u1.history_dict)
    # print(type(u1.history_dict))
    # print(u1.history_dict["user"])
    # print(type(u1.history_dict["user"]))
    # print(u1.history_dict["assistant"])
    print("="*20)
    while True:
        print_hi()
        choice = input()
        #while True:   --->死循环一直一个case执行
        match choice:
            case "1":
                # question = input("What is the question:")
                # config.ask_question(question)
                User().ask_ai()
            case "2":
                User().check_history()
            case "3":
                User().delete_history()
                #break 选项里的函数报错才break
            case "4":
                pass
            case "5":
                break
