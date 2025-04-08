#!/usr/bin/env python3

import os
import shutil
import logging
from pathlib import Path

from huggingface_hub import HfApi
from huggingface_hub.utils import validate_repo_id

from lerobot.common.datasets.utils import create_lerobot_dataset_card, create_branch
from lerobot.common.constants import HF_LEROBOT_HOME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_dataset_to_hf(
    local_dataset_path: str,
    repo_id: str,
    version: str = "v2.1",
    description: str = "Robotics dataset uploaded via LeRobot",
    private: bool = False,
):
    """
    Upload a locally stored LeRobot dataset to Hugging Face Hub with proper versioning.
    
    Args:
        local_dataset_path: Path to the local dataset directory
        repo_id: The Hugging Face repo_id (username/dataset_name)
        version: The version tag to create (should match the codebase_version in info.json)
        description: Short description for the dataset
        private: Whether the repository should be private
    """
    # Validate paths and repo ID
    local_path = Path(local_dataset_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local dataset path does not exist: {local_path}")
    
    # Check if meta/info.json exists
    info_path = local_path / "meta" / "info.json"
    if not info_path.exists():
        raise FileNotFoundError(f"Required metadata file not found: {info_path}")
    
    # Initialize Hugging Face API
    validate_repo_id(repo_id)
    api = HfApi()
    logger.info(f"Creating or updating dataset repository: {repo_id}")
    
    try:
        # Create repo if it doesn't exist
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            exist_ok=True,
            private=private,
        )
        
        # Create dataset card with basic info
        readme_content = create_lerobot_dataset_card(
            repo_id=repo_id,
            description=description,
        )
        
        # Upload all files
        logger.info(f"Uploading dataset files to {repo_id}...")
        api.upload_folder(
            folder_path=local_path,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Upload dataset with version {version}",
        )
        
        # Create version branch/tag
        create_branch(repo_id=repo_id, branch=version, repo_type="dataset")
        logger.info(f"Successfully created version branch/tag: {version}")
        
        logger.info(f"Dataset uploaded successfully to {repo_id} with version {version}")
        return f"https://huggingface.co/datasets/{repo_id}"
    
    except Exception as e:
        logger.error(f"Error uploading dataset: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload a local LeRobot dataset to Hugging Face Hub")
    parser.add_argument(
        "--local-path",
        type=str,
        default="/Users/artem/.cache/huggingface/lerobot/Demonion/socks_basket/",
        help="Path to the local dataset directory"
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="Demonion/socks_basket",
        help="HuggingFace repository ID (username/dataset_name)"
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v2.1",
        help="Version tag to create (should match codebase_version in info.json)"
    )
    parser.add_argument(
        "--description",
        type=str,
        default="Robotics dataset for socks task",
        help="Short description for the dataset"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Whether the repository should be private"
    )
    
    args = parser.parse_args()
    result_url = upload_dataset_to_hf(
        local_dataset_path=args.local_path,
        repo_id=args.repo_id,
        version=args.version,
        description=args.description,
        private=args.private,
    )
    
    print(f"\nDataset uploaded successfully!")
    print(f"Dataset URL: {result_url}")
    print(f"To visualize it, run: python lerobot/scripts/visualize_dataset.py --repo-id {args.repo_id} --episode-index 0") 