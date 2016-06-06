import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import json
import time
import copy
import random
from random import randint

class Ego:
    """A cog meant to keep track of stats given by fellow members of the discord"""

    def __init__(self, bot):
        self.bot = bot
        self.profiles = fileIO("data/ego/profiles.json", "load")

    @commands.command(pass_context=True)
    async def addquote(self, ctx, user : discord.Member=None):
        """Allows you to save quotes said by a given user

        [p]writequote [user] \"Hello World!\" 
        Will store the quote \"Hello World!\" """

        if not user:
            return await self.bot.say("No actual user given")

        #create profile if user doesn't exist in it 
        if not self.profile_check(user.id):
            self.create_profile(user)
        #parse the message, removing command and user id
        length = 14 + len(str(user.id))
        self.profiles[user.id]["quotes"].append(ctx.message.content[length:])
        fileIO("data/ego/profiles.json", "save", self.profiles)
        await self.bot.say("Quote for " + user.name + " added.")


    @commands.command(pass_context=True)
    async def quote(self, ctx, user : discord.Member=None):
        """Prints quotes that have been saved from a given user

        Will pick a randomly saved quote from the list
        [p]quote [user] #
        Will pick the quote at number # in the list
        [p]quote [user] word
        Will pick the first quote containing 'word' in the list
        """

        if not user:
            #randomly select a quote using weights to prevent favoring users
            totals = []
            currIndex = 0
            for userID in self.profiles.keys():
                currIndex += len(self.profiles[userID]["quotes"])
                totals.append([currIndex, userID])
            i = randint(0, currIndex - 1)
            temp = 0

            for num in range(0, len(totals)):
                if i < totals[num][0]:
                    index = randint(0, len(self.profiles[totals[num][1]]["quotes"]) - 1)
                    return await self.bot.say("{}, - {}".format(self.profiles[totals[num][1]]["quotes"][index], self.profiles[totals[num][1]]["name"]))
                temp += totals[num][0]


        else:
            if not self.profile_check(user.id):
                self.create_profile(user)
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("User doesn't have any quotes saved!")
            if len(self.profiles[user.id]["quotes"]) is 0:
                return await self.bot.say("User doesn't have any quotes saved!")

            #parsing message for specific commands
            length = 11 + len(str(user.id))
            #no other parameters given, randomize quote
            if len(ctx.message.content) <= length:
                return await self.bot.say("{}, - {}".format(random.choice(self.profiles[user.id]["quotes"]), user.name))

            try:
                # see if it's a number
                index = int(ctx.message.content[length:])
                if len (self.profiles[user.id]["quotes"]) < index:
                    return await self.bot.say("No quote at {} since {} only has {}".format(str(index), user.name, str(len(self.profiles[user.id]["quotes"]))))
                return await self.bot.say("{}, - {}".format(self.profiles[user.id]["quotes"][index-1], user.name))
            except ValueError:
                #it's a string, search quotes for ones that contain it
                for num in range(0, len(self.profiles[user.id]["quotes"])):
                    if ctx.message.content[length:] in self.profiles[user.id]["quotes"][num]:
                        return await self.bot.say("{}, - {}".format(self.profiles[user.id]["quotes"][num], user.mention))
                return await self.bot.say("No quote containing {} found for {}".format(ctx.message.content[length:], user.name))

    @commands.command(pass_context=True)
    async def cheers(self, ctx, user : discord.Member=None):
        """Give cheers, props, kudos, or praise to a member

        Will give one of the command sender's daily alloted cheers points to [user] """

        #Your code will go here
        await self.bot.say("Not implemented")

    @commands.command(pass_context=True)
    async def plus1(self, ctx,  statistic : "", user : discord.Member=None):
        """Add a point to a stat on a given user

        Will give [user] the /"Ego/" stat if they didn't have it already, and then add 1 to it.
        This does not take you cheers points, but you may only do this once every few minutes
        """

        #Your code will go here
        await self.bot.say("Not implemented")

    @commands.command(pass_context=True)
    async def stats(self, ctx, user : discord.Member=None):
        """Provides Ego stats assigned to the user

        Will provide number of quotes, number of cheers point gained, cheers points remaining, and any misc. points given by other discord members"""

        #Your code will go here

        if user.id in self.profiles:
            quotelist = self.profiles[user.id]["quotes"]
            message = "User {}, whose quote alias is {}, has a total of {} quotes attributed to them:\n".format(user.name, self.profiles[user.id]["name"], len(quotelist))
            for q in quotelist:
                message += q + "\n"
            return await self.bot.say("{}".format(message))

        self.create_profile(user)
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return 


    def profile_check(self, id):
        if id in self.profiles:
            return True
        else:
            return False

    def quotes_check(self, id):
        if id in self.profiles and "quotes" in self.profiles[id]:
            return True
        else:
            return False

    def create_profile(self, user):
        if user.id in self.profiles:
            return
        self.profiles[user.id] = {"name" : user.name, "cheers_points" : 3, "props" : 0, "quotes" : []}



def setup(bot):
    bot.add_cog(Ego(bot))
