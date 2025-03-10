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
from collections import defaultdict
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d


def savgol_smoothing(y, window=7, poly_order=2):
    return savgol_filter(y, window_length=window, polyorder=poly_order)

def polynomial_fit(x, y, degree=3):
    x_num = date2num(x)
    coeffs = np.polyfit(x_num, y, degree)
    poly_func = np.poly1d(coeffs)
    return x, poly_func(x_num)  # Returns fitted y values



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
    
    # Apply smoothing
    window_size = 3  # Adjust this value for more/less smoothing
    # avg_commits_smooth = moving_average(avg_commits_filtered, window_size)

    # Adjust months to match the shorter smoothed data
    # avg_commits_smooth2 = gaussian_filter1d(avg_commits_filtered, sigma=2)  # Adjust sigma for more/less smoothing
    
    if len(months_filtered) != len(avg_commits_filtered):
        print("Error: Mismatch in the number of filtered months and commits.")
        return
    # Apply LOWESS smoothing
    # smoothed_months, smoothed_avg_commits = lowess_smoothing(months_filtered, avg_commits_filtered, frac=0.2)  # Adjust frac for smoothness

    # Apply Savitzky-Golay filtering
    avg_commits_smooth = savgol_smoothing(avg_commits_filtered, window=7, poly_order=2)
    months_smooth = months_filtered[:len(avg_commits_smooth)]
    # Apply polynomial fit (degree 3 for a smooth curve)
    poly_months, poly_avg_commits = polynomial_fit(months_filtered, avg_commits_filtered, degree=3)
    # Create finer granularity for months (e.g., interpolate for monthly data)
    # months_interpolated = np.linspace(min(months_filtered), max(months_filtered), 500)
    # interpolated_commits = interp1d(months_filtered, avg_commits_filtered, kind='cubic')(months_interpolated)



    plt.figure(figsize=(10, 5))
    # plt.plot(months_interpolated, interpolated_commits, label="Interpolated Commits", color='pink')
    plt.plot(poly_months, poly_avg_commits, label="Polynomial Fit", color='red', linestyle='-', alpha=0.6, linewidth=2) #Polynomial Fit
    # plt.plot(months_filtered, avg_commits_smooth, label="Savitzky-Golay Smoothed", color='blue', linestyle='-', alpha=0.6, linewidth=2)
    # plt.plot(months_smooth, avg_commits_smooth, label="Average Commits", color='red', linestyle='-')
    # plt.plot(months_filtered, avg_commits_smooth2, label="Average Commits Gaussian", color='purple', linestyle='-')
    plt.plot(months_filtered, avg_commits_filtered, label="Average Commits", color='blue', linestyle='-', alpha=0.6, linewidth=2)
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
