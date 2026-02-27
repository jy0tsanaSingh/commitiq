# 🧠 CommitIQ — Cross-Meeting Execution Intelligence Engine

> Fireflies remembers your meetings. CommitIQ reasons across all of them.

Most AI meeting tools summarize one meeting at a time and stop there.
CommitIQ tracks commitments **across multiple meetings**, detects accountability
risks, and tells you where execution is breaking down — before it's too late.

---

## 🎥 Demo
[![CommitIQ Demo](https://img.youtube.com/vi/NWBih731XAw/0.jpg)](https://youtu.be/NWBih731XAw)

---

## 🚀 Live Demo
- **Demo Video:** [Watch 2-minute demo](https://youtu.be/NWBih731XAw)
- **API Docs:** Coming soon
- **Dashboard:** Coming soon

---

## 🎯 What Makes This Different

| Feature | Fireflies / Notion AI / Copilot | CommitIQ |
|---|---|---|
| Single meeting summary | ✅ | ✅ |
| Task extraction | ✅ | ✅ |
| Cross-meeting memory | ❌ | ✅ |
| Repeated unresolved topic detection | ❌ | ✅ |
| Accountability risk scoring | ❌ | ✅ |
| Natural language memory query | ❌ | ✅ |
| Execution Health Score | ❌ | ✅ |

---

## 🏗️ Architecture
```
Raw Transcript (meeting notes, email, voice summary)
        ↓
FastAPI /ingest endpoint
        ↓
LangChain Extraction Chain — gpt-4o-mini
        ↓
Structured Commitments
(task, owner, deadline, priority, is_vague)
        ↓
Dual Memory Store
├── SQLite   → structured queries by owner, meeting, status
└── ChromaDB → semantic embeddings for cross-meeting RAG
        ↓
Risk Detection Engine (pure Python)
├── No owner assigned
├── No deadline set
├── Vague commitment
├── Overloaded owner (4+ open tasks)
└── Repeated unresolved topic (cross-meeting intelligence)
        ↓
Execution Health Score (0 — 100)
Critical / At Risk / Healthy
        ↓
JSON Response + Streamlit Dashboard
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| AI Extraction | LangChain + OpenAI gpt-4o-mini |
| Structured Memory | SQLite |
| Semantic Memory | ChromaDB |
| Dashboard | Streamlit |
| Language | Python 3.11 |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ingest` | Ingest transcript, extract commitments, return risks + score |
| GET | `/api/v1/commitments` | Get all commitments, filter by owner |
| GET | `/api/v1/health-score` | Get current execution health score |
| GET | `/api/v1/risks` | Get all active risk flags |
| POST | `/api/v1/query` | Natural language question answered from memory |

---

## 📊 Sample API Response
```json
{
  "meeting_title": "Q3 Product Planning",
  "commitments_extracted": 6,
  "health_score": 57,
  "health_label": "At Risk",
  "commitments": [
    {
      "task": "Complete API documentation",
      "owner": "Abhishek",
      "deadline": "next Friday",
      "priority": "high",
      "is_vague": false
    },
    {
      "task": "Write the release notes",
      "owner": null,
      "deadline": null,
      "priority": "medium",
      "is_vague": true
    }
  ],
  "risk_flags": [
    {
      "type": "no_owner",
      "insight": "No owner assigned for: 'write the release notes'",
      "severity": "high"
    },
    {
      "type": "repeated_topic",
      "insight": "'API documentation' appeared in 2 meetings without resolution",
      "severity": "high"
    }
  ]
}
```

---

## 💬 Natural Language Query — Cross-Meeting Intelligence
```
Question: "What has Abhishek committed to?"
Answer:   "Abhishek has committed to completing the API
           documentation by next Friday."

Question: "Which commitments have no owner?"
Answer:   "The commitments with no owner are:
           1. Write the release notes
           2. Follow up with the client about the project delay"

Question: "What are the high priority tasks?"
Answer:   "The high priority tasks are:
           1. Schedule the design review session (Priya, Wednesday)
           2. Complete the API documentation (Abhishek, next Friday)
           3. Deploy the staging environment (Rishabh, tomorrow)"
```

---

## 📦 Setup & Installation

**1. Clone the repo**
```bash
git clone https://github.com/jy0tsanaSingh/commitiq.git
cd commitiq
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your OpenAI API key**
```bash
# Create a .env file in root
OPENAI_API_KEY=your_openai_key_here
```

**5. Run the API**
```bash
uvicorn app.main:app --reload
```

**6. Open API docs**
```
http://127.0.0.1:8000/docs
```

**7. Run the dashboard**
```bash
streamlit run dashboard.py
```

---

## 🧪 Running Tests
```bash
python -m tests.test_extractor
python -m tests.test_memory
python -m tests.test_risk_engine
```

---

## 📁 Project Structure
```
commitiq/
├── app/
│   ├── config.py          # Environment and settings
│   ├── schemas.py         # Pydantic data models
│   ├── extractor.py       # LangChain extraction chain
│   ├── memory.py          # SQLite + ChromaDB memory layer
│   ├── risk_engine.py     # Risk detection + health score
│   ├── routes.py          # FastAPI route handlers
│   └── main.py            # App entry point
├── tests/
│   ├── test_extractor.py
│   ├── test_memory.py
│   └── test_risk_engine.py
├── sample_transcripts/
│   └── product_planning.txt
├── dashboard.py           # Streamlit UI
├── requirements.txt
└── .env                   # Never committed
```

---

## 🗺️ Roadmap

- [ ] Jira integration for auto ticket creation
- [ ] Slack notifications for overdue commitments
- [ ] Email and Slack transcript ingestion
- [ ] Multi-user support with authentication
- [ ] LangGraph multi-agent upgrade

---

## 👩‍💻 Author

**Jyotsana Singh**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/jyotsana-singh-46b33791/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/jy0tsanaSingh)


BackendEngineering 
#LLM #VectorDatabase #OpenAI #MachineLearning #OpenToWork
