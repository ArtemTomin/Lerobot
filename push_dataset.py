from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
import os

# Target repository ID on Hugging Face Hub
# This ID should match the directory name in the cache
hub_repo_id = "Demonion/socks_basket"

# Assumes dataset is now located at ~/.cache/huggingface/lerobot/Demonion/socks_basket
# Initialize the dataset object with the target Hub repo ID
dataset = LeRobotDataset(repo_id=hub_repo_id)

print(f"Pushing dataset '{hub_repo_id}' to the Hub...")
# Set private=True if you want the repository to be private on the Hub
dataset.push_to_hub(private=False)
print("Done.") 