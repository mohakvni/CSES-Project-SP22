# bot.py
import os
import importlib
# import discord
from discord.ext import commands
from dotenv import load_dotenv
spotify_methods = importlib.import_module('Spotify-methods')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='queue')
async def queue(ctx):
    spotify_methods.helper(10,100)
    await ctx.send('queue')
bot.run(TOKEN)
# client = discord.Client()

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

# client.run(TOKEN)