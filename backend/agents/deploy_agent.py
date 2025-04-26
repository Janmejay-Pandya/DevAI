import json
import os
import subprocess
import time

# Load deployment commands
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "deployment_commands.json"), "r") as file:
    commands = json.load(file)

project_dir = os.path.abspath(os.path.join(".", "code-environment"))

def deploy_to_github(github_username = "Miran-Firdausi", repo_name = "automated-repo-3"):
    for command_item in commands:
        try:
            raw_command = command_item["command"]
            description = command_item["description"]

            # Format the command dynamically
            command = raw_command.replace("{USERNAME}", github_username).replace("{REPO}", repo_name)

            # Special case: sleep
            if command.startswith("sleep"):
                seconds = int(command.split()[1])
                print(f"Sleeping for {seconds} seconds...")
                time.sleep(seconds)
                continue

            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_dir,
            )
            print(f"{description}. Command '{command}' executed successfully:\n{result.stdout.decode()}")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command '{command}':\n{e.stderr.decode()}")
