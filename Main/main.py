import discord
import json
import shutil
import os
from discord.ext import commands
import requests

with open('config.json') as config:
    config = json.loads(config.read())
    token = config["Discord"]['Token']

with open('Markdowns/def_help_en.md') as en_help:
    english_help = en_help.read()

with open('Markdowns/def_help_ja.md', encoding="utf-8") as ja_help:
    japanese_help = ja_help.read()

with open('Markdowns/admin_help.md') as admin_help:
    admin_help = admin_help.read()

with open('Markdowns/op_help.md') as op_help:
    op_help = op_help.read()


Zisty_News = "zisty-news"
isWatchLog = [1077177658758152253]
getZistyNews = config['Discord']['GetNewsChannels']
developers = []

def find_key_by_value(data, target_value):
    for key, value in data.items():
        if value == target_value:
            return key
    return None

class select_language(discord.ui.View):
    language = "English"
    def __init__(self, msg: discord.Message):
        super().__init__()
        self.msg: discord.Message = msg

    @discord.ui.button(label="Japanese", style=discord.ButtonStyle.blurple, row=4)
    async def pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="help",
            description=japanese_help if self.language == "English" else english_help,
            color=discord.Color.blurple()
        )
        await self.msg.edit(embed=embed)
        button.label = "English" if self.language == "English" else self.language
        self.language = "Japanese" if self.language == "English" else "English"
        await interaction.response.edit_message(view=self)
        return
class selectMode(discord.ui.View):
    mode = "Default help"
    def __init__(self, msg: discord.Message):
        super().__init__()
        self.msg: discord.Message = msg
    @discord.ui.button(label="Admin help", style=discord.ButtonStyle.blurple, row=4)
    async def pressed(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="help",
            description=english_help if self.mode == "Admin help" else admin_help,
            color=discord.Color.blurple()
        )
        await self.msg.edit(embed=embed)
        button.label = "Default help" if self.mode == "Default help" else self.mode
        self.mode = "Admin help" if self.mode == "Default help" else "Default help"
        await interaction.response.edit_message(view=self)


intents = discord.Intents.all()
bot = discord.Client(intents=intents)
@bot.event
async def on_ready():
    print("Bot is ready.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.unknown))

    # get developers
    Zisty_guild = bot.get_guild(1185947730363826236)
    Developer_role = Zisty_guild.get_role(1185947950275379270)
    Developers = Developer_role.members
    for user in Developers:
        # await pprint(f"{user.name}({user.id}) add developers.")
        developers.append(user.id)

    # Leave guilds because bot's permission
    join_guilds = bot.guilds
    for guild in join_guilds:
        roles = guild.get_member(1238450606998556712).roles
        isAdmin = False
        for role in roles:
            permissions = role.permissions
            if permissions.administrator:
                isAdmin = True
                break

        if isAdmin is False:
            # await pprint(f"{guild.name}({guild.id}) leave.")
            print(f"{guild.name}({guild.id}) leave.")
            embed = discord.Embed(title="Zisty bot leaves this server.", description="This bot needs administrator permissions.", colour=discord.Colour.red())
            await guild.system_channel.send(embed=embed)
            await guild.leave()

@bot.event
async def on_message(message):
    content = message.content
    user_id = message.author.id
    # Logging
    user_name = message.author.name
    guild_id = message.guild.id
    channel_id = message.channel.id

    categories_data = config['server_category'].keys()
    if str(guild_id) in categories_data:
        print(content)
        log_channel_id = config['logs_channels'][str(channel_id)]
        embed = discord.Embed(
            title="{}({})".format(user_name, user_id),
            description=content,
            color=discord.Color.blurple()
        )
        if not user_id == 1238450606998556712:
            await bot.get_channel(log_channel_id).send(embed=embed)
    # Commands
    # default commands
    if content[0:6] == "Zisty!":
        command = content.replace("Zisty!", "").split(" ")
        print(command)
        name = command[0]
        if name == "help":
            description = english_help
            embed = discord.Embed(title="Zisty-help", description=description, color=discord.Color.blue())

            msg = await message.channel.send(embed=embed)
            await message.channel.send(view=select_language(msg))
            await message.channel.send(view=selectMode(msg))
            return

        elif name == "members":
            role_obj = config['Discord']['Zisty']
            zisty_guild = bot.get_guild(1185947730363826236)
            default_role = zisty_guild.get_role(role_obj['default_role'])
            admin_role = zisty_guild.get_role(role_obj['admin_role'])
            default_members = default_role.members
            admin_members = admin_role.members
            description = "## Staff and developer\n"
            for admin in admin_members:
                description += f"### {admin.name}\ndisplay_name: {admin.display_name}\nid: {admin.id}\n"
                if admin in default_members:
                    default_members.remove(admin)
            description += "## default Member\n"
            for member in default_members:
                description += f"### {member.name}\ndisplay_name: {member.display_name}\nid: {member.id}\n"
            embed = discord.Embed(title="Zisty-members", description=description, color=discord.Color.brand_green())
            await message.channel.send(embed=embed)
            return

        elif name == "projects":
            url = "https://api.github.com/users/zisty-h/repos"
            projects = json.loads(requests.get(url).text)
            description = ""
            for project in projects:
                description += f"## {project['name']}\nCreated Date: {project['created_at']}\nfinal update: {project['updated_at']}\nurl: {project['svn_url']}\n"

            embed = discord.Embed(title="Zisty-projects", description=description, color=discord.Color.blurple())
            try:
                global dm
                dm = await message.author.send(embed=embed)
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Error.",
                    description="Zisty can't send message to your dm.\nPlease allow me to receive DMs",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed)
                return

            link = f'https://discord.com/channels/@me/{dm.channel.id}/{dm.id}'
            await message.channel.send(embed=discord.Embed(title="Zisty-projects", description="レスポンスはDMに送信されました。\nlink: {}".format(link), color=discord.Color.blurple()))
            return

        elif name == "download":
            if len(command) == 2:
                project_name = command[1]
                embed = discord.Embed(title="Begin getting...", description="get and analysis {} info...".format(project_name), color=discord.Color.yellow())
                await message.channel.send(embed=embed)
                url = "https://api.github.com/users/zisty-h/repos"
                projects = json.loads(requests.get(url).text)
                hasName = False
                for project in projects:
                    if project['name'] == project_name:
                        hasName = True
                        break
                if hasName is False:
                    embed = discord.Embed(
                        title="Error",
                        description="This project doesn't exist!",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return


                url = f'https://github.com/zisty-h/{project_name}'
                await message.channel.send(embed=discord.Embed(title="Begin Download. url: {}".format(url), description="Begin downloading...", color=discord.Color.yellow()))
                os.system('git clone {}'.format(url))
                file = shutil.make_archive(project_name, "zip", root_dir=f"{os.getcwd()}\\{project_name}")
                embed = discord.Embed(title="Done download", description="Send file!!", color=discord.Color.blue())
                await message.channel.send(embed=embed)
                await message.channel.send(file=discord.File("./{}.zip".format(project_name), filename="{}.zip".format(project_name)))
                os.remove(file)
                os.removedirs("./{}".format(project_name))
                return
            else:
                embed = discord.Embed(
                    title="Error",
                    description="This project doesn't exist!",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
        elif name == "join":
            link = await bot.get_channel(1187754444687949986).create_invite()
            embed = discord.Embed(title="Zisty-join", description=f"Zisty link is {link}.\nLet's enjoy programming!!", color=discord.Color.blue())
            await message.channel.send(embed=embed)
            return

        elif name == "getNews":
            select = command[1]
            logEmbed = discord.Embed(title=f"{message.guild.name} will get Zisty's news.", description=f"### Server_id: {message.guild.id}", color=discord.Color.blue())

            guild = message.guild
            channels = guild.channels
            if select == "true":
                hasNews = False
                for channel in channels:
                    print(channel.name)
                    if channel.name == Zisty_News:
                        hasNews = True
                        break
                if hasNews == False:
                    News_channel = await guild.create_text_channel(
                        Zisty_News,
                        topic="Zistyの開発者からのお知らせが送信されます",
                        reason="Created by Zisty",
                    )
                    embed = discord.Embed(title="Created news channel.", description="This channel gets zisty's news.", color=discord.Color.blurple())
                    await News_channel.send(embed=embed)
                    getZistyNews.append(News_channel.id)
                    config['Discord']['GetNewsChannels'] = getZistyNews
                    with open('./config.json', 'w') as outfile:
                        json.dump(config, outfile, indent=2)
                    await message.channel.send(embed=discord.Embed(title="Created channel", description="Create news channel.", color=discord.Color.blurple()))
                    return
                else:
                    embed = discord.Embed(
                        title="Created channel",
                        description="The channel has already been created",
                        color=discord.Color.red()
                    )

                    await message.channel.send(embed=embed)
                    return
                return

            elif select == "false":
                channels = guild.channels
                for channel in channels:
                    if channel.name == Zisty_News:
                        id = channel.id
                        await channel.delete()
                        embed = discord.Embed(title="Deleted channel", description="Done deleted channel.", color=discord.Color.blurple())
                        await message.channel.send(embed=embed)
                        getZistyNews.remove(id)
                        config['Discord']['GetNewsChannels'] = getZistyNews
                        with open('./config.json', 'w') as outfile:
                            json.dump(config, outfile, indent=2)
                        return
                embed = discord.Embed(title="None channel", description="News channel is None", color=discord.Color.red())
                await message.channel.send(embed=embed)
                return
        elif name == "display_all_links":
            response = requests.get("https://raw.githubusercontent.com/zisty-h/Zisty-links/main/Links.txt").text
            embed = discord.Embed(title="Links", description=response, color=discord.Color.blurple())
            await message.channel.send(embed=embed)
        else:
            pass

        # Admin commands
        if user_id in developers:
            if name == "News-Post":
                title = command[1]
                text = command[2]
                embed = discord.Embed(title=title, description=text, color=discord.Color.blurple())
                for channel in getZistyNews:
                    await bot.get_channel(channel).send(embed=embed)
                embed = discord.Embed(title="Done post", description="Done send news to all channels.", color=discord.Color.blurple())
                await message.channel.send(embed=embed)
                return

            elif name == "News-Reset":
                embed = discord.Embed(title="Zisty-Reset", description="Try delete all news channels...", color=discord.Color.blurple())
                await message.channel.send(embed=embed)
                guilds = bot.guilds
                for guild in guilds:
                    channels = guild.text_channels
                    for channel in channels:
                        if channel.name == Zisty_News:
                            await channel.delete()
                owner = guild.owner
                await owner.send(
                    embed=discord.Embed(
                        title="Deleted channel",
                        description="Your senevee's news channel is deleted.",
                        color=discord.Color.red()
                    )
                )
                config['Discord']['GetNewsChannels'] = {}
                with open('./config.json', 'w') as outfile:
                    json.dump(config, outfile, indent=2)

                embed = discord.Embed(
                    title="Deleted channels",
                    description="Done deleted all news channels",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                pass
            elif name == "logging":
                invite = await bot.get_channel(1241352665863294976).create_invite(max_uses=1, max_age=600)
                embed = discord.Embed(
                    title="Zisty-Logging server",
                    description=f"Zisty logs server is {invite.url}",
                    color=discord.Color.blurple()
                )
                try:
                    DM = await message.author.send(embed=embed)
                    link = 'https://discord.com/channels/@me/{}/{}'.format(DM.channel.id, DM.id)
                    embed = discord.Embed(
                        title="Go to your DM",
                        description=f"Go to DM!!\n{link}",
                        color=discord.Color.blurple()
                    )
                    await message.channel.send(embed=embed)
                    return
                except discord.Forbidden:
                    embed = discord.Embed(
                        title="Error",
                        description="Zisty can't send message to your dm.",
                        color=discord.Color.red()
                    )
                    await message.author.send(embed=embed)
                    return
            elif user_id == 851357394976899116 or user_id == 1077177658758152253:
                if name == "setRole":
                    guild = message.guild
                    # ToUser and SetRole
                    user_obj = command[1]
                    role_obj = command[2]
                    print(user_obj, role_obj)
                    if "&" in user_obj:
                        embed = discord.Embed(
                            title="Error 01",
                            description=f"You can't set role in setRole.\nPlease specify a user and a role as arguments",
                            color=discord.Color.red()
                        )
                        await message.channel.send(embed=embed)
                        return

                    if not "&" in role_obj:
                        embed = discord.Embed(
                            title="Error 02",
                            description=f"You can't set role in setRole.\nPlease specify a user and a role as arguments",
                            color=discord.Color.red()
                        )
                        await message.channel.send(embed=embed)
                        return

                    ToUser = user_obj.replace("<@", "").replace(">", "")
                    SetRole = role_obj.replace("<@&", "").replace(">", "")

                    embed = discord.Embed(
                        title="Set role",
                        description=f"Try set <@&{SetRole}> to <@{ToUser}>",
                        color=discord.Color.blurple()
                    )

                    await message.channel.send(embed=embed)
                    role = guild.get_role(int(SetRole))
                    print(role)
                    user = guild.get_member(int(ToUser))
                    print(user)
                    try:
                        await user.add_roles(role)
                    except discord.Forbidden:
                        embed = discord.Embed(
                            title="Error",
                            description="Zisty doesn't have permission.\nPlease try adjust the role hierarchy",
                            color=discord.Color.red()
                        )
                        await message.channel.send(embed=embed)
                        return

                    embed = discord.Embed(
                        title="Done set role",
                        description="Done set role.\nUser: <@{}>\nRoles: <@&{}>".format(user.id, role.id),
                        color=discord.Color.blurple()
                    )
                    await message.channel.send(embed=embed)
                    return




    # Not reaction
    if message.author == bot.user:
        return

    response_server = bot.get_guild(1241346608365568031)
    if channel_id == 1241598259642761319:
        if content[0:len("op!")] == "op!":
            command = content[len("op!"):].split(" ")
            name = command[0]
            if name == "help":
                embed = discord.Embed(
                    title="Help",
                    description=op_help,
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
            elif name == "join_servers":
                embed = discord.Embed(
                    title="Try get servers...",
                    description="Please wait sametime.",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                guilds = bot.guilds
                description = ""
                for guild in guilds:
                    if not guild.id == 1223873836794118184:
                        invite = await guild.text_channels[0].create_invite()
                        description += '## {}\nid: {}\nlink: {}\n'.format(guild.name, guild.id, invite.url)
                embed = discord.Embed(
                    title="Join servers",
                    description=description,
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return
            elif name == "leave_server":
                embed = discord.Embed(
                    title="Try leave server...",
                    description="Please wait sametime.",
                    color=discord.Color.yellow()
                )
                await message.channel.send(embed=embed)
                guild = bot.get_guild(int(command[1]))
                await guild.leave()
                embed = discord.Embed(
                    title="Done leave server.",
                    description="Done leave server.\nServer: {}".format(guild.name),
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return

            elif name == "create_server_log":
                guild_id = int(command[1])
                guild = bot.get_guild(guild_id)
                embed = discord.Embed(
                    title="Try create server's log...",
                    description="Please wait sametime.\nServer: {}".format(guild.name),
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                channels = guild.text_channels
                category = await response_server.create_category(
                    name="{}".format(guild.name),
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(view_channel=False)
                    }
                )
                for channel in channels:
                    log_channel = await category.create_text_channel(name=channel.name)
                    config['logs_channels'][channel.id] = log_channel.id
                    config['server_category'][guild.id] = category.id
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                embed = discord.Embed(
                    title="Done create server's log",
                    description="Done create server's log",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return

            elif name == "delete_server_log":
                guild_id = int(command[1])
                guild = bot.get_guild(guild_id)
                embed = discord.Embed(
                    title="Try delete server's log...",
                    description="Please wait sametime.\nServer: {}".format(guild.name),
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                if not str(guild_id) in config['server_category'].keys():
                    embed = discord.Embed(
                        title="Error",
                        description=f"This server doesn't have the category {guild_id}.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return

                category_id = config['server_category'][str(guild_id)]

                category = discord.utils.get(response_server.categories, id=category_id)
                print(category)
                log_channels = category.channels

                for channel in log_channels:
                    await channel.delete()
                await category.delete()

                # remove channels data
                embed = discord.Embed(
                    title="Done delete server's log.",
                    description="Done delete server's log.\nTry remove channels data",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                del config['server_category'][str(guild_id)]
                channels = guild.text_channels
                for channel in channels:
                    channels_id = channel.id
                    del config['logs_channels'][str(channels_id)]

                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=2)

                embed = discord.Embed(
                    title="Done deleted.",
                    description="Done delete channels and category and channels data.",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return

            elif name == "display_config":
                send_config = config
                del send_config['Discord']['Token']
                await message.channel.send("```json\n" + str(send_config) + "\n```")
                return
            elif name == "clear_message":
                embed = discord.Embed(
                    title="Try clear message...",
                    description="Please wait sametime.",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)

                channel = message.channel
                await channel.purge()
            elif name == "get_invite":
                guild_id = int(command[1])
                guild = bot.get_guild(guild_id)
                text_channels = guild.text_channels
                invite = await text_channels[0].create_invite()
                embed = discord.Embed(
                    title="Done create invite.",
                    description="Done create invite.\ninvite: {}".format(invite.url),
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return
            elif name == "display_channels":
                guild_id = int(command[1])
                guild = bot.get_guild(guild_id)
                embed = discord.Embed(
                    title="Try display channels...",
                    description="Please wait sametime.\nServer: {}".format(guild.name),
                    color=discord.Color.random()
                )
                await message.channel.send(embed=embed)
                channels = guild.channels
                description = ""
                for channel in channels:
                    description += f"## {channel.name}\nchannel_type: **{channel.type}**\n"
                embed = discord.Embed(
                    title="{}".format(guild.name),
                    description=description,
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return
            elif name == "delete_all_channels":
                embed = discord.Embed(
                    title="Try delete all channels...",
                    description="Please wait sametime.",
                    color=discord.Color.yellow()
                )
                await message.channel.send(embed=embed)
                safe_channels = [
                    bot.get_channel(1241598259642761319),
                    bot.get_channel(1241352665863294976),
                    bot.get_channel(1241659032196874241)
                ]
                delete_channels = response_server.channels
                for channel in delete_channels:
                    if not channel in safe_channels:
                        await channel.delete()

                config['logs_channels'] = {}
                config['server_category'] = {}
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                embed = discord.Embed(
                    title="Done delete all channels.",
                    description="Done delete all channels.",
                    color=discord.Color.blurple()
                )
                await message.channel.send(embed=embed)
                return
            elif name == "add_news_server":
                guild_id = int(command[1])
                guild = bot.get_guild(guild_id)

                embed = discord.Embed(
                    title="Try add news server.",
                    description="Please wait sametime.\nServer: {}".format(guild.name),
                    color=discord.Color.yellow()
                )
                await message.channel.send(embed=embed)

                text_channels = guild.text_channels
                hasZistyChannel = False
                for channel in text_channels:
                    if channel.name == Zisty_News:
                        hasZistyChannel = True
                        break
                if not hasZistyChannel:
                    News_channel = await guild.create_text_channel(
                        Zisty_News,
                        topic="Zistyの開発者からのお知らせが送信されます",
                        reason="Created by Zisty",
                    )
                    embed = discord.Embed(title="Created news channel.", description="This channel gets zisty's news.",
                                          color=discord.Color.blurple())
                    await News_channel.send(embed=embed)
                    getZistyNews.append(News_channel.id)
                    config['Discord']['GetNewsChannels'] = getZistyNews
                    with open('./config.json', 'w') as outfile:
                        json.dump(config, outfile, indent=2)
                    await message.channel.send(
                        embed=discord.Embed(title="Created channel", description="Create news channel.",
                                            color=discord.Color.blurple()))
                    embed = discord.Embed(
                        title="Done add news channel.",
                        description="Done add news channel.",
                        color=discord.Color.blurple()
                    )
                    await message.channel.send(embed=embed)
                    return
                else:
                    embed = discord.Embed(
                        title="Error",
                        description="The channel has already been created.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)

    # log channel events
    if guild_id == 1241346608365568031:
        message_channel = message.channel.id
        channel_id = find_key_by_value(config['logs_channels'], message_channel)
        if channel_id is None:
            if not message_channel in [1241659032196874241, 1241598259642761319, 1241352665863294976]:
                embed = discord.Embed(
                    title="Error",
                    description="Zisty can't find channel id",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed)
            return
        await bot.get_channel(int(channel_id)).send(message.content)
        return

@bot.event
async def on_guild_join(guild):
    # When zisty join server,
    # if zisty doesn't have admin permission,
    # zisty leave this server.
    roles = guild.get_member(1238450606998556712).roles
    willLeave = True
    for role in roles:
        permissions = role.permissions
        if permissions.administrator:
            willLeave = False
    if willLeave:
        embed = discord.Embed(title="Error", description="This bot needs administrator permission.", color=discord.Color.red())
        await guild.system_channel.send(embed=embed)
        await guild.leave()

bot.run(token)