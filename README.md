![Python](https://img.shields.io/badge/Python-3.6-informational.svg)

# GamerBodBot

This repo contains source code for a discord bot for my server GamerBodSquad. It has various commands and connects to the [GamerBodBot-API](https://github.com/mjpin7/GamerBodBot-API) and is deployed on Heroku.

## Contents
* [Dependancies](#dependancies)
* [Commands](#commands)

---

## <a name="dependancies"></a>Dependancies
#### Discord py
- API wrapper for Discord

## <a name="commands"></a>Commands
- !hello: 
    - Sends simple greetings to the user executing
- !commands:
    - Lists all of the commands to the user
- !help:
    - Helps the user if they are unsure of what to do
- !meme:
    - Connects to the [GamerBodBot-API](https://github.com/mjpin7/GamerBodBot-API) and send the user a random meme
- !backlog (args: add/finished/playing/view) `<game>/all`
    - add `<game>`: Creates a backlog item with title `<game>` and status 'unplayed'
    - finished `<game>`: Marks `<game>` with status 'finished'
    - playing `<game>`: Marks `<game>` with status 'playing'
    - view `<game>`: Returns the summary of info for `<game>`
    - view all: Returns the list of the users backlog
