from youtube_transcript_api import YouTubeTranscriptApi

video_id = "b4d32pBa3UY"  # Change this for other videos

ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch(video_id)

# Save full transcript to text file
with open("transcript.txt", "w", encoding="utf-8") as f:
    for entry in transcript:
        f.write(f"[{entry.start:.1f}s] {entry.text}\n")

print(f"✅ Full transcript saved to transcript.txt ({len(transcript)} entries)")
print("Open it with: cat transcript.txt | head -20")