# PlaylistRAG

I built this because I kept forgetting where exactly in a playlist a topic was explained. Like I'd remember "yeah he explained recursion somewhere in this DSA playlist" but not which video, not which timestamp — and scrubbing through 2 hour videos to find one 3 minute explanation is just painful.

So this project basically lets you type a topic/question and it tells you the exact video + timestamp + a quick summary of what's explained there, using RAG (Retrieval-Augmented Generation).

Right now I've built it for Apna College's playlist (Hindi content), but it should work for any YouTube playlist as long as captions exist for the videos.

## How it works (the pipeline)

```
YouTube Playlist
      ↓
Fetch video IDs + titles (YouTube Data API v3)
      ↓
Extract transcripts (youtube-transcript-api)
      ↓
Chunk the transcript text (~150 words per chunk, timestamps preserved)
      ↓
Generate embeddings for each chunk (sentence-transformers)
      ↓
Store as points in Qdrant (embedding + payload: video_id, title, text, start/end time)
      ↓
User query → embed the query → similarity search in Qdrant → top matching chunks
      ↓
Pass matched chunks to LLM → returns video link + timestamp + short summary
```

## Tech stack

- **Python** (obviously)
- **YouTube Data API v3** — to get playlist metadata (video IDs, titles)
- **youtube-transcript-api** — to pull transcripts without downloading audio
- **sentence-transformers** (`all-MiniLM-L6-v2`) — for generating embeddings
- **Qdrant** — vector database, stores embeddings + payload (payload = metadata basically, that's just what Qdrant calls it)
- **Groq API** (`openai/gpt-oss-120b`) — LLM that generates the final answer/summary from retrieved chunks
- `python-dotenv` — for keeping API keys out of the code

## Project structure

```
├── metadata/              # playlist video IDs + titles (from YouTube API)
├── transcripts/           # raw transcript per video, saved as {video_id}.json
├── chunks/                # transcripts broken into ~150 word chunks with timestamps
├── progress.json          # tracks which videos are already processed (checkpoint system)
├── 1get_metadata.py       # fetches playlist video list from YouTube API
├── 2get_transcipts.py     # fetches transcript for each video, with retry + resume logic
├── chunking.py            # breaks transcripts into chunks
├── embedding.py           # generates embeddings and upserts points into Qdrant
├── quad_search.py         # takes a query, searches Qdrant, sends result to LLM
└── llm.py                 # handles the Groq LLM call, builds the final response
```

## Some things I had to figure out / fix along the way

- **YouTube blocks your IP** if you hit their servers too fast with too many requests — had to add delays (`time.sleep`) between requests and process videos in smaller batches instead of all 100+ at once.
- **Checkpointing** — since fetching transcripts for the whole playlist takes time and can get interrupted (laptop shuts, IP gets blocked mid-way), I added a `progress.json` that saves after every single video, so re-running the script skips whatever's already done instead of starting over.
- **Retry logic** — sometimes YouTube gives a random 502 error for a request that isn't actually blocked, just a temporary hiccup. So each video gets a few retry attempts before giving up on it.
- **Language handling** — transcripts are kept in Hindi (Devanagari) as-is, no translation. Turns out you don't need the transcript and the query to be in the same language for search to work well — a good multilingual embedding model can match a Hinglish query like "python loops kaise likhte hain" to a Hindi transcript chunk just fine, because embeddings work on meaning, not exact words. What language the final answer comes back in is controlled separately, through how the LLM is prompted.
- Chunking here is word-count based (not true semantic chunking) — it splits every ~150 words rather than detecting topic changes. Simple, works decently, and something I want to improve later maybe using embedding similarity to detect actual topic shifts.

## Status

Still a work in progress — not all videos in the playlist have transcripts pulled yet because of the IP rate-limiting issue, so I'm adding the rest in batches. The core pipeline (transcript → chunk → embed → store → query) is working end to end for the videos processed so far.

## What I'd want to add next

- A proper interface instead of running scripts manually (maybe a simple Streamlit app)
- Support for multiple playlists at once with filters
- Better chunking (semantic instead of fixed word count)
