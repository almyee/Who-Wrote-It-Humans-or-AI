from github import Github
from collections import Counter
import matplotlib.pyplot as plt
#from pydriller import Repository
#include "./pydriller/pydriller/repository.py" as Repository 
#import sys
#import os
from pydriller.repository import Repository
#sys.path.append(os.path.abspath("./pydriller/pydriller/repository.py"))

#import repository  # Now Python can find it

# ===== Configuration =====
ACCESS_TOKEN = # Replace with your GitHub token
REPO_NAME = # Replace with your target repository (e.g., "octocat/Hello-World")
REPO_PATH = # Local path for PyDriller
OUTPUT_FILE = "analysis_results2.txt"
KEYWORDS = ["chatgpt", "copilot", "ai-generated", "ai-assisted"]


# ===== Helper Functions =====
def write_to_file(contents):
    """Writes multiple lines to the output file in one operation."""
    with open(OUTPUT_FILE, "a") as file:
        file.writelines([line + "\n" for line in contents])


# ===== GitHub Analysis Functions =====
def analyze_pull_requests(repo):
    results = ["\nAnalyzing Pull Requests:"]
    for pr in repo.get_pulls(state='all'):
        pr_comments = pr.get_comments()
        if any(keyword in pr.title.lower() for keyword in KEYWORDS):
            results.append(f"AI-related PR #{pr.number}: {pr.title}")

        for comment in pr_comments:
            if any(keyword in comment.body.lower() for keyword in KEYWORDS):
                results.append(f"Comment mentioning AI: {comment.body}")

        results.append(f"PR #{pr.number}: {pr.title} by {pr.user.login} - {pr.state}")
        results.append(f"Created at: {pr.created_at}, Merged at: {pr.merged_at}")
        results.append(f"Additions: {pr.additions}, Deletions: {pr.deletions}\n")

    write_to_file(results)


def analyze_issues(repo):
    results = ["\nAnalyzing Issues:"]
    for issue in repo.get_issues(state='all'):
        if issue.pull_request is None:  # Exclude PRs
            results.append(f"Issue #{issue.number}: {issue.title} by {issue.user.login}")
            results.append(f"Created at: {issue.created_at}, Closed at: {issue.closed_at}\n")

    write_to_file(results)


# ===== PyDriller Analysis Functions =====
def analyze_commits(repo_path):
    results = ["\nAnalyzing Git Commits:"]
    dates = []
    total_insertions = 0
    total_deletions = 0

    for commit in Repository(repo_path).traverse_commits():
        if any(keyword in commit.msg.lower() for keyword in KEYWORDS):
            results.append(f"Commit {commit.hash} by {commit.author.name} on {commit.author_date}")
            results.append(f"Message: {commit.msg}\n")
            dates.append(commit.author_date.strftime("%Y-%m"))
            total_insertions += commit.insertions
            total_deletions += commit.deletions

    # Temporal trend plot
    commit_counts = Counter(dates)
    if commit_counts:
        plot_commit_trends(commit_counts)

    results.append(f"Total Insertions: {total_insertions}, Total Deletions: {total_deletions}\n")
    write_to_file(results)


def plot_commit_trends(commit_counts):
    dates, counts = zip(*sorted(commit_counts.items()))
    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker='o')
    plt.title("Frequency of AI-related Commits Over Time")
    plt.xlabel("Month")
    plt.ylabel("Number of AI-related Commits")
    plt.xticks(rotation=45)
    plt.show()


# ===== Main Execution =====
def main():
    # Clear the output file
    open(OUTPUT_FILE, "w").close()

    # GitHub API setup
    github = Github(ACCESS_TOKEN)
    repo = github.get_repo(REPO_NAME)

    # Analyze GitHub Data
    analyze_pull_requests(repo)
    analyze_issues(repo)

    # Analyze Local Git Data
    analyze_commits(REPO_PATH)


if __name__ == "__main__":
    main()

