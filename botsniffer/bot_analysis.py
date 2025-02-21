
import os
import re
import statistics

def extract_botsniffer_metrics(text):
    """
    Extracts metrics from a botsniffer text file.
    Adjust regex patterns as needed to match your specific output format.
    """
    metrics = {
        "comment_quality": [],
        "indentation_consistency": [],
        "style_adherence": [],
        "repetitive_patterns": [],
        "code_complexity": [],
    }

    # Define regex patterns for extracting numerical values from 'Features' dictionary
    patterns = {
        "comment_quality": r"'comment_quality':\s*([\d.]+)",
        "indentation_consistency": r"'code_identation':\s*([\d.]+)",
        "style_adherence": r"'style_adherence':\s*([\d.]+)",
        "repetitive_patterns": r"'repetitive_patterns':\s*([\d.]+)",
        "code_complexity": r"'code_complexity':\s*([\d.]+)",
    }

    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            metrics[key] = [float(m) for m in matches]

    return metrics

def summarize_statistics(values):
    """Calculates statistical summaries including mean, median, mode, and more."""
    if not values:
        return {"mean": None, "min": None, "max": None, "std_dev": None, "count": 0, "median": None, "mode": None}
    
    return {
        "mean": round(statistics.mean(values), 2),
        "min": min(values),
        "max": max(values),
        "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        "count": len(values),
        "median": round(statistics.median(values), 2),
        "mode": round(statistics.mode(values), 2) if len(set(values)) > 1 else "No unique mode",
    }

def process_botsniffer_folder(folder_path):
    """Processes all text files in a folder and summarizes trends across them."""
    trends = {
        "total_files": 0,
        "ai_generated_count": 0,
        "ai_files": [],
        "comment_quality": [],
        "indentation_consistency": [],
        "style_adherence": [],
        "repetitive_patterns": [],
        "code_complexity": [],
    }

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Only process .txt files
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # Detect AI-generated mention (based on AI: True/False)
                if "AI: True" in text:
                    trends["ai_generated_count"] += 1
                    trends["ai_files"].append(filename)

                # Extract numerical metrics
                file_metrics = extract_botsniffer_metrics(text)
                for key in trends.keys():
                    if key in file_metrics:
                        trends[key].extend(file_metrics[key])

                trends["total_files"] += 1

            except Exception as e:
                print(f"Warning: Could not process {filename} - {e}")

    # Compute summary statistics
    summary = {
        "AI Generated Files": trends["ai_files"],
        "AI Generated Count": trends["ai_generated_count"],
        "Total Files": trends["total_files"],
        "Comment Quality Stats": summarize_statistics(trends["comment_quality"]),
        "Indentation Consistency Stats": summarize_statistics(trends["indentation_consistency"]),
        "Style Adherence Stats": summarize_statistics(trends["style_adherence"]),
        "Repetitive Patterns Stats": summarize_statistics(trends["repetitive_patterns"]),
        "Code Complexity Stats": summarize_statistics(trends["code_complexity"]),
    }

    return summary

def save_summary_to_text(summary, output_file):
    """Save the summary statistics to a text file in a human-readable format."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Total Files Processed: {summary['Total Files']}\n")
        f.write(f"AI Generated Files Count: {summary['AI Generated Count']}\n")
        f.write("AI Generated Files:\n")
        for file in summary["AI Generated Files"]:
            f.write(f"  - {file}\n")

        f.write("\nStatistical Analysis:\n")
        for key, stats in summary.items():
            if key.endswith("Stats"):
                f.write(f"\n{key.replace('Stats', '')}:\n")
                for stat_key, value in stats.items():
                    f.write(f"  {stat_key.capitalize()}: {value}\n")

# Example usage:
folder_path = "./before_ai"  # Update this to your folder path
output_file = "summary_output.txt"
summary = process_botsniffer_folder(folder_path)
print(summary)
save_summary_to_text(summary, output_file)

