import os
from discord.ext import commands
import discord
import asyncio
import json

# bot.py

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command("help")


@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1

    print(f"PomoBot is in {guild_count} guilds")


@bot.group(invoke_without_command=True)
async def help(ctx):
    global em
    em = discord.Embed(title="HELP", description="")
    em.set_image(
        url="https://media.discordapp.net/attachments/1007428518415708162/1008536901034188830/Pomo.PNG"
    )
    em.add_field(
        name="Command Prefix",
        value="!",
    )
    em.add_field(name="Commands", value="!help, !self, !study_with, !scoreboard, !quit")
    em.add_field(
        name="Other",
        value="Type !help 'command' for details on a command.",
        inline=False,
    )

    em.add_field(
        name="Description",
        value="PomoBot is a project to help you study! It applies the Pomodoro study method: you completely focus for 25 minutes but get a 5-minute break afterward. This 30 minute session is 1 'Pomodoro.' After 4 pomodoros, you get a long break of 15 minutes. There's a server scoreboard to track each user's total Pomodoros consumed!",
        inline=False,
    )

    em.add_field(
        name="Details and Usage",
        value="The Bot's commands create private rooms under the 'study' category, whether by yourself, or with others. Only admins, owners, and members of the 'Students' role (created upon Pomobot joining) can view the channels, unless you are targeted by the 'study_with' command.",
        inline=False,
    )

    em.add_field(
        name="Source Code",
        value="View and improve the source code here: https://github.com/lucasz-student/Discord_Pomo_bot/blob/a3fcf5920baabf0439ed09769c26c4970700b180/README.md",
        inline=False,
    )
    em.set_footer(
        text="Pomodoro free icon designed by Flat Icons https://www.flaticon.com/premium-icon/pomodoro_3696891?term=pomodoro via @flaticon"
    )

    await ctx.send(embed=em)


@help.command()
async def self(ctx):
    await ctx.send(
        "```Self\nCreate a private room and set a timer by yourself\ntakes the arguments:\n !self 'pomodoros count'\n pomodoros count must be an integer from 1 to 16\nScore will be added to scoreboard```"
    )


@help.command()
async def study_with(ctx):
    await ctx.send(
        "```study_with\nCreate a private room with another user\ntakes the arguments:\n !study_with 'user' 'pomodoros count'\n pomodoros count must be an integer from 1 to 16\nScore will be added to scoreboard```"
    )


@help.command()
async def scoreboard(ctx):
    await ctx.send("```Display the scoreboard for the server```")


@help.command()
async def quit(ctx):
    await ctx.send(
        "```Quit the current room\n Score will not be added to scoreboard```"
    )


@bot.event
async def on_guild_join(guild):

    player_dictionary = {}
    for members in guild.members:
        player_dictionary[members.name] = 0

    with open(f"{guild.name}.json", "w") as outfile:
        json.dump(player_dictionary, outfile, indent=4)

    study = await guild.create_category("study")

    for channel in guild.channels:
        if channel.name == "general":
            await channel.send(
                "'!' is my command prefix! I've created the 'study' category and the 'Students' role, which is required for bot usage.\nPlease type !help for details."
            )
    await guild.create_role(name="Students", color=discord.Colour.blue(), mentionable=True, hoist=True, reason="This role is allowed to view Pomobots rooms!")


@bot.command(name="scoreboard")
async def display_scoreboard(ctx):
    with open(f"{ctx.guild}.json", "r") as openfile:
        scores = json.load(openfile)
        scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    em = discord.Embed(
        title="SCOREBOARD", description="Displaying total Pomodoros completed!   "
    )
    list_of_scores = []

    for key, value in scores.items():
        list_of_scores.append(f"{str(key)} {str(value)}")

    for index, score in enumerate(list_of_scores):
        if index == 0:
            list_of_scores[0] = f":first_place: {score}"
        elif index == 1:
            list_of_scores[1] = f":second_place: {score}"
        elif index == 2:
            list_of_scores[2] = f":third_place: {score}"
        else:
            list_of_scores[index] = f":medal:  {score}"

    embeded_scores = "\n".join(list_of_scores)

    em.add_field(name="Most Studied! :book:", value=f"{embeded_scores}", inline=False)
    em.set_thumbnail(
        url="https://media.discordapp.net/attachments/1007428518415708162/1008536901034188830/Pomo.PNG"
    )

    await ctx.message.channel.send(embed=em)


@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1

    print(f"PomoBot is in {guild_count} guilds")


@bot.command(name="study_with")
@commands.cooldown(1, 150, commands.BucketType.user)
async def create_private(ctx, name="", pomodoros=1):
    pomodoros = int(pomodoros)

    # checks if pomodoros argument is an integers
    if type(pomodoros) != int:
        await ctx.channel.send("```pomodoros argument must be an integer```")
    if int(pomodoros) > 16 or pomodoros == 0:
        await ctx.channel.send(
            "```max pomodoro count is 16 ( > 8 hours)```\n min pomodoro count is 1"
        )

    guild = ctx.guild
    author = ctx.author
    for members in guild.members:
        if name == members.display_name or name == members.nick:
            var = members
            if var == author:
                dm = await var.create_dm()
                await dm.send(
                    "Need a timer by yourself? Run the '!self' command in the server."
                )
                return

    private = await var.create_dm()
    await private.send(f"Hey! Study with {author} in {guild}. !quit the channel if you're not in the mood.")

    for role in guild.roles: 
        if role.name == "Students":
            study_role = role 


    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
        author: discord.PermissionOverwrite(read_messages=True),
        study_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        var: discord.PermissionOverwrite(read_messages=True, connect=True)
    }

    text_channel = await guild.create_text_channel(
        f"Study_with_{name}", overwrites=overwrites
    )
    voice_channel = await guild.create_voice_channel(
        f"Study_with_{name}", overwrites=overwrites
    )

    if pomodoros == 1:
        await text_channel.send(f"Lets study for {pomodoros} pomodoro!")
    else:
        await text_channel.send(f"Let's study for {pomodoros} pomodoros together!")

    for category in guild.categories:
        if category.name == "study":
            study = category
            await text_channel.edit(category=study)
            await voice_channel.edit(category=study)

    async def sleep():
        count = pomodoros
        run = True
        while run:
            if count == 0:
                await text_channel.send(
                    "\nCongratulations, you've done it! You've finished you're studying period :partying_face:\n The scoreboard has been updated just for you and we'll clean up here soon!"
                )
                asyncio.sleep(3)
                # TODO update scoreboard here

                with open(f"{guild}.json", "r") as openfile:
                    guild_dict = json.load(openfile)
                    guild_dict[author.name] += pomodoros
                    guild_dict[var.name] += pomodoros
                with open(f"{guild}.json", "w") as outfile:
                    json.dump(guild_dict, outfile)

                await text_channel.send(
                    "```This channel will be deleted in a few seconds```"
                )
                await asyncio.sleep(10)
                await text_channel.delete()
                await voice_channel.delete()
                run = False
                break
            elif count % 4 != 0:
                await asyncio.sleep(1500)
                await text_channel.send("5 minutes left! :alarm_clock:\nYou can do it!")
                await asyncio.sleep(300)
                await text_channel.send("Take a 5 minute break!")
                await asyncio.sleep(900)
                if count > 1: 
                    await text_channel.send("Now let's focus again.:books:")
                count = count - 1

            elif count % 4 == 0:
                await asyncio.sleep(1500)
                await text_channel.send("5 minutes left! :alarm_clock:\nYou got this!")
                await asyncio.sleep(300)
                await text_channel.send("Take a 15 minute break!")
                await asyncio.sleep(900)
                if count > 1: 
                    await text_channel.send("Now try your best to concentrate. :books:")
                count = count - 1

    await sleep()


@bot.command(name="self")
@commands.cooldown(1, 150, commands.BucketType.user)
async def create_private(ctx, pomodoros=1):
    pomodoros = int(pomodoros)

    # checks if pomodoros argument is an integers
    if type(pomodoros) != int:
        await ctx.channel.send("```pomodoros argument must be an integer```")
    if int(pomodoros) > 16 or pomodoros == 0:
        await ctx.channel.send(
            "```max pomodoro count is 16 ( > 8 hours)```\n min pomodoro count is 1"
        )

    guild = ctx.guild
    author = ctx.author

    for role in guild.roles: 
        if role.name == "Students":
            study_role = role 


    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
        author: discord.PermissionOverwrite(read_messages=True),
        study_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
    }

    self_text_channel = await guild.create_text_channel(
        f"{author.display_name}s_room", overwrites=overwrites
    )
    self_voice_channel = await guild.create_voice_channel(
        f"{author.display_name}s_room", overwrites=overwrites
    )

    if pomodoros == 1:
        await self_text_channel.send(f"Let's study for {pomodoros} pomodoro!")
    else:
        await self_text_channel.send(f"Let's study for {pomodoros} pomodoros together!")

    for category in guild.categories:
        if category.name == "study":
            study = category
            await self_text_channel.edit(category=study)
            await self_voice_channel.edit(category=study)

    async def sleep():
        count = pomodoros
        run = True
        while run:
            if count == 0:
                await self_text_channel.send(
                    "\nCongratulations, you've done it! You've finished you're studying period :partying_face:\n The scoreboard has been updated just for you and we'll clean up here soon!"
                )
                await asyncio.sleep(3)
                # TODO update scoreboard here

                with open(f"{guild}.json", "r") as openfile:
                    guild_dict = json.load(openfile)
                    guild_dict[author.name] += pomodoros
                with open(f"{guild}.json", "w") as outfile:
                    json.dump(guild_dict, outfile)

                await self_text_channel.send(
                    "```This channel will be deleted in a few seconds```"
                )
                await asyncio.sleep(10)
                await self_text_channel.delete()
                await self_voice_channel.delete()
                run = False
                break
            elif count % 4 != 0:
                await asyncio.sleep(1500)
                await self_text_channel.send(
                    "5 minutes left! :alarm_clock:\nWe can do it!"
                )
                await asyncio.sleep(300)
                await self_text_channel.send("Let's take a 5 minute break!")
                await asyncio.sleep(300)
                if count > 1: 
                    await self_text_channel.send("Now let's focus again.:books:")
                count = count - 1

            elif count % 4 == 0:
                await asyncio.sleep(1500)
                await self_text_channel.send(
                    "Only 5 minutes left! :alarm_clock:\nWe've got this!"
                )
                await asyncio.sleep(300)
                await self_text_channel.send("How's a 15 minute break sound?")
                await asyncio.sleep(900)
                if count > 1: 
                    await self_text_channel.send("Now try our best to concentrate. :books:")
                count = count - 1

    await sleep()


@bot.command(name="quit")
@commands.cooldown(1, 100, commands.BucketType.user)
async def quit(ctx):
    guild = ctx.guild
    channel = ctx.message.channel
    for category in guild.categories:
        if category.name == "study":
            study = category
    if channel.category == study:
        await channel.send("```this session will be deleted in a few seconds```")
        await asyncio.sleep(3)
        for voice in study.voice_channels:
            if voice.name.lower() == channel.name.lower():
                await voice.delete()
                await channel.delete()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command.")
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(error)


bot.run(TOKEN)
