from dotenv import load_dotenv  # .env file se env vars load karne ke liye

load_dotenv()  # Env variables ko process me inject karo

from .graph import create_chat_graph  # Graph factory import
from langgraph.checkpoint.mongodb import MongoDBSaver  # MongoDB checkpoint saver

MONGODB_URI = "mongodb://admin:admin@localhost:27018/?authSource=admin"  # Local MongoDB connection string
config = {"configurable": {"thread_id": "1"}}  # Thread id se session isolate hota hai
 
def init():  # App ka entry flow
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:  # DB saver init
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)  # Stateful graph
    
        while True:  # REPL loop: user se input lete raho
            user_input = input("> ")  # User ka prompt
            for event in graph_with_mongo.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
                stream_mode="values",
            ):  # Graph se streaming events lo
                if "messages" in event:  # Naya message mila to print karo
                    event["messages"][-1].pretty_print()  # Last message pretty format me

init()  # Script run hote hi app start

# Workflow (detailed ASCII diagram)
#
#   [START]
#      |
#      v
#   load_dotenv -> env vars ready
#      |
#      v
#   MongoDBSaver.from_conn_string
#      |
#      v
#   create_chat_graph(checkpointer)
#      |
#      v
#   while True loop
#      |
#      v
#   input("> ") -> user_input
#      |
#      v
#   graph.stream({messages:[user]})
#      |
#      v
#   for each event
#      |
#      +--> if "messages" in event
#      |        |
#      |        v
#      |     pretty_print last msg
#      |
#      v
#   (loop continues)
