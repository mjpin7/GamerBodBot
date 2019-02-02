import discord
import os

client = discord.Client()

@client.event  # event decorator/wrapper (anytime some event is going to occur)
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    # For messages from itself
    if message.author == client.user:
        return

    if str(message.author) == "MahDoood#9478" and "!hey" in message.content.lower():
        client.send_message(message.channel, f"Hey sexy {message.author.mention} . You are the only good looking one in here <3")

client.run(os.environ.get('TOKEN'))