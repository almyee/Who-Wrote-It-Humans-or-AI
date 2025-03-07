import os
from collections import defaultdict
import requests
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np
import re  # Import regex module for date validation
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access the variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# print(os.getenv("GITHUB_TOKEN"))  # Should print the token (or part of it)
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Fetch data from GitHub API
def fetch_github_data(endpoint, owner, repo, params={}):
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
    results = []
    params["per_page"] = 100  # Max per request
    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Error: {response.json()}")
            break
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Handle pagination
    return results

# Convert ISO date (e.g., "2024-02-01T14:30:00Z") to YYYY-MM format
def to_month(date_str):
    return date_str[:7] if date_str else None  # Extract YYYY-MM

# Get issue and PR statistics
def get_issue_and_pr_stats(owner, repo):
    data = fetch_github_data("issues", owner, repo, {"state": "all"})

    opened_issues = defaultdict(int)
    closed_issues = defaultdict(int)
    opened_prs = defaultdict(int)
    closed_prs = defaultdict(int)
    bug_issues = defaultdict(int)
    issue_close_times = []
    pr_close_times = []

    for item in data:
        created_month = to_month(item.get("created_at"))
        closed_month = to_month(item.get("closed_at"))

        if "pull_request" in item:  # It's a PR
            if created_month:
                opened_prs[created_month] += 1
            if closed_month:
                closed_prs[closed_month] += 1

            # Track PR close times
            if item.get("closed_at"):
                opened_time = dt.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                closed_time = dt.strptime(item["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                pr_close_times.append((closed_time - opened_time).total_seconds() / 86400)  # Convert to days
        else:  # It's an issue
            if created_month:
                opened_issues[created_month] += 1
            if closed_month:
                closed_issues[closed_month] += 1

            # Track issue close times
            if item.get("closed_at"):
                opened_time = dt.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                closed_time = dt.strptime(item["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                issue_close_times.append((closed_time - opened_time).total_seconds() / 86400)  # Convert to days

            # Track bug-related issues
            labels = [label["name"].lower() for label in item.get("labels", [])]
            if "bug" in labels:
                bug_issues[created_month] += 1

    return {
        "opened_issues": dict(opened_issues),
        "closed_issues": dict(closed_issues),
        "opened_prs": dict(opened_prs),
        "closed_prs": dict(closed_prs),
        "bug_issues": dict(bug_issues),
        "issue_close_times": issue_close_times,
        "pr_close_times": pr_close_times
    }

# # Process all repositories in a folder
# def process_repos_in_folder(folder_path):
#     repo_stats = defaultdict(lambda: defaultdict(list))  # Nested dict to store per-month data

#     for repo_dir in os.listdir(folder_path):
#         repo_path = os.path.join(folder_path, repo_dir)
#         if os.path.isdir(repo_path):
#             parts = repo_dir.split('/')  # Assuming folder name is 'owner/repo'
#             if len(parts) == 2:
#                 owner, repo = parts
#             else:
#                 print(f"Skipping invalid directory name: {repo_dir}")
#                 continue

#             print(f"Processing {owner}/{repo}...")
#             stats = get_issue_and_pr_stats(owner, repo)

#             for key, value in stats.items():
#                 if isinstance(value, dict):  
#                     # Handle dictionary-type stats (per-month counts)
#                     for month, count in value.items():
#                         repo_stats[key][month].append(count)
#                 elif isinstance(value, list):  
#                     # Handle list-type stats (e.g., issue close times)
#                     repo_stats[key]["all"].extend(value)  
#                 else:  
#                     # Handle scalar values (e.g., avg close time, which we no longer use)
#                     repo_stats[key]["all"].append(value)

#     # Compute averages for dictionary-type stats
#     averaged_stats = {}
#     for key, monthly_data in repo_stats.items():
#         if isinstance(monthly_data, dict):
#             averaged_stats[key] = {
#                 month: sum(values) / len(values) for month, values in monthly_data.items() if values
#             }
#         else:
#             averaged_stats[key] = sum(monthly_data) / len(monthly_data) if monthly_data else 0

#     return averaged_stats

# Process all repositories in a folder
def process_repos_in_folder(folder_path):
    repo_stats = defaultdict(lambda: defaultdict(list))  # Nested dict to store per-month data
    count = 0
    for owner in os.listdir(folder_path):  # First level: Owner folders
        owner_path = os.path.join(folder_path, owner)
        if not os.path.isdir(owner_path):
            continue  # Skip if it's not a folder
        count += 1
        if (count > 2):
                break
        for repo in os.listdir(owner_path):  # Second level: Repo folders
            repo_path = os.path.join(owner_path, repo)
            if not os.path.isdir(repo_path):
                continue  # Skip if it's not a folder
            print(f"Processing {owner}/{repo}...")
            stats = get_issue_and_pr_stats(owner, repo)

            for key, value in stats.items():
                if isinstance(value, dict):  
                    # Handle dictionary-type stats (per-month counts)
                    for month, count in value.items():
                        repo_stats[key][month].append(count)
                elif isinstance(value, list):  
                    # Handle list-type stats (e.g., issue close times)
                    repo_stats[key]["all"].extend(value)  
                else:  
                    # Handle scalar values (e.g., avg close time, which we no longer use)
                    repo_stats[key]["all"].append(value)

    # Compute averages for dictionary-type stats
    averaged_stats = {}
    for key, monthly_data in repo_stats.items():
        print("key: ", key)
        if isinstance(monthly_data, dict):
            averaged_stats[key] = {
                month: sum(values) / len(values) for month, values in monthly_data.items() if values
            }
        else:
            averaged_stats[key] = sum(monthly_data) / len(monthly_data) if monthly_data else 0

    return averaged_stats


import matplotlib.pyplot as plt
from datetime import datetime as dt

def plot_stats(stats):
    # Define full month range
    start_month = "2019-10"
    end_month = "2025-01"
    start_dt = dt.strptime(start_month, "%Y-%m")
    end_dt = dt.strptime(end_month, "%Y-%m")
    # Example GPT release dates (convert to datetime)
    gpt_dates = [
    ("gpt-3.5", "2022-11"),
    ("gpt-4", "2023-03"),
    ("gpt-4o", "2024-05")
    ]
    gpt_dates_dt = [dt.strptime((date[1]), "%Y-%m") for date in gpt_dates]
    gpt_dates_num = [date2num(gpt_date) for gpt_date in gpt_dates_dt]
    # Find the index positions of GPT release dates in xmonths_complete
    # gpt_indices = [xmonths_complete.index(date[1]) for date in gpt_dates if date[1] in xmonths_complete]
    # Generate all months in range
    xmonths_complete_dt = []
    current_dt = start_dt
    while current_dt <= end_dt:
        xmonths_complete_dt.append(current_dt)
        next_month = current_dt.month + 1
        next_year = current_dt.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        current_dt = dt(next_year, next_month, 1)

    xmonths_numeric = date2num(xmonths_complete_dt)  # Convert to numerical format
    xmonths_complete = [dt.strftime(date, "%Y-%m") for date in xmonths_complete_dt]

    # Fill missing months with zero values
    def fill_missing(data):
        return [data.get(month, 0) for month in xmonths_complete]

    # Prepare data for plotting
    opened_issues = fill_missing(stats.get("opened_issues", {}))
    closed_issues = fill_missing(stats.get("closed_issues", {}))
    opened_prs = fill_missing(stats.get("opened_prs", {}))
    closed_prs = fill_missing(stats.get("closed_prs", {}))
    bug_issues = fill_missing(stats.get("bug_issues", {}))

    # Select labels every 3 months
    tick_labels = xmonths_complete[::3]
    tick_positions = list(range(0, len(xmonths_complete), 3))

    # Plot Data
    plt.figure(figsize=(10, 8))

    plt.subplot(3, 1, 1)
    plt.plot(xmonths_numeric, opened_issues, linestyle="-", color="red", alpha=0.6, linewidth=2, label="Average Opened Issues")
    plt.plot(xmonths_numeric, closed_issues, linestyle="-", color="blue", alpha=0.6, linewidth=2, label="Average Closed Issues")
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label= f"({i+1}) " + label)
        plt.text(date_num + 0.5, plt.ylim()[1] * 0.88, f"({i+1})", color='orange', rotation=0, verticalalignment='bottom', horizontalalignment='left')
    plt.xlabel("Months")
    plt.ylabel("Number of Issues")
    plt.title("Opened & Closed Issues Over Time")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout(pad=5.0)
    plt.xticks(xmonths_numeric[::3], tick_labels, rotation=45)

    plt.subplot(3, 1, 2)
    plt.plot(xmonths_numeric, opened_prs, linestyle="-", color="red", alpha=0.6, linewidth=2, label="Average Opened PRs")
    plt.plot(xmonths_numeric, closed_prs, linestyle="-", color="blue", alpha=0.6, linewidth=2, label="Average Closed PRs")
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=f"({i+1}) " + label)
        plt.text(date_num + 0.5, plt.ylim()[1] * 0.88, f"({i+1})", color='orange', rotation=0, verticalalignment='bottom', horizontalalignment='left')
    plt.xlabel("Months")
    plt.ylabel("Number of PRs")
    plt.title("Opened & Closed Pull Requests Over Time")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout(pad=5.0)
    plt.xticks(xmonths_numeric[::3], tick_labels, rotation=45)

    plt.subplot(3, 1, 3)
    plt.plot(xmonths_numeric, bug_issues, label="Average Bugs", color='green', linestyle='-')
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=f"({i+1}) " + label)
        plt.text(date_num + 0.5, plt.ylim()[1] * 0.88, f"({i+1})", color='orange', rotation=0, verticalalignment='bottom', horizontalalignment='left')
    plt.xlabel("Months")
    plt.ylabel("Number of Bugs")
    plt.title("Bugs Over Time")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout(pad=5.0)
    plt.xticks(xmonths_numeric[::3], tick_labels, rotation=45)

    plt.tight_layout()
    plt.show()

# Function to compute averages before and after a given date
def compute_averages(data):
    # before = []
    all = []
    # Define threshold date
    # threshold_date = dt(2022, 11, 1)
    for date_str, value in data.items():
        # Check if the key matches the YYYY-MM format
        if not re.match(r"^\d{4}-\d{2}$", date_str):
            continue  # Skip non-date keys like 'all'
        # Convert YYYY-MM to datetime object
        date_obj = dt.strptime(date_str, "%Y-%m")
        # if date_obj < threshold_date:
        #     before.append(value)
        # else:
        all.append(value)
    
    # avg_before = sum(before) / len(before) if before else 0
    avg_all = sum(all) / len(all) if all else 0

    return avg_all
def merge_averaged_stats(*folders):
    merged_stats = defaultdict(dict)

    for folder in folders:
        for category, data in folder.items():
            if category not in merged_stats:
                merged_stats[category] = {}
            for date, value in data.items():
                merged_stats[category][date] = value  # Overwrites if duplicate, but should be the same
    
    return dict(merged_stats)

# Main execution
if __name__ == "__main__":
    folder_path =   "test_repos" #"../cloned_commits" # Path to your local folder of repos
    folder_stats = {}
    merge_avg = {}
    for folder in os.listdir(folder_path):
        print("date: ", folder)
        folder_full_path = os.path.join(folder_path, folder)
        
        if os.path.isdir(folder_full_path):  # Check if it's a directory
            averaged_stats = process_repos_in_folder(folder_full_path)  # Run your function
            # print("averaged_stats: ", averaged_stats)    
            merge_avg = merge_averaged_stats(merge_avg, averaged_stats)
    # Compute averages for each category
    # Iterate through averaged_stats and find fields containing 'all'
        for field, data in averaged_stats.items():
            if 'all' in data:
                print(f"{field}: {data['all']}")

        for category, data in averaged_stats.items():
            if 'all' in data:
                print(f"{category}: {data['all']}")
                continue
            avg_data = compute_averages(data)
            print("avg ", category, ": ", avg_data)
   
    # print("merge_avg: ", merge_avg)
    plot_stats(merge_avg)
