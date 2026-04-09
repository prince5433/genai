import json
import requests
from dotenv import load_dotenv
from langfuse import observe
from langfuse.openai import openai
import os

from langsmith import traceable

# Load environment variables from .env file (API keys etc.)
load_dotenv()

# Create OpenAI client using langfuse wrapper
client = openai.Client()


# -------------------- TOOLS --------------------

@observe()
def run_command(command):
    # Executes a system command (like 'ls', 'dir', etc.)
    # os.system returns exit status (0 = success)
    result = os.system(command)
    return result

#basically decorators functions ka kam hota hai ki hum ek function ke behavior ko modify kar sakte hai bina uske code ko change kiye. Yaha pe observe() decorator ka use kiya gaya hai jo ki langfuse ka feature hai. Iska purpose hai ki jab bhi ye function call ho to uski details ko observe karna, jaise ki input parameters, output, execution time, etc. Ye information langfuse dashboard pe jaake dekh sakte hai jisse hume apne tools ke usage aur performance ka insight milta hai.


@observe()
def get_weather(city: str):
    # Tool to fetch weather using wttr.in API
    print("🔨 Tool Called: get_weather", city)
    
    # API endpoint → returns weather condition + temperature
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    # If request successful → return formatted weather string
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    # If API fails
    return "Something went wrong"


@observe()
def add(x, y):
    # Simple addition tool (not used currently)
    print("🔨 Tool Called: add", x, y)
    return x + y


# Dictionary of available tools for the agent
avaiable_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city"
    },
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns output"
    }
}


# -------------------- SYSTEM PROMPT --------------------

# This prompt defines how the AI agent behaves
system_prompt = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    
    You work on 4 steps:
    1. plan → understand problem
    2. action → call tool
    3. observe → get result
    4. output → final answer

    Rules:
    - Always return JSON
    - One step at a time
    - Think before acting

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "tool name if action",
        "input": "input to tool"
    }}

    Available Tools:
    - get_weather
    - run_command
"""

# Initial message (system role)
messages = [
    { "role": "system", "content": system_prompt }
]


# -------------------- MAIN LOOP --------------------

# Outer loop: handles one user prompt at a time and preserves full conversation history.
# The model is expected to reason in small JSON steps (plan/action/output).

while True:
    # Take user input
    user_query = input('> ')
    
    # Add user message to conversation history
    messages.append({ "role": "user", "content": user_query })

    # Inner loop → continues until final output is generated
    while True:
        # Call OpenAI model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},  # Force JSON output
            messages=messages
        )

        # Parse model response JSON
        parsed_output = json.loads(response.choices[0].message.content)

        # Store assistant response in history
        # We store the structured JSON as text so the next model call can see its prior step.
        messages.append({ "role": "assistant", "content": json.dumps(parsed_output) })


        # -------- PLAN STEP --------
        if parsed_output.get("step") == "plan":
            # Just print thinking step
            print(f"🧠: {parsed_output.get('content')}")
            continue
        
        # -------- ACTION STEP --------
        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            # Check if tool exists
            if avaiable_tools.get(tool_name, False) != False:
                
                # Call the tool function
                # Note: this implementation passes one input value directly to the tool.
                # Tools requiring multiple arguments would need a dict/JSON input parser.
                output = avaiable_tools[tool_name].get("fn")(tool_input)

                # Send observation back to model
                # The model sees this as the result of its action and can decide next step.
                messages.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "step": "observe",
                        "output": output
                    })
                })
                continue
        
        # -------- FINAL OUTPUT STEP --------
        if parsed_output.get("step") == "output":
            # Print final answer to user
            print(f"🤖: {parsed_output.get('content')}")
            # Break inner loop only; outer loop keeps the chat session alive for next query.
            break