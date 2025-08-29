from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

llm = init_chat_model("google_genai:gemini-2.5-flash")

class ChatState(TypedDict):
    message : Annotated[list[BaseMessage],add_messages]

def chatNode(state : ChatState) -> ChatState:
    message = state["message"]

    res = llm.invoke(message)
    res = AIMessage(content=res.content)
    return {
        'message' : [res]
    }

conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)   
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

graph.add_node("chatNode",chatNode)

graph.add_edge(START,"chatNode")
graph.add_edge("chatNode",END)

chatBot = graph.compile(checkpointer=checkpointer)




def findThreads():
    threads = set()
    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config['configurable']['thread_id'])
    return list(threads)

# print(findThreads())

# CONFIG = {'configurable' : {
#     'thread_id' : '5'
# }}

# res = chatBot.invoke({'message':[HumanMessage(content = "What is the recipie to make pasta")]},config=CONFIG)
# print(res)

def deleteDb(dbPath : str,table_name : str = 'checkpoints'):
    if not os.path.exists(dbPath):
        print("Db file not found")
        return
    
    conn = None
    try:
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not cursor.fetchone():
            print(f"Table '{table_name}' not found in the database. Nothing to delete.")
            return

        # Delete all rows from the table
        sql = f"DELETE FROM {table_name}"
        cursor.execute(sql)
        conn.commit()
        print(f"Successfully deleted all history from table: '{table_name}' in {dbPath}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

def createName(chatMessage):
    
    prompt = f"Given the chat history between user and AI generate a small 1-2 line summary of the converstion that will be used as the name of the chat thread \n\n {chatMessage}"

    name = llm.invoke(prompt).content
    return name
