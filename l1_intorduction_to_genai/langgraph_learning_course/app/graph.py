from typing import Annotated  # Types ko metadata dene ke liye
from typing_extensions import TypedDict  # Structured state ke liye typed dict
from langgraph.graph.message import add_messages  # Messages append karne ka reducer
from langchain_openai import ChatOpenAI  # OpenAI chat model
from langgraph.graph import StateGraph, START, END  # Graph builder + start/end
from langchain_core.tools import tool  # Tool register karne ka decorator
from langgraph.types import interrupt  # Human input ke liye graph pause
from langgraph.prebuilt import ToolNode, tools_condition  # Tool node + routing

@tool()  # Is function ko tool ke roop me expose karo
def human_assistance_tool(query: str):  # Tool signature: query string leta hai
    """Request assistance from a human."""  # LLM ko tool ka purpose batata hai
    human_response = interrupt({ "query": query })  # Pause karke query store karo
    return human_response["data"]  # Human data ke sath resume karo

tools = [human_assistance_tool]  # LLM ke liye tool registry

llm = ChatOpenAI(model="gpt-4o-mini")  # Base chat model
llm_with_tools = llm.bind_tools(tools=tools)  # Tool calling enable karo


class State(TypedDict):  # Graph state ka schema
    messages: Annotated[list, add_messages]  # Messages list + reducer

def chatbot(state: State):  # Node: LLM call karke new message return
    message = llm_with_tools.invoke(state["messages"])  # Model run karo
    assert len(message.tool_calls) <= 1  # Max 1 tool call enforce karo
    return {"messages": [message]}  # Model response append karo

# Tool node LLM ke tool_calls ko run karta hai
tool_node = ToolNode(tools=tools)  # Tool calls execute karne wala node

# StateGraph ko state schema do, taaki data flow clear rahe
graph_builder = StateGraph(State)  # Graph build karna start

graph_builder.add_node("chatbot", chatbot)  # Chatbot node add karo
graph_builder.add_node("tools", tool_node)  # Tools node add karo

graph_builder.add_edge(START, "chatbot")  # Entry edge

# Agar LLM ne tool call kiya to "tools" node par jao, warna END ho sakta hai
graph_builder.add_conditional_edges(  # Tool calls ke basis pe route
    "chatbot",  # Source node
    tools_condition,  # Condition function
)  # Conditional routing end
graph_builder.add_edge("tools", "chatbot")  # Tools ke baad chatbot par wapas

graph_builder.add_edge("chatbot", END)  # Chatbot se finish allow

# Memory ke bina simple stateless graph
graph = graph_builder.compile()  # Stateless graph compile

# Checkpointer do to conversation state persist ho jata hai
def create_chat_graph(checkpointer):  # Stateful graph ke liye factory
    return graph_builder.compile(checkpointer=checkpointer)  # Memory ke sath compile

# Workflow (detailed ASCII diagram)
#
#   [START]
#      |
#      v
#   chatbot(state)
#      |
#      v
#   llm_with_tools.invoke(messages)
#      |
#      +--> if tool_calls present
#      |        |
#      |        v
#      |     tools_condition -> route to [tools]
#      |        |
#      |        v
#      |     ToolNode runs tool_calls
#      |        |
#      |        v
#      |     back to [chatbot]
#      |
#      +--> if no tool_calls
#               |
#               v
#             [END]
