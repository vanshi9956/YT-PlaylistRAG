import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
if my_api_key is None:
    raise ValueError("Groq api key not found")
client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"
def askllm(query , context):
    system_prompt = f"""You are a helpful assistant that answers questions based ONLY on the following context:

{context}

Rules:
1. If the context does not contain relevant information, respond only with: "No information provided regarding this."
2. Do not hallucinate or add information not present in the context.
3. If relevant information is found, respond in EXACTLY this format:

Summary: [2-3 line concise explanation for a first-time learner]
Source Video: [video_title from context]
Video Link: [video_link from context]
Timestamp: [start_time] - [end_time]
"""
    message_system={
    "role":"system",
    "content":system_prompt
     }
    prompt=f"""query :{query} answer query """
    message={
        "role":"user",
        "content":prompt
    }
    messages=[message_system , message]
    response=client.chat.completions.create(model=model , messages=messages , temperature=0.2 , max_tokens=600, stream=True)

    for chunks in response:
        text=chunks.choices[0].delta.content
        if text:
            yield text  
        