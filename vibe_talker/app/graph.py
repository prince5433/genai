import os  # OS level operations ke liye
from typing import Annotated  # type annotation helper
from typing_extensions import TypedDict  # TypedDict support
from langgraph.graph.message import add_messages  # message aggregator
from langchain.chat_models import init_chat_model  # LLM init helper
from langgraph.prebuilt import ToolNode, tools_condition  # tool node utilities
from langgraph.graph import StateGraph, START, END  # graph primitives
from langchain_core.tools import tool  # tool decorator
from langchain_core.messages import SystemMessage  # system message type


# state basically graph me aage-pass hone wala data structure hai, isme hum messages rakh rahe hain jo user aur AI ke beech exchange honge
class State(TypedDict):  # graph state shape
    messages: Annotated[list, add_messages]  # messages list with reducer

@tool  # tool expose karne ke liye
def run_command(cmd: str):  # command execute helper
    """  # docstring start
    Takes a command line prompt and executes it on the user's machine and  # tool description
    returns the output of the command.  # output description
    Example: run_command(cmd="ls") where ls is the command to list the files.  # example usage
    """  # docstring end
    result = os.system(command=cmd)  # OS command run karo
    return result  # result return karo

llm = init_chat_model(  # LLM initialize karo
    model_provider="openai", model="gpt-4o-mini"  # provider aur model set
)  # init end
llm_with_tool = llm.bind_tools(tools=[run_command])  # tool binding karo

def chatbot(state: State):  # chatbot node function
    system_prompt = SystemMessage(content="""  # system prompt create
        You are an AI Coding assistant who takes an input from user and based on available  # role guidance
        tools you choose the correct tool and execute the commands.  # tool usage guidance
                                  
        You can even execute commands and help user with the output of the command.  # extra instruction

        Always make sure to keep your generated codes and files in chat_gpt/ folder. you can create one if not already there.                           
    """)  # prompt end

    message = llm_with_tool.invoke([system_prompt] + state["messages"])  # model call
    # assert len(message.tool_calls) <= 1  # optional tool call limit
    return {"messages": [message]}  # updated state return

tool_node = ToolNode(tools=[run_command])  # tool node create

graph_builder = StateGraph(State)  # graph builder init

graph_builder.add_node("chatbot", chatbot)  # chatbot node add
graph_builder.add_node("tools", tool_node)  # tools node add

graph_builder.add_edge(START, "chatbot")  # start -> chatbot
graph_builder.add_conditional_edges(  # conditional edges add
    "chatbot",  # from chatbot
    tools_condition,  # tool condition
)  # conditional edges end
graph_builder.add_edge("tools", "chatbot")  # tools -> chatbot
graph_builder.add_edge("chatbot", END)  # chatbot -> end

graph = graph_builder.compile()  # graph compile

def create_chat_graph(checkpointer):  # exported graph factory
    return graph_builder.compile(checkpointer=checkpointer)  # checkpoint support