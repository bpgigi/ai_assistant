import assistant
def print_hi():
    print("="*5 + "AI学习助手" + "="*5)
    print("1.向AI提问")
    print("2.查看历史对话")
    print("3.清空历史对话")
    print("4.修改AI角色")
    print("5.退出")
    print("请选择：",end="")
# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi()
    choice = input()
    match choice:
        case "1":
            print("你好！我是大笨猪，有什么可以帮你。")
            question = input()
            assistant.ai_assistant(question)
        case "2":
            pass
        case "3":
            pass
        case "4":
            pass
        case "5":
            exit()


