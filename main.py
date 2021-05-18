import discord
import os
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import os
import sqlite3
import keep_alive

print(discord.__version__)
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="*",
                   intents=discord.Intents.all(),
                   case_insensitive=True)

slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


async def SelectMember(member_id):

	a = cursor.execute(
	    f"SELECT * FROM users where id_member = {member_id}").fetchone()
	return a


async def SelectJoinGuild(Guild_id):
	a = cursor.execute(
	    f"SELECT Guild_id FROM server where Guild_id = {Guild_id}").fetchone()
	return a


async def SelectGuild(Guild_id):
	a = cursor.execute(
	    f"SELECT * FROM server where Guild_id = {Guild_id}").fetchone()
	return a


@bot.event
async def on_guild_join(guild):
	channel = bot.get_channel(843553799615807548)

	await channel.send(f"Бот присоединился к серверу - {guild.name}")
	if await SelectJoinGuild(guild.id) == None:

		cursor.execute(
		    f"INSERT INTO server VALUES ({guild.id},'0', '0', '50')")
		conn.commit()

	memList = await guild.fetch_members(limit=100000).flatten()
	for member in memList:

		if await SelectMember(member.id) == None:
			cursor.execute(
			    f"INSERT INTO users VALUES ({member.id}, '0', 'None')"
			)  #вводит все данные об участнике в БД

	conn.commit()


@bot.event
async def on_member_join(member):
	if await SelectMember(member.id) != None:
		cursor.execute(f"INSERT INTO users VALUES ({member.id}, '0', 'None')")
		conn.commit()


@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(
	    name="Команды через слэш /"))
	for guild in bot.guilds:
		print(guild)

		if await SelectJoinGuild(guild.id) == None:
			memList = await guild.fetch_members(limit=100000).flatten()

			cursor.execute(
			    f"INSERT INTO server VALUES ({guild.id},'0', '0', '50')")
			conn.commit()

			for member in memList:

				if await SelectMember(member.id) == None:
					cursor.execute(
					    f"INSERT INTO users VALUES ({member.id}, '0', 'None')"
					)  #вводит все данные об участнике в БД
					conn.commit()


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
async def dd(ctx, Guild_id=627899942593363968):
	print(ctx.guild.id)


@bot.command()
async def UploadDB(ctx):
	await ctx.send(file=discord.File(r'Discord.db'))


conn = sqlite3.connect("Discord.db")  # или :memory:
cursor = conn.cursor()

cursor.execute(
    f"CREATE TABLE IF NOT EXISTS users (id_member INTEGER, CountGeneration INTEGER, LastGenerationId INTEGER)"
)
conn.commit()

cursor.execute(
    f"CREATE TABLE IF NOT EXISTS history (ids INTEGER PRIMARY KEY NOT NULL, text TEXT,PeopleWords TEXT, member_id INTEGER, server_id INTEGER)"
)
conn.commit()

cursor.execute(
    f"CREATE TABLE IF NOT EXISTS server (Guild_id INTEGER,Premium INTEGER, Count INTEGER, MaxCount INTEGER)"
)
conn.commit()

cursor.execute(
    f"CREATE TABLE IF NOT EXISTS sponsor (id_member INTEGER, data TEXT)"
)
conn.commit()

keep_alive.keep_alive()
bot.run(os.environ.get("token"))
