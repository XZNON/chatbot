from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

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


checkpointer = InMemorySaver()
graph = StateGraph(ChatState)

graph.add_node("chatNode",chatNode)

graph.add_edge(START,"chatNode")
graph.add_edge("chatNode",END)

chatBot = graph.compile(checkpointer=checkpointer)

