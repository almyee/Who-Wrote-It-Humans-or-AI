# Who-Wrote-It-Humans-or-AI-
Who Wrote It: Humans or AI? A research project that uses Botsniffer, Pydriller, and Github API to get statistics to help answer research questions on the impact of AI-generated OSS code.

Botsniffer Files:
- botsniffervalid folder:
    - ai_generated foler: contains all the AI=generated Python files we used to validate Botsniffer
    - human_written folder: contains all the human-written Python files we used to validate Botsniffer
 
- ai_code_detected_for_commit.py: one of the scripts used to checkout the commits from each repository we wanted to run our metrics on. Also ran the Botsniffer tool on each repository to get the metrics Botsniffer provided such as AI detection, complexity, repetition, etc.
- bot_analysis2.py: script that analyzed the files returned AI=True from running botsniffer and ran further analysis on those files to capture metrics like kewword analysis and structural patterns.

GitHub API Files:
- issues_pr_bugs2.py: code uses the GitHub API to get the pull request, issues, bugs, comments and reviewers per PR, and comments per issue for all the repositories we checked out, and get the averages for each of those metrics from 2019 to 2025. The graph the results for each metric using Matplotlib.
- reviewers.py: this code uses the GitHub API to get the number of reviewers per pull request and get the average. We used this code to mainly get the average reviewers per PR since the file above was slow. 

Pydriller Files:
- avg_churn4.py: code that uses Pydriller to get the number of insertions and deletions for each repository and that is how we kept track of churn per commit. Then average the churn for every repository for commits between 2019 and 2025. Using Matplotlib graph this metric.
- avg_commits2.py: similar to the churn code this uses Pydriller to get the number of commits  between 2019 and 2025 for each repository. Then average the commits for every repository between 2019 and 2025. Using Matplotlib graph this metric.

clone_repos_by_date.py: script used to clone the repositories we wanted to get our metrics on