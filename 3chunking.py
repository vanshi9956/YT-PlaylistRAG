## phele hum saare videos ke transcripts se text ko extract krenge aur phr uss text pe fixed size chunking krenge
import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
with open("metadata/playlist_videos.json", "r", encoding="utf-8") as f:
        videos = json.load(f)
def get_title(video_id):
    
        for video in videos:
            if(video['video_id']==video_id):
                return video['title']
        return "Unknown Title"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=30,
    length_function=lambda x: len(x.split()),
    add_start_index=True
)

     
 
file=os.listdir("transcripts")## ye humareko jitni bhi files hai transcript folder mein vo de dega

for filename in file:
    video_id=filename.replace(".json","")

    video_title=get_title(video_id)

    with open(f"transcripts/{filename}", "r", encoding="utf-8") as f:
        transcript=json.load(f)

    text = " ".join(
        entry["text"]
        for entry in transcript
    )  ## join all text entries into a single string

    docs=splitter.create_documents([text])  ## ab ye chunks mein split ho jayega 

    ## humare paas chunking ho gyi hai but humme start or end possition b chaiye un chunks ki to ye work uske liye hai
    final_chunks=[]
    ## humnne start or end time bhi chaiye jo chunks bne hai unke soo
    for i, doc in enumerate(docs):

      chunk = doc.page_content
      start_position = doc.metadata['start_index']
      end_position = start_position + len(chunk)
  
      start_time = None
      end_time = None
      current_position = 0

      for entry in transcript:
        entry_text = entry["text"]
        entry_start = current_position
        entry_end = current_position + len(entry_text)

        if entry_end >= start_position and entry_start <= end_position:
            if start_time is None:
                start_time = entry["start"]
            end_time = entry["start"] + entry["duration"]

        current_position = entry_end + 1

      final_chunks.append({
        "chunk_id": i,
        "video_id": video_id,
        "video_title": video_title,
        "text": chunk,
        "start": start_time,
        "end": end_time
    })
      

    with open(f"chunks/{video_id}_chunks.json","w" , encoding="utf-8") as f:
         json.dump(final_chunks , f , indent=2 , ensure_ascii=False)
    print(
        f"{video_title} → {len(final_chunks)} chunks"
    )

print("done")