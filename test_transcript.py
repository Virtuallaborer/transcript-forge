from youtube_transcript_api import YouTubeTranscriptApi

video_id = "b4d32pBa3UY"

try:
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    
    print("✅ Success! Transcript fetched.")
    print(f"Language: {transcript.language}")
    print(f"Total snippets: {len(transcript)}\n")
    
    print("First 5 entries:")
    for entry in list(transcript)[:5]:
        print(f"{entry.start:.1f}s: {entry.text}")
except Exception as e:
    print("❌ Error:", str(e))