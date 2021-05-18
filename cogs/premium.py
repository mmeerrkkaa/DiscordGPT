import discord
from discord.ext import commands
import json
import sqlite3
import datetime
import math


async def SelectMember(member_id):

    a = cursor.execute(f"SELECT * FROM users where id_member = {member_id}").fetchone()
    return a


async def SelectGuild(Guild_id):
    a = cursor.execute(f"SELECT * FROM server where Guild_id = {Guild_id}").fetchone()
    return a

async def SelectHistory(ids):
    a = cursor.execute(f"SELECT * FROM history where ids = {ids}").fetchone()
    return a

async def SelectSponsor(member_id):

    a = cursor.execute(f"SELECT * FROM sponsor where id_member = {member_id}").fetchone()
    return a


class sponsor(commands.Cog):

    
    
    def __init__(self, bot):

        self.bot = bot
    
    @commands.command()
    async def addpremium(self, ctx, id_member):

        if ctx.author.id!= 336119947736514560:
            return
        
        if await SelectSponsor(id_member) != None:
            await ctx.send("Он уже имеет премиум")
            return

        dsa = await SelectMember(id_member)

        if dsa == None:
            await ctx.send("Нет такого в базе данных")
        
        times = datetime.datetime.today() + datetime.timedelta(hours=3)

        cursor.execute(f"INSERT INTO sponsor VALUES ({id_member}, '{times.day}.{times.month}.{times.year} - {times.hour}:{times.minute}')")#вводит все данные об участнике в БД

        conn.commit()
        await ctx.send("Премиум статус выдан")
    

    @commands.command()
    async def history(self,ctx, ids):

        if await SelectSponsor(ctx.author.id) == None:
            await ctx.send("Вы не имеете премиум статуса")
            return

        dsa = await SelectHistory(ids)

        text = f"Автор: {dsa[1].split()}"
        PeopleWords = json.loads(dsa[2])


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

        if await SelectSponsor(ctx.author.id) == None:
            await ctx.send("Вы не имеете премиум статуса")
            return

        dsa = await SelectMember(ctx.author.id)

        await ctx.send(f"{ctx.author} у вас за всё время сгенерированно {dsa[1]} историй. Последняя под идом {dsa[2]}")
    
    
        
        



conn = sqlite3.connect("Discord.db") # или :memory:
cursor = conn.cursor()


def setup(bot):
    bot.add_cog(sponsor(bot))