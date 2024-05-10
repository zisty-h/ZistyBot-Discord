import json
import discord
import requests

with open(file="./info.json", mode="r", encoding="utf-8") as f:
    info = json.loads(f.read())

developers = []
Discord_token = info['Discord']['token']
intents = discord.Intents.all()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready!")
    servers = list(bot.guilds)
    for server in servers:
        if server.id == 1185947730363826236:
            members = server.members
            for member in members:
                for role in member.roles:
                    if 1185947950275379270 == role.id:
                        developers.append(member.id)
                        break
            print(developers)
        else:
            print(f"{server.name} has {len(server.members)} members")


def admin_control(msg):
    return
@bot.event
async def on_message(message):
    if message.author == bot.user:
        print(f"{message.author.name} says '{message.content}'")
        return

    else:
        user_id = message.author.id
        if user_id in developers:
            admin_control(message)

        if message.content == "!Zisty-projects":
            print("Zisty projects")
            await message.channel.send("Zisty projects")
            projects = json.loads(requests.get('https://api.github.com/users/zisty-h/repos').content)
            print(projects)




bot.run(Discord_token)