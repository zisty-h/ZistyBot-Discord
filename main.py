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


def admin_control(msg):
    return
@bot.event
async def on_message(message):
    if message.author == bot.user:
        # print(f"{message.author.name} says '{message.content}'")
        return
    else:
        user_id = message.author.id
        if user_id in developers:
            admin_control(message)

        if message.content == "!zisty-projects":
            print("Zisty projects")
            await message.channel.send("現在公開されているZistyのprojectは以下の道りです")
            projects = json.loads(requests.get('https://api.github.com/users/zisty-h/repos').content)
            send_text = ''
            for project in projects:
                send_text += f'# {project["name"]}\ndescription: {project["description"]}\nurl: {project["html_url"]}\n'
            await message.channel.send(send_text)
        elif message.content == "!zisty-members":
            await message.channel.send("Please wait.\nGetting members...")
            members = bot.get_guild(1185947730363826236).get_role(1187750962694193243).members
            await message.channel.send("現在参加しているZistyの開発者は以下のユーザーです")
            for member in members:
                await message.channel.send(f'## {member.display_name}\nID: {member.name}...(User_id: {member.id}) ')
        elif message.content == "!zisty-join":
            server = bot.get_guild(1185947730363826236)
            link = await server.get_channel(1187754444687949986).create_invite()
            print(link)
            await message.channel.send(f'Zisty join link: {link}')

@bot.event
async def on_member_join(member):
    return

@bot.event
async def on_member_remove(member):
    await member.remove_roles(member.guild.get_role(1187750962694193243))
    print(member)
    return
bot.run(Discord_token)