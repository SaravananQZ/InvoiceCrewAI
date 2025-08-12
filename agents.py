from dotenv import load_dotenv
# from crewai import LLM
from crewai import Agent
import os

from llm_config import ollama_llm

# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# llm = LLM(model="gpt-4o-mini", temperature=0)
# llm=LLM(model="ollama/llama3", base_url="http://localhost:11434")

initInvoiceAgent=Agent(
    role="Invoice extractor and decision maker",
    backstory="you are the invoice analyzer and convert them to json file for next level process",
    goal="Get invoice pdfs from testdata folder and read them and write to json files in dataoutput folder and update the names and unique value into 'InvoiceLog.xlsx'",
    verbose=True,
    memory=True,
    llm=ollama_llm,
    prompt="""
    Convert the pdf data into json files using ReadandWritePDF tool.
    After converted all pdf file into json files ,Get Json file name and update it into "Filename" column
    and update it into excel for correstponding column [Filename]
"""
)

invoice_Amount_Validation_Agent=Agent(
    role="Invoice Total Amount Validation",
    backstory="you are the invoice amount validator and based on critiria mentioned in below points,read  the json files from dataoutput folder and  update",
    goal="Extract Total Amount from each JSON files and follow the rules and  update the 'First Level' ,'Second Level' or 'Direct Process' to 'InvoiceLog.xlsx' columns",
    verbose=True,
    memory=True,
    llm=ollama_llm,
)
invoice_Vendor_Validation_Agent=Agent(
    role="Invoice Vendor Validation",
    backstory="you are the invoice vendor checker and based on critiria ,take the json files from dataoutput folder and  process it vendor valid or invalid",
    goal="Extract the vendor name from JSON files and check it with vendor names which is available in validVendors.txt and update to 'InvoiceLog.xlsx' columns",
    verbose=True,
    memory=True,
    llm=ollama_llm,
)

invoice_filegroup_Agent=Agent(
    role="Invoice File Organzier",
    backstory="Read The InvoiceLog.xlsx each columns and Move it to Appropirate folders",
    goal="Read the invoicelog.xlsx columns and based on 'PostProcess' column and 'Vendor Status' values ,copy and paste the correspoinding PDF files to that folders ['First Level','Second Level','Invalid Vendor']",
    verbose=True,
    memory=True,
    llm=ollama_llm,
)