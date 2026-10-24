from database import Database
#管理历史信息
class Conversation:
    def __init__(self,conversation_id,db):
        self.db = db
        self.conversation_id = conversation_id
        self.history = self.db.get_messages(conversation_id)

    def add_user_message(self,content):
        self.db.add_message(self.conversation_id,"user",content)
        self.history.append({"role":"user","content":content,"sources":[]})

    def add_assistant_message(self, content, sources=None):
        if sources is None:
            sources = []

        self.db.add_message(
            self.conversation_id,
            "assistant",
            content,
            sources
        )

        self.history.append({
            "role": "assistant",
            "content": content,
            "sources": sources
        })

    def check_history(self):
        print(self.history)
    def delete_history(self):
        delete_count = self.db.delete_messages(self.conversation_id)
        self.history = []
        print(f"已删除{delete_count}条历史信息")
