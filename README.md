# Transcript Forge

**YouTube → Summary → Action Items → Build Prompts**

A **local-first** tool that turns any YouTube video into:
- Clean markdown transcripts
- Concise summaries
- Key action items
- Ready-to-use build prompts for AI coding assistants

Built with **Ollama**, **youtube-transcript-api**, and **Streamlit**.

![Demo](screenshot.png)

## Features

- Works with **any YouTube video** (short or long)
- Automatic **chunking** for videos > 20 minutes
- **Download all** as ZIP or individual files
- Fully local & private (nothing leaves your machine)
- Customizable model and tone

## Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/Virtuallaborer/transcript-forge.git
   cd transcript-forge
   ```

2. Install dependencies:
   ```bash
   conda create -n transcript-forge python=3.12 -y
   conda activate transcript-forge
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run transcript_forge.py
   ```

4. Paste any YouTube link and click **Forge Transcript**.

## Requirements

- [Ollama](https://ollama.com) running locally
- A model like `qwen3:8b` or `llama3.2` (pull with `ollama pull qwen3:8b`)

## Screenshots

![Main Interface](screenshot.png)
*Main interface with model selection*

![Processing](screenshot2.png)
*Chunked processing for long videos*

## Tech Stack

- **youtube-transcript-api**
- **Ollama** (local LLMs)
- **Streamlit** (beautiful UI)

## Contributing

Pull requests welcome! Open an issue for bugs or ideas.

## License

MIT © [Virtuallaborer](https://github.com/Virtuallaborer)

---

**Made for solopreneurs, knowledge workers, and AI enthusiasts.**