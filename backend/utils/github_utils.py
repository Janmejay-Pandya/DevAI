import requests


def github_user_exists(username):
    try:
        response = requests.get(f"https://api.github.com/users/{username}", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def github_repo_exists(username, repo_name):
    try:
        response = requests.get(
            f"https://api.github.com/repos/{username}/{repo_name}", timeout=5
        )
        return response.status_code == 200
    except requests.RequestException:
        return False
