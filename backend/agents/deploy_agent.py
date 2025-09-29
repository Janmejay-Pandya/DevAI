import os
import json
import asyncio
import subprocess
from utils.terminal_utils import TerminalLogger

# Load deployment commands
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "deployment_commands.json"), "r") as file:
    commands = json.load(file)


async def deploy_to_github(
    github_username="Miran-Firdausi", repo_name="automated-repo-test", project_id=1
):
    project_dir = os.path.abspath(
        os.path.join(".", "code-environment", f"project-{project_id}")
    )

    for command_item in commands:
        try:
            raw_command = command_item["command"]
            description = command_item["description"]

            # Format the command dynamically
            command = raw_command.replace("{USERNAME}", github_username).replace(
                "{REPO}", repo_name
            )

            if command.startswith("sleep"):
                seconds = int(command.split()[1])
                print(f"Sleeping for {seconds} seconds...")
                await asyncio.sleep(seconds)
                continue

            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_dir,
            )
            success_message = f"{description}. Command '{command}' executed successfully:\n{result.stdout.decode()}"
            await TerminalLogger.log("success", "deployment", success_message)

        except subprocess.CalledProcessError as e:
            error_message = f"Error executing command '{command}':\n{e.stderr.decode()}"
            await TerminalLogger.log("error", "deployment", error_message)
