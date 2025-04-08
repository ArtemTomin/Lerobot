import argparse
import logging
import requests.exceptions
# Only import HfApi
from huggingface_hub import HfApi

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Delete a branch from a Hugging Face Hub repository.")
    parser.add_argument("--repo_id", type=str, required=True, help="Repository ID (e.g., 'YourUsername/repo-name').")
    parser.add_argument("--branch", type=str, required=True, help="Branch name to delete.")
    parser.add_argument("--repo_type", type=str, default="dataset", help="Type of repository ('dataset', 'model', 'space').")

    args = parser.parse_args()

    if args.branch == "main":
         logging.warning("Warning: Attempting to delete the 'main' branch.")
         logging.warning("Ensure you have set a different default branch first via the website settings.")

    api = HfApi()

    try:
        logging.info(f"Attempting to delete branch '{args.branch}' from {args.repo_type} repository '{args.repo_id}'...")
        api.delete_branch(repo_id=args.repo_id, branch=args.branch, repo_type=args.repo_type)
        logging.info(f"Successfully deleted branch '{args.branch}'.")

    # Catch only generic HTTPError and check status codes
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        if status_code == 401: # Unauthorized
             logging.error(f"Error: Authentication failed (HTTP 401). Check your Hugging Face token.")
        elif status_code == 403: # Forbidden
             logging.error(f"Error: Access denied (HTTP 403). Make sure you have rights to modify this repository.")
        elif status_code == 404: # Not Found
             logging.error(f"Error: Repository '{args.repo_id}' or branch '{args.branch}' not found (HTTP 404).")
        elif status_code == 412: # Precondition Failed
             logging.error(f"Error: Cannot delete branch '{args.branch}' because it is likely the default branch (HTTP 412).")
             logging.error("Please set a different default branch first in the repository settings on the Hugging Face website.")
        else:
             # Log other HTTP errors
             logging.error(f"HTTP Error deleting branch (Status: {status_code}): {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 