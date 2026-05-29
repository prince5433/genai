from typing_extensions import TypedDict  # Typed state shape define karne ke liye
from langgraph.graph import StateGraph, START, END  # Graph builder + start/end nodes
from typing import Literal  # Return type ko fixed options me rakhne ke liye
from langsmith.wrappers import wrap_openai  # OpenAI client ko structured output ke liye wrap
from openai import OpenAI  # OpenAI client
from pydantic import BaseModel  # Response schema validation
from dotenv import load_dotenv  # .env loader


# Schema: LLM response ko strictly validate karne ke liye
class DetectCallResponse(BaseModel):
    is_question_ai: bool  # True/False: kya query coding se related hai

class CodingAIResponse(BaseModel):
    answer: str  # Final reply text


# .env file se API keys load karne ke liye
load_dotenv()  # Environment variables load

# OpenAI client ko wrap kiya taaki structured output parse ho sake
client = wrap_openai(OpenAI())  # Wrapped client instance

class State(TypedDict):
    # Ye state graph me aage-pass hone wala data hai
    user_message: str  # User ka input
    ai_message: str  # AI ka output
    is_coding_question: bool  # Routing flag

def detect_query(state: State):
    # User message uthao
    user_message = state.get("user_message")  # Current user query

    SYSTEM_PROMPT = """  # System instruction for detection
    You are an AI assistant. Your job is to detect if the user's query is related
    to coding question or not.
    Return the response in specified JSON boolean only.
    """

    # OpenAI Call: check karo query coding se related hai ya nahi
    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",  # Lightweight model for classification
        response_format=DetectCallResponse,  # Structured output schema
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },  # System prompt
            { "role": "user", "content": user_message }  # Actual user query
        ]
    )

    # Parsed response se boolean state me set karo
    state["is_coding_question"] = result.choices[0].message.parsed.is_question_ai
    return state  # Updated state return

# Routing function: decide karo next node based on detect_query ka output
# ye langgraph ka ek limitation hai ki conditional edges ke liye fixed return type chahiye hota hai, isliye Literal use kar rahe hain
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    # Route decide karne ke liye flag uthao
    is_coding_question = state.get("is_coding_question")  # Boolean flag

    if is_coding_question:  # Agar coding query hai
        return "solve_coding_question"  # Coding handler par jao
    else:  # Agar general chat hai
        return "solve_simple_question"  # Simple handler par jao

def solve_coding_question(state: State):
    # Coding-type query ka reply generate karo
    user_message = state.get("user_message")  # User input

    # OpenAI Call (Coding Question gpt-4o-mini)
    SYSTEM_PROMPT = """  # System instruction for coding help
    You are an AI assistant. Your job is to resolve the user query based on coding 
    problem he is facing
    """

    # OpenAI Call
    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",  # Available model for coding answers
        response_format=CodingAIResponse,  # Structured output schema
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },  # System prompt
            { "role": "user", "content": user_message }  # User query
        ]
    )
    # Answer ko state me save karo
    state["ai_message"] = result.choices[0].message.parsed.answer

    return state  # Updated state return

def solve_simple_question(state: State):
    # Simple chat-type query ka reply generate karo
    user_message = state.get("user_message")  # User input

    # OpenAI Call (Coding Question gpt-mini)
    SYSTEM_PROMPT = """  # System instruction for casual chat
    You are an AI assistant. Your job is to chat with user
    """

    # OpenAI Call
    result = client.beta.chat.completions.parse(
        model="gpt-4o-mini",  # Fast/cheap model for normal chat
        response_format=CodingAIResponse,  # Structured output schema
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },  # System prompt
            { "role": "user", "content": user_message }  # User message
        ]
    )
    # Answer ko state me save karo
    state["ai_message"] = result.choices[0].message.parsed.answer

    return state  # Updated state return


# StateGraph banake nodes + edges wire karo
graph_builder = StateGraph(State)  # Graph builder instance


graph_builder.add_node("detect_query", detect_query)  # Node: detect
graph_builder.add_node("solve_coding_question", solve_coding_question)  # Node: coding solve
graph_builder.add_node("solve_simple_question", solve_simple_question)  # Node: simple chat
graph_builder.add_node("route_edge", route_edge)  # Node: router

# Start se pehle detect_query run hoga
graph_builder.add_edge(START, "detect_query")  # START -> detect
graph_builder.add_conditional_edges("detect_query", route_edge)  # detect -> route

# Jo bhi route select hua, uske baad END
graph_builder.add_edge("solve_coding_question", END)  # coding -> END
graph_builder.add_edge("solve_simple_question", END)  # simple -> END

# Graph ko compile karna zaroori hai before invoke
graph = graph_builder.compile()  # Final runnable graph


# Use the Graph

def call_graph():
    # Initial state set karo
    state = {
        "user_message": "Can you explain pydantic in Python?",  # Sample user input
        "ai_message": "",  # Placeholder for AI reply
        "is_coding_question": False  # Default routing flag
    }
    
    # Graph run karke final state lo
    result = graph.invoke(state)  # Graph execution
    
    # Output print karo
    print("Final Result", result)  # Final state output

call_graph()  # Function call