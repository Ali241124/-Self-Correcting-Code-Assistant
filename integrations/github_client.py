
import os
import base64
import requests

from dotenv import load_dotenv
from urllib.parse import quote


# Load credentials from the local .env file.
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API_URL = "https://api.github.com"


def get_headers():
    """Create authenticated GitHub API headers."""

    if not GITHUB_TOKEN:
        raise ValueError(
            "GitHub token not found. Add GITHUB_TOKEN to your .env file."
        )

    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def get_github_file(owner, repo, file_path, branch="main"):
    """
    Retrieve a file from a GitHub repository.

    Returns the decoded file content and its SHA.
    """

    try:
        if not all([owner, repo, file_path, branch]):
            return {
                "success": False,
                "message": "Owner, repository, file path and branch are required."
            }

        encoded_owner = quote(owner, safe="")
        encoded_repo = quote(repo, safe="")
        encoded_path = quote(file_path, safe="/")

        url = (
            f"{GITHUB_API_URL}/repos/"
            f"{encoded_owner}/{encoded_repo}/contents/{encoded_path}"
        )

        response = requests.get(
            url,
            headers=get_headers(),
            params={"ref": branch},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if data.get("type") != "file":
            return {
                "success": False,
                "message": "The selected GitHub path is not a file."
            }

        if not data.get("content"):
            return {
                "success": False,
                "message": "GitHub returned no file content."
            }

        file_content = base64.b64decode(
            data["content"]
        ).decode("utf-8")

        return {
            "success": True,
            "content": file_content,
            "sha": data["sha"],
            "file_path": data["path"],
            "message": "GitHub file retrieved successfully."
        }

    except requests.exceptions.HTTPError as error:

        status = error.response.status_code

        return {
            "success": False,
            "message": f"GitHub API returned HTTP {status}."
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "message": f"GitHub connection failed: {error}"
        }

    except (ValueError, KeyError, UnicodeDecodeError) as error:

        return {
            "success": False,
            "message": f"Could not process GitHub file: {error}"
        }


def update_github_file(
    owner,
    repo,
    file_path,
    branch,
    content,
    sha,
    commit_message="AI: Fix Python code"
):
    """
    Update an existing GitHub file.

    The SHA must come from the file retrieved earlier.
    """

    try:
        if not all([owner, repo, file_path, branch, sha]):
            return {
                "success": False,
                "message": "Missing required GitHub file information."
            }

        if not isinstance(content, str):
            return {
                "success": False,
                "message": "File content must be a string."
            }

        encoded_owner = quote(owner, safe="")
        encoded_repo = quote(repo, safe="")
        encoded_path = quote(file_path, safe="/")

        url = (
            f"{GITHUB_API_URL}/repos/"
            f"{encoded_owner}/{encoded_repo}/contents/{encoded_path}"
        )

        encoded_content = base64.b64encode(
            content.encode("utf-8")
        ).decode("utf-8")

        payload = {
            "message": commit_message,
            "content": encoded_content,
            "sha": sha,
            "branch": branch
        }

        response = requests.put(
            url,
            headers=get_headers(),
            json=payload,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return {
            "success": True,
            "message": "File successfully committed to GitHub.",
            "commit_sha": data["commit"]["sha"],
            "commit_url": data["commit"]["html_url"]
        }

    except requests.exceptions.HTTPError as error:

        status = error.response.status_code

        return {
            "success": False,
            "message": f"GitHub API returned HTTP {status}."
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "message": f"GitHub connection failed: {error}"
        }

    except (ValueError, KeyError) as error:

        return {
            "success": False,
            "message": f"Could not process GitHub response: {error}"
        }
