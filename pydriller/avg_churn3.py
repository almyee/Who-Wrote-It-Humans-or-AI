import hashlib
import multiprocessing as mp
import shutil
from multiprocessing import Lock
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num
from dateutil.relativedelta import relativedelta
from pydriller import Repository
from datetime import datetime as dt
from tqdm import tqdm
import numpy as np
from calendar import monthrange
import gc

# Constants for date range
GLOBAL_START_DATE = dt(2019, 10, 1)
GLOBAL_END_DATE = dt(2025, 2, 1)

# Generates a list of dates from startDate to endDate split by the given stepSize (e.g., one month).
# Useful for chunking data into consistent time intervals for analysis.
def createMonthList(startDate: dt, endDate: dt, stepSize: relativedelta):
    monthList = []
    while startDate < endDate:
        monthList.append(startDate)
        startDate += stepSize
    monthList.append(endDate)
    return monthList

# Creates a new temporary directory with versioning to avoid overwriting existing ones.
def get_new_temp_dir(base_dir):
    version = 0
    new_temp_dir = f"{base_dir}_v{version}"
    while os.path.exists(new_temp_dir):
        version += 1
        new_temp_dir = f"{base_dir}_v{version}"
    os.mkdir(new_temp_dir)
    return new_temp_dir

# Splits the total date range of the repository into smaller intervals (timeDelta).
# Distributes the date ranges across multiple worker directories for parallel processing.
def createJobsByTimeDelta(repoPath: str, timeDelta: relativedelta, directories: list[str]) -> list:
    assert os.path.exists(repoPath)
    monthList = createMonthList(GLOBAL_START_DATE, GLOBAL_END_DATE, timeDelta)
    # print("month list: " , monthList)
    monthPairs = [(monthList[i], monthList[i + 1]) for i in range(len(monthList) - 1)]
    jobList = []
    for i, dateRanges in zip(range(len(directories)), np.array_split(monthPairs, len(directories))):
        jobList.append({
            "id": i,
            "dateRanges": dateRanges.tolist(),
            "directory": directories[i]
        })
    return jobList

# A worker function that runs in parallel.
# For a given time interval, calculates:
# Insertions: Number of lines added.
# Deletions: Number of lines removed.
# Churn: Total changes (insertions + deletions).
# Returns results grouped by time range.
# def codeChurnJob(job) -> tuple:
#     id = job["id"]
#     repoPath = job["directory"]
#     dateRanges = job["dateRanges"]
#     finishedJobs = []
#     for (startDate, endDate) in tqdm(dateRanges, position=id, desc=f"Thread {id}: "):
#         temp = {
#             "id": id,
#             "repoPath": repoPath,
#             "startDate": startDate,
#             "endDate": endDate,
#             "insertions": 0,
#             "deletions": 0,
#             "churn": 0
#         }
#         for commit in Repository(path_to_repo=repoPath, since=startDate, to=endDate).traverse_commits():
#             temp["insertions"] += commit.insertions
#             temp["deletions"] += commit.deletions
#         temp["churn"] = temp["insertions"] + temp["deletions"]
#         finishedJobs.append(temp)
#     return id, repoPath, finishedJobs
def codeChurnJob(job):
    id = job["id"]
    repoPath = job["directory"]
    dateRanges = job["dateRanges"]
    finishedJobs = []
    try:
        for (startDate, endDate) in tqdm(dateRanges, position=id, desc=f"Thread {id}: "):
            temp = {
                "id": id,
                "repoPath": repoPath,
                "startDate": startDate,
                "endDate": endDate,
                "insertions": 0,
                "deletions": 0,
                "churn": 0
            }
            for commit in Repository(path_to_repo=repoPath, since=startDate, to=endDate).traverse_commits():
                temp["insertions"] += commit.insertions
                temp["deletions"] += commit.deletions
            temp["churn"] = temp["insertions"] + temp["deletions"]
            finishedJobs.append(temp)
    except Exception as e:
        print(f"Error in Thread {id}: {e}")
    return id, repoPath, finishedJobs

# Orchestrates the parallel execution of codeChurnJob across multiple processes.
# Splits the repository analysis into several jobs to improve performance.
# Collects results from all worker processes.
def codeChurnPerDelta(repoPath: str, timeDelta: relativedelta, tempDir: str, numDirectories) -> (list, list):
    assert numDirectories <= mp.cpu_count() - 1 

    new_temp_dir = get_new_temp_dir(tempDir)
    dirs = createMultipleRepos(repoPath, new_temp_dir, numDirectories)
    jobs = createJobsByTimeDelta(repoPath, timeDelta, dirs)

    # Use a safer multiprocessing context
    ctx = mp.get_context("spawn")

    # with ctx.Pool(processes=numDirectories) as pool:
    #     result = pool.map(codeChurnJob, jobs)
    with ctx.Pool(processes=numDirectories) as pool:
        result = list(pool.imap_unordered(codeChurnJob, jobs))
        pool.close()  # Explicitly close the pool
        pool.join()   # Ensure all processes terminate properly

    gc.collect()  # Force garbage collection to clean up semaphores
    return result

# Copies the source Git repository into several directories.
# Each copy will be processed in parallel by separate processes.
def createMultipleRepos(sourceDir: str, tempDir: str, numCopies: int) -> list[str]:
    directories = []
    for i in range(numCopies):
        tempDirName = os.path.join(tempDir, f"tempDir_{i}", ".git")
        # shutil.copytree(sourceDir, tempDirName)
        shutil.copytree(sourceDir, tempDirName, ignore=shutil.ignore_patterns('.git'))

        directories.append(tempDirName)
    return directories

def plot_stats(months, avg_churn):
    start_dt = dt(2019, 10, 1)
    end_dt = dt(2025, 1, 1)
    xmonths_complete_dt = []
    current_dt = start_dt
    gpt_dates = [
    ("gpt-3.5", "2022-11"),
    ("gpt-4", "2023-03"),
    ("gpt-4o", "2024-05")
    ]
    gpt_dates_dt = [dt.strptime((date[1]), "%Y-%m") for date in gpt_dates]
    gpt_dates_num = [date2num(gpt_date) for gpt_date in gpt_dates_dt]

    while current_dt <= end_dt:
        xmonths_complete_dt.append(current_dt)
        current_dt += relativedelta(months=3)
    
    xmonths_numeric = date2num(xmonths_complete_dt)
    months_numeric = date2num(months)
    
    # valid_indices = [i for i, m in enumerate(months) if start_dt <= m <= end_dt]
    months_dt = [dt.strptime(m, "%Y-%m") for m in months]  # Convert string dates to datetime objects
    valid_indices = [i for i, m in enumerate(months_dt) if start_dt <= m <= end_dt]

    # months_filtered = [months[i] for i in valid_indices]
    # avg_churn_filtered = [avg_churn[i] for i in valid_indices]
    months_filtered = [months_dt[i] for i in valid_indices]
    avg_churn_filtered = [avg_churn[i] for i in valid_indices]

    
    # print(f"Filtered months: {len(months_filtered)}")  # Debugging line
    # print(f"Filtered avg_commits: {len(avg_churn_filtered)}")  # Debugging line
    
    if len(months_filtered) != len(avg_churn_filtered):
        print("Error: Mismatch in the number of filtered months and commits.")
        return
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(months_numeric, avg_churn, label="Average Churn")  # Use numerical dates

    # Now uncomment the GPT vertical lines with the correct x-axis scale
    for i, (label, date_num) in enumerate(zip([d[0] for d in gpt_dates], gpt_dates_num)):
        plt.axvline(x=date_num, color='orange', linestyle='--', linewidth=1, label=f"({i+1}) {label}")
        plt.text(date_num + 20, plt.ylim()[1] * 0.88, f"({i+1})", color='orange', rotation=0, 
                verticalalignment='bottom', horizontalalignment='center')

    # Adjust x-axis ticks to use the correct datetime format
    plt.xticks(ticks=date2num(xmonths_complete_dt), labels=[dt.strftime(date, "%Y-%m") for date in xmonths_complete_dt], rotation=45)

    plt.xlabel("Months")
    plt.ylabel("Code Churn")
    plt.title("Code Churn Over Time")
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()


# Defines the main execution block of the script.
# Calls the analysis functions and gathers results.
# Sorts the results by date.
# Uses matplotlib to plot code churn (total changes) over time.
if __name__ == "__main__":
    repoFolder = "../cloned_commits" #"../github-api/test_repo"
    tempDir = "../temp/tempDir"

    # folder_path =   "../cloned_commits" #"../github-api/test_repo" # Path to your local folder of repos
    folder_stats = {}
    merged_avg_churn = []
    merged_months = []
    for folder in os.listdir(repoFolder): #folder = date
        # print("date: ", folder)
        merged_churn_per_date = []
        # all_repos = [os.path.join(repoFolder, d) for d in os.listdir(repoFolder) if os.path.isdir(os.path.join(repoFolder, d))]
        combined_data = {}
        if (folder == ".DS_Store"):
            continue
        folder_full_path = os.path.join(repoFolder, folder)
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
                for folder4 in os.listdir(folder_full_path3): #folder = repo name 2
                    if (folder4 == ".DS_Store"):
                        continue
                    folder_full_path4 = os.path.join(folder_full_path3, folder4)
                    print("folder_full_path3: ", folder_full_path4)
                    if os.path.isdir(folder_full_path3):  # Check if it's a directory
                        result = codeChurnPerDelta(
                            repoPath=folder_full_path4,
                            timeDelta=relativedelta(months=1),
                            tempDir=tempDir,
                            numDirectories=7  # One less than CPU count
                        )
                        ids, paths, data = zip(*result)
                        dataSorted = sorted([item for sublist in data for item in sublist], key=lambda x: x["startDate"])
                        for item in dataSorted:
                            month = item["startDate"].strftime("%Y-%m")
                            combined_data.setdefault(month, []).append(item["churn"])
                    # print("averaged_stats: ", avg_commits)   
                    months = sorted(combined_data.keys())
                    merged_months.extend(months)
                    avg_churn = [np.mean(combined_data[month]) for month in months] #combined_data.values() #
                    merged_avg_churn.extend(avg_churn)
                    merged_churn_per_date.extend(avg_churn)
                    # merged_months, merged_avg_commits = merge_averaged_stats((merged_months, merged_avg_commits), (months, avg_commits))
        avg_churn_date = sum(merged_churn_per_date)/len(merged_churn_per_date)
        print("avg_churn_date: ", avg_churn_date, folder)
    # Sort merged data properly
    if merged_months and merged_avg_churn:
        merged_data = sorted(zip(merged_months, merged_avg_churn), key=lambda x: x[0])
        merged_months, merged_avg_churn = zip(*merged_data)
        merged_months = list(merged_months)
        merged_avg_churn = list(merged_avg_churn)
    plot_stats(merged_months, merged_avg_churn)