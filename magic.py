import discord
from discord import app_commands, Intents, Interaction
import json
import os

# Define the goal items, their quantities, and prices in gold
goal_items = {
    "Dark Erg Chunk": {"quantity": 1, "price": 600000},
    "Adamantine": {"quantity": 25, "price": 12500000},
    "Glas Heart": {"quantity": 25, "price": 12000000},
    "Glas Feather": {"quantity": 25, "price": 13000000},
    "Condensed Strength Fragment": {"quantity": 100, "price": 200000},
    "Phantasmal Ingot": {"quantity": 20, "price": 150000},
    "Sturdy Loop": {"quantity": 20, "price": 100000},
    "Firm Blade Fragment": {"quantity": 15, "price": 200000}
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
    if user_progress[str(interaction.user.id)][item] > goal_items[item]["quantity"]:
        user_progress[str(interaction.user.id)][item] = goal_items[item]["quantity"]

    # Save progress to file
    with open(progress_file, "w") as f:
        json.dump(user_progress, f, indent=2)

    await interaction.response.send_message(f"Added {quantity} {item}(s). You now have {user_progress[str(interaction.user.id)][item]} / {goal_items[item]['quantity']}.")

@bot.tree.command(name="progress")
async def progress(interaction: Interaction):
    """Show your progress for all items."""
    if str(interaction.user.id) not in user_progress:
        await interaction.response.send_message("You have no progress tracked yet.", ephemeral=True)
        return

    total_obtained = 0
    total_required = 0
    total_gold_needed = 0
    progress_list = []

    for item, data in goal_items.items():
        required = data["quantity"]
        price = data["price"]
        obtained = user_progress[str(interaction.user.id)].get(item, 0)

        total_obtained += obtained
        total_required += required

        remaining = required - obtained
        total_gold_needed += remaining * price

        percentage = (obtained / required) * 100
        progress_list.append(f"{item}: {obtained} / {required} ({percentage:.2f}%) - Remaining cost: {remaining * price} gold")

    total_percentage = (total_obtained / total_required) * 100 if total_required > 0 else 0
    progress_message = "\n".join(progress_list)
    progress_message += f"\n\n**Total Progress:** {total_percentage:.2f}%"
    progress_message += f"\n**Gold Needed to Purchase Remaining Materials:** {total_gold_needed} gold"

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
