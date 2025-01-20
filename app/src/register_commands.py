import json
import os

import requests

# Constants
DISCORD_API_BASE = "https://discord.com/api/v9"
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Replace with your bot token
APPLICATION_ID = os.getenv("APPLICATION_ID")  # Replace with your application ID


# Read commands from JSON file
def load_commands(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []


# Register a command with Discord
def register_command(command_data):
    url = f"{DISCORD_API_BASE}/applications/{APPLICATION_ID}/commands"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=command_data)
    if response.status_code == 201:
        print(f"Command '{command_data['name']}' registered successfully!")
    else:
        print(f"Failed to register command '{command_data['name']}'. Status Code: {response.status_code}. Response: {response.text}")


# Main function
def main():
    commands = load_commands("discord_commands.json")
    if not commands:
        print("No commands to register.")
        return

    for command in commands:
        register_command(command)


if __name__ == "__main__":
    main()
