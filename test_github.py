
from integrations.github_client import GITHUB_TOKEN

if GITHUB_TOKEN:
    print("GitHub token loaded successfully!")
else:
    print("GitHub token not found. Check your .env file.")
