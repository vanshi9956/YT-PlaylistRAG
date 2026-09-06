## ab humare paas data aa gya chunking ho gyi embedding hoke qdrant mein store b ho gya hai ab hume search krna hai
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from llm import askllm
load_dotenv()

client = QdrantClient(
    api_key=os.getenv("QUAD_API_KEY"),
    url=os.getenv("QUAD_URL")
)

collection_name = "youtube_chunks"

model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

def search(query , top_k=3):
    query_embedding=model.encode(query)
    results=client.query_points(
        collection_name=collection_name,
        query=query_embedding.tolist(),
        limit=top_k,
    )
    return results

query = "OOPs?"

results = search(query)

context = "\n\n".join([
    f"Video: {p.payload['video_title']}\n"
    f"Video Link: https://www.youtube.com/watch?v={p.payload['video_id']}&t={int(p.payload['start_time'])}s\n"
    f"Timestamp: {p.payload['start_time']}-{p.payload['end_time']}\n"
    f"Content: {p.payload['text']}"
    for p in results.points
])


for chunk in askllm(query , context):
    print(chunk , end="")
print("end reached")