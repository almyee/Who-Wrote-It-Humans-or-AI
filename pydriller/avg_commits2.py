import os
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from pydriller import Repository
from datetime import datetime
from tqdm import tqdm
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import numpy as np
from collections import defaultdict

def createMonthList(startDate: datetime, endDate: datetime, stepSize: relativedelta):
    startDate = datetime(year=startDate.year, month=startDate.month, day=1, hour=0)
    endDate = datetime(year=endDate.year, month=endDate.month, day=1, hour=0)
    
    monthList = []
    while startDate < endDate:
        monthList.append(startDate)
        startDate = startDate + stepSize
    monthList.append(endDate)
    return monthList

def getFirstLastCommitDate(repoPath: str):
    # print("in get first/last commit")
    startDate, endDate = None, None
    # print("before calling Repo with pydriller, repoPath: ", repoPath)
    for commit in Repository(path_to_repo=repoPath).traverse_commits():
        if startDate is None:
            startDate = commit.author_date
        else:
            endDate = commit.author_date
    # print("after calling Repo with pydriller")
    return startDate, endDate

def createJobsByTimeDelta(repoPath: str, timeDelta: relativedelta):
    # print("in create jobs by time delta")
    startDate, endDate = getFirstLastCommitDate(repoPath)
    # print("after get first/last commit")
    if startDate is None or endDate is None:
        return []
    
    monthList = createMonthList(startDate, endDate, timeDelta)
    jobs = [{"from": monthList[i], "to": monthList[i + 1], "repo_path": repoPath} for i in range(len(monthList) - 1)]
    return jobs

def commitsJob(job):
    commits = sum(1 for _ in Repository(path_to_repo=job["repo_path"], since=job["from"], to=job["to"]).traverse_commits())
    return (job["from"], commits)

def processRepositories(folderPath, timeDelta):
    # print("in processRepo")
    repoPaths = [os.path.join(folderPath, d) for d in os.listdir(folderPath) if os.path.isdir(os.path.join(folderPath, d))]
    all_months = set()
    commit_data = {}
    # print("before for loops")
    for repoPath in repoPaths:
        # print("before jobs created")
        jobs = createJobsByTimeDelta(repoPath, timeDelta)
        # print("job created")
        for job in tqdm(jobs, desc=f"Processing {repoPath}"):
            month, commits = commitsJob(job)
            all_months.add(month)
            commit_data.setdefault(month, []).append(commits)
    
    sorted_months = sorted(all_months)
    avg_commits = [sum(commit_data[m]) / len(commit_data[m]) for m in sorted_months]
    # print("sorted months and got avg commits")
    return sorted_months, avg_commits

def plot_stats(months, avg_commits):
    start_dt = datetime(2019, 1, 1)
    end_dt = datetime(2025, 1, 1)

    gpt_dates = [
        ("gpt-3.5", "2022-11"),
        ("gpt-4", "2023-03"),
        ("gpt-4o", "2024-05")
    ]
    gpt_dates_dt = [datetime.strptime(date[1], "%Y-%m") for date in gpt_dates]
    gpt_dates_num = [date2num(gpt_date) for gpt_date in gpt_dates_dt]

    # Generate fixed x-axis range (quarterly from 2019–2025)
    xquarters_complete_dt = []
    current_dt = start_dt
    while current_dt <= end_dt:
        xquarters_complete_dt.append(current_dt)
        current_dt += relativedelta(months=3)
    
    xquarters_numeric = date2num(xquarters_complete_dt)

    # Aggregate commits by quarter
    quarterly_commits = defaultdict(list)
    for month, commits in zip(months, avg_commits):
        quarter_start = datetime(month.year, (month.month - 1) // 3 * 3 + 1, 1)  # Normalize to quarter start
        quarterly_commits[quarter_start].append(commits)
    
    # Compute quarterly averages (fill missing quarters with NaN)
    avg_commits_by_quarter = []
    for quarter in xquarters_complete_dt:
        if quarter in quarterly_commits:
            avg_commits_by_quarter.append(sum(quarterly_commits[quarter]) / len(quarterly_commits[quarter]))
        else:
            avg_commits_by_quarter.append(np.nan)  # Preserve gaps

    plt.figure(figsize=(10, 5))
    plt.plot(xquarters_numeric, avg_commits_by_quarter, label="Average Commits", color='blue', linestyle='-', marker='o')

    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=f"({i+1}) " + label)
        plt.text(date_num + 0.5, plt.ylim()[1] * 0.88, f"({i+1})", color='orange', rotation=0, verticalalignment='bottom', horizontalalignment='left')

    plt.title("Average Commits Over Time")
    plt.xlabel("Months")
    plt.ylabel("Average Commits")
    plt.xticks(xquarters_numeric, [q.strftime("%Y-%m") for q in xquarters_complete_dt], rotation=45)  # Show quarters
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()

if __name__ == "__main__":
    folder_path =   "../cloned_commits" #"../github-api/test_repo" # Path to your local folder of repos
    folder_stats = {}
    merged_avg_commits = []
    merged_months = []
    for folder in os.listdir(folder_path):
        # print("date: ", folder)
        merged_commits_per_date = []
        if (folder == ".DS_Store"):
            continue
        folder_full_path = os.path.join(folder_path, folder)
        # print("folder_full_path: ", folder_full_path)
        for folder2 in os.listdir(folder_full_path):
            if (folder2 == ".DS_Store"):
                continue
            folder_full_path2 = os.path.join(folder_full_path, folder2)
            # print("folder_full_path2: ", folder_full_path2)
            for folder3 in os.listdir(folder_full_path2):
                if (folder3 == ".DS_Store"):
                    continue
                folder_full_path3 = os.path.join(folder_full_path2, folder3)
                if os.path.isdir(folder_full_path2):  # Check if it's a directory
                    months, avg_commits = processRepositories(folder_full_path3, relativedelta(months=3))
                    # print("averaged_stats: ", avg_commits)   
                # else:
                #     print("this folder2 not a dir: ", folder_full_path) 
                    merged_months.extend(months)
                    merged_avg_commits.extend(avg_commits)
                    merged_commits_per_date.extend(avg_commits)
                    # merged_months, merged_avg_commits = merge_averaged_stats((merged_months, merged_avg_commits), (months, avg_commits))
        avg_commits_date = sum(merged_commits_per_date)/len(merged_commits_per_date)
        # print("avg_commits_date: ", avg_commits_date, folder)
    # Sort merged data properly
    if merged_months and merged_avg_commits:
        merged_data = sorted(zip(merged_months, merged_avg_commits), key=lambda x: x[0])
        merged_months, merged_avg_commits = zip(*merged_data)
        merged_months = list(merged_months)
        merged_avg_commits = list(merged_avg_commits)
    # print("Sorted Months:", [m.strftime("%Y-%m") for m in merged_months])
    plot_stats(merged_months, merged_avg_commits)
