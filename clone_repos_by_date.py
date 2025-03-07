# able to clone all repos, organized commit by date cloned_commits folder has folders: "2022-11-29", "2023-03-13", "2023-06-25", "2024-03-06"
import os
import subprocess
from datetime import datetime

# List of GitHub repository URLs
repo_urls = [
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


# Dates for commits
# 11/29/22,  right before gpt-4 release 3/13/23, 6/25/23, 3/6/2025 
commit_dates = [
    "2022-11-29",
    "2023-03-13",
    "2023-06-25",
    "2024-03-06"
]

# Directory to store cloned commits
base_dir = "cloned_commits"
os.makedirs(base_dir, exist_ok=True)

for repo_url in repo_urls:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_owner = repo_url.rstrip("/").split("/")[-2]
    temp_clone_dir = f"{base_dir}/temp/{repo_owner}/{repo_name}"

    if not os.path.exists(temp_clone_dir):
        # Print debug info
        print(f"Cloning into: {temp_clone_dir}")
        os.makedirs(temp_clone_dir, exist_ok=True)  # Ensure directory exists

        # Clone the repo into a temporary directory
        print(f"Cloning {repo_url} into {temp_clone_dir}...")
        subprocess.run(["git", "clone", repo_url, temp_clone_dir], check=True)

    # Ensure the clone actually succeeded
    if not os.path.exists(temp_clone_dir) or not os.listdir(temp_clone_dir):
        print(f"Error: {temp_clone_dir} does not exist or is empty after cloning!")
        continue

    print(f"Successfully cloned into {temp_clone_dir}")

    for date in commit_dates:
        if not os.path.exists(f"{base_dir}/{date}"):
            os.makedirs(f"{base_dir}/{date}", exist_ok=True)

        if not os.path.exists(temp_clone_dir) or not os.listdir(temp_clone_dir):
            print(f"Error: {temp_clone_dir} does not exist or is empty after cloning!")
            continue

        # Use absolute paths instead of changing directories with os.chdir
        commit_hash = subprocess.check_output(
            ["git", "rev-list", "-n", "1", "--before", date, "HEAD"],
            cwd=temp_clone_dir  # Specify the working directory here
        ).decode().strip()

        if commit_hash:
            target_dir = f"{base_dir}/{date}/{repo_owner}/{repo_name}"
            os.makedirs(target_dir, exist_ok=True)

            # Instead of cloning again, just checkout the commit in the target directory
            subprocess.run(["git", "checkout", commit_hash], cwd=temp_clone_dir, check=True)

            # Now copy the necessary files to target_dir (if needed)
            # subprocess.run(["cp", "-r", temp_clone_dir, target_dir], check=True)
            try:
                subprocess.run(["cp", "-r", temp_clone_dir, target_dir], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error during copy: {e}")
                print("Some files or directories may be missing.")  


    # Cleanup temporary clone after processing
    subprocess.run(["rm", "-rf", temp_clone_dir], check=True)





