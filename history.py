#用户对话历史
import json
import config
flag = True
#user1 = config.User("lll")
def add_history(User,s,flag):
    if flag:
        User.history_dict["user"].append(s)
    else:
        User.history_dict["assistant"].append(s)
    with open("history.json","w",encoding="utf-8") as f:
        json.dump(User.history_dict,f,ensure_ascii=False,indent=4)
# def user_history():
#     pass
# #ai历史
# def assistant_history():
#     pass
def check_history():

    with open("history.json","r",encoding="utf-8") as f:
        history_dict = json.load(f)
        choice = input("你想要哪个历史记录？你的问题->1,我的回答->2:")
        if choice == "1":
            print(history_dict["user"])
        else:
            print(history_dict["assistant"])
        #查看不需分用户历史还是ai的回答历史吧？
        # if("user" in history_dict):
        #     return history_dict["user"]
if __name__ == "__main__":
    u1 = config.User()
    add_history(u1,"1",True)

