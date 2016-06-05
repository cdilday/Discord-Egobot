import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import json
import time

class Ego:
    """A cog meant to keep track of stats given by fellow members of the discord"""

    def __init__(self, bot):
        self.bot = bot
        self.profiles = fileIO("data/ego/profiles.json", "load")

    @commands.command(pass_context=True)
    async def addquote(self, ctx, user : discord.Member=None):
        """Allows you to save quotes said by a given user

        [p]writequote [user] \"Hello World!\" 
       	Will store the quote \"Hello World!\" at the given date for user"""

        #Your code will go here
        if not user:
        	await self.bot.say("No user given")
        else:
        	if not self.profile_check(user.id):
        		self.create_profile(user)
        	self.profiles[user.id]["quotes"].append(ctx.message.content)
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

        #Your code will go here
        await self.bot.say("Not implemented")

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
        await self.bot.say("Not implemented")


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
