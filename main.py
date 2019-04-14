import discord
import os
import requests
from random import randint
import json

class ApiError(Exception):
    pass

# Class to handle commands
class CommandHandle:

    def __init__(self, client):
        self.client = client
        self.commands = []

    # Function to add a command to the commands list
    #
    # @Param command        The command to add to the list
    def add_command(self, command):
        self.commands.append(command)

    # Funciton to handle messages to check if they are commands
    #
    # @Param message        The message to handle
    #
    def handle_command(self, message):
        for command in self.commands:
            if message.content.startswith(command['trigger']):
                args = message.content.split(' ')
                
                # If the message starts with a trigger
                if args[0] == command['trigger']:
                    args.pop(0)

                    # If there are no arguments in the selected command, return the response
                    if command['number_args'] == 0:
                        return self.client.send_message(message.channel, str(command['function'](self, message, self.client, args)))
                    else:
                        # If there are a correct number of arguments, return a response. Else return an error message
                        if len(args) >= command['number_args']:
                            return self.client.send_message(message.channel, str(command['function'](self, message, self.client, args)))
                        else:
                            return self.client.send_message(message.channel, 'command "{}" requires {} argument(s): "{}"'.format(command['trigger'], command['number_args'], ', '.join(command['args_val'])))
                else:
                    break




# Create instance of the discord client
client = discord.Client()

# Create the CommandHandle object passing in the client
handler = CommandHandle(client)

## ALL FUNCTIONS FOR COMMANDS GO HERE WITH HANDLER BELOW RESPECTIVE FUNCTION

# Simple function for hello command
def function_greetings(self, message, client, args):
    try:
        return "Hello {}".format(message.author.mention)
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!hello',
    'function': function_greetings,
    'number_args': 0,
    'args_val': [],
    'desc': 'Sends greetings to the user'
})

# Function to handle the meme command
#
# References the google custom search api and a created custom google search to search multiple sites for a meme. Returns a random image.
#
def function_meme(self, message, client, args):
    try:
        resp = requests.get("https://gamerbodbot-api.herokuapp.com/meme", headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})

        if resp.status_code != 200:
            if resp.status_code == 401:
                raise ApiError('Get error {}, unauthorized. Token may be expired'.format(resp.status_code))
            else:
                raise ApiError('Get error {}'.format(resp.status_code))
            


        meme = resp.json()["Meme"]
        return meme

    except ApiError as a:
        return a
    except Exception as e:
        return e

handler.add_command({
    'trigger': '!meme',
    'function': function_meme,
    'number_args': 0,
    'args_val': [],
    'desc': 'Sends a meme to user'
})

# Function to handle the commands command
#
# Returns a list of the commands
def function_commands(self, message, client, args):
    try:
        response = "Commands:\n```"
        
        for command in self.commands:
            response += "{}: {}\n".format(command['trigger'], command['desc'])

        response+= "```"

        return response
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!commands',
    'function': function_commands,
    'number_args': 0,
    'args_val': [],
    'desc': 'Lists commands'
})

# Function to handle the help command
def function_help(self, message, client, args):
    try:
        return "Type in command as ```!<command>``` or type in ```!commands``` for list of commands"
    except  Exception as e:
        return e

handler.add_command({
    'trigger': '!help',
    'function': function_help,
    'number_args': 0,
    'args_val': [],
    'desc': 'Helps user'
})


@client.event  # event decorator/wrapper (anytime some event is going to occur)
async def on_ready():
    try:
        print(f"We have logged in as {client.user}")
    except Exception as e:
        print(e)

@client.event
async def on_message(message):
    # For messages from itself
    if message.author == client.user:
        pass
    else:
        try:
            await handler.handle_command(message)

        # Message does not have a command, just pass
        except TypeError as t:
            pass

        except Exception as e:
            print(e)


client.run(os.environ.get('TOKEN'))
