# Who-Wrote-It-Humans-or-AI

### Project Overview

"Who Wrote It: Humans or AI?" is our research project that uses Botsniffer, Pydriller, and Github API to get statistics to help answer research questions on the impact of AI-generated OSS code. Our aim is to assess ChatGPT's influence on code generation in OSS development and analyze how the AI tool affects productivity and collaboration over time.

---

### File Breakdown

#### **Botsniffer Files**

- **botsniffervalid Folder**:
  Contains the results from the Botsniffer tool, which was used to validate the classification of code as AI-generated or human-written.

  - **ai_generated Folder**:
    Contains all AI-generated Python files that were used to validate Botsniffer.

  - **human_written Folder**:
    Contains human-written Python files used to validate Botsniffer.

  - **ai_code_detected_for_commit.py**:
    Script to checkout commits from repositories for analysis. It also runs Botsniffer to gather metrics such as AI detection, complexity, repetition, etc.

  - **bot_analysis2.py**:
    Analyzes files flagged as AI-generated (`AI=True`) from Botsniffer's output. This script performs further analysis to capture metrics like keyword analysis and structural patterns.

#### **GitHub API Files**

- **issues_pr_bugs2.py**:
  Code uses the GitHub API to get the pull request, issues, bugs, comments and reviewers per PR, and comments per issue for all the repositories we checked out, and get the averages for each of those metrics from 2019 to 2025. The graph the results for each metric using Matplotlib.

- **reviewers.py**:
  This code uses the GitHub API to get the number of reviewers per pull request and get the average. We used this code to mainly get the average reviewers per PR since the file above was slow.

#### **Pydriller Files**

- **avg_churn4.py**:
  Code that uses Pydriller to get the number of insertions and deletions for each repository, and that's how we kept track of churn per commit. Then average the churn for every repository for commits between 2019 and 2025. Using Matplotlib, graph this metric.

- **avg_commits2.py**:
  Similar to the churn code, this uses Pydriller to get the number of commits between 2019 and 2025 for each repository. Then average the commits for every repository between 2019 and 2025. Using Matplotlib, graph this metric.

- **clone_repos_by_date.py**:
  This script is used to clone the repositories that we analyzed for metrics.

