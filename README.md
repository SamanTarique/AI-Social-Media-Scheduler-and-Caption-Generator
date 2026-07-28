# AI Social Media Scheduler & Caption Generator

An AI-powered social media content generation and scheduling system developed as part of the **SafeX Solutions Internship – Week 3 Project**.

The application generates **brand-consistent, platform-optimized social media captions** using **Google Gemini Flash**, **Retrieval-Augmented Generation (RAG)**, **FAISS**, and **LangChain**. It also creates a complete **7-day content calendar** that can be exported as CSV for social media planning and management.

The system combines Large Language Models with a local knowledge base to ensure captions follow predefined brand guidelines, tone of voice, hashtags, and campaign objectives instead of relying solely on generic AI responses.

---

#  Features

*  AI-powered caption generation using Google Gemini Flash.
*  Retrieval-Augmented Generation (RAG) using FAISS and LangChain.
*  Generates platform-specific captions for different social media platforms.
*  Produces brand-aligned CTAs and verified hashtags.
* Automatically creates a complete 7-day content schedule.
*  Export generated schedules as CSV.
*  Production-ready Flask backend with Gunicorn.
*  using replit for deploy and Frontend


---

# 🛠 Tech Stack

| Category             | Technologies                             |
| -------------------- | ---------------------------------------- |
| Programming Language | Python 3.11                              |
| Backend              | Flask, Gunicorn                          |
| Frontend             | Replit                                   |
| LLM                  | Google Gemini Flash API                  |
| RAG Framework        | LangChain                                |
| Vector Database      | FAISS                                    |
| Embeddings           | sentence-transformers (all-MiniLM-L6-v2) |
| Data Processing      | Pandas, NumPy                            |
| Deployment           | Replit, Render(after upgrading), Railway |

---

# 🏗 System Workflow

```text
Knowledge Base
      │
      ▼
Document Loader
      │
      ▼
Text Chunking
      │
      ▼
FAISS Vector Database
      │
      ▼
Relevant Context Retrieval
      │
      ▼
Google Gemini Flash
      │
      ▼
Caption Generation
      │
      ▼
Weekly Scheduler
      │
      ▼
CSV Export
```

---

# 📂 Project Structure

```text
AI-Social-Media-Scheduler-and-Caption-Generator/
│
├── Knowledge_base/                 # Brand guidelines, hashtags and company knowledge
├── faiss_index/ (gitignore)        # Generated FAISS vector database
├── frontend/                       # Replit frontend
├── output/                         # Generated weekly calendars
│
├── app.py                          # Flask application
├── Ai_Scheduler_Caption_Generator.py
├── Gemni_Services.py
├── Rag.py
├── Knowladge_loader.py
│
├── requirements.txt
├── Procfile
├── README.md
└── .env(git ignored)
```

---

# 🚀 Getting Started

## Prerequisites

* Python 3.11
* Google Gemini API Key

---

## 1. Clone Repository

```bash
git clone https://github.com/SamanTarique/AI-Social-Media-Scheduler-and-Caption-Generator.git

cd AI-Social-Media-Scheduler-and-Caption-Generator
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
Saman2_api=YOUR_GEMINI_API_KEY

PORT=5000
```

> Replace `YOUR_GEMINI_API_KEY` with your own Gemini API key.

---

## 5. Run the Application

```bash
python app.py
```

Open your browser:

```
http://localhost:5000
```

---

# 🌐 Deployment

## Flask Deployment (Recommended)

The repository is configured for Flask deployment using Gunicorn.

**Procfile**

```procfile
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 180
```

This configuration works on platforms such as:

* Replit
* Railway
* Any Gunicorn-compatible hosting provider

---

##  Deployment Resource Requirements

This project uses:

* SentenceTransformer embeddings
* FAISS vector search
* LangChain
* Google Gemini Flash
* Flask API

Because these components load AI models and vector indexes into memory, the application generally requires **approximately 800 MB to 1.2 GB of RAM**, depending on the hosting environment.

Platforms limited to **512 MB RAM** may terminate the application with an **Out of Memory (OOM)** error.

> **Note:** The project was successfully deployed and tested on **Replit**. However, publishing it publicly on Replit requires an upgraded plan. If you encounter memory-related issues on free hosting services, deploying on a platform that provides **1 GB RAM or more** is recommended.

---

# 📱 Alternative Streamlit Version

A separate **Streamlit implementation** of this project is also available in another branch of this repository.

If you prefer building or deploying the project with **Streamlit** instead of **Flask**, you can use that version.

### Switch to the Streamlit branch

```bash
git checkout streamlit
```

### Run the Streamlit application

```bash
streamlit run streamlit_app.py
```

### Procfile for Streamlit

```procfile
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

The Streamlit version is intended for users who prefer a lightweight interface while keeping the same AI generation workflow.

---

#  Example Output

The application generates:

* AI-generated captions
* Platform-specific content
* Call-to-actions (CTAs)
* Verified hashtags
* Weekly content calendar
* Downloadable CSV schedule

---

# 📸 Demo

A demonstration video showing the complete workflow of the project is available.

> **Demo Video:** *(Add your Google Drive or YouTube link here.)*

---

#  Future Improvements

* Multi-language caption generation
* Image generation support
* Direct publishing through social media APIs
* Analytics dashboard
* Multiple brand support
* User authentication
* Campaign performance insights

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👩‍💻 Author

**Saman Tarique**

BS Artificial Intelligence Student

Developed during the **SafeX Solutions Internship (Week 3 Project)** as part of an AI-based automation initiative.
