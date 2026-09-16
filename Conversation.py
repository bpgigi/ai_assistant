import json
#管理历史信息
class Conversation:

    def __init__(self):
        #history_dict = {}->不行，必须加self

        self.history_dict = [
            # {"role":"user","content":""}, #u1.history_dict[0]["content"]  偶数个
            # {"role":"assistant","content":""},
        ]
        #定义就加载数据
        self.load_history()
    def load_history(self):
        try:
            with open("history.json", "r", encoding="utf-8") as f:
                self.history_dict = json.load(f)
        except FileNotFoundError:
            print("没有数据文件")

    # def add_history(self, s , flag = True):
    #     if flag:
    #         user_dict = {"role":"user","content":s}
    #         # self.history_dict["user"].append(s)
    #         self.history_dict.append(user_dict)
    #     else:
    #         assistant_dict = {"role":"assistant","content":s}
    #         self.history_dict.append(assistant_dict)
    #
    #     with open("history.json", "w", encoding="utf-8") as f:
    #         json.dump(self.history_dict, f, ensure_ascii=False, indent=4)
    def add_history(self,role,content):
        self.history_dict.append({"role":role,"content":content})
            # user_dict = {"role":"user","content":content}
            # self.history_dict.append(user_dict)
            #
            # assistant_dict = {"role":"assistant","content":s}
            # self.history_dict.append(assistant_dict)

        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history_dict, f, ensure_ascii=False, indent=4)
    def check_history(self):
        print(self.history_dict)
        # choice = input("你想要哪个历史记录？你的问题->1,我的回答->2:")
        # if choice == "1":
        #     print(self.history_dict["user"])
        # else:
        #     print(self.history_dict["assistant"])
    def delete_history(self):
        # 清空直接空字典？
        # self.history_dict = {"user": [], "assistant": []}
        self.history_dict = [
            # {"role": "user", "content": ""},  # u1.history_dict[0]["content"]  偶数个
            # {"role": "assistant", "content": ""},
        ]
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history_dict, f, ensure_ascii=False, indent=4)