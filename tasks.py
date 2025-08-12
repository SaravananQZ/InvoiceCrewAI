from crewai import Task
from tools import LogFileReader,ConvertPDFJSON,ReadExcelColumn,UpdateLineItemsValues,returnSpecificJSONvalues,UpdateVendorName,ReadVendorName,ConvertAmount
from agents import initInvoiceAgent,invoice_Amount_Validation_Agent


readLogfile_task =Task(
     description=(
        "**Task Description:**\n"
        "Get all pdf files from testdata folder and convert all pdf files into json files ,store in dataoutput folder"
    )
    ,
    agent=initInvoiceAgent,
    tools=[ConvertPDFJSON()],
    expected_output="all converted json files avaialble  dataoutput folder and if any convertion fails just skip and update in console"
)

updatefileDetails_task=Task(
    description=("Iterate each json file in the dataoutput folder and get its name and  update it in 'Filename' column in Excel file named 'InvoiceLog.xlsx'"),
    agent=initInvoiceAgent,
    tools=[LogFileReader()],
    expected_output="Each json filename should be available 'Filename' column in 'InvoiceLog.xlsx' file"
    )


amountValidateTask=Task(
     description=(
      """
        Objective:
            Read JSON files in 'dataoutput' folder  whichver available in InvoiceLog.xlsx Filename column and get it's Line items count and calculate total amount and finally update it in 'InvoiceLog.xlsx'.
            Also print a summary for each file to the console.

        Steps:
        1. Read Excel:
            1- Open 'InvoiceLog.xlsx' and get the list of filenames from the Filename column.
            2. For each file name Read its JSON file from dataoutput folder by passing json filename.
            3. After that do the following operation and update back to 'InvoiceLog.xlsx'.
                Calculate Item Count & Total Amount:
                    - Get number of line Item Count and Total Amount from JSON.
                    - Convert total amount to numeric using ConvertAmount tool.
                    - Apply rules (priority order):
                        1. If Total Amount > 1000 OR Item Count > 20 → "First Level approval"
                        2. Else If Item Count > 5 OR Total Amount > 100 → "First Level approval"
                        3. Else If Item Count ≤ 5 AND Total Amount > 500 → "First Level approval"
                        4. Else If Item Count ≤ 5 AND Total Amount ≤ 100 → "Second Level approval"
                    - Update PostProcess column accordingly.
                    - Update Line Items column with item count.

        4. Save Changes:
            - Save and close 'InvoiceLog.xlsx' after processing each file.

        5. Console Output:
            - For each processed file, print:
                Filename: <filename>, Line Items: <count>, Total Amount: <amount>, PostProcess: <approval type>
        """
    )
    ,
    agent=invoice_Amount_Validation_Agent,
    tools=[ReadExcelColumn(),returnSpecificJSONvalues(),ConvertAmount(),UpdateLineItemsValues()],
    expected_output="""
        "Updated Excel file and printed detailed To summary for each processed file."
    """
)
vendorValidateTask=Task(
     description=(
      """
        Objective:
            Process all JSON files in 'dataoutput' and get Vendor name and check valid or not then update results in 'InvoiceLog.xlsx'.
            Also print a summary for each file to the console.

        Steps:
        1. Read Excel:
            1- Open 'InvoiceLog.xlsx' and get the list of filenames from the 'Filename' column.
            2. For each filename in Excel:
                - If the file exists in 'dataoutput', read its JSON data using returnSpecificJSON tool.

        Item Count & Total Amount:
            - Get vendor name from JSON.
            - Check the vendor name is present in validVendors.txt using ReadVendorName tool.
            - Then update the vendor name "Vendor" column and its vendor status "valid" or "invalid" in column "Vendor Status" in 'InvoiceLog.xlsx'.

        4. Save Changes:
            - Save and close 'InvoiceLog.xlsx' after processing each json file.

        5. Console Output:
            - For each processed file, print:
                Filename: <filename>, Vendor name: <Vendor>, Vendor status: <Vendor Status>
        """
    )
    ,
    agent=invoice_Vendor_Validation_Agent,
    tools=[returnSpecificJSONvalues(),ReadVendorName(),UpdateVendorName()],
    expected_output="""
        "Updated Excel file and printed detailed To summary for each processed file."
    """
)

# preProcessInvoiceTask =Task(
#      description=(
#       """
#         Objective: Process a set of JSON files, validate vendor information, and perform item count and Total amount analysis then  update an results to Excel file named `InvoiceLog.xlsx`.

#         Steps:
#         1.  **Validate Total Amount,Line Items and Vendor name and update the result to  `InvoiceLog.xlsx`:**
#             * Open `InvoiceLog.xlsx` and Get List of Filenames from Filename column
#             * Open 'validVendors.txt' and Get List of Validvendors
#             * For each Filename ,if it is matches with JSON file name which is available in dataoutput folder then read JSON file using returnSpecificJSON tool and check the following details :
#                 * **Vendor Check:** Compare the vendor name from the JSON data against the list of vendors in the Validvendors.txt file
#                     * If the vendor is not found in Validvendors.txt, set the value in the 'Vendor Status' column to "Invalid Vendor".
#                     * If the vendor found in Validvendors.txt,set the value in the 'Vendor Status' column to "Valid Vendor".
#                     * After above conditions update Vendor Name in 'Vendor' Column 
#                 * **Item Count and Total Amount** Get the number of items and Total Amount from the JSON data.Validate Below Critiria
#                     use ConvertAmount tool to convert string value into numeric amount to compare
#                     Item Count and Total Amount Processing Rules
#                     If Item Count > 5 OR Total Amount > 100,
#                     → Set PostProcess column to "First Level approval"
#                     If Item Count ≤ 5 AND Total Amount > 500,
#                     → Set PostProcess column to "First Level approval"
#                     If Total Amount > 1000 OR Item Count > 20,
#                     → Set PostProcess column to "First Level approval"
#                     If Item Count ≤ 5 AND Total Amount ≤ 100,
#                     → Set PostProcess column to "Second Level approval"
#                     Final Step
#                     Always set "Linecount" in "Line Items" column to the extracted item count from JSON.

#         2.  **Save Changes:**
#             * For each update in excel save and close the `InvoiceLog.xlsx` file.
#         """
#     )
#     ,
#     agent=preProcessInvoiceAgent,
#     tools=[returnSpecificJSONvalues(),ConvertAmount(),UpdateLineItemsValues(),ReadVendorName(),UpdateVendorName()],
#     expected_output="""
#     * Each filename the "PostProcess" column should be filled with "First Level approval" or "Second Level approval"
#     * "Vendor Status" column  should be filled with "Invalid Vendor" or "Valid Vendor" 
#     * "Vendor" column  should be filled with Vendor Name
#     * "Line Items" column  should be filled with Linecount
#     """
# )