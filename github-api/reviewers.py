import os
import asyncio
import aiohttp
from collections import defaultdict
from datetime import datetime as dt
from dotenv import load_dotenv
# this code was used to generate the pr/issue/bug graph from our final report
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np
import re  # Import regex module for date validation
import requests
import time

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def to_month(date_str):
    return date_str[:7] if date_str else None

async def fetch_json(session, url, params=None):
    """ Asynchronously fetch JSON data from a GitHub API endpoint. """
    async with session.get(url, headers=HEADERS, params=params) as response:
        if response.status == 403 and "X-RateLimit-Reset" in response.headers:
            reset_time = int(response.headers["X-RateLimit-Reset"])
            wait_time = max(reset_time - time.time(), 1)
            print(f"Rate limit exceeded. Sleeping for {wait_time:.2f} seconds...")
            await asyncio.sleep(wait_time)
            return await fetch_json(session, url, params)
        if response.status != 200:
            print(f"Failed request: {url} - {response.status}")
            return []
        return await response.json()

async def fetch_pr_reviews(session, owner, repo, pr_number):
    """ Fetch reviewers for a specific PR asynchronously. """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    reviews_data = await fetch_json(session, url)
    if not reviews_data:
        return 0
    reviewers = {review["user"]["login"] for review in reviews_data if "user" in review and review["user"]}
    return len(reviewers)

async def get_reviewers_per_pr(owner, repo):
    """ Fetch number of reviewers per PR asynchronously. """
    async with aiohttp.ClientSession() as session:
        issues = await fetch_json(session, f"https://api.github.com/repos/{owner}/{repo}/issues", {"state": "all", "per_page": 100})
        reviewers_per_pr = defaultdict(int)

        # Identify PRs from issues
        prs = [(issue["number"], to_month(issue["created_at"])) for issue in issues if "pull_request" in issue]

        # Fetch reviews concurrently
        tasks = [fetch_pr_reviews(session, owner, repo, pr_number) for pr_number, _ in prs]
        results = await asyncio.gather(*tasks)

        # Aggregate results
        for (pr_number, month), num_reviewers in zip(prs, results):
            if month:
                reviewers_per_pr[month] += num_reviewers
        
        return dict(reviewers_per_pr)

def get_issue_and_pr_stats(owner, repo):
    """ Wrapper to run async functions synchronously. """
    return asyncio.run(get_reviewers_per_pr(owner, repo))

# Process all repositories in a folder
def process_repos_in_folder(folder_path):
    print("in process repos to: ", folder_path)
    repo_stats = defaultdict(lambda: defaultdict(list))  # Nested dict to store per-month data
    count = 0
    for owner in os.listdir(folder_path):  # First level: Owner folders
        owner_path = os.path.join(folder_path, owner)
        if not os.path.isdir(owner_path):
            continue  # Skip if it's not a folder
        # count += 1
        # if (count > 2):
        #         break
        for repo in os.listdir(owner_path):  # Second level: Repo folders
            repo_path = os.path.join(owner_path, repo)
            if not os.path.isdir(repo_path):
                # print("not a repo")
                continue  # Skip if it's not a folder
            # print(f"Processing {owner}/{repo}...")
            stats = get_issue_and_pr_stats(owner, repo)
            print("got issue and pr stats: ", stats)
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
        # print("key: ", key)
        if isinstance(monthly_data, dict):
            averaged_stats[key] = {
                month: sum(values) / len(values) for month, values in monthly_data.items() if values
            }
        else:
            averaged_stats[key] = sum(monthly_data) / len(monthly_data) if monthly_data else 0

    return averaged_stats

# Function to compute averages before and after a given date
def compute_averages(data):
    # before = []
    all = []
    # Define threshold date
    for date_str, value in data.items():
        # Check if the key matches the YYYY-MM format
        if not re.match(r"^\d{4}-\d{2}$", date_str):
            continue  # Skip non-date keys like 'all'
        # Convert YYYY-MM to datetime object
        date_obj = dt.strptime(date_str, "%Y-%m")
        all.append(value)
    
    # avg_before = sum(before) / len(before) if before else 0
    avg_all = sum(all) / len(all) if all else 0

    return avg_all
def merge_averaged_stats(*folders):
    merged_stats = defaultdict(dict)
    print("in merge stats")
    for folder in folders:
        for category, data in folder.items():
            if category not in merged_stats:
                merged_stats[category] = {}
            for date, value in data.items():
                merged_stats[category][date] = value  # Overwrites if duplicate, but should be the same
    
    return dict(merged_stats)


# Main execution
if __name__ == "__main__":
    folder_path =  "../cloned_commits" #  "test_repos" # Path to your local folder of repos
    folder_stats = {}
    merge_avg = {}
    for folder in os.listdir(folder_path):
        print("date: ", folder)
        if (folder == ".DS_Store"):
            continue
        if (folder != "2022-11-29"): #(folder != "2022-11-29") and "2024-03-06"
            continue
        folder_full_path = os.path.join(folder_path, folder)
        
        if os.path.isdir(folder_full_path):  # Check if it's a directory
            averaged_stats = process_repos_in_folder(folder_full_path)  # Run your function
            print("averaged_stats: ", averaged_stats)    
            merge_avg = merge_averaged_stats(merge_avg, averaged_stats)
            break
    # # Compute averages for each category
    # # Iterate through averaged_stats and find fields containing 'all'
        # for field, data in averaged_stats.items():
        #     if 'all' in data:
        #         print(f"{field}: {data['all']}")
    data_list = []
    for category, data in merge_avg.items():
        if 'all' in data:
            print(f"{category}: {data['all']}")
            data_list.append(data['all'])
            continue
        avg_data = compute_averages(data)
        print("avg ", category, ": ", avg_data)
   
    print("avg data list: ", np.mean(data_list))
    # plot_stats(merge_avg)