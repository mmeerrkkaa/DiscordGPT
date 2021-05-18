import discord
from discord.ext import commands
import requests
import json
from io import StringIO
import math
import sqlite3
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option




guild_ids = [627899942593363968]



async def SelectMember(member_id):

    a = cursor.execute(f"SELECT * FROM users where id_member = {member_id}").fetchone()
    return a


async def SelectGuild(Guild_id):
    a = cursor.execute(f"SELECT * FROM server where Guild_id = {Guild_id}").fetchone()
    return a

async def SelectHistory(ids):
    a = cursor.execute(f"SELECT * FROM history where ids = {ids}").fetchone()
    return a




class RuGpt(commands.Cog):

    
    
    def __init__(self, bot):

        self.bot = bot
        self.url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'

        self.headers = {'Content-type': 'application/json',  # Определение типа данных
           'Accept': 'text/plain',
           'Content-Encoding': 'utf-8'}
    
    #  @commands.command()
    @cog_ext.cog_slash(name="генерировать",
             description="генерирует текст с помощью нейросети",
             options=[
               create_option(
                 name="текст",
                 description="Входной текст",
                 option_type=3,
                 required=True
               )
             ])
    async def ww(self, ctx, **args):
        
        args = args["текст"].split()
        
        if len(args) == 0:
            return

        sendschan = await ctx.send(f"Генерация текста... **{' '.join(args)}**...")

        channel = self.bot.get_channel(843553799615807548)

        data = {"text" :  " ".join(args)}
        
        


        answer = requests.post(self.url, data=json.dumps(data), headers=self.headers)
        response = answer.json()
        text = response["predictions"].split()
        textone = response["predictions"]
        
        PeopleWords = []
        for i in range(len(args)):
            PeopleWords.append(i)
            text[i] = "**"+text[i]+"**"
            
        text = " ".join(text)
        #  s = StringIO()
        #  s.write(text)
        #  s.seek(0)
        countSend = math.ceil(len(text)/2000)
        count = 1
        for i in range(countSend):
            if count == 1:
                await sendschan.edit(content = text[i*2000:2000*count])
                count += 1
                continue

            await ctx.send(text[i*2000:2000*count])
            count += 1
        


        

        PeopleWords = json.dumps(PeopleWords)
        #textone = json.dumps(textone)
        cursor.execute(f"INSERT INTO history VALUES (NULL, ?, ?, ?, ?)", (textone, PeopleWords, ctx.author.id, ctx.guild.id))

        lastid = cursor.execute("SELECT * FROM history ORDER BY ids DESC LIMIT 1;").fetchone()
        await channel.send(f"[{ctx.guild.name}] {ctx.author} генерирует текст - начало: {' '.join(args)}. Ид - {lastid[0]}")

        dsa = await SelectMember(ctx.author.id)

        if dsa == None:
            cursor.execute(f"INSERT INTO users VALUES ({ctx.author.id}, '0', 'None')")#вводит все данные об участнике в БД
            conn.commit()
        
        cursor.execute(f'UPDATE users SET CountGeneration = (?), LastGenerationId = (?) where id_member={int(ctx.author.id)}', (int(dsa[1]) + 1, lastid[0]))
        conn.commit()
        dsa = await SelectGuild(ctx.guild.id)
        conn.commit()

        if dsa == None:
            memList = await ctx.guild.fetch_members(limit=100000).flatten()

            if len(memList) < 50:
                nums = 30
            else:
                nums = 100
            
            cursor.execute(f"INSERT INTO server VALUES ({ctx.guild.id},'0', '0', '{nums}')")
            conn.commit()

        cursor.execute(f'UPDATE server SET Count = {int(dsa[2]) + 1} where Guild_id={int(ctx.guild.id)}')


        conn.commit()
        # await ctx.send(file=discord.File(s, filename="text.txt"))
    

    @cog_ext.cog_slash(name="Продолжить",
             description="Продолжает генерировать ваш последний текст.",
             options=[
               create_option(
                 name="текст",
                 description="Входной текст.",
                 option_type=3,
                 required=False
               )
             ])
    async def wwnext(self, ctx, **args):

        if len(args) != 0:
            args = args["текст"].split()
        
        authorDB = await SelectMember(ctx.author.id)
        if authorDB[2] == "None":
            await ctx.send("У вас нету сгенерированных текстов!")
            return

        if len(args) == 0:
            sendschan = await ctx.send(f"Продолжение последнего текста...")
        else:
            sendschan = await ctx.send(f"Продолжение последнего текста... **{' '.join(args)}**...")
            

        dsa = await SelectHistory(authorDB[2])

        PeopleWords = []
        if len(args) != 0:

            PeopleWords = [i for i in range(len(dsa[1].split()), len(dsa[1].split() + args))]

            args = dsa[1].split() +  args
        else:
            args = dsa[1].split()

        

        data = {"text" : " ".join(args)}

        
        
        answer = requests.post(self.url, data=json.dumps(data), headers=self.headers)
        response = answer.json()

        
        text = response["predictions"].split()
        textone = response["predictions"]
        
        
        PeopleWords = json.loads(dsa[2]) + PeopleWords


        for i in range(len(PeopleWords)):
            text[PeopleWords[i]] = "**"+text[PeopleWords[i]]+"**"
            
        text = " ".join(text)
        #  s = StringIO()
        #  s.write(text)
        #  s.seek(0)
        countSend = math.ceil(len(text)/2000)
        count = 1
        for i in range(countSend):
            if count == 1:
                await sendschan.edit(content = text[i*2000:2000*count])
                count += 1
                continue

            await ctx.send(text[i*2000:2000*count])
            count += 1
        


        
        
        PeopleWords = json.dumps(json.loads(dsa[2]) + PeopleWords)

        #textone = json.dumps(textone)
        cursor.execute(f'UPDATE history SET text = (?), PeopleWords = (?) where ids={authorDB[2]}', (textone, PeopleWords))

        conn.commit()


conn = sqlite3.connect("Discord.db") # или :memory:
cursor = conn.cursor()


def setup(bot):
    bot.add_cog(RuGpt(bot))

'''

url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'

headers = {'Content-type': 'application/json',  # Определение типа данных
           'Accept': 'text/plain',
           'Content-Encoding': 'utf-8'}
           
data = {"text" : "Империя"}
answer = requests.post(url, data=json.dumps(data), headers=headers)
print(answer)
response = answer.json()
print(response["predictions"])
'''