import pdfplumber
import pandas as pd

# Extract text from PDF
def extract_text(pdf_path):
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_data.append(text)
    return "\n".join(extracted_data)

pdf_path = "sample.pdf"
extracted_text = extract_text(pdf_path)

# Save to CSV
df = pd.DataFrame({"Extracted Text": [extracted_text]})
df.to_csv("extracted_text.csv", index=False)
print("Text saved to extracted_text.csv")

