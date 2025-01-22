import discord
from discord import app_commands, Intents, Interaction
import json
import os

# Define the goal items and their quantities
goal_items = {
    "Per Attempt": 1,
    "-------------------------------------------------------": 1,
    "Crystallized Remnants of Winter": 6,
    "Condensed Reverie Crystal": 48,
    "Scrap of Frozen Fabric": 18,
    "Strand of Thin Metal Wire": 48,
    "Fog Silk": 30,
    "Finest Fabric": 60,
    "-------------------------------------------------------------": 1,
    "Finishing Materials": 1,
    "------------------------------------------------------------------": 1,
    "Winter Dream Terminus Crystal": 1,
    "Terminus Crystal": 1,
    "Frozen Braid": 6,
    "Incomplete Seal Emblem": 5,
    "Soft Fur Fabric": 5
}

# File to store user progress
progress_file = "user_progress.json"

# Load progress from file if it exists
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        user_progress = json.load(f)
else:
    user_progress = {}

class ProgressTrackerBot(discord.Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = ProgressTrackerBot(intents=Intents.default())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready to track progress!")

@bot.tree.command(name="add_item")
@app_commands.describe(item="The item to add progress for", quantity="The quantity to add")
async def add_item(interaction: Interaction, item: str, quantity: int):
    """Add progress for a specific item."""
    if item not in goal_items:
        await interaction.response.send_message(f"{item} is not a tracked item.", ephemeral=True)
        return

    if str(interaction.user.id) not in user_progress:
        user_progress[str(interaction.user.id)] = {key: 0 for key in goal_items.keys()}

    user_progress[str(interaction.user.id)][item] += quantity
    if user_progress[str(interaction.user.id)][item] > goal_items[item]:
        user_progress[str(interaction.user.id)][item] = goal_items[item]

    # Save progress to file
    with open(progress_file, "w") as f:
        json.dump(user_progress, f, indent=2)

    await interaction.response.send_message(f"Added {quantity} {item}(s). You now have {user_progress[str(interaction.user.id)][item]} / {goal_items[item]}.")

@bot.tree.command(name="progress")
async def progress(interaction: Interaction):
    """Show your progress for all items."""
    if str(interaction.user.id) not in user_progress:
        await interaction.response.send_message("You have no progress tracked yet.", ephemeral=True)
        return

    progress_list = []
    for item, required in goal_items.items():
        obtained = user_progress[str(interaction.user.id)].get(item, 0)
        percentage = (obtained / required) * 100
        progress_list.append(f"{item}: {obtained} / {required} ({percentage:.2f}%)")

    progress_message = "\n".join(progress_list)
    await interaction.response.send_message(f"Your progress:\n{progress_message}")

@bot.tree.command(name="reset_progress")
async def reset_progress(interaction: Interaction):
    """Reset your progress for all items."""
    if str(interaction.user.id) in user_progress:
        user_progress[str(interaction.user.id)] = {key: 0 for key in goal_items.keys()}

        # Save progress to file
        with open(progress_file, "w") as f:
            json.dump(user_progress, f, indent=2)

        await interaction.response.send_message("Your progress has been reset.")
    else:
        await interaction.response.send_message("You have no progress to reset.", ephemeral=True)

# Enter your bot token directly here
token = ""

if token:
    bot.run(token)
else:
    print("Bot token is required to run the bot.")

