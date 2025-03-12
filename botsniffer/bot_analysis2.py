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
    print(file_paths)  # Output: khoj
    # for file_path in file_paths:
    for file_path in os.listdir(file_paths):
        # repo_name = get_repo_name(file_path)
        # print("file_path: ", file_path)
        if (file_path == ".") or (file_path == "/"):continue
        full_path = os.path.join(file_paths, file_path)  # Ensure correct path
        # print("full path: ", full_path)
        if os.path.exists(full_path):
            if os.path.isfile(full_path) and full_path.endswith(".py"):
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
def save_results(output_file, ai_files, keyword_counts, struct_patterns, num_repos):
    print("keyword_counts, struct_patterns: ", keyword_counts, struct_patterns)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("AI-Generated Files:\n")
        # for file in ai_files:
        #     f.write(f"  - {file}\n")
        
        f.write("\nKeyword Analysis:\n")
        for keyword, count in keyword_counts.items():
            f.write(f"  {keyword}: {count/num_repos}\n")
        
        f.write("\nStructural Patterns:\n")
        for pattern, count in struct_patterns.items():
            f.write(f"  {pattern}: {count/num_repos}\n")

# Main execution
folder_path = "../cloned_commits/2022-11-29" #"./before_ai" 2024-03-06 2022-11-29
output_file = "ai_code_analysis.txt"
keywords_dict = {}
struct_dict = {}
num_repos = 0
for folder in os.listdir(folder_path): #folder = date
        # print("date: ", folder)
        num_repos += 1
        merged_churn_per_date = []
        # all_repos = [os.path.join(repoFolder, d) for d in os.listdir(repoFolder) if os.path.isdir(os.path.join(repoFolder, d))]
        combined_data = {}
        if (folder == ".DS_Store"):
            continue
        folder_full_path = os.path.join(folder_path, folder)
        # print("folder_full_path: ", folder_full_path)
        for folder2 in os.listdir(folder_full_path): #folder = repo name 1
            if (folder2 == ".DS_Store"):
                continue
            folder_full_path2 = os.path.join(folder_full_path, folder2)
            # print("folder_full_path2: ", folder_full_path2)
            for folder3 in os.listdir(folder_full_path2): #folder = repo name 2
                if (folder3 == ".DS_Store"):
                    continue
                folder_full_path3 = os.path.join(folder_full_path2, folder3)
                # for folder4 in os.listdir(folder_full_path3): #folder = repo name 2
                #     if (folder4 == ".DS_Store"):
                #         continue
                    # folder_full_path4 = os.path.join(folder_full_path3, folder4)
                # print("folder_full_path3: ", folder_full_path3)
                if os.path.isdir(folder_full_path3):  # Check if it's a directory
                    # ai_files = extract_ai_generated_files(folder_full_path3)
                    keyword_counts, struct_patterns = analyze_ai_code(folder_full_path3)
                    # print(keyword_counts, struct_patterns)
                    for keyw, count in keyword_counts.items():
                        if keyw in keywords_dict:
                            keywords_dict[keyw] += count
                        else:
                            keywords_dict[keyw] = count
                    for structp, count in struct_patterns.items():
                        if structp in struct_dict:
                            struct_dict[structp] += count
                        else:
                            struct_dict[structp] = count
    
save_results(output_file, folder_full_path3, keywords_dict, struct_dict, num_repos)

print(f"Analysis complete. Results saved to {output_file}")

