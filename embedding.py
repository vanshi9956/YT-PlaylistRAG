import string

from sentence_transformers import SentenceTransformer
import os
import json
from  qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct , Filter , FieldCondition , MatchValue
from dotenv import load_dotenv
import uuid ## random id bnayega humare qdrant point ke liye

load_dotenv()

client=QdrantClient(
    api_key=os.getenv("QUAD_API_KEY"),
    url=os.getenv("QUAD_URL")
)
collection_name="youtube_chunks"
if client.collection_exists(collection_name):
    print("deleting existing collection")
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    ))

model=SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

points=[]
file=os.listdir("chunks")
all_chunks=[]
for filename in file:
    with open(f"chunks/{filename}", "r", encoding="utf-8") as f:
        chunks=json.load(f)
        all_chunks.extend(chunks)  ## ye all_chunks mein jitne bhi chunks hai unko add kar dega


texts = [chunk["text"] for chunk in all_chunks]
embeddings = model.encode(
    texts,
     batch_size=25,
    show_progress_bar=True
    )
points = []

for i, chunk in enumerate(all_chunks):

    # Deterministic UUID
    point_id = str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{chunk['video_id']}_{chunk['chunk_id']}"
        )
    )

    point = PointStruct(
        id=point_id,

        # embedding belonging to THIS chunk
        vector=embeddings[i].tolist(),

        # information about THIS chunk
        payload={
            "start_time": chunk["start"],
            "end_time": chunk["end"],
            "video_id": chunk["video_id"],
            "video_title": chunk["video_title"],
            "text": chunk["text"]
        }
    )

    points.append(point)


        
qdrant_batch_size = 25   ## ab hum qdrant mein jitne bhi points hai unko batch mein upload karenge taki qdrant ke server pe load na ho aur humari request block na ho
## jaise 1000 points bni hai to ab hum 25 ke batch mein upload krenge taki qdrant ke server pe load na ho aur humari request block na ho
for i in range(0, len(points), qdrant_batch_size):

    batch = points[i:i + qdrant_batch_size]

    client.upsert(
        collection_name=collection_name,
        points=batch
    )

    uploaded = min(i + qdrant_batch_size, len(points))

    print(f"Uploaded {uploaded}/{len(points)}")

