Norwegian Immigration AI Agent (RAG)
A Retrieval Augmented Generation (RAG) system that answers questions about Norwegian immigration rules based on official UDI documentation.

Project Overview : This project is an educational AI assistant designed to navigate the regulations of the Norwegian Directorate of Immigration (UDI). Unlike standard LLMs which often hallucinate legal details this system uses RAG (Retrieval Augmented Generation) 
to ground every answer in verified documentation scraped directly from udi.no.

Ethical Data Pipeline: Implemented a respectful scraper that adheres to robots.txt,filters utility pages and enforces rate limiting (2s delay) to zero load the target servers.
Production Ready API: Built with FastAPI exposing an OpenAI compatible endpoint (/v1/chat/completions) allowing seamless integration with existing frontend tools (Chatbox, LibreChat, etc.).
Hybrid Architecture: Designed to support Hybrid RAG, utilizing OpenAI for high precision embeddings while allowing local LLMs (like Llama 3 via Ollama) for inference to reduce costs and enhance privacy.
Self Correcting Evaluation: Includes a custom benchmarking suite that generates synthetic test data, audits it for hallucinations using an "LLM as a Judge" approach, and grades the model's accuracy.

ETL Pipeline:

Extract: Parses sitemap.xml to identify valid content pages.

Transform: Cleans raw HTML (removing navbars, forms, and scripts) using BeautifulSoup.

Load: Chunks text into semantic segments and indexes them into ChromaDB.

Retrieval: Uses OpenAI Embeddings (text embedding 3 small) to locate the top k most relevant legal paragraphs.

Generation: Synthesizes the retrieved context into a precise answer using strict system prompts to prevent hallucination.

Prerequisites: 

-Python 3.10+

-Docker Desktop (Optional, for containerization)

-An OpenAI API Key

1. Installation

# Clone the repository
git clone https://github.com/kimia1999/norwegian-rag-bot.git
cd norwegian-rag-bot
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
