import csv
import json
import os.path
import subprocess
from datetime import datetime
from urllib.parse import urlparse

from dateutil.relativedelta import relativedelta

from pydriller import Repository, Git
import uuid
from tqdm import tqdm

# List of GitHub repository URLs
repo_url_links = [
    "https://github.com/bitcoin/bitcoin",
    "https://github.com/google/osv.dev",
    "https://github.com/mitmproxy/mitmproxy",
    "https://github.com/deepspeedai/DeepSpeed",
    "https://github.com/ultralytics/ultralytics",
    "https://github.com/OpenBB-finance/OpenBB",
    "https://github.com/gradio-app/gradio",
    "https://github.com/hankcs/HanLP",
    "https://github.com/sqlmapproject/sqlmap",
    "https://github.com/huggingface/pytorch-image-models",
    "https://github.com/python-poetry/poetry",
    "https://github.com/certbot/certbot",
    "https://github.com/jax-ml/jax",
    "https://github.com/facebookresearch/detectron2",
    "https://github.com/khoj-ai/khoj",
    "https://github.com/deezer/spleeter",
    "https://github.com/explosion/spaCy",
    "https://github.com/tqdm/tqdm",
    "https://github.com/Lightning-AI/pytorch-lightning",
    "https://github.com/tinygrad/tinygrad",
    "https://github.com/huggingface/diffusers",
    "https://github.com/mindsdb/mindsdb",
    "https://github.com/python-telegram-bot/python-telegram-bot",
    "https://github.com/vwxyzjn/cleanrl",
    "https://github.com/ytdl-org/youtube-dl",
    "https://github.com/electron/electron",
    "https://github.com/yt-dlp/yt-dlp",
    "https://github.com/open-webui/open-webui",
    "https://github.com/OpenInterpreter/open-interpreter",
    "https://github.com/Stirling-Tools/Stirling-PDF",
    "https://github.com/krahets/hello-algo",
    "https://github.com/langgenius/dify",
    "https://github.com/langflow-ai/langflow",
    "https://github.com/All-Hands-AI/OpenHands",
    "https://github.com/oobabooga/text-generation-webui",
    "https://github.com/karpathy/nanoGPT",
    "https://github.com/openai/whisper",
    "https://github.com/abi/screenshot-to-code",
    "https://github.com/microsoft/markitdown",
    "https://github.com/myshell-ai/OpenVoice",
    "https://github.com/browser-use/browser-use",
    "https://github.com/unslothai/unsloth",
    "https://github.com/openai/chatgpt-retrieval-plugin",
    "https://github.com/PromtEngineer/localGPT",
    "https://github.com/openai/swarm",
    "https://github.com/GaiZhenbiao/ChuanhuChatGPT",
]


def dir_from_repo_url(repo_url: str, root_dir: str) -> str:
    """
    Construct a directory path of git repository in a given directory that exists already
    """
    path = urlparse(repo_url).path
    repo_owner = path.split(sep= '/')[-2]
    repo_name = path.split(sep= '/')[-1]
    return os.path.join(root_dir, repo_owner, repo_name)

def check_repos(repo_urls: list[str], root_dir: str) -> list[str]:
    """
    This function checks to see if the repositories given are installed
    on the system in the given directory

    Returns list of repos that have not been installed in the root directory
    """
    # Check if the root directory exists.
    # If not, then every repository needs to be downloaded
    if not os.path.exists(root_dir):
        return repo_urls

    repos_not_installed = []
    for repo_url in repo_urls:
        if not os.path.exists(dir_from_repo_url(repo_url, root_dir)):
            repos_not_installed.append(repo_url)

    return repos_not_installed

def download_repos(root_dir: str, repo_urls: list[str]) -> None:
    """
    Download git repositories in the given root directory.

    If the root directory does not exist, then create it
    """

    if len(repo_urls) <= 0:
        raise Exception("Repository URL list is empty")

    # Create root directory if it does not exist
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)

    # Download git repositories
    for repo_url in repo_urls:
        subprocess.run(args= ["git", "clone", repo_url, dir_from_repo_url(repo_url, root_dir)])

def assert_dir(directory: str):
    assert(os.path.exists(directory))

def analyze_repos_for_ai(dates_to_analyze: list[datetime], repo_urls: list[str], root_dir: str, temp_dir: str) -> list[dict]:
    """
    Analyse github repositories in a directory for AI usage with botsniffer
    Analyze the repository at 4 commits:
        - Just before GPT-3.5 release
        - Just before GPT-4 release
        - 104 Days after GPT-4 release
        - Latest commit (6 march 2025)
    """
    # check if temp dir exists
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    ret = []
    pbar = tqdm(repo_urls, position=0)

    for repo_url in pbar:
        pbar_desc_format = f"Analyzing Repository: {repo_url}"
        pbar.set_description(pbar_desc_format)
        # print(f"\n--- Analyizing: {repo_url} ---")
        repo_path = dir_from_repo_url(repo_url, root_dir)
        if not os.path.exists(repo_path):
            # print("f\nREPO NOT FOUND")
            continue
        if not os.path.exists(os.path.join(repo_path, ".git")):
            # print("\nNOT A GIT REPOSITORY")
            continue

        ret.append({
            "repository_path": repo_path,
            "commits": []
        })
        for date in dates_to_analyze:
            commit_hash = getCommitOnDate(date, repo_path)
            pbar.set_description(pbar_desc_format + f"\nDate: {date}\nCommit: {commit_hash}")
            if commit_hash is None:
                # print(f"Could not find commit after date: {date}")
                ret[-1]["commits"].append({
                    "date": date,
                    "commit_hash": "NOT FOUND",
                    "found_commit": False
                })
            else:
                gr = Git(path= repo_path)
                temp_file_path = os.path.join(temp_dir, uuid.uuid4().hex[:8]) + ".out"
                # Try catch in case something breaks, we still need to restore git repository to master branch
                # or sometimes pydriller can't find commits when the repo is in a detatched head mode.
                try:

                    gr.reset()

                    # print(f"Analyzing {commit_hash} ({date})\n")
                    gr.checkout(commit_hash)

                    subprocess.run(args=["botsniffer", "--train", repo_path], capture_output=True)

                    # Create a file name for this run to store the botsniffer output

                    with open(temp_file_path, "w+") as file:
                        subprocess.run(args=["botsniffer", "--identify", repo_path], stdout=file)

                    ret[-1]["commits"].append({
                        "date": date,
                        "commit": commit_hash,
                        "data": parseBotsnifferOutput(temp_file_path),
                        "found_commit": True
                    })

                    # Need to reset repository or sometime pydriller can't find commits
                    gr.reset()
                except Exception as e:
                    gr.reset()
                    err_msg = f"""
                    Error: {e}
                    File Path: [red] {temp_file_path} [/red]
                    Repository: {repo_url}
                    Repository has been reset to master branch
                    """
                    raise Exception(err_msg)

    return ret

def parseBotsnifferOutput(file_path: str) -> list[dict]:
    ret = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        if len(lines) <= 3:
            return ret
        for i in range(0, len(lines), 3):
            if "Done!" in lines[i]:
                break
            file_path = lines[i].split(' ', 1)[1]
            is_ai = True if "True" in lines[i + 1] else False
            features = lines[i + 2].split(' ', 1)[1]
            ret.append({
                "file": file_path,
                "is_ai": is_ai,
                "features": features
            })
    return ret

def getCommitOnDate(date: datetime, repo_path: str) -> str | None:
    """
    Returns the first commit hash after a specified date
    """
    if not os.path.exists(os.path.join(repo_path, ".git")):
        # print("returning none?")
        return None

    # print(date)
    end_date = date + relativedelta(days=2)
    # print(repo_path)
    for commit in Repository(path_to_repo= repo_path, since= date, to=end_date).traverse_commits():
        # print(commit)
        return commit.hash

def process_data(data: list[dict]) -> list[dict]:
    """
    """
    ret = []
    for repository in data:
        new_dict = {
            "repository": repository["repository_path"],
            "commits": []
        }
        for commits in repository["commits"]:
            if not commits["found_commit"]:
                continue
            commit_dict = {
                "num_files": 0,
                "num_files_ai": 0,
                "commit_hash": commits["commit"],
                "date": commits["date"].strftime("%m-%d-%Y"),
                "features": {
                    "comment_quality": 0.0,
                    "code_identation": 0.0,
                    "style_adherence": 0.0,
                    "repetitive_patterns": 0.0,
                    "code_complexity": 0.0
                }
            }
            for file in commits["data"]:
                commit_dict["num_files"] += 1
                if file["is_ai"]:
                    commit_dict["num_files_ai"] += 1

                file["features"] = file["features"].replace("'", '"').replace("np.float64(", "").replace(")","")

                # print(file["features"])
                features = json.loads(file["features"])
                for key, val in features.items():
                    commit_dict["features"][key] += features[key]
                # commit_dict["features"]["comment_quality"] += features["comment_quality"]
                # commit_dict["features"]["code_indentation"] += features["code_indentation"]
                # commit_dict["features"]["style_adherence"] += features["style_adherence"]
                # commit_dict["features"]["repetitive_patterns"] += features["repetitive_patterns"]
                # commit_dict["features"]["code_complexity"] += features["code_complexity"]

            for key, val in commit_dict["features"].items():
                commit_dict["features"][key] = commit_dict["features"][key] / len(commits["data"])
            new_dict["commits"].append(commit_dict)
        ret.append(new_dict)
    return ret
def save_data_to_csv(save_dir: str, processed_data: list[dict]) -> str:
    # Create save dir if it doesn't exist
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    csv_data = []
    for data in processed_data:
        repository = data["repository"]
        for commit in data["commits"]:
            features = commit["features"]
            new_dict = {
                "repository": repository,
                "date": commit["date"],
                "commit_hash": commit["commit_hash"],
                "num_files": commit["num_files"],
                "num_ai": commit["num_files_ai"],
                "code_identation": features["code_identation"],
                "comment_quality": features["comment_quality"],
                "style_adherence": features["style_adherence"],
                "repetitive_patterns": features["repetitive_patterns"],
                "code_complexity": features["code_complexity"]
            }
            csv_data.append(new_dict)
    save_file_path = os.path.join(save_dir, uuid.uuid4().hex[:8] + ".csv")
    fieldnames = ["repository", "date", "commit_hash", "num_files", "num_ai", "code_identation","comment_quality", "style_adherence","repetitive_patterns", "code_complexity"]
    with open(save_file_path, "w+") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    return save_file_path

def repo_path_generator(root_dir: str, repo_urls: list[str]):
    """
    Yields repositories in a directory
    The nested directories must contain a .git folder
    """
    # print(path)
    for repo_url in repo_urls:
        if os.path.exists(dir_from_repo_url(repo_url, root_dir)):
            yield dir_from_repo_url(repo_url, root_dir)

if __name__ == "__main__":
    repo_dir = "tempRepos"
    # lis = list(repo_path_generator(temp_dir, repo_urls))
    # print(lis)
    # print(len(lis))
    # repos_not_downloaded = check_repos(repo_urls, temp_dir)
    # download_repos(root_dir= temp_dir, repo_urls= repo_urls)
    # test = ['tempRepos/bitcoin/bitcoin']
    # repos = list(repo_path_generator(temp_dir, repo_urls))
    commit_dates = [
        datetime(year=2021, month=10, day= 28),
        datetime(year=2022, month=11, day=29),
        datetime(year=2023, month=3, day=13),
        datetime(year=2023, month=6, day=25),
        datetime(year=2024, month=3, day=6),
        datetime(year=2024, month=9, day=6),
        datetime(year=2025, month=3, day=6)
    ]


    data = analyze_repos_for_ai(repo_urls= repo_url_links,
                         dates_to_analyze=commit_dates,
                         root_dir=repo_dir,
                         temp_dir= "temp_files")

    processed_data = process_data(data)
    # print(processed_data)
    save_file = save_data_to_csv("save_data", processed_data)
    print(f"Done!\n\nSaved output to: {save_file}")
