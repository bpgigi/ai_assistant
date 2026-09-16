from assistant import Assistant
from Conversation import Conversation
def print_hi():
    print("="*5 + "AI学习助手" + "="*5)
    print("1.向AI提问")
    print("2.查看历史对话")
    print("3.清空历史对话")
    print("4.修改AI角色")
    print("5.退出")
    print("请选择：",end="")

if __name__ == "__main__":
    c1 = Conversation()
    assist1 = Assistant(c1)
    print("="*20)
    while True:
        print_hi()
        choice = input()
        #while True:   --->死循环一直一个case执行
        match choice:
            case "1":
                # question = input("What is the question:")
                # config.ask_question(question)
                assist1.ask_ai()
            case "2":
                c1.check_history()
            case "3":
                c1.delete_history()
                #break 选项里的函数报错才break
            case "4":
                prompt = input("What is the prompt:")
                assist1.set_prompt(prompt)
            case "5":
                break