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

                    if command['type'] == 'public':
                        # If there are no arguments in the selected command, return the response
                        if command['number_args'] == 0:
                            return message.channel.send(str(command['function'](self, message, self.client, args)))
                        else:
                            # If there are a correct number of arguments, return a response. Else return an error message
                            if len(args) >= command['number_args']:
                                return message.channel.send(str(command['function'](self, message, self.client, args)))
                            else:
                                return message.channel.send(message.channel, 'command "{}" requires at least {} argument(s): "{}"'.format(command['trigger'], command['number_args'], ', '.join(command['args_val'])))
                    else:
                        # If there are no arguments in the selected command, return the response
                        if command['number_args'] == 0:
                            return message.author.send(str(command['function'](self, message, self.client, args)))
                        else:
                            # If there are a correct number of arguments, return a response. Else return an error message
                            if len(args) >= command['number_args']:
                                return message.author.send(message.author, str(command['function'](self, message, self.client, args)))
                            else:
                                return message.author.send(message.author, 'command "{}" requires at least {} argument(s): "{}"'.format(command['trigger'], command['number_args'], ', '.join(command['args_val'])))
                else:
                    break




# Create instance of the discord client
client = discord.Client()

# Create the CommandHandle object passing in the client
handler = CommandHandle(client)

def refresh_token():
    resp = requests.get("https://gamerbodbot-api.herokuapp.com/refresh", headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})

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
    'desc': 'Sends greetings to the user',
    'type': 'public'
})

# Function to handle the commands command
#
# Returns a list of the commands
def function_commands(self, message, client, args):
    try:
        response = "Commands:\n```"
        
        for command in self.commands:
            response += command['trigger']

            # Add the args (if any) to the response
            if command['trigger'] == "!backlog":
                response += " {} <{}>/all".format(command['args_val'][0], command['args_val'][1])
            else:
                for arg in command['args_val']:
                    response += " <{}>".format(arg)
            

            response += ": {}\n\n".format(command['desc'])

        response+= "```"

        return response
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!commands',
    'function': function_commands,
    'number_args': 0,
    'args_val': [],
    'desc': 'Lists commands',
    'type': 'public'
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
    'desc': 'Helps user',
    'type': 'message.channel'
})

# Function to handle the meme command
#
# References the google custom search api and a created custom google search to search multiple sites for a meme. Returns a random image.
#
def function_meme(self, message, client, args):
    try:
        # Make request for the meme
        resp = requests.get("https://gamerbodbot-api.herokuapp.com/meme", headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})

        if resp.status_code != 200:
            if resp.status_code == 401:
                raise ApiError('Get error {}, unauthorized. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
            else:
                raise ApiError('Get error {}. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
            
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
    'desc': 'Sends a meme to user',
    'type': 'public'
})

def function_backlog(self, message, client, args):
    try:
        
        if(len(args) > 1):
            # If game has multiple word titles, join the multiple words from args list
            if args[1] != "all":
                game = ' '.join(args[1:])

            if args[0] == "add":
                resp = requests.post("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game), "status": "unplayed"}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
                message = resp.json()['message']
            elif args[0] == "finished":
                resp = requests.put("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game), "status": "finished"}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
                message = resp.json()['message']
            elif args[0] == "playing":
                resp = requests.put("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game), "status": "playing"}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
                message = resp.json()['message']
            elif args[0] == "view":
                if args[1] == "all" or args[1] == "unplayed" or args[1] == "finished" or args[1] == "playing":
                    resp = requests.get("https://gamerbodbot-api.herokuapp.com/backloglist/{}/{}".format(message.author.display_name, args[1]), headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
                    message = resp.json()['message']
                else:
                    resp = requests.get("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game)}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
                    message = resp.json()['message']
            else:
                message = 'Command argument "{}" not valid. Type !help to help'.format(args[0])

            if resp.status_code != 200:
                if resp.status_code == 401:
                    raise ApiError('Get error {}, unauthorized. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
                else:
                    raise ApiError('Get error {}. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
        else:
            if args[0] == "view":
                message = 'Command arguments not valid. Try "!backlog view all", "!backlog view <game>" or type "!help" for more help.'
            elif args[0] == "add":
                message = 'Command arguments not valid. Missing game, try "!backlog add <game>".'
            elif args[0] == "finished":
                message = 'Command arguments not valid. Missing game, try "!backlog finished <game>".'
            elif args[0] == "playing":
                message = 'Command arguments not valid. Missing game, try "!backlog playing <game>".'
            else:
                message = "Command argument not valid. Valid arguments are view, add, finished and playing."

        return message
    except ApiError as a:
        return a
    except Exception as e:
        return e


handler.add_command({
    'trigger': '!backlog',
    'function': function_backlog,
    'number_args': 1,
    'args_val': ['add/finished/playing/view', 'game'],
    'desc': 'Command to interact (add, finish, update, get) backlog items',
    'type': 'public'
})

# Simple function for hello command
def function_test(self, message, client, args):
    try:
        return "Hello, this is to test the messaging functionality :D"
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!test',
    'function': function_test,
    'number_args': 0,
    'args_val': [],
    'desc': 'Command to test functionality of PMing users',
    'type': 'private'
})

# Simple function for hello command
def function_vers(self, message, client, args):
    try:
        return discord.__version__
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!vers',
    'function': function_vers,
    'number_args': 0,
    'args_val': [],
    'desc': 'Command to check version summary (for testing)',
    'type': 'public'
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
            if message.content.startswith('!test'):
                await message.author.send("You have started a new game of hangman, please respond with the word you would like to use:")

                def pred(m):
                    return m.author == message.author and m.channel == message.author.dm_channel

                msg = await client.wait_for('message', check=pred)

                await msg.author.send(msg.content)
            else:
                await handler.handle_command(message)

        # Message does not have a command, just pass
        except TypeError as t:
            pass

        except Exception as e:
            print(e)


client.run(os.environ.get('TOKEN'))
