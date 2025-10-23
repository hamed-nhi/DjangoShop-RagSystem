# 🛍️ DjangoShop RAG System
**An Intelligent E-commerce Platform for Laptops with an AI Shopping Assistant based on LLM & RAG**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-4.0%2B-success.svg)](https://www.djangoproject.com/)
[![Project Status](https://img.shields.io/badge/status-completed-green.svg)]()

---

A **modern, intelligent e-commerce platform** built with the **Django framework**, designed for laptop and accessory sales. This project integrates a sophisticated **AI Shopping Assistant** that allows users to search, compare, and add products to their cart using **natural language**.

The core of this project is built on a **Retrieval-Augmented Generation (RAG)** architecture and a powerful **Hybrid Search** system, combining **FAISS** (for semantic vector search) and **Meilisearch** (for fast, typo-tolerant keyword search) to deliver the most accurate and relevant results.

---

## 📸 Screenshots

| Home Page | Product Listing Page |
| :---: | :---: |
| ![Home Page](screenshots/homepage.png) | ![Product Page](screenshots/products-page.png) |
| **AI Assistant (Widget)** | **AI Assistant (Full Page)** |
| ![AI Assistant Widget](screenshots/widget-chatbot.png) | ![AI Assistant Chat](screenshots/chatbot.png) |
| **Product Comparison** | **User Account Page** |
| ![Product Comparison](screenshots/compare-product.png) | ![User Account Page](screenshots/account-page.png) |
---

## 🚀 Key Features

-   **🧠 AI Shopping Assistant ("Hushyar")**: An intelligent agent powered by LangChain capable of understanding conversational context, answering complex queries, providing recommendations, and executing actions.
-   **🔍 Hybrid Search System**: Merges semantic search (Vector Search) with **FAISS** to understand *intent* and keyword search with **Meilisearch** for *precision* and typo tolerance.
-   **💬 Real-time Streaming Chat**: AI responses are streamed token-by-token using Django's `StreamingHttpResponse` for a natural and live chat experience.
-   **🛒 Full E-commerce Functionality**:
    -   Complete user authentication (registration, login, user profile).
    -   Shopping cart and checkout process.
    -   Order history and management.
    -   Product review and scoring system.
    -   Favorites / Wishlist functionality.
-   **⚙️ Powerful Admin Panel**: Full management of products, categories, brands, orders, and users via the built-in Django Admin.
-   **📦 Product Comparison System**: Ability to add products to a comparison list and view a side-by-side feature table.
-   **📱 Responsive UI**: Built with HTML, CSS, Bootstrap, and JavaScript (AJAX) to work seamlessly on desktop and mobile devices.
-   **🧩 Modular Architecture**: Clean Separation of Concerns (SoC) using distinct Django apps for high scalability and maintainability.

---

## 🧰 Tech Stack & Rationale

| Category | Technologies Used |
| :--- | :--- |
| **Backend** | Django, Django REST Framework (DRF), Python |
| **Frontend** | HTML, CSS, Bootstrap, JavaScript, AJAX |
| **Database** | PostgreSQL |
| **AI Orchestration** | LangChain |
| **Search (Hybrid)** | **FAISS** (Semantic), **Meilisearch** (Keyword) |
| **AI Models** | LLM (e.g., OpenAI API), Local Embeddings (Sentence-Transformers) |
| **Architecture** | Multi-layered (Presentation, Business Logic, Data Access, AI Layer) |

---

### Why This Tech Stack?

-   **Django & PostgreSQL**: Chosen for stability, security, scalability, and the rich ecosystem (ORM, Admin Panel), forming the robust core of the e-commerce platform.
-   **LangChain**: Acts as the "nervous system" of the AI assistant. It allows us to build a true **Agent**, equip it with "Tools", and orchestrate the complex RAG logic.
-   **Meilisearch (Keyword Search)**:
    -   **Lightning Fast**: Delivers results in milliseconds.
    -   **Typo Tolerance**: Its most significant advantage. If a user searches for "Laptob," Meilisearch intelligently returns results for "Laptop," which is critical for a good user experience.
    -   **Excellent Persian Support**: Optimized for Persian language out-of-the-box.
-   **FAISS (Semantic Search)**:
    -   **Local Execution**: Unlike cloud Vector DBs, Faiss is a library and runs locally. This means **zero cost** and **complete data privacy**.
    -   **High Speed**: Written in C++, it's highly optimized for similarity search among millions of vectors.
-   **Local Embedding Model**:
    -   Uses `paraphrase-multilingual-MiniLM-L12-v2`.
    -   **Privacy & Cost**: By running the model locally, no product data is sent to external APIs for embedding, and there are no per-token embedding costs.

---

## 🧠 AI & RAG Deep Dive

The innovative core of this project is the AI assistant "Hushyar". This is not just a simple RAG implementation; it's an intelligent **Agent** with advanced capabilities.

### 1. Weighted Hybrid Retriever
We use a weighted **RRF (Reciprocal Rank Fusion)** algorithm. In an e-commerce store, an exact model name match (keyword) is often more important than general semantic similarity. Therefore, **Meilisearch** results are given more weight (`MEILI_WEIGHT = 2.0`) than **FAISS** results (`FAISS_WEIGHT = 1.0`) to ensure exact matches always rank higher.

### 2. Advanced Prompt Engineering
A detailed system prompt was engineered for "Hushyar" that defines its:
-   **Persona**: Defines it as an "expert and polite sales assistant".
-   **Rules of Engagement**: Instructs it on handling ambiguous queries (e.g., by asking for "budget" or "use case") and how to analyze prices.
-   **Tool-Based Behavior**: Instructed to *analyze* tool outputs, not just list them (e.g., "explain that 16GB of RAM is great for multitasking").
-   **Output Formatting**: Strict rules for formatting product lists to be parsed by the frontend.

### 3. LangChain Agent Tools
"Hushyar" is equipped with custom `@tool`s to interact with the store:

-   `search_products(query, brand, price_min, price_max)`: Invokes the hybrid search with dynamic filters.
-   `get_product_details(product_id)`: Fetches full specifications for a single product from the database.
-   `compare_products(product_ids: List[int])`: Takes a list of IDs and dynamically generates a full comparison table in **Markdown** format.
-   `add_to_cart(product_id)`: **(Advanced)** This tool uses a custom Middleware to access the current user's `request` object and adds the product directly to their session-based cart.

### 4. AI Flow Architecture

```mermaid
flowchart TD
    A["💬 User sends message (Widget or Full Page)"] --> B["API: /chat/ View"]
    B --> C{Widget or Full Page Request?}
    C --> D["Retrieve or Create Conversation from DB"]
    D --> E["Prepare Chat History"]
    E --> F["🧠 Invoke LangChain Agent"]
    F -- "1️⃣ Query" --> G["🔍 Hybrid Retriever (RRF)"]
    G -- "→ FAISS" --> H["Vector DB (Semantic)"]
    G -- "→ Meilisearch" --> I["Keyword DB (Typo-Tolerant)"]
    I & H --> G
    G -- "2️⃣ Context" --> F
    F -- "3️⃣ (Optional)" --> J["🛠️ Call Tool (e.g. compare_products, add_to_cart)"]
    J -- "4️⃣ Tool Output" --> F
    F -- "5️⃣" --> K["🤖 LLM Generates Final Response"]
    K --> L["⚡ Stream Response (Token-by-Token) to User"]
    L --> M["🗂️ Save User & AI Messages to DB"]

```


### 🏗️ System Architecture
```bash

DjangoShop-RagSystem/
├── Shop/                 # Core Django project config and settings
├── apps/
│   ├── accounts/         # User authentication, registration, and profiles
│   ├── products/         # Product catalog, brands, categories, filtering
│   ├── orders/           # Shopping cart, checkout, and order processing
│   ├── ai_assistant/     # The AI core: Agent, Tools, RAG, and chat logic
│   ├── c_s_f/            # Comments, Scoring, Favorites
│   └── warehouse/        # Inventory and stock management
├── templates/            # HTML files using Django Template Engine
├── static/               # CSS, JS, Bootstrap, and images
└── media/                # User-uploaded product images
```




### ⚙️ Installation & Setup
## 🧾 Prerequisites
Python 3.8+ 

PostgreSQL  (Create an empty database)

Meilisearch (The Meilisearch server must be running. Install Guide) 

# 📥 Installation Steps
1. Clone the repository

```bash

git clone [https://github.com/hamed-nhi/DjangoShop-RagSystem.git](https://github.com/hamed-nhi/DjangoShop-RagSystem.git)
cd DjangoShop-RagSystem
Create and activate a virtual environment
```
```bash

python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables Rename .env.example to .env:

```bash

cp .env.example .env
```
Then, edit the .env file with your credentials:

```codesnippet
DEBUG=True
SECRET_KEY=your-django-secret-key

# PostgreSQL Database URL
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME

# Meilisearch Config
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=your-meilisearch-api-key

# Language Model API Key
OPENAI_API_KEY=your-openai-api-key
Run database migrations
```
```bash


python manage.py migrate
```
Index data into search engines (You must first load data, e.g., via the admin panel or a custom script ) To index your product data into Meilisearch and Faiss, you may need to use custom management commands:



```bash
# (Note: These are examples; you may need to create these commands)
python manage.py index_products_meili
python manage.py index_products_faiss
```


Run the development server



```bash

python manage.py runserver
```
The site is now available at http://127.0.0.1:8000.

💡 Example AI Use Cases
💬 "Hi, I'm looking for a gaming laptop under 90 million Toman." OR say it in persian

🔍 "Compare the Asus TUF F15 with the HP Victus 15 for me."

💡 "What do you recommend for programming and university work? My budget is low."

🧾 "Is the Lenovo IdeaPad 5 in stock? Add it to my cart."


### 👥 Contributing
Contributions are welcome! To contribute:

Fork the repository.

Create your feature branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m "Add AmazingFeature").

Push to your branch (git push origin feature/AmazingFeature).

Open a Pull Request.

### 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

### 📞 Contact
Hamed Nahali 

GitHub Profile

For collaboration or questions, please open an Issue on GitHub.
