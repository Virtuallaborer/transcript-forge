import ollama
from pathlib import Path

transcript_path = Path("transcript.txt")
transcript = transcript_path.read_text(encoding="utf-8")

print("📄 Transcript loaded. Using qwen3:8b...\n")

model = "qwen3:8b"

# Summarize
summary_response = ollama.chat(model=model, messages=[
    {'role': 'system', 'content': 'You are an expert, concise summarizer.'},
    {'role': 'user', 'content': f"Summarize this transcript clearly and concisely:\n\n{transcript[:20000]}"}
])

summary = summary_response['message']['content']
print("📝 SUMMARY:\n", summary, "\n")

# Generate build prompt
prompt_response = ollama.chat(model=model, messages=[
    {'role': 'system', 'content': 'You are an expert prompt engineer for coding assistants.'},
    {'role': 'user', 'content': f"""Create a detailed, step-by-step prompt I can give to an AI coding assistant (like Cursor or Continue.dev) to build the system described in this summary:

Summary: {summary}"""}
])

build_prompt = prompt_response['message']['content']
print("🚀 BUILD PROMPT:\n", build_prompt)

# Save
Path("summary_qwen.txt").write_text(summary, encoding="utf-8")
Path("build_prompt_qwen.txt").write_text(build_prompt, encoding="utf-8")
print("\n✅ Saved: summary_qwen.txt and build_prompt_qwen.txt")