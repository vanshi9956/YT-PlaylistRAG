import os
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct , Filter , FieldCondition , MatchValue
from googleapiclient.discovery import build

import json

# .env file se API key load karo
load_dotenv()
API_KEY = os.getenv("YT_API_KEY")

# Yaha apni playlist ID daalo
PLAYLIST_ID = os.getenv("VIDEO_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)

## ye code metadata folder mein playlist ke videos ka metadata save karega mtlb video title aur video id save karega
def get_playlist_videos(playlist_id):
    videos = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response["items"]:
            videos.append({
                "video_id": item["contentDetails"]["videoId"],
                "title": item["snippet"]["title"],
                "position": item["snippet"]["position"]
            })
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return videos

# Function chalao
videos = get_playlist_videos(PLAYLIST_ID)

# metadata folder mein save karo
with open("metadata/playlist_videos.json", "w", encoding="utf-8") as f:
    json.dump(videos, f, indent=2, ensure_ascii=False)

print(f"Total videos found: {len(videos)}")
print(f"Saved to metadata/playlist_videos.json")