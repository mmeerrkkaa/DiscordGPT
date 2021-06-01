import discord
from discord.ext import commands
import json
import sqlite3
import datetime
import math
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

class sponsor(commands.Cog):

    
    
    def __init__(self, bot):

        self.bot = bot
    
    @commands.command()
    async def addpremium(self, ctx, id_member):

        if ctx.author.id!= 336119947736514560:
            return
        
        if await SelectMember(id_member) == None:
            await ctx.send("Нет такого в базе данных")

        if await SelectMember(id_member)['premium'] != 0:
            await ctx.send("Он уже имеет премиум")
            return


        collestionuser.update_one({"id_member": id_member}, {"$set": {"premium": 1}})

        await ctx.send("Премиум статус выдан")
    

    @commands.command()
    async def history(self,ctx, ids):

        if await SelectMember(ctx.author.id)['premium'] == 0:
            await ctx.send("Вы не имеете премиум статуса")
            return

        dsa = await SelectHistory(ids)

        text = f"Автор: {dsa['text'].split()}"
        
        PeopleWords = json.loads(dsa['PeopleWords'])


        for i in range(len(PeopleWords)):
            text[PeopleWords[i]] = "**"+text[PeopleWords[i]]+"**"
            
        text = " ".join(text)
        #  s = StringIO()
        #  s.write(text)
        #  s.seek(0)
        count = 1
        countSend = math.ceil(len(text)/2000)
        for i in range(countSend):
            await ctx.send(text[i*2000:2000*count])
            count += 1
    
    @commands.command()
    async def info(self,ctx):

        if await SelectMember(ctx.author.id) == 0:
            await ctx.send("Вы не имеете премиум статуса")
            return

        dsa = await SelectMember(ctx.author.id)

        await ctx.send(f"{ctx.author} у вас за всё время сгенерированно {dsa['countGeneration']} историй. Последняя под идом {dsa['LastGenerationId']}")
    
    
        
        


def setup(bot):
    bot.add_cog(sponsor(bot))