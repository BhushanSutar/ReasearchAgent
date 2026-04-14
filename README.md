# 🚀 AI Research Pipeline (Multi-Agent System)

A full-stack AI-powered research engine that performs real-time web search, content extraction, report generation, and critical evaluation using a multi-agent architecture.

Built with Flask + LangChain + LLMs + Streaming UI, this project simulates how modern AI systems like Perplexity or ChatGPT perform deep research.

---

## 🌟 Features

- 🔍 Search Agent  
  Retrieves real-time information using Tavily API  

- 📄 Reader Agent  
  Scrapes and extracts structured content from URLs  

- ✍️ Writer Agent  
  Generates a clean, structured research report  

- 🧐 Critic Agent  
  Evaluates the report with strengths, weaknesses, and score  

- ⚡ Real-Time Streaming (SSE)  
  Step-by-step pipeline updates in UI  

- 🎨 Modern UI  
  Animated pipeline, markdown rendering, clean layout  

---

## 🧠 Architecture

User Input  
↓  
Search Agent (Tavily API)  
↓  
Reader Agent (Web Scraping)  
↓  
Writer Agent (LLM Report Generation)  
↓  
Critic Agent (Evaluation)  
↓  
Frontend (Streaming UI via SSE)  

---

## 🛠️ Tech Stack

- Backend: Flask  
- AI Framework: LangChain  
- LLM: Mistral / Gemini  
- Search API: Tavily  
- Web Scraping: BeautifulSoup  
- Frontend: HTML, CSS, JavaScript  
- Streaming: Server-Sent Events (SSE)  

---

## ⚙️ Installation & Setup

### 1. Clone Repository

git clone https://github.com/your-username/your-repo-name.git  
cd your-repo-name  

---

### 2. Create Virtual Environment + Install + Run

# Create virtual environment  
python -m venv venv  

# Activate (Windows)  
venv\Scripts\activate  

# Activate (Mac/Linux)  
source venv/bin/activate  

# Install dependencies  
pip install -r requirements.txt  

# Run the application  
python app.py  

---

### 3. Setup Environment Variables

Create a `.env` file:

TAVILY_API_KEY=your_key  
MISTRAL_API_KEY=your_key  

---

### 4. Open in Browser

http://127.0.0.1:5000  
