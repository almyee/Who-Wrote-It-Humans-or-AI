# PRs/Time and Issues/Time with colored lines and gpt release lines

import os
from collections import defaultdict
import requests
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access the variables
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

# Constants
# GITHUB_TOKEN = # Replace with your GitHub token
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

# Fetch commit statistics
def get_commit_stats(owner, repo):
    commits = fetch_github_data("commits", owner, repo)
    commit_counts = defaultdict(int)
    churn_data = defaultdict(int)
    
    for commit in commits:
        commit_date = to_month(commit["commit"]["committer"]["date"])
        commit_counts[commit_date] += 1
        
        # Fetch commit details to calculate churn
        commit_details = requests.get(commit["url"], headers=HEADERS).json()
        if "files" in commit_details:
            total_churn = sum(f.get("additions", 0) + f.get("deletions", 0) for f in commit_details["files"])
            churn_data[commit_date] += total_churn
    
    return commit_counts, churn_data

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

# Process all repositories in a folder
def process_repos_in_folder(folder_path):
    repo_stats = defaultdict(lambda: defaultdict(list))  # Nested dict to store per-month data

    for repo_dir in os.listdir(folder_path):
        repo_path = os.path.join(folder_path, repo_dir)
        if os.path.isdir(repo_path):
            parts = repo_dir.split(':')  # Assuming folder name is 'owner/repo'
            if len(parts) == 2:
                owner, repo = parts
            else:
                print(f"Skipping invalid directory name: {repo_dir}")
                continue

            print(f"Processing {owner}/{repo}...")
            stats = get_issue_and_pr_stats(owner, repo)
            commit_counts, churn_data = get_commit_stats(owner, repo)

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
            for month, count in commit_counts.items():
                repo_stats["commits"][month].append(count)
            for month, churn in churn_data.items():
                repo_stats["churn"][month].append(churn)
    # Compute averages for dictionary-type stats
    averaged_stats = {}
    for key, monthly_data in repo_stats.items():
        if isinstance(monthly_data, dict):
            averaged_stats[key] = {
                month: sum(values) / len(values) for month, values in monthly_data.items() if values
            }
        else:
            averaged_stats[key] = sum(monthly_data) / len(monthly_data) if monthly_data else 0

    return averaged_stats

def process_multiple_folders(folder_paths):
    combined_stats = defaultdict(lambda: defaultdict(list))

    for folder_path in folder_paths:
        folder_stats = process_repos_in_folder(folder_path)

        for key, monthly_data in folder_stats.items():
            if isinstance(monthly_data, dict):  
                for month, values in monthly_data.items():
                    combined_stats[key][month].append(values)
            else:
                combined_stats[key]["all"].extend(monthly_data)

    # Compute final averages
    averaged_stats = {
        key: {month: sum(values) / len(values) for month, values in monthly_data.items() if values}
        for key, monthly_data in combined_stats.items()
    }

    return averaged_stats

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
    plt.plot(xmonths_numeric, opened_issues, linestyle="-", color="red", alpha=0.6, linewidth=2, label="Opened Issues")
    plt.plot(xmonths_numeric, closed_issues, linestyle="-", color="blue", alpha=0.6, linewidth=2, label="Closed Issues")
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=label)
    plt.xlabel("Months")
    plt.ylabel("Number of Issues")
    plt.title("Opened & Closed Issues Over Time")
    plt.legend()
    plt.xticks(xmonths_numeric[::3], tick_labels, rotation=45)

    plt.subplot(3, 1, 2)
    plt.plot(xmonths_numeric, opened_prs, linestyle="-", color="red", alpha=0.6, linewidth=2, label="Opened PRs")
    plt.plot(xmonths_numeric, closed_prs, linestyle="-", color="blue", alpha=0.6, linewidth=2, label="Closed PRs")
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=label)
    plt.xlabel("Months")
    plt.ylabel("Number of PRs")
    plt.title("Opened & Closed Pull Requests Over Time")
    plt.legend()
    plt.xticks(xmonths_numeric[::3], tick_labels, rotation=45)

    plt.subplot(3, 1, 3)
    # plt.figure(figsize=(10, 5))
    plt.plot(xmonths_numeric, bug_issues, label="Bugs", color='green', linestyle='-')
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=label)
    plt.xlabel("Months")
    plt.ylabel("Number of Bugs")
    plt.title("Bugs Over Time")
    plt.legend()
    plt.xticks(xmonths_numeric[::3], tick_labels, rotation=45)

    plt.tight_layout()
    plt.show()

    # def plot_stats(averaged_stats):
    commit_months = sorted(averaged_stats["commits"].keys())
    commits = [averaged_stats["commits"].get(month, 0) for month in commit_months]
    churn = [averaged_stats["churn"].get(month, 0) for month in commit_months]

    # plt.figure(figsize=(10, 5))
    # plt.plot(commit_months, commits, label="Commits", color='blue')
    # plt.plot(commit_months, churn, label="Churn", color='red')
    # plt.xlabel("Month")
    # plt.ylabel("Count")
    # plt.title("Commits and Code Churn Over Time")
    # plt.legend()
    # plt.xticks(rotation=45)
    # plt.show()

    # Plot commits over time
    plt.figure(figsize=(10, 5))
    plt.plot(commit_months, commits, label="Commits per Month", color='purple')
    plt.xlabel("Month")
    plt.ylabel("Number of Commits")
    plt.title("Commits Over Time")
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

    # Plot churn over time
    plt.figure(figsize=(10, 5))
    plt.plot(commit_months, churn, label="Churn per Month", color='orange')
    plt.xlabel("Month")
    plt.ylabel("Code Churn (Lines Added + Deleted)")
    plt.title("Code Churn Over Time")
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

# Main execution
if __name__ == "__main__":
    folder_paths = ["./repos/test", "./repos/all"]  # List of folders to process
    averaged_stats = process_multiple_folders(folder_paths)
    plot_stats(averaged_stats)
