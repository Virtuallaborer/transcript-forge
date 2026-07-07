import streamlit as st
import ollama
import re
import zipfile
from pathlib import Path
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import io

st.set_page_config(page_title="Transcript Forge", layout="centered")
st.title("🔨 Transcript Forge")
st.markdown("**YouTube → Summary → Action Items → Build Prompts**  \n*Local-first. Private. Powerful.*")

# Config
col1, col2 = st.columns(2)
with col1:
    model = st.selectbox("Model", ["qwen3:8b", "llama3.2", "deepseek-coder-v2"], index=0)
with col2:
    tone = st.text_input("Tone/Style", "professional, clear, concise, and actionable")

url = st.text_input("YouTube URL or Video ID", "", placeholder="https://youtu.be/... or just the ID")

if st.button("🚀 Forge Transcript", type="primary", use_container_width=True):
    if not url:
        st.error("Please enter a YouTube URL or Video ID")
        st.stop()

    video_id_match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", url)
    video_id = video_id_match.group(1) if video_id_match else url
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    with st.spinner("Fetching transcript..."):
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_obj = ytt_api.fetch(video_id)
            full_transcript = "\n".join([f"[{entry.start:.1f}s] {entry.text}" for entry in transcript_obj])

            st.success(f"Transcript loaded ({len(full_transcript)//1000}k characters)")

            # Chunking
            chunk_size = 15000
            chunks = [full_transcript[i:i+chunk_size] for i in range(0, len(full_transcript), chunk_size)]
            progress_bar = st.progress(0)
            summaries = []

            for i, chunk in enumerate(chunks):
                st.info(f"Processing chunk {i+1}/{len(chunks)}...")
                resp = ollama.chat(model=model, messages=[
                    {'role': 'system', 'content': f'Expert summarizer. {tone} style.'},
                    {'role': 'user', 'content': f'Summarize concisely:\n\n{chunk}'}
                ])
                summaries.append(resp['message']['content'])
                progress_bar.progress((i + 1) / len(chunks))

            final_summary = "\n\n".join(summaries)

            # Action Items
            st.info("Extracting key action items...")
            action_resp = ollama.chat(model=model, messages=[
                {'role': 'system', 'content': f'Expert extractor. {tone} style.'},
                {'role': 'user', 'content': f'Extract key action items as bullets:\n\n{final_summary}'}
            ])
            action_items = action_resp['message']['content']

            # Build Prompt
            st.info("Generating build prompt...")
            prompt_resp = ollama.chat(model=model, messages=[
                {'role': 'system', 'content': f'Expert prompt engineer. {tone} style.'},
                {'role': 'user', 'content': f'Create detailed coding assistant prompt based on this:\n\nSummary: {final_summary}\n\nActions: {action_items}'}
            ])
            build_prompt = prompt_resp['message']['content']

            # Save files
            files = {
                f"summary_{timestamp}.md": f"# Summary\n\n**Video:** {video_id}\n\n{final_summary}",
                f"action_items_{timestamp}.md": f"# Key Action Items\n\n**Video:** {video_id}\n\n{action_items}",
                f"build_prompt_{timestamp}.md": f"# Build Prompt\n\n**Video:** {video_id}\n\n{build_prompt}"
            }

            for name, content in files.items():
                Path(name).write_text(content, encoding="utf-8")

            st.success("✅ Forging complete!")

            # ZIP Download
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for name, content in files.items():
                    zip_file.writestr(name, content)

            st.download_button(
                label="📦 Download All Files (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"transcript_forge_{video_id}_{timestamp}.zip",
                mime="application/zip",
                use_container_width=True
            )

            st.info("Individual files also available below:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("Summary", files[f"summary_{timestamp}.md"], f"summary_{timestamp}.md")
            with col2:
                st.download_button("Action Items", files[f"action_items_{timestamp}.md"], f"action_items_{timestamp}.md")
            with col3:
                st.download_button("Build Prompt", files[f"build_prompt_{timestamp}.md"], f"build_prompt_{timestamp}.md")

        except Exception as e:
            st.error(f"Error: {str(e)}")