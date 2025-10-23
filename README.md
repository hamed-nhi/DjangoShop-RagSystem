# 🛍️ DjangoShop RAG System
**An Intelligent E-commerce Platform for Laptops with an AI Shopping Assistant based on LLM & RAG**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-4.0%2B-success.svg)](https://www.djangoproject.com/)
[![Project Status](https://img.shields.io/badge/status-completed-green.svg)]()

---

[cite_start]A **modern, intelligent e-commerce platform** built with the **Django framework** [cite: 69][cite_start], designed for laptop and accessory sales[cite: 7]. [cite_start]This project integrates a sophisticated **AI Shopping Assistant** that allows users to search, compare, and add products to their cart using **natural language**[cite: 70, 826].

[cite_start]The core of this project is built on a **Retrieval-Augmented Generation (RAG)** [cite: 78, 342] [cite_start]architecture and a powerful **Hybrid Search** system [cite: 77, 831][cite_start], combining **FAISS** (for semantic vector search) [cite: 73, 359] [cite_start]and **Meilisearch** (for fast, typo-tolerant keyword search) [cite: 73, 390] [cite_start]to deliver the most accurate and relevant results[cite: 74, 831].

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

-   [cite_start]**🧠 AI Shopping Assistant ("Hushyar")**: An intelligent agent powered by LangChain [cite: 73, 352] [cite_start]capable of understanding conversational context, answering complex queries, providing recommendations, and executing actions[cite: 70, 116, 826].
-   [cite_start]**🔍 Hybrid Search System**: Merges semantic search (Vector Search) with **FAISS** [cite: 359] [cite_start]to understand *intent* and keyword search with **Meilisearch**  [cite_start]for *precision* and typo tolerance[cite: 394].
-   [cite_start]**💬 Real-time Streaming Chat**: AI responses are streamed token-by-token using Django's `StreamingHttpResponse` [cite: 753] [cite_start]for a natural and live chat experience[cite: 754].
-   **🛒 Full E-commerce Functionality**:
    -   [cite_start]Complete user authentication (registration, login, user profile)[cite: 157].
    -   [cite_start]Shopping cart and checkout process[cite: 157].
    -   [cite_start]Order history and management[cite: 157, 162].
    -   [cite_start]Product review and scoring system[cite: 157, 257].
    -   [cite_start]Favorites / Wishlist functionality[cite: 157, 258].
-   [cite_start]**⚙️ Powerful Admin Panel**: Full management of products, categories, brands, orders, and users via the built-in Django Admin[cite: 147, 161, 475].
-   [cite_start]**📦 Product Comparison System**: Ability to add products to a comparison list and view a side-by-side feature table[cite: 157, 542, 543].
-   [cite_start]**📱 Responsive UI**: Built with HTML, CSS, Bootstrap, and JavaScript (AJAX) to work seamlessly on desktop and mobile devices[cite: 218, 286, 289, 293, 297].
-   [cite_start]**🧩 Modular Architecture**: Clean Separation of Concerns (SoC) using distinct Django apps for high scalability and maintainability[cite: 215, 428].

---

## 🧰 Tech Stack & Rationale

| Category | Technologies Used |
| :--- | :--- |
| **Backend** | [cite_start]Django [cite: 308][cite_start], Django REST Framework (DRF) [cite: 311][cite_start], Python  |
| **Frontend** | [cite_start]HTML [cite: 286][cite_start], CSS [cite: 289][cite_start], Bootstrap [cite: 297][cite_start], JavaScript, AJAX [cite: 293, 479] |
| **Database** | [cite_start]PostgreSQL [cite: 72, 325] |
| **AI Orchestration** | [cite_start]LangChain [cite: 73, 352] |
| **Search (Hybrid)** | [cite_start]**FAISS** (Semantic) [cite: 359][cite_start], **Meilisearch** (Keyword)  |
| **AI Models** | [cite_start]LLM (e.g., OpenAI API) [cite: 329][cite_start], Local Embeddings (Sentence-Transformers) [cite: 412] |
| **Architecture** | [cite_start]Multi-layered (Presentation, Business Logic, Data Access, AI Layer) [cite: 215, 217, 220, 221, 223] |

---

### Why This Tech Stack?

-   [cite_start]**Django & PostgreSQL**: Chosen for stability, security, scalability, and the rich ecosystem (ORM, Admin Panel), forming the robust core of the e-commerce platform[cite: 308, 309, 325, 328].
-   [cite_start]**LangChain**: Acts as the "nervous system" of the AI assistant[cite: 355]. [cite_start]It allows us to build a true **Agent**, equip it with "Tools" [cite: 356][cite_start], and orchestrate the complex RAG logic[cite: 352, 356].
-   **Meilisearch (Keyword Search)**:
    -   [cite_start]**Lightning Fast**: Delivers results in milliseconds[cite: 393].
    -   **Typo Tolerance**: Its most significant advantage. [cite_start]If a user searches for "Laptob," Meilisearch intelligently returns results for "Laptop," which is critical for a good user experience[cite: 394].
    -   [cite_start]**Excellent Persian Support**: Optimized for Persian language out-of-the-box[cite: 396, 405].
-   **FAISS (Semantic Search)**:
    -   [cite_start]**Local Execution**: Unlike cloud Vector DBs, Faiss is a library and runs locally[cite: 372]. [cite_start]This means **zero cost** and **complete data privacy**[cite: 374, 375].
    -   [cite_start]**High Speed**: Written in C++, it's highly optimized for similarity search among millions of vectors[cite: 369, 371].
-   **Local Embedding Model**:
    -   [cite_start]Uses `paraphrase-multilingual-MiniLM-L12-v2`[cite: 414].
    -   [cite_start]**Privacy & Cost**: By running the model locally, no product data is sent to external APIs for embedding [cite: 420][cite_start], and there are no per-token embedding costs[cite: 421].

---

## 🧠 AI & RAG Deep Dive

The innovative core of this project is the AI assistant "Hushyar". This is not just a simple RAG implementation; it's an intelligent **Agent** with advanced capabilities.

### 1. Weighted Hybrid Retriever
[cite_start]We use a weighted **RRF (Reciprocal Rank Fusion)** algorithm[cite: 581]. In an e-commerce store, an exact model name match (keyword) is often more important than general semantic similarity. [cite_start]Therefore, **Meilisearch** results are given more weight (`MEILI_WEIGHT = 2.0`) than **FAISS** results (`FAISS_WEIGHT = 1.0`) [cite: 583, 584] [cite_start]to ensure exact matches always rank higher[cite: 585].

### 2. Advanced Prompt Engineering
[cite_start]A detailed system prompt was engineered for "Hushyar" that defines its[cite: 593]:
-   [cite_start]**Persona**: Defines it as an "expert and polite sales assistant"[cite: 595].
-   [cite_start]**Rules of Engagement**: Instructs it on handling ambiguous queries (e.g., by asking for "budget" or "use case") [cite: 596] [cite_start]and how to analyze prices[cite: 596].
-   [cite_start]**Tool-Based Behavior**: Instructed to *analyze* tool outputs, not just list them (e.g., "explain that 16GB of RAM is great for multitasking")[cite: 597].
-   [cite_start]**Output Formatting**: Strict rules for formatting product lists to be parsed by the frontend[cite: 598].

### 3. LangChain Agent Tools
[cite_start]"Hushyar" is equipped with custom `@tool`s [cite: 628] to interact with the store:

-   [cite_start]`search_products(query, brand, price_min, price_max)`: Invokes the hybrid search with dynamic filters[cite: 630, 631, 640].
-   [cite_start]`get_product_details(product_id)`: Fetches full specifications for a single product from the database[cite: 703, 706, 707].
-   [cite_start]`compare_products(product_ids: List[int])`: Takes a list of IDs and dynamically generates a full comparison table in **Markdown** format[cite: 670, 675, 699].
-   [cite_start]`add_to_cart(product_id)`: **(Advanced)** This tool uses a custom Middleware [cite: 723] [cite_start]to access the current user's `request` object and adds the product directly to their session-based cart[cite: 723, 731, 735, 736].

### 4. AI Flow Architecture

```mermaid
flowchart TD
    A[💬 User sends message (Widget or Full Page)] --> B(Api/chat/ View)
    B --> C{Widget or Full Page Request?}
    C --> D[Retrieve or Create Conversation from DB]
    D --> E[Prepare Chat History]
    E --> F[🧠 Invoke LangChain Agent]
    F -- 1. Query --> G[🔍 Hybrid Retriever (RRF)]
    G -- Faiss --> H[Vector DB (Semantic)]
    G -- Meilisearch --> I[Keyword DB (Typo-Tolerant)]
    I & H --> G
    G -- 2. Context --> F
    F -- 3. (Optional) --> J[🛠️ Call Tool (e.g., compare_products, add_to_cart)]
    J -- 4. Tool Output --> F
    F -- 5. --> K[🤖 LLM Generates Final Response]
    K --> L[⚡️ Stream Response (Token-by-Token) to User]
    L --> M[Save User & AI Messages to DB]

```



### 🏗️ System Architecture
The project is organized into modular Django apps for clear separation of concerns.

DjangoShop-RagSystem/
├── Shop/           # Core Django project config and settings
├── apps/
│ ├── accounts/     # User auth, registration, and profiles [cite: 430]
│ ├── products/     # Product catalog, brands, categories, filtering [cite: 431]
│ ├── orders/       # Shopping cart, checkout, and order processing [cite: 432]
│ ├── ai_assistant/ # The AI core: Agent, Tools, RAG, and chat logic [cite: 435]
│ ├── c_s_f/        # Comments, Scoring, Favorites [cite: 434]
│ └── warehouse/    # Inventory and stock management [cite: 436]
├── templates/      # HTML files using Django Template Engine [cite: 317]
├── static/         # CSS, JS, Bootstrap, and images
└── media/          # User-uploaded product images




### ⚙️ Installation & Setup
## 🧾 Prerequisites
Python 3.8+ 

PostgreSQL  (Create an empty database)

Meilisearch (The Meilisearch server must be running. Install Guide) 

# 📥 Installation Steps
Clone the repository

Bash

git clone [https://github.com/hamed-nhi/DjangoShop-RagSystem.git](https://github.com/hamed-nhi/DjangoShop-RagSystem.git)
cd DjangoShop-RagSystem
Create and activate a virtual environment

Bash

python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
Install dependencies

Bash

pip install -r requirements.txt
Set up environment variables Rename .env.example to .env:

Bash

cp .env.example .env
Then, edit the .env file with your credentials:

Code snippet

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

Bash

python manage.py migrate
Index data into search engines (You must first load data, e.g., via the admin panel or a custom script ) To index your product data into Meilisearch and Faiss, you may need to use custom management commands:

Bash

# (Note: These are examples; you may need to create these commands)
python manage.py index_products_meili
python manage.py index_products_faiss
Run the development server

Bash

python manage.py runserver
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
