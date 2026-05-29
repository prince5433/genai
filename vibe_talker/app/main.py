from dotenv import load_dotenv  # env vars load karne ke liye
import speech_recognition as sr  # speech recognition ke liye alias
from langgraph.checkpoint.mongodb import MongoDBSaver  # MongoDB checkpoint saver
import asyncio  # async utilities ke liye
import os
from openai.helpers import LocalAudioPlayer  # audio play helper

from openai import AsyncOpenAI  # async OpenAI client

load_dotenv()  # .env se variables load karo

openai = AsyncOpenAI()  # OpenAI client instance banao

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://admin:admin@localhost:27019",
)  # MongoDB connection string
config = {"configurable": {"thread_id": "7"}}  # graph config with thread id


def main():  # main entry function
    from .graph import create_chat_graph  # local graph builder import

    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:  # DB saver context
        graph = create_chat_graph(checkpointer=checkpointer)  # graph create karo

        r = sr.Recognizer()  # recognizer object banao

        with sr.Microphone() as source:  # mic input stream
            r.adjust_for_ambient_noise(source)  # noise calibration
            r.pause_threshold = 2  # pause threshold set

            while True:  # continuous listen loop
                print("Say something!")  # user prompt
                audio = r.listen(source)  # mic se audio capture

                print("Processing audio...")  # status log
                sst = r.recognize_google(audio)  # Google STT se text banao

                print("You Said:", sst)  # recognized text show
                for event in graph.stream({"messages": [{"role": "user", "content": sst}]}, config, stream_mode="values"):  # graph stream
                    if "messages" in event:  # safety check
                        event["messages"][-1].pretty_print()  # last message print


async def speak(text: str):  # TTS helper function
    async with openai.audio.speech.with_streaming_response.create(  # streaming TTS request
        model="gpt-4o-mini-tts",  # model name
        voice="coral",  # voice selection
        input=text,  # input text
        instructions="Speak in a cheerful and positive tone.",  # tone instruction
        response_format="pcm",  # audio format
    ) as response:  # response context
        await LocalAudioPlayer().play(response)  # audio play karo

if __name__ == "__main__":
    main()  # main run karo

# if __name__ == "__main__":  # optional entry check
#      asyncio.run(speak(text="This is a sample voice. Hi Piyush"))  # sample TTS run
