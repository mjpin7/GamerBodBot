import discord
import os
import requests
from random import randint
import json

######################## GLOBAL VARIABLES AND FUNCTIONS ########################
hangman = False

HANGMANPICS = ['''
  +---+
  |   |
      |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========''']

######################## CLASSES ########################

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
    async def handle_command(self, message):
        for command in self.commands:
            if message.content.startswith(command['trigger']):
                args = message.content.split(' ')
                
                # If the message starts with a trigger
                if args[0] == command['trigger']:
                    args.pop(0)

                    if command['type'] == 'public':
                        # If there are no arguments in the selected command, return the response
                        if command['number_args'] == 0:
                            return await message.channel.send(str(command['function'](self, message, self.client, args)))
                        else:
                            # If there are a correct number of arguments, return a response. Else return an error message
                            if len(args) >= command['number_args']:
                                return await message.channel.send(str(command['function'](self, message, self.client, args)))
                            else:
                                return await message.channel.send(message.channel, 'command "{}" requires at least {} argument(s): "{}"'.format(command['trigger'], command['number_args'], ', '.join(command['args_val'])))
                    elif command['type'] == 'private':
                        # If there are no arguments in the selected command, return the response
                        if command['number_args'] == 0:
                            return await message.author.send(str(command['function'](self, message, self.client, args)))
                        else:
                            # If there are a correct number of arguments, return a response. Else return an error message
                            if len(args) >= command['number_args']:
                                return await message.author.send(message.author, str(command['function'](self, message, self.client, args)))
                            else:
                                return await message.author.send(message.author, 'command "{}" requires at least {} argument(s): "{}"'.format(command['trigger'], command['number_args'], ', '.join(command['args_val'])))
                    else:
                        return await command['function'](self, message, self.client, args)
                else:
                    break




# Create instance of the discord client
client = discord.Client()

# Create the CommandHandle object passing in the client
handler = CommandHandle(client)

def refresh_token():
    resp = requests.get("https://gamerbodbot-api.herokuapp.com/refresh", headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})


######################## ALL FUNCTIONS FOR COMMANDS GO HERE WITH HANDLER BELOW RESPECTIVE FUNCTION ########################

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
    'type': 'public'
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
async def function_hangman(self, message, client, args):
    global hangman
    try:
        if hangman:
            await message.channel.send("Game of hangman in progress, can not start a new one")
            return
        else:
            if message.channel.id == 606546204825878528 or message.channel.id == 568126260757397508:
                hangman = True
                numGuess = 0
                guessed = []
                await message.author.send("You have started a new game of hangman, please respond with the word you would like to use:")

                def pred(m):
                    return m.author == message.author and m.channel == message.author.dm_channel

                msg = await client.wait_for('message', check=pred)

                # Creates a list of strings
                words = msg.content.lower().split()

                # For printing out the words
                wordsStr = ' '.join(words)
                await msg.author.send("You have chosen the word(s): '{}'. Game starting in channel {}.".format(wordsStr, message.channel))

                # This creates a nice response
                resp = "```"
                for word in words:
                    resp += '_ ' * len(word)
                    resp += '  '
                resp += '\n\n{}```'.format(HANGMANPICS[numGuess])
                
                

                await message.channel.send("New game of hangman started by {}.\n{}".format(message.author.mention, resp))

                # To make sure the character gotten is one character and in the alphabet
                def pred1(m):
                    return m.channel == message.channel and len(m.content) == 1 and m.content.isalpha()

                for word in words:
                    resp = '_ ' * len(word)
                    resp += '  '

                # While the game is still going on, listen for a message
                while resp.count('_') != 0 and numGuess < 6:
                    # Get guess
                    msg = await client.wait_for('message', check=pred1)
                    charGuess = msg.content.lower()

                    # If the character has already been guessed
                    if charGuess in guessed:
                        await message.channel.send("\"{}\" has already been guessed, guess again!".format(charGuess))
                    else:
                        isRight = [i for i in words if charGuess in i]
                        # If the response from user is not in any of the words, the list created above will be empty
                        if not isRight:
                            numGuess += 1
                            await message.channel.send("Guess \"{}\" from {} was incorrect, guess again!".format(charGuess, msg.author.mention))
                        
                        guessed.append(charGuess)
                        

                    resp = ""
                    # loop to go through each word and replace with guessed characters, and put extra space between words
                    for word in words:
                        resp += ''.join(c+' ' if c in guessed else '_ ' for c in word)
                        resp += "  "
                        
                        
                    guesses = ', '.join(guessed)
                    await message.channel.send("```{}\n\nIncorrect Guesses: {}\nYou have guessed: {}\n\n{}```".format(resp, numGuess, guesses, HANGMANPICS[numGuess]))
                
                if numGuess >= 6:
                    await message.channel.send("You did not get it <:PepeHands:538761089136066565> The phrase/word was \"{}\"".format(wordsStr))
                else:
                    await message.channel.send("You got it! The phrase/word was \"{}\" :tada: :tada: ".format(wordsStr))

                hangman = False
                return "Done"
            else:
                game_channel = client.get_channel(606546204825878528)
                await message.channel.send("Please start the game in {}".format(game_channel.mention))
            
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!hangman',
    'function': function_hangman,
    'number_args': 0,
    'args_val': [],
    'desc': 'Command to start a hangman game',
    'type': 'special'
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
            await handler.handle_command(message)
        # Message does not have a command, just pass
        except TypeError as t:
            pass

        except Exception as e:
            print(e)


client.run(os.environ.get('TOKEN'))
