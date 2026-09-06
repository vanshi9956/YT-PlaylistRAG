from youtube_transcript_api import YouTubeTranscriptApi
import os
import json
import time
with open("metadata/playlist_videos.json", "r", encoding="utf-8") as f:
    videos = json.load(f)

count=0
max_count=20
if os.path.exists("progress.json"):
    with open("progress.json", "r", encoding="utf-8") as f:
        progress = json.load(f)
     
else:
     progress = {"completed": []}

for video in videos:
    if(count>=max_count):
            print(f"Reached maximum count of {max_count} transcripts. Stopping...")
            break
    video_id=video["video_id"]
    

    ## checking if that video alredy gets transcript or not
    if video_id in progress["completed"]:
         print(f"Transcroi8ipt already exists for video ID {video_id}. Skipping...")
         continue
   
    for attempt in range(3):  ## humne yha pe loop isliye lagaya hai taki agar transcript fetch karne mein koi error aa jaye to hum 3 baar try kar sakein
        try:
            youtube=YouTubeTranscriptApi()
        
            transcript_data=youtube.fetch(video_id , languages=['hi' , 'en'])  ## video id ye metadata se aayi haiii
            transcript=transcript_data.to_raw_data() ## ab ye json mein aaram se convert ho jayega 
        ## uss video ki transcript ki json file mein store krna

            with open(f"transcripts/{video_id}.json","w", encoding="utf-8")as f:
                    json.dump(transcript , f, indent=2, ensure_ascii=False)

            print(f"saved file {video_id}.json")
            count+=1
            progress["completed"].append(video_id)
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for video ID {video_id}: {e}")
            time.sleep(5)  # Wait before retrying
        ## progress mein store krna ki ye video id transcript ho chuki hai
        
    ## permanent store krna progress.json mein taki agr laptop bnd ho jaye tb ye data delete na ho 
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
   
    
    time.sleep(2) ##regular request na jaaye aur humari request block na ho isliye 2 second ka delay daal diya hai
    



## ye code basically transcripts folder mein jitne bhi videos ke transcripts save ho chuke hain unke naam ko progress.json file mein save karega taki aage ke process mein pata chal sake ki kaunse videos ke transcripts already available hain aur kaunse nahi.

