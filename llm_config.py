from crewai import LLM
from langchain_openai import ChatOpenAI

import os
os.environ['OPENAI_API_KEY'] = 'testapikey'
ollama_llm = ChatOpenAI(
    model="ollama/llama3",
    base_url="http://localhost:11434",
    api_key="NA"  # placeholder, avoids OpenAI key check
)
