# 🛍️ DjangoShop RAG System | سامانه فروشگاه هوشمند جنگو (دستیار خرید مبتنی بر هوش مصنوعی)

A **modern, intelligent e-commerce platform** built with the **Django framework**, designed for laptop and accessory sales.  
This project integrates **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG)**, and **hybrid search technologies** (FAISS + Meilisearch) to provide users with **AI-driven shopping guidance**, smart recommendations, and natural-language-based product search.

---

## 🚀 Key Features

- **🧠 AI Shopping Assistant** — Intelligent chatbot powered by LLM + LangChain  
- **🔍 Hybrid Search System** — Combines FAISS (semantic search) and Meilisearch (keyword search)  
- **💬 Real-time Streaming Chat** — Token-by-token chat streaming for natural AI conversations  
- **🛒 Full E-commerce Functionality** — User authentication, cart, checkout, orders, reviews  
- **⚙️ Admin Panel** — Complete product, order, and user management with Django Admin  
- **📦 Product Comparison System** — Compare multiple products in real-time  
- **📱 Responsive UI** — Built with HTML, CSS, Bootstrap, and JavaScript  
- **🧩 Modular Architecture** — Clean separation of concerns for scalability and maintainability  

---

## 🧰 Tech Stack

| Category | Technologies |
|-----------|--------------|
| **Backend** | Django, Django REST Framework (DRF), Python |
| **Frontend** | HTML, CSS, Bootstrap, JavaScript, AJAX |
| **Database** | PostgreSQL |
| **Search** | FAISS (semantic vector search), Meilisearch (keyword search) |
| **AI/ML** | LangChain, OpenAI API, Local Embedding Models (Sentence-Transformers) |
| **Caching / Queues** | Redis |
| **Architecture** | Multi-layered (Presentation, Business Logic, Data Access, AI Layer) |
| **Deployment Ready** | Easily containerizable with Docker (optional) |

---

## 🧠 AI & RAG Overview

The system leverages **LangChain** to orchestrate LLM interactions and **RAG (Retrieval-Augmented Generation)** to enhance accuracy and contextuality.

- **LLM Core:** Processes user requests and generates natural responses.  
- **Retriever:** Hybrid mechanism combining:
  - `FAISS` for **semantic vector search**
  - `Meilisearch` for **keyword-based ranking**
- **Prompt Engineering:** Carefully designed rules and persona for the “AI Laptop Sales Assistant.”
- **Local Embeddings:** Uses multilingual Sentence-Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) for private, cost-free inference.

---

## 🏗️ System Architecture

DjangoShop-RagSystem/
├── Shop/ # Django project configuration
├── apps/
│ ├── accounts/ # Authentication and user management
│ ├── products/ # Product catalog and filtering
│ ├── orders/ # Cart, checkout, and order processing
│ ├── ai_assistant/ # Core AI and RAG system (LLM integration)
│ ├── search/ # Hybrid FAISS + Meilisearch integration
│ └── c_s_f/ # Comments, scoring, favorites
├── templates/ # HTML templates
├── static/ # JS, CSS, images
└── media/ # Uploaded product images


---

## 📸 Screenshots

### 🏠 Home Page  
*(Insert your screenshot here — e.g. `screenshots/home.png`)*

### 🤖 AI Chat Assistant  
*(Insert your screenshot here — e.g. `screenshots/chat.png`)*

### 🔎 Product Search  
*(Insert your screenshot here — e.g. `screenshots/search.png`)*

---

## ⚙️ Installation & Setup

### 🧾 Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL
- Redis
- Meilisearch server running locally or remotely

---

### 📥 Installation Steps

1. **Clone the repository**
   ```
   git clone https://github.com/hamed-nhi/DjangoShop-RagSystem.git
   cd DjangoShop-RagSystem
Create a virtual environment

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install dependencies


pip install -r requirements.txt
Set up environment variables

cp .env.example .env
# Then edit .env with your own credentials
Example .env:

env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/djangoshop
REDIS_URL=redis://localhost:6379
MEILISEARCH_URL=http://localhost:7700
OPENAI_API_KEY=your-openai-api-key
Run database migrations


python manage.py migrate
Start the development server


python manage.py runserver

### 🤖 How the AI Assistant Works

### 🤖 How the AI Assistant Works

```mermaid
flowchart TD
    A[💬 User interacts via chat page or widget] --> B[🔍 Preprocessing & Embedding using local model]
    B --> C[🧠 Hybrid Retriever combines FAISS + Meilisearch]
    C --> D[📄 Retrieve relevant product data and context]
    D --> E[⚙️ LangChain orchestrates LLM call with context]
    E --> F[🗣️ LLM generates natural-language response]
    F --> G[💡 Stream token-by-token response to frontend]
    G --> H[🎯 User receives AI-powered answer & recommendations]
```

1- User interacts through the chat widget or chat page.

2- User query → pre-processed and embedded using a local embedding model.

3- Hybrid retriever fetches relevant product data using FAISS + Meilisearch.

4- Retrieved context is passed to the LLM via LangChain.

5- he LLM generates a natural-language answer with suggestions and explanations.

6- Responses stream token-by-token to the frontend for a live chat experience.

## 🧩 Example Use Cases
💬 “Find me a gaming laptop with RTX 4060 and at least 16GB RAM.”

🔍 “Compare Asus TUF F15 with HP Victus 15.”

💡 “Suggest laptops under 50 million toman for programming.”

🧾 “Add Lenovo IdeaPad 5 to my cart.”

💻 Development Notes
Streaming Responses: Implemented with Django’s StreamingHttpResponse for real-time LLM output.

Prompt Engineering: Defines assistant persona, tone, and safety constraints.

Custom Tools: LangChain tools for searching, comparison, cart updates, and product details retrieval.

Secure by Design: No external API calls for embedding; full privacy control.

### 👥 Contributing
Contributions are welcome!
To contribute:

Fork the repository

Create your feature branch:



git checkout -b feature/AmazingFeature
Commit your changes:



git commit -m "Add AmazingFeature"
Push to your branch:



git push origin feature/AmazingFeature
Open a Pull Request

## 📜 License
This project is licensed under the MIT License.
See the LICENSE file for details.

## 📞 Contact
Hamed Nahali
GitHub Profile
📧 For collaboration or questions, feel free to reach out via GitHub Issues.