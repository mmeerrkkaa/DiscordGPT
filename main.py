import discord
import os
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import os
import sqlite3
import keep_alive
from pymongo import MongoClient



cluster = MongoClient(f"mongodb+srv://root:{os.environ.get('passdb')}@cluster0.ej8oe.mongodb.net/discord?retryWrites=true&w=majority")


db = cluster['discord']
collestionuser = db['user']
collestionguild = db['guild']

#collestion.insert_one({"id_member": "902313", "countGeneration": 0, "LastGenerationId": 0})

print(discord.__version__)
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="*",
                   intents=discord.Intents.all(),
                   case_insensitive=True)
bot.remove_command('help')
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


async def SelectMember(member_id):

    a = collestionuser.find_one({'id_member' : member_id})
    return a


async def SelectJoinGuild(Guild_id):
    a = collestionguild.find_one({'Guild_id' : Guild_id})
    return a


@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(843553799615807548)

    await channel.send(f"Бот присоединился к серверу - {guild.name}")
    if collestionguild.find_one({"Guild_id": guild.id}) is None:
        collestionguild.insert_one({"Guild_id": guild.id, "count": 0})

    memList = await guild.fetch_members(limit=100000).flatten()
    for member in memList:
        if collestionuser.find_one({"id_member": member.id}) is None:
            collestionuser.insert_one({"id_member": member.id,"premium": 0, "countGeneration": 0, "LastGenerationId": 0})



@bot.event
async def on_member_join(member):
    collestionuser.insert_one({"id_member": member.id,"premium": 0, "countGeneration": 0, "LastGenerationId": 0})


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(
	    name="Команды через слэш /"))
    for guild in bot.guilds:
        print(guild)


        if collestionguild.find_one({"Guild_id": guild.id}) is None:
            collestionguild.insert_one({"Guild_id": guild.id, "count": 0})

        memList = await guild.fetch_members(limit=100000).flatten()
        for member in memList:
            if collestionuser.find_one({"id_member": member.id}) is None:
                collestionuser.insert_one({"id_member": member.id,"premium": 0, "countGeneration": 0, "LastGenerationId": 0})



@bot.event
async def on_raw_reaction_add(messages):
    if messages.emoji.name == "❌":
        msg = await bot.get_channel(messages.channel_id).fetch_message(messages.message_id)
        await msg.delete()



@bot.command()
async def reload(ctx, extension):

    if ctx.author.id != 336119947736514560:
        return

    #bot.unload_extension(f"cogs.{extension}")
    bot.unload_extension(f"cogs.{extension}")

    bot.load_extension(f"cogs.{extension}")
    await ctx.send("cogs reload")


for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")


@bot.command()
async def dd(ctx):
	print(collestionguild.find().count())


keep_alive.keep_alive()
bot.run(os.environ.get("token"))
