### Pubmed QA Chatbot!

This repository contains the code for a chatbot that retrieves relevant articles from PubMed based on free-form user queries.

##### Capabilities:
- Retrieve relevant articles from PubMed based on user queries
- Search based on configurable parameters:
    - Number of articles to retrieve
    - Set of keywords to search for
    - Date range to search within
    - Journal of the articles
    - Author of the articles

##### How to use:
1. Clone the repository
```bash
git clone https://github.com/codamin/pubmed-chat-search.git
```

2. Install the required packages
```bash
pip install -r requirements.txt
```

3. Add the AZURE OPENAI LLM API KEY and ENDPOINT to the `.env` file
```bash
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
```

3. Run the chatbot
```bash
streamlit run app.py
```