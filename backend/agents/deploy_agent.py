import json
import os
import subprocess

with open("deployment_commands.json", "r") as file:
    commands = json.load(file)

project_dir = None  # Stores the working directory dynamically

# Execute each command
for command_item in commands:
    try:
        command = command_item["command"]

        # Detect `cd <folder_name>` and update project_dir
        if command.startswith("cd "):
            project_dir = os.path.abspath(command.split(" ", 1)[1])

        # Use the extracted `project_dir` as `cwd` for subsequent commands
        work_dir = project_dir if project_dir else None

        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=work_dir,
        )
        print(
            f"{command_item["description"]}. Command '{command}' executed successfully:\n{result.stdout.decode()}"
        )
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}':\n{e.stderr.decode()}")
