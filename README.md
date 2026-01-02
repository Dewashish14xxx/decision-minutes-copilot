# Decision-Minutes Copilot

🎙️ **Convert meeting recordings into actionable minutes with AI**

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.11+-blue)

## 🚀 Features

- **Audio Upload**: Drag-and-drop support for MP3, WAV, M4A, WebM
- **AI Transcription**: OpenAI Whisper for accurate speech-to-text
- **Smart Extraction**: GPT-4 extracts action items, owners & deadlines
- **Confidence Scores**: Visual indicators for extraction confidence
- **Human Confirmation**: Edit and approve before finalizing

## 📊 Performance

| Metric | Value |
|--------|-------|
| Transcription Accuracy | ~95% (Whisper large-v3) |
| Extraction Accuracy | TBD after eval |
| Avg Processing Time | TBD |
| Cost per Request | ~$0.05-0.10 |

## 🛠️ Setup

```bash
# Clone and enter directory
cd decision-minutes-copilot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
copy .env.example .env
# Add your OPENAI_API_KEY to .env

# Run the app
python -m app.main
```

## 📁 Project Structure

```
decision-minutes-copilot/
├── app/
│   ├── main.py          # Flask entry point
│   ├── routes.py        # API endpoints
│   └── services/        # ASR & LLM services
├── static/              # CSS & JS
├── evals/               # Test cases
└── uploads/             # Temporary audio storage
```

## 🎬 Demo

[90-second walkthrough video coming soon]

## 📝 License

MIT
