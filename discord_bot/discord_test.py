import discord
from discord.ext import commands

from config.config import agent_executor, discord_token
from llm.validate import validating_market
from utils.tavily_search import search_util

token = discord_token
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:

        author = message.author
        content = message.content
        channel = message.channel
        print(f"User {author} in {channel} mention: {content}")

        result, steps = validating_market(content, agent_executor, search_util)

        if result.get("is_valid", False):
            # 回复或处理消息
            await message.channel.send(f"hello, {author.mention}! ")


# 启动 Bot
bot.run(token)
