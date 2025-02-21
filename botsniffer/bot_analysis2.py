# script to get the keywords analysis and structural patterns
import os
import re
import collections

# Function to extract AI-generated files from botsniffer output
def extract_ai_generated_files(folder_path):
    ai_files = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Process only text files
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read()
                if lines:
                    # Extract repository name from first line
                    match = re.search(r"\(venv\) .*?:([^ ]+) ", lines[0])
                    repo_name = match.group(1) if match else filename[:-4]  # Default to filename if not found
                content = "".join(lines)
                matches = re.findall(r"File: (.+?)\nAI: True", content)
                # ai_files.extend(matches)
                for match in matches:
                    clean_path = match.strip().lstrip(".")  # Remove "./src/"
                    # Replace the leading period with the repo name
                    full_file_path = os.path.join("/" + repo_name +  clean_path)
                    ai_files.append(full_file_path)
    return ai_files

# Function to analyze patterns and categorize purpose
def analyze_ai_code(file_paths):
    keyword_counts = collections.Counter()
    struct_patterns = collections.Counter()
    # print(repo_name)  # Output: khoj
    for file_path in file_paths:
        # repo_name = get_repo_name(file_path)
        full_path = os.path.join("../repos/before_ai" + file_path)  # Ensure correct path
        # print("full path: ", full_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()
                keywords = re.findall(r"\b(def|class|import|from|lambda|return|yield)\b", code)
                keyword_counts.update(keywords) 
                if "class" in keywords:
                    struct_patterns["Object-Oriented"] += 1
                if "def" in keywords:
                    struct_patterns["Functions"] += 1
                if "import" in keywords or "from" in keywords:
                    struct_patterns["External Dependencies"] += 1
        else:
            print(f"Warning: File not found - {full_path}")
    return keyword_counts, struct_patterns

# Function to save results to a text file
def save_results(output_file, ai_files, keyword_counts, struct_patterns):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("AI-Generated Files:\n")
        for file in ai_files:
            f.write(f"  - {file}\n")
        
        f.write("\nKeyword Analysis:\n")
        for keyword, count in keyword_counts.items():
            f.write(f"  {keyword}: {count}\n")
        
        f.write("\nStructural Patterns:\n")
        for pattern, count in struct_patterns.items():
            f.write(f"  {pattern}: {count}\n")

# Main execution
folder_path = "./before_ai"
output_file = "ai_code_analysis.txt"

ai_files = extract_ai_generated_files(folder_path)
keyword_counts, struct_patterns = analyze_ai_code(ai_files)
save_results(output_file, ai_files, keyword_counts, struct_patterns)

print(f"Analysis complete. Results saved to {output_file}")

