import ollama
import re
from pathlib import Path
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url_or_id):
    match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", url_or_id)
    return match.group(1) if match else url_or_id

# CONFIG
model = "qwen3:8b"
tone = "professional, clear, concise, and actionable"
video_input = input("\nEnter YouTube URL or Video ID: ").strip()
video_id = extract_video_id(video_input)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
chunk_size = 15000  # characters per chunk
# ===========================================

print(f"🔍 Processing: {video_id}")

try:
    ytt_api = YouTubeTranscriptApi()
    transcript_obj = ytt_api.fetch(video_id)
    full_transcript = "\n".join([f"[{entry.start:.1f}s] {entry.text}" for entry in transcript_obj])

    Path(f"transcript_{timestamp}.md").write_text(f"# Full Transcript\n\n**Video ID:** {video_id}\n\n{full_transcript}", encoding="utf-8")
    print(f"✅ Full transcript saved ({len(full_transcript)//1000}k chars)")

    # Chunking for long transcripts
    chunks = [full_transcript[i:i+chunk_size] for i in range(0, len(full_transcript), chunk_size)]
    print(f"Split into {len(chunks)} chunks for processing.")

    # Summarize chunks
    summaries = []
    for i, chunk in enumerate(chunks):
        print(f"📝 Summarizing chunk {i+1}/{len(chunks)}...")
        resp = ollama.chat(model=model, messages=[
            {'role': 'system', 'content': f'Expert summarizer. {tone} style.'},
            {'role': 'user', 'content': f'Summarize this section concisely:\n\n{chunk}'}
        ])
        summaries.append(resp['message']['content'])

    final_summary = "\n\n".join(summaries)

    # Action Items from full (or combined)
    print("📋 Extracting key action items...")
    action_resp = ollama.chat(model=model, messages=[
        {'role': 'system', 'content': f'Expert at extracting actions. {tone} style.'},
        {'role': 'user', 'content': f'Extract key action items and steps from the transcript as bullets:\n\n{final_summary}'}
    ])
    action_items = action_resp['message']['content']

    # Build Prompt
    print("🚀 Generating build prompt...")
    prompt_resp = ollama.chat(model=model, messages=[
        {'role': 'system', 'content': f'Expert prompt engineer. {tone} style.'},
        {'role': 'user', 'content': f'Create detailed prompt for AI coding assistant:\n\nSummary: {final_summary}\n\nActions: {action_items}'}
    ])
    build_prompt = prompt_resp['message']['content']

    # Save
    Path(f"summary_{timestamp}.md").write_text(f"# Summary\n\n**Video:** {video_id}\n\n{final_summary}", encoding="utf-8")
    Path(f"action_items_{timestamp}.md").write_text(f"# Key Action Items\n\n**Video:** {video_id}\n\n{action_items}", encoding="utf-8")
    Path(f"build_prompt_{timestamp}.md").write_text(f"# Build Prompt\n\n**Video:** {video_id}\n\n{build_prompt}", encoding="utf-8")

    print(f"\n✅ Processing complete with chunking! Files saved with timestamp {timestamp}")

except Exception as e:
    print(f"❌ Error: {e}")