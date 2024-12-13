from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama.llms import OllamaLLM

import requests
from langchain_openai.chat_models import AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")

model = AzureChatOpenAI(
    deployment_name="gpt4",
    model_name="gpt-4",
    openai_api_version="2023-05-15",
)

class KeywordExtractorBot:
    def __init__(self):
        self.template = """Question: Return the list of keywords in this question asked by a user, separated by commas.
            Only extract the keywords that would help searching relevant articles in the pubmed database.
            Keyword must not have white spaces.
            Wrap the answer in <answer></answer> tags. Here is the question:
            {question}"""

        prompt = ChatPromptTemplate.from_template(self.template)
        self.chain = prompt | model

    def llm_clean_answer(self, result: str) -> str: 
        start = result.content.find("<answer>")
        end = result.content.find("</answer>")
        keywords = result.content[start+len("<answer>"):end].split(",")
        return [keyword.strip() for keyword in keywords]
    
    def get_keywords(self, user_input: str) -> list:
        result = self.chain.invoke({"question": {user_input}})
        return self.llm_clean_answer(result)
    

class AbstractExtractorBot:
    def __init__(self):
        self.template = """Question: Extract the abstract of the document from the following text. Ignore the rest of the text.
            Wrap the answer in <answer></answer> tags.
            {question}"""

        prompt = ChatPromptTemplate.from_template(self.template)
        self.chain = prompt | model
        
    def get_abstract(self, abstract_raw) -> str:
        result = self.chain.invoke({"question": {abstract_raw}})
        abstract = result.content.strip("<answer>").strip("</answer>").strip()

        return abstract

def construct_search_query(keywords, sdate=None, edate=None, author=None, journal=None):
    query = " AND ".join(keywords)
    if author:
        query += f" AND {author}[AUTH]"
    if journal:
        query += f" AND {journal}[JOUR]"
    if sdate and edate:
        query += f" AND ({sdate}[PDAT] : {edate}[PDAT])"

    return query

# pubmed api
def search_pubmed(config: dict):
    keywords = config["keywords"]
    sdate = config["sdate"]
    edate = config["edate"]
    author = config["author"]
    journal = config["journal"]
    retmax = config["retmax"]

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    # filter by journal, author, time range
    params = {
        "db": "pubmed",
        "term": construct_search_query(keywords, sdate, edate, author, journal), 
        "retmax": retmax,
        "retmode": "json"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_doc_details(pubmed_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "json"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_abstract(pubmed_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "text",
        "rettype": "abstract",
        "retmode": "text"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.text

def run(user_input: str, config: dict):
    keyword_extractor_bot = KeywordExtractorBot()
    chat_keywords = keyword_extractor_bot.get_keywords(user_input)
    print("keywords extracted:", chat_keywords)
    config["keywords"] = chat_keywords + config["keywords"]
    print("keywords extracted:", config["keywords"] )

    response = search_pubmed(config)
    pubmed_ids = response["esearchresult"]["idlist"][0:config["retmax"]]

    if not pubmed_ids:
        return

    for pubmed_id in pubmed_ids:
        details = fetch_doc_details(pubmed_id)
        abstract_raw = fetch_abstract(pubmed_id)
        abstract_extractor_bot = AbstractExtractorBot()
        abstract = abstract_extractor_bot.get_abstract(abstract_raw)
        yield {
            "doc_id": pubmed_id,
            "doc_details": details,
            "doc_abstract": abstract
        }