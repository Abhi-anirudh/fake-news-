# Fake News & Deepfake Detection AI 🛡️

A powerful, AI-driven web application designed to combat misinformation by verifying news text and detecting deepfake or manipulated images. Powered by **Google Gemini 1.5 Flash** (or latest) and integrated with **Google Search** for real-time fact-checking.

## 🌟 Features

- **Multi-Modal Detection**: Analyze text, images, or both simultaneously.
- **Deepfake Image Analysis**: Expert visual analysis to identify AI-generated or manipulated photographs.
- **Real-Time Fact-Checking**: Integrated with Google Search to verify claims against current web data.
- **Multilingual Support**: Supports verification in multiple languages including:
  - English 🇬🇧
  - Hindi 🇮🇳 (हिंदी)
  - Marathi 🇮🇳 (मराठी)
  - Telugu 🇮🇳 (తెలుగు)
- **Detailed Verdicts**: Provides a "REAL" or "FALSE" verdict, a confidence score, and clear reasoning with extracted claims status.
- **Responsive UI**: Clean and modern interface for easy interaction.

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **AI Model**: Google Gemini Pro & Vision (via `google-genai` SDK)
- **Tools**: Google Search Integration for fact-checking
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Image Processing**: PIL (Pillow)

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A Google Gemini API Key. Get one at [Google AI Studio](https://aistudio.google.com/).

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Abhi-anirudh/fake-news-.git
   cd fake-news-
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install flask google-genai pillow
   ```

4. **Set your API Key**:
   Set an environment variable named `GEMINI_API_KEY`.
   - **Windows (PowerShell)**:
     ```powershell
     $env:GEMINI_API_KEY="your_api_key_here"
     ```
   - **Linux/Mac**:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```

### Running the Application

Start the Flask server:
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000/`

## 📁 Project Structure

- `app.py`: Main Flask backend handling API routing and Gemini integration.
- `index.html`: Landing page explaining the project.
- `detect.html`: Main detection interface.
- `assets/`: Static files (CSS, JS, Images).
- `temp_uploads/`: Temporary storage for uploaded images during analysis.
- `.gitignore`: Excludes environment files and temporary caches.

## 🛡️ How it Works

1. **Input**: User provides news text and/or an image.
2. **Analysis**: 
   - For **Text**, Gemini uses Google Search to find supporting or refuting evidence.
   - For **Images**, Gemini performs a forensic visual scan for artifacts typical of deepfakes or manipulation.
3. **Verdict**: The model returns a JSON response containing the final verdict, confidence level, and step-by-step reasoning.

---
Developed with ❤️ to build a more informed world.