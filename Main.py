import discord
from discord.ext import commands
import os
import asyncio
import dotenv
dotenv.load_dotenv()

# discord token
DiscordToken = os.getenv("DISCORD_TOKEN")

# Setup Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    print(f"✅ Main System Logged in as {bot.user}")

async def Loadextentions():
    await bot.load_extension("cogs.Clubs_Stats")
    # await bot.load_extension("cogs.Members_Stats")
    await bot.load_extension("cogs.Staff")
    
async def main():
    async with bot:
        await Loadextentions()
        await bot.start(DiscordToken)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")