import streamlit as st
import ollama
import re
import zipfile
from pathlib import Path
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import io

st.set_page_config(page_title="Transcript Forge", layout="centered", page_icon="🔨")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 2rem; border-radius: 10px; text-align: center; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🔨 Transcript Forge</h1><p>Turn YouTube Videos into Actionable Insights</p></div>', unsafe_allow_html=True)

# Config
obsidian_vault = st.text_input("Obsidian Vault Path (optional)", value="~/Second-Brain", help="Path to your Obsidian vault root")
manual_title = st.text_input("Custom Title (Highly Recommended)", "", help="Short descriptive title for files (e.g. 'Claude AI Workflow')")
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
    timestamp = datetime.now().strftime("%Y%m%d")

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
                resp = ollama.chat(model=model, messages=[{'role': 'system', 'content': f'Expert summarizer. {tone} style.'}, {'role': 'user', 'content': f'Summarize concisely:\n\n{chunk}'}])
                summaries.append(resp['message']['content'])
                progress_bar.progress((i + 1) / len(chunks))

            final_summary = "\n\n".join(summaries)

            st.info("Extracting key action items...")
            action_resp = ollama.chat(model=model, messages=[{'role': 'system', 'content': f'Expert extractor. {tone} style.'}, {'role': 'user', 'content': f'Extract key action items as bullets:\n\n{final_summary}'}])
            action_items = action_resp['message']['content']

            st.info("Generating build prompt...")
            prompt_resp = ollama.chat(model=model, messages=[{'role': 'system', 'content': f'Expert prompt engineer. {tone} style.'}, {'role': 'user', 'content': f'Create detailed coding assistant prompt based on this:\n\nSummary: {final_summary}\n\nActions: {action_items}'}])
            build_prompt = prompt_resp['message']['content']

            # Save with Frontmatter + Obsidian Folder
            vault_path = Path(obsidian_vault).expanduser()
            agent_folder = vault_path / "Agents" / "YouTube-Forge"
            agent_folder.mkdir(parents=True, exist_ok=True)
            moc_folder = vault_path / "MOCs"
            moc_folder.mkdir(parents=True, exist_ok=True)

            # Title logic (use manual or clean from transcript)
            clean_title = manual_title if manual_title else video_id
            if not manual_title:
                try:
                    for entry in transcript_obj:
                        if entry.text.strip() and len(entry.text) > 10:
                            raw = entry.text.strip()[:80]
                            clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', raw).strip().replace(' ', '_')[:60]
                            break
                except:
                    pass
            if len(clean_title) < 5:
                clean_title = video_id

            def save_with_frontmatter(prefix, content, video_id, category):
                date_str = datetime.now().strftime("%Y%m%d")
                filename = f"{prefix}_{clean_title}_{date_str}.md"
                frontmatter = f"""---
title: "{clean_title.replace('_', ' ')}"
tags: [youtube, transcript, {category}]
created: {datetime.now().strftime("%Y-%m-%d")}
source: YouTube
video-id: {video_id}
---

"""
                full_path = agent_folder / filename
                full_path.write_text(frontmatter + content, encoding="utf-8")
                return str(full_path)

            # Save files
            summary_path = save_with_frontmatter("summary", final_summary, video_id, "summary")
            action_path = save_with_frontmatter("action-items", action_items, video_id, "action-items")
            prompt_path = save_with_frontmatter("build-prompt", build_prompt, video_id, "build-prompt")
            transcript_path = agent_folder / f"transcript_{clean_title}_{timestamp}.md"
            transcript_path.write_text(f"# Transcript\n\n**Video ID:** {video_id}\n\n{full_transcript}", encoding="utf-8")

            st.success(f"✅ Files saved to Agents/YouTube-Forge/")

            # Create Index Note in MOCs
            index_content = f"""---
title: "YouTube-Forge - {clean_title}"
tags: [youtube-forge, index]
created: {datetime.now().strftime("%Y-%m-%d")}
---

# {clean_title} - Video Processing Results

- **Transcript**: [[transcript_{clean_title}_{timestamp}.md]]
- **Summary**: [[{Path(summary_path).name}]]
- **Action Items**: [[{Path(action_path).name}]]
- **Build Prompt**: [[{Path(prompt_path).name}]]

---
*Generated by Transcript Forge on {datetime.now().strftime("%Y-%m-%d")}*
"""
            index_file = moc_folder / f"YouTube-Forge_{clean_title}_{timestamp}.md"
            index_file.write_text(index_content, encoding="utf-8")

            st.info(f"Index note created in MOCs/: {index_file.name}")

            # ZIP Download
            files = {
                Path(transcript_path).name: Path(transcript_path).read_text(encoding="utf-8"),
                Path(summary_path).name: Path(summary_path).read_text(encoding="utf-8"),
                Path(action_path).name: Path(action_path).read_text(encoding="utf-8"),
                Path(prompt_path).name: Path(prompt_path).read_text(encoding="utf-8")
            }

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for name, content in files.items():
                    zip_file.writestr(name, content)

            st.download_button(
                label="📦 Download All Files (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"transcript_forge_{clean_title}_{timestamp}.zip",
                mime="application/zip",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")