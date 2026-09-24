
import assistant
from database import Database
from Conversation import Conversation
from assistant import Assistant
def print_hi():
    print("="*5 + "AI学习助手" + "="*5)
    print("1.向AI提问")
    print("2.查看历史对话")
    print("3.清空历史对话")
    print("4.修改AI角色")
    print("5.退出")
    print("请选择：",end="")

if __name__ == "__main__":
    db = Database()
    conversations = db.get_conversations()
    print("已有会话：")
    for conversation_id,title in conversations:
        print(conversation_id,title)
    choice = input("输入会话 id 继续聊天，输入 n 创建新会话：")
    if choice == "n":
        conversation_id = db.create_conversation("新会话")
    else:
        conversation_id = int(choice)

    conversation = Conversation(conversation_id)
    assistant = Assistant(conversation)

    print("="*20)
    while True:
        print_hi()
        choice = input()
        #while True:   --->死循环一直一个case执行
        match choice:
            case "1":
                # config.ask_question(question)
                question = input("What is the question:")
                assistant.ask_ai(question)
            case "2":
                conversation.check_history()
            case "3":
                conversation.delete_history()
                #break 选项里的函数报错才break
            case "4":
                prompt = input("What is the prompt:")
                assistant.set_prompt(prompt)
            case "5":
                break


