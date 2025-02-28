import os
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from pydriller import Repository
from datetime import datetime
from tqdm import tqdm
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import numpy as np
from scipy.ndimage import gaussian_filter1d




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
    startDate, endDate = None, None
    
    for commit in Repository(path_to_repo=repoPath).traverse_commits():
        if startDate is None:
            startDate = commit.author_date
        else:
            endDate = commit.author_date
    
    return startDate, endDate

def createJobsByTimeDelta(repoPath: str, timeDelta: relativedelta):
    startDate, endDate = getFirstLastCommitDate(repoPath)
    if startDate is None or endDate is None:
        return []
    
    monthList = createMonthList(startDate, endDate, timeDelta)
    jobs = [{"from": monthList[i], "to": monthList[i + 1], "repo_path": repoPath} for i in range(len(monthList) - 1)]
    return jobs

def commitsJob(job):
    commits = sum(1 for _ in Repository(path_to_repo=job["repo_path"], since=job["from"], to=job["to"]).traverse_commits())
    return (job["from"], commits)

def processRepositories(folderPath, timeDelta):
    repoPaths = [os.path.join(folderPath, d) for d in os.listdir(folderPath) if os.path.isdir(os.path.join(folderPath, d))]
    all_months = set()
    commit_data = {}
    
    for repoPath in repoPaths:
        jobs = createJobsByTimeDelta(repoPath, timeDelta)
        
        for job in tqdm(jobs, desc=f"Processing {repoPath}"):
            month, commits = commitsJob(job)
            all_months.add(month)
            commit_data.setdefault(month, []).append(commits)
    
    sorted_months = sorted(all_months)
    avg_commits = [sum(commit_data[m]) / len(commit_data[m]) for m in sorted_months]
    
    return sorted_months, avg_commits

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def plot_stats(months, avg_commits):
    start_dt = datetime(2019, 10, 1)
    end_dt = datetime(2025, 1, 1)
    xmonths_complete_dt = []
    current_dt = start_dt
    gpt_dates = [
    ("gpt-3.5", "2022-11"),
    ("gpt-4", "2023-03"),
    ("gpt-4o", "2024-05")
    ]
    gpt_dates_dt = [datetime.strptime((date[1]), "%Y-%m") for date in gpt_dates]
    gpt_dates_num = [date2num(gpt_date) for gpt_date in gpt_dates_dt]

    while current_dt <= end_dt:
        xmonths_complete_dt.append(current_dt)
        current_dt += relativedelta(months=3)
    
    xmonths_numeric = date2num(xmonths_complete_dt)
    months_numeric = date2num(months)
    
    valid_indices = [i for i, m in enumerate(months) if start_dt <= m <= end_dt]
    months_filtered = [months[i] for i in valid_indices]
    avg_commits_filtered = [avg_commits[i] for i in valid_indices]
    
    # print(f"Filtered months: {len(months_filtered)}")  # Debugging line
    # print(f"Filtered avg_commits: {len(avg_commits_filtered)}")  # Debugging line
    
    # Apply smoothing
    window_size = 3  # Adjust this value for more/less smoothing
    avg_commits_smooth = moving_average(avg_commits_filtered, window_size)

    # Adjust months to match the shorter smoothed data
    # avg_commits_smooth = gaussian_filter1d(avg_commits_filtered, sigma=2)  # Adjust sigma for more/less smoothing
    months_smooth = months_filtered[:len(avg_commits_smooth)]
    if len(months_filtered) != len(avg_commits_filtered):
        print("Error: Mismatch in the number of filtered months and commits.")
        return
    
    plt.figure(figsize=(10, 5))
    plt.plot(months_smooth, avg_commits_smooth, label="Average Commits", color='red', linestyle='-')

    # plt.plot(months_filtered, avg_commits_smooth, label="Average Commits", color='green', linestyle='-')
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=f"({i+1}) " + label)
        plt.text(date_num + 0.5, plt.ylim()[1] * 0.88, f"({i+1})", color='orange', rotation=0, verticalalignment='bottom', horizontalalignment='left')
    plt.title("Commits Over Time")
    plt.xlabel("Months")
    plt.ylabel("Number of Commits")
    plt.xticks(xmonths_numeric, [m.strftime("%Y-%m") for m in xmonths_complete_dt], rotation=45)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()


if __name__ == "__main__":
    folder_path = "./repos/all" #path to all repos
    months, avg_commits = processRepositories(folder_path, relativedelta(months=3))
    # sum_avg_commits = 0
    # threshold_date = datetime(2022, 11, 1)

    # # Initialize lists to hold commits before and after the threshold
    # before_nov_2022_commits = []
    # after_nov_2022_commits = []

    # # Split the months and avg_commits into two groups
    # for month, commit in zip(months, avg_commits):
    #     if month < threshold_date:
    #         before_nov_2022_commits.append(commit)
    #     else:
    #         after_nov_2022_commits.append(commit)

    # # Calculate the average of avg_commits before and after November 2022
    # avg_before_nov_2022 = sum(before_nov_2022_commits) / len(before_nov_2022_commits) if before_nov_2022_commits else 0
    # avg_after_nov_2022 = sum(after_nov_2022_commits) / len(after_nov_2022_commits) if after_nov_2022_commits else 0

    # print("Avg commits before November 2022: ", avg_before_nov_2022)
    # print("Avg commits after November 2022: ", avg_after_nov_2022)

    plot_stats(months, avg_commits)