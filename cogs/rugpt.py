import discord
from discord.ext import commands
import aiohttp
from aiohttp_requests import requests
import json
from io import StringIO
import math
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from fake_useragent import UserAgent
import os
from pymongo import MongoClient



cluster = MongoClient(f"mongodb+srv://root:{os.environ.get('passdb')}@cluster0.ej8oe.mongodb.net/discord?retryWrites=true&w=majority")


db = cluster['discord']
collestionuser = db['user']
collestionguild = db['guild']
collestionhistory = db['history']




async def SelectMember(member_id):

    a = collestionuser.find_one({'id_member' : member_id})
    return a


async def SelectGuild(Guild_id):
    a = collestionguild.find_one({'Guild_id' : Guild_id})
    return a


async def SelectHistory(ids):
    a = collestionhistory.find_one({'ids' : ids})
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
               
        answer = await requests.post(self.url, data=json.dumps(data), headers=self.headers)
        response = await answer.json()
        print(answer)
        text = response["predictions"].split()
        textone = response["predictions"]
        
        print(len(textone))

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

        



        add = collestionhistory.find().count() + 1
        collestionhistory.insert_one({"ids": add,"text": textone, "PeopleWords": PeopleWords, "id_member": ctx.author.id, "guild_id": ctx.guild.id})



        await channel.send(f"[{ctx.guild.name}] {ctx.author} генерирует текст - начало: {' '.join(args)}. Ид - {add}")


        dsa = await SelectMember(ctx.author.id)

        if dsa == None:
            collestionuser.insert_one({"id_member": ctx.author.id,"premium": 0, "countGeneration": 0, "LastGenerationId": 0})
        
        dsa = await SelectMember(ctx.author.id)
        
        collestionuser.update_one({"id_member": ctx.author.id}, {"$set": {"countGeneration": dsa['countGeneration']+1, "LastGenerationId": add}})
        

        if await SelectGuild(ctx.guild.id) == None:

            collestionguild.insert_one({"Guild_id": ctx.guild.id, "count": 0})

        dsa = await SelectGuild(ctx.guild.id)
        collestionguild.update_one({"Guild_id": ctx.guild.id}, {"$set": {"count": dsa['count']+1}})

    

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
        print(authorDB)
        if authorDB['LastGenerationId'] == "None":
            await ctx.send("У вас нету сгенерированных текстов!")
            return

        if len(args) == 0:
            sendschan = await ctx.send(f"Продолжение последнего текста...")
        else:
            sendschan = await ctx.send(f"Продолжение последнего текста... **{' '.join(args)}**...")
            

        dsa = await SelectHistory(authorDB['LastGenerationId'])
        
        PeopleWords = []
        if len(args) != 0:
            print(dsa['PeopleWords'])
            PeopleWords = [i for i in range(len(dsa['text'].split()), len(dsa['text'].split() + args))]

            print(PeopleWords)

            args = dsa['text'].split() +  args
        else:
            args = dsa['text'].split()

        

        data = {"text" : " ".join(args)}

        
        
        answer = await requests.post(self.url, data=json.dumps(data), headers=self.headers)
        response = await answer.json()

        
        text = response["predictions"].split()
        textone = response["predictions"]
        
        
        PeopleWords = json.loads(dsa['PeopleWords']) + PeopleWords


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
        


        
        
        PeopleWords = json.dumps(json.loads(dsa['PeopleWords']) + PeopleWords)

        #textone = json.dumps(textone)


        collestionhistory.update_one({"ids": authorDB['LastGenerationId']}, {"$set": {"text": textone, "PeopleWords": PeopleWords}})





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