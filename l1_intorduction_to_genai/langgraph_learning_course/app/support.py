from dotenv import load_dotenv  # .env se env vars load
import json  # Tool args decode karne ke liye
from langgraph.types import Command  # Resume command banane ke liye
from langgraph.checkpoint.mongodb import MongoDBSaver  # MongoDB checkpointer

load_dotenv()  # Env variables load

from .graph import create_chat_graph  # Graph factory import

MONGODB_URI = "mongodb://admin:admin@localhost:27018/?authSource=admin"  # Auth ke sath MongoDB URI
config = {"configurable": {"thread_id": "1"}}  # Main app ke same thread ko resume karo
 
def init():  # Support flow ka entry
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:  # DB saver init
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)  # Stateful graph
    
        state = graph_with_mongo.get_state(config=config)  # Saved state fetch karo
        # for message in state.values['messages']:
        #     message.pretty_print()  # Full history dekhna ho to uncomment

        if "messages" not in state.values or not state.values["messages"]:  # Empty thread guard
            print("No saved messages found. Run app.main first and ask something that triggers human_assistance_tool.")
            return
        
        last_message = state.values["messages"][-1]  # Latest message nikalo
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])  # Tool calls list

        user_query = None  # Human tool ka query yahan store hoga

        for call in tool_calls:  # Har tool call check karo
            if call.get("function", {}).get("name") == "human_assistance_tool":  # Target tool
                args = call["function"].get("arguments", "{}")  # Args JSON string
                try:  # JSON parse attempt
                    args_dict = json.loads(args)  # String ko dict banao
                    user_query = args_dict.get("query")  # Query extract karo
                except json.JSONDecodeError:  # Invalid JSON mila to handle
                    print("Failed to decode function arguments.")  # Error log
        
        print("User is Tying to Ask:", user_query)  # Human ko question dikhao
        ans = input("Resolution > ")  # Human ka answer lo

        # OpenAI Call to mimic human  # Yahan actual model call add kar sakte ho

        resume_command = Command(resume={"data": ans})  # Graph ko resume karo
        
        for event in graph_with_mongo.stream(
            resume_command,
            config,
            stream_mode="values",
        ):  # Resume ke baad events stream karo
            if "messages" in event:  # New message aaya to print karo
                event["messages"][-1].pretty_print()  # Last message pretty format

init()  # Script run hote hi support flow start

# Workflow (detailed ASCII diagram)
#
#   [START]
#      |
#      v
#   load_dotenv  -> env vars ready
#      |
#      v
#   MongoDBSaver.from_conn_string
#      |
#      v
#   create_chat_graph(checkpointer)
#      |
#      v
#   get_state(config)  -> last saved state
#      |
#      v
#   last_message -> tool_calls
#      |
#      v
#   for each tool_call
#      |
#      +--> if name == human_assistance_tool
#      |        |
#      |        v
#      |     parse JSON args -> user_query
#      |
#      v
#   print user_query -> input("Resolution > ")
#      |
#      v
#   Command(resume={data: ans})
#      |
#      v
#   graph.stream(resume_command)
#      |
#      v
#   if messages -> pretty_print last msg
