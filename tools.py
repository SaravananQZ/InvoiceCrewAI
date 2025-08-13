from crewai.tools import BaseTool
# from crewai_tools.tools import PDFSearchTool
import os
import pandas as pd
import json
import fitz # PyMuPDF
# from openai import OpenAI
import pytesseract
from PIL import Image
from pdf2image import convert_from_path 
import base64
import re
import ollama
import requests
# # Initialize the tool
# file_writer_tool = FileWriterTool()

# # Write content to a file in a specified directory
# result = file_writer_tool._run('example.txt', 'This is a test content.', 'test_directory')
# print(result)
        
# This function will extract the raw text from a PDF
# openai.api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI(
#     # This is the default and can be omitted
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

client = ollama.Client(host='http://localhost:11434') 

def extract_text(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

# def gpt_to_json(text):
#     prompt = f"""
#     You are an intelligent document parser.

#     Extract structured information from the following OCR text and format it as JSON. Include fields and tables if present.

#     OCR Text:
#     {text}
#     """

#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You convert OCR text to structured JSON."},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     return response.choices[0].message.content
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def get_text_gpt(imagepath):
    prompt = "What is in this image?"
    base64_image = encode_image(imagepath)
 
    payload = {
        "model": "llama3.2-vision",
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Extract all text from the image and return it as markdown.\n"
                    "Do not describe the image or add extra text.\n"
                    "Only return the text found in the image."
                ),
                "images": [base64_image]
            }
        ]
    }
   
    response = requests.post(
        "http://localhost:11434/api/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
   
    return response.json().get('message', {}).get('content', 'No text extracted')
def extract_text_from_pdf_img(pdf_path,pdfname, output_folder="temppdfpages", dpi=300, fmt="png"):
    os.makedirs(output_folder+"\\"+pdfname, exist_ok=True)
    print(f"Converting '{pdf_path}' to images...")

    # Convert all pages
    pages = convert_from_path(pdf_path, dpi=dpi)

    textLists = []
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder,pdfname, f"page_{i+1}.{fmt}")
        page.save(image_path, fmt.upper())
        # image_paths.append(image_path)
        print(f"Saved: {image_path}")
        try:
            temptext = get_text_gpt(image_path)
            textLists.append(temptext)
        except Exception as e:
            print(e)
    return textLists

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

def getFormattedTextfromJSON(jsonfilename):
    with open(jsonfilename, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # Step 2: Get the specific text field from JSON
    # Change 'invoice_text' to the actual key in your JSON file
    invoice_text = json_data.get("content", "")

    if not invoice_text:
        raise ValueError("No invoice text found in JSON file.")

    # Step 3: Create the GPT prompt
    prompt = f"""
    You are given invoice text.
    Extract the following in JSON format:
    1. vendor_name: Vendor name in the text.
    2. line_items: A list of objects with fields: date, room, description, amount.
    3. item_count: Number of line items.

    Text:
    \"\"\"{invoice_text}\"\"\"
    """

    # Step 4: Send to GPT
    response = client.responses.create(
        # model="gpt-4o-mini",
        model="ollama/llama3",
        input=prompt,
        temperature=0
    )

    # Step 5: Parse GPT output
    gpt_output = response.output_text.strip()

    try:
        # 1. Remove ```json or ``` wrappers if present
        clean_json_str = re.sub(r"^```json\s*|\s*```$", "", gpt_output.strip(), flags=re.DOTALL)
        result = json.loads(clean_json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON from GPT:\n" + gpt_output)

    # Step 6: Print the results
    # print("Vendor Name:", result.get("vendor_name"))
    # print("Line Items:", result.get("line_items", []))
    # print("Item Count:", result.get("item_count"))
    return result

class ReadExcelColumn(BaseTool):
    name: str = "Read Excel File Column Data"
    description: str = "A tool to read Column Data as List based on Column Name we passed from the 'InvoiceLog.xlsx' Excel file" 
    def _run(self, excelfilename: str,excelcolumnname:str) -> list:
        dfReadLog = pd.read_excel(excelfilename)
        colDataList = dfReadLog[excelcolumnname].tolist()
        return colDataList

class LogFileReader(BaseTool):
    name: str = "Log File Reader"
    description: str = "A tool to read file names from dataoutput folder and update in Filename column  in 'InvoiceLog.xlsx' Excel file" 
    def _run(self, folderpath: str,excelcolumnname:str) -> list:
        retFilenames=[]
        getfiles=os.listdir(folderpath)
        dfReadLog = pd.read_excel("InvoiceLog.xlsx")
        processedFiles = dfReadLog['Filename'].tolist()


        for eachfile in  getfiles:
            if eachfile not in processedFiles:
                retFilenames.append(eachfile)
                row_count = len(dfReadLog)
                row_num=row_count+1
                dfReadLog.at[row_num, excelcolumnname] = eachfile
        dfReadLog.to_excel("InvoiceLog.xlsx", index=False)
        return retFilenames

   

class ConvertPDFJSON(BaseTool):
    name: str = "Read pdf files and write to json files"
    description: str = "Read each pdf file content from  testdata folder and create a json file in dataoutput folder" 
    def _run(self, outputfolder: str,testdatafolder:str) -> str:
        pdfilenames = os.listdir(testdatafolder)
        for eachpdf in pdfilenames:
            # pdf_tool = PDFSearchTool(pdf_path=eachpdf)
            # result = pdf_tool.run("Summarize the entire document.")
            pdfname = os.path.splitext(eachpdf)[0]
            inputpdf = "testdata\\"+eachpdf
            result = extract_text_from_pdf_img(inputpdf,pdfname)
            output_path = os.path.join(outputfolder, f"{pdfname}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"pdf_file": eachpdf, "content": result}, f, indent=4, ensure_ascii=False)
            print(f"✅ Saved: {output_path}")


class UpdateLogFile(BaseTool):
    name: str = "Log File Updater"
    description: str = "A tool to read/write invoiceLog.xlsx file , get appropritate columnname and valuetowrite and update in invoiceLog.xlsx file" 
    def _run(self, columnname:str,valuetowrite:str,filename:str ="InvoiceLog.xlsx"):
        dfReadLog = pd.read_excel(filename)
        row_count = len(dfReadLog)
        row_num=row_count+1
        dfReadLog.at[row_num, columnname] = valuetowrite
        dfReadLog.to_excel(filename, index=False)


class UpdateLineItemsValues(BaseTool):
    name: str = "Log File Updater based JSON Line Items count "
    description: str = "A tool to read/write invoiceLog.xlsx file .Get JSON values of Line Item and Total Amount and COmpare with expected and update in invoiceLog.xlsx file corresponding row  and Preprocess column where filename available" 
    def _run(self, LineItemsCount:int,jsonfilename:str,excelfilenamecolumn:str,update_column:str,approvalType:str,reasonColumn:str,Linecount:str,TotalAmountColumn:str,TotalAmount:str,excelfilename:str ="InvoiceLog.xlsx"):
        dfUpdateLog = pd.read_excel(excelfilename)
        jsonName=jsonfilename.split("/")[1]
        dfUpdateLog.loc[dfUpdateLog[excelfilenamecolumn] == jsonName, update_column] =approvalType
        dfUpdateLog.loc[dfUpdateLog[excelfilenamecolumn] == jsonName, reasonColumn] = LineItemsCount
        dfUpdateLog.loc[dfUpdateLog[excelfilenamecolumn] == jsonName, TotalAmountColumn] = TotalAmount
        dfUpdateLog.to_excel(excelfilename, index=False)

class ReadVendorName(BaseTool):
    name: str = "Read Vendor Names "
    description: str = "A tool to read validVendors.txt .Get list of Vendor Names" 
    def _run(self, VendorFilename:str)->list:
        validVendorList = open(VendorFilename,"r").readlines()
        validVendorList = [eachvendor.replace("\n",'') for eachvendor in validVendorList]
        return validVendorList

class ConvertAmount(BaseTool):
    name: str = "Convert Amount string to Integer value"
    description: str = "A tool to read Amount string values and remove character and convert to number and return" 
    def _run(self, amount:str)->float:
        original_amount = amount
        numeric_string = re.sub(r'[^0-9.]', '', original_amount)
        print(f"Numeric string: {numeric_string}")
        try:
            converted_integer = float(numeric_string)
            return  converted_integer
        except Exception as e:
            print(e)
        return original_amount

class UpdateVendorName(BaseTool):
    name: str = "Log File Updater based JSON Vendor Name"
    description: str = "A tool to read/write invoiceLog.xlsx file .Get JSON values of Vendor Name and Update in invoiceLog.xlsx file corresponding row  and Preprocess column where filename available" 
    def _run(self, vendorname:str,jsonfilename:str,excelfilenamecolumn:str,VendorStatus:str,VendorName_column:str,VendorStatus_column:str,excelfilename:str ="InvoiceLog.xlsx"):
        jsonName=jsonfilename.split("/")[1]
        dfUpdateLog = pd.read_excel(excelfilename)
        dfUpdateLog.loc[dfUpdateLog[excelfilenamecolumn] == jsonName, VendorName_column] =vendorname
        dfUpdateLog.loc[dfUpdateLog[excelfilenamecolumn] == jsonName, VendorStatus_column] =VendorStatus
        dfUpdateLog.to_excel(excelfilename, index=False)


class returnSpecificJSONvalues(BaseTool):
    name: str = "JSON data clean and return needed values"
    description: str = "A tool to read JSON file and return following items as dict [Lineitems,Vendor Name,Total Amount]" 
    def _run(self, dataoutputfolder:str,JSONFilename:str)->dict:
        pathjson= dataoutputfolder+"\\"+JSONFilename
        retValues = getFormattedTextfromJSON(pathjson)
        return retValues