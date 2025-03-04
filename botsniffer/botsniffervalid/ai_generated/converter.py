import csv
import json

# AI-driven schema inference based on column names
def infer_schema(columns):
    return {col: 'string' for col in columns}  # AI assumes all columns are strings initially

# Function to convert CSV to JSON with inferred schema
def csv_to_json(csv_file, json_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        schema = infer_schema(columns)
        data = [dict(zip(columns, row)) for row in reader]
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)
        print(f"Data successfully converted to JSON with inferred schema: {schema}")

# Example conversion
csv_to_json('input.csv', 'output.json')

