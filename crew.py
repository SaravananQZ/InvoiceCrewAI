from crewai import Crew,Process
from agents import initInvoiceAgent,invoice_Amount_Validation_Agent
from tasks import readLogfile_task,amountValidateTask,updatefileDetails_task
from crewai import LLM
# from llm_config import ollama_llm
import os
# crew = Crew(
#   agents=[invoice_Amount_Validation_Agent],
#   tasks=[amountValidateTask],
#   # memory=True,
#   # cache=True,
#   # max_rpm=100,
#   # share_crew=True,
#   max_iter=200,
#   # max_iter=50,
#   max_retry_limit=5

# )ollama/llama3
# os.environ["OPENAI_API_KEY"] = "sk-proj-1111" #dummy key should be  for ollama 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
crew = Crew(
  agents=[initInvoiceAgent,invoice_Amount_Validation_Agent],
  tasks=[readLogfile_task,updatefileDetails_task,amountValidateTask]
  # memory=True,
  # cache=True,
  # max_rpm=100,
  # share_crew=True,
  # max_iter=40,
  # max_iter=50,
  # max_retry_limit=5

)

# crew = Crew(
#   agents=[initInvoiceAgent],
#   tasks=[readLogfile_task,updatefileDetails_task],
#   memory=True,
#   cache=True,
#   max_rpm=100,
#   share_crew=True,
#   max_iter=100
# )


result=crew.kickoff()
print(result)
# for entry in result:
#     print(f"Filename: {entry['Filename']}, Vendor: {entry['Vendor']}, Vendor Status: {entry['Vendor Status']}, "
#           f"Line Items: {entry['Line Items']}, Total Amount: {entry['Total Amount']}, PostProcess: {entry['PostProcess']}")