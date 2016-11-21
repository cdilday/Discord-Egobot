import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import json
import datetime
import copy
import random
from random import randint
import os

class Ego:
    """A cog to keep track of stats and attributes given by fellow members of the discord"""

    def __init__(self, bot):
        self.bot = bot
        #check to make sure the directory exists
        if not os.path.exists("data/ego"):
            os.makedirs("data/ego")
            with open("data/ego/profiles.json", "w") as outfile:
                json.dump({}, outfile, indent=4)
                
        #check to make sure the json wasn't deleted by itself
        if not os.path.exists("data/ego/profiles.json"):
            with open("data/ego/profiles.json", "w") as outfile:
                json.dump({}, outfile, indent=4)
        self.profiles = fileIO("data/ego/profiles.json", "load")

    @commands.command(pass_context=True)
    async def addquote(self, ctx, user : discord.Member=None):
        """Allows you to save quotes said by a given user

        [p]addquote [user] \"Hello World!\" 
        Will store the quote \"Hello World!\" for [user] """

        if not user:
            return await self.bot.say("`No actual user given`")

        #create profile if user doesn't exist in it 
        if not self.profile_check(user.id):
            self.create_profile(user)

        #parse the message, removing command and user id
        messStart = self.find_message_start(ctx, user, "addquote")

        quoteStr = ctx.message.content[messStart:]

        #add quotation mark if the user forgot to put them and it's actually a quote (not an action or description)
        if "\"" not in quoteStr and quoteStr[0] != "*" and quoteStr[0] != "(":
            quoteStr = "\"" + quoteStr + "\""

        self.profiles[user.id]["quotes"].append(quoteStr)
        fileIO("data/ego/profiles.json", "save", self.profiles)
        await self.bot.say("`Quote for " + user.name + " added.`")


    @commands.command(pass_context=True)
    async def quote(self, ctx, user : discord.Member=None):
        """Prints quotes that have been saved from a given user, or just a random quote if no user given

        Will pick a randomly saved quote from the list
        [p]quote [user] #
        Will pick the quote at number # in the list
        [p]quote [user] word
        Will pick the first quote containing 'word' in the list
        """
        #with no parameters, this will select a completely random quote
        if not user:
            #randomly select a quote using weights to prevent favoring users
            totals = []
            currIndex = 0
            for userID in self.profiles.keys():
                currIndex += len(self.profiles[userID]["quotes"])
                totals.append([currIndex, userID])

            # if there are no quotes, there's nothing to do here
            if currIndex is 0:
                return await self.bot.say("`You have no quotes saved! Use [p]addquote [user] <quote> to add some!`")

            i = randint(0, currIndex - 1)
            temp = 0

            for num in range(0, len(totals)):
                if i < totals[num][0]:
                    index = randint(0, len(self.profiles[totals[num][1]]["quotes"]) - 1)
                    return await self.bot.say("{}, - {}".format(self.profiles[totals[num][1]]["quotes"][index], self.profiles[totals[num][1]]["name"]))
                temp += totals[num][0]

        # Now to handle parameters
        else:
            #first check to make sure the user exists and has quotes
            if not self.profile_check(user.id):
                self.create_profile(user)
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`User doesn't have any quotes saved!`")
            if len(self.profiles[user.id]["quotes"]) is 0:
                return await self.bot.say("`User doesn't have any quotes saved!`")

            #parsing message for specific commands, gotta find where the user ends and the parameters start in a way that's API compatible
            messStart = self.find_message_start(ctx, user, "quote")

            #no other parameters given, give quote from user
            if len(ctx.message.content) <= messStart:
                return await self.bot.say("{}, - {}".format(random.choice(self.profiles[user.id]["quotes"]), user.name))

            try:
                # see if it's a number
                index = int(ctx.message.content[messStart:])
                if len (self.profiles[user.id]["quotes"]) < index:
                    return await self.bot.say("`No quote at {} since {} only has {}`".format(str(index), user.name, str(len(self.profiles[user.id]["quotes"]))))
                return await self.bot.say("{}, - {}".format(self.profiles[user.id]["quotes"][index-1], user.name))
            except ValueError:
                #it's a string, search quotes for ones that contain it
                for num in range(0, len(self.profiles[user.id]["quotes"])):
                    if ctx.message.content[messStart:].lower() in self.profiles[user.id]["quotes"][num].lower():
                        return await self.bot.say("{}, - {}".format(self.profiles[user.id]["quotes"][num], user.name))
                return await self.bot.say("`No quote containing {} found for {}`".format(ctx.message.content[messStart:], user.name))

    @commands.command(pass_context=True)
    async def fixquote(self, ctx, user : discord.Member=None, word : str=""):
        """Allows you to update a selected quote for the given user

        [p]fixquote [user] <word> <string>
        Will pick the quote in [user]'s quotes with <word> in it and replace it with <string>
        Do not use quotes or spaces in the word key. It must be a single word or part of a word.
        """
        #first check to make sure the user exists and has quotes
        if user is None:
            return await self.bot.say("`I need a user to fix a quote for!`")

        if not self.profile_check(user.id):
            self.create_profile(user)
            fileIO("data/ego/profiles.json", "save", self.profiles)
            return await self.bot.say("`User doesn't have any quotes saved!`")
        if len(self.profiles[user.id]["quotes"]) is 0:
            return await self.bot.say("`User doesn't have any quotes saved!`")

        if word is "":
            return await self.bot.say("`I can't find a quote without a key`")

        #get message start, add word length
        messStart = self.find_message_start(ctx, user, "fixquote")

        messStart += len(word) + 1

        if messStart >= len(ctx.message.content):
            return await self.bot.say("`I can't fix a quote with nothing`")
        # add quotemarks to given quote as needed
        quoteStr = ctx.message.content[messStart:]

        for num in range(0, len(self.profiles[user.id]["quotes"])):
            if word.lower() in self.profiles[user.id]["quotes"][num].lower():
                if "\"" not in quoteStr and quoteStr[0] != "*" and quoteStr[0] != "(":
                    quoteStr = "\"" + quoteStr + "\""
                self.profiles[user.id]["quotes"][num] = quoteStr
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`Quote for " + user.name + " changed to`\n" + quoteStr)
        return await self.bot.say("`No quote containing {} found for {}`".format(word, user.name))

    @commands.command(pass_context=True)
    async def removequote(self, ctx, user : discord.Member=None, word : str=""):
        """Allows you to remove a selected quote for the given user

        [p]removequote [user] <word>
        Will pick the quote in [user]'s quotes with <word> in it and remove it
        """
        #first check to make sure the user exists and has quotes
        if user is None:
            return await self.bot.say("`I need a user to remove a quote from!`")

        if not self.profile_check(user.id):
            self.create_profile(user)
            fileIO("data/ego/profiles.json", "save", self.profiles)
            return await self.bot.say("`User doesn't have any quotes saved!`")
        if len(self.profiles[user.id]["quotes"]) is 0:
            return await self.bot.say("`User doesn't have any quotes saved!`")

        if word is "":
            return await self.bot.say("`I can't find a quote to remove without a key`")

        for num in range(0, len(self.profiles[user.id]["quotes"])):
            if word.lower() in self.profiles[user.id]["quotes"][num].lower():
                del self.profiles[user.id]["quotes"][num]
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`Quote for " + user.name + " removed`\n")
        return await self.bot.say("`No quote containing {} found for {}`".format(word, user.name))

    @commands.command(pass_context=True)
    async def cheers(self, ctx, user : discord.Member=None):
        """Give cheers, props, kudos, or otherwise praise to a member

        Will give one of the command sender's daily alloted cheers points to [user] """
        #check to make sure both users have profiles first
        if not self.profile_check(user.id):
            self.create_profile(user)
        if not self.profile_check(ctx.message.author.id):
            self.create_profile(ctx.message.author)

        #housekeeping with points refreshing everyday
        today = datetime.date.today()

        if "refresh_time" not in self.profiles[ctx.message.author.id]:
            self.profiles[ctx.message.author.id]["refresh_time"] = [today.day, today.month, today.year]

        #checking to see if points need to be reset
        lasttime = self.profiles[ctx.message.author.id]["refresh_time"]
        if lasttime[0] != today.day or lasttime[1] != today.month or lasttime[2] != today.year:
            self.profiles[ctx.message.author.id]["cheers_points"] = 3

        #prevent people from cheering themselves
        if user.id == ctx.message.author.id:
            return await self.bot.say("`You can pat yourself on the back, but you can't give props to yourself, {}.`".format(ctx.message.author.name))

        #check if author has any points to give
        if self.profiles[ctx.message.author.id]["cheers_points"] <= 0:
            return await self.bot.say("`You've given out too many cheers today, {}. Make them count tomorrow!`".format(ctx.message.author.name))

        #author uses his points, update appropriately
        self.profiles[ctx.message.author.id]["refresh_time"] = [today.day, today.month, today.year]
        self.profiles[ctx.message.author.id]["cheers_points"] -= 1
        self.profiles[user.id]["props"] += 1
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return await self.bot.say("`Cheers to you, {}! {}, you have {} points left to give for today`".format(user.name,ctx.message.author.name, self.profiles[ctx.message.author.id]["cheers_points"]))

    @commands.command(pass_context=True)
    async def plus1(self, ctx, user : discord.Member=None):
        """Add a point to a stat on a given user

        Will give [user] the given stat if they didn't have it already, and then add 1 to it.
        This does not take your cheers points, but you may only do this once every few minutes
        """

        #make sure the people involved have profiles

        if not user:
            return await self.bot.say("`Need a user and a stat to add to`")

        if not self.profile_check(user.id):
            self.create_profile(user)
        if not self.profile_check(ctx.message.author.id):
            self.create_profile(ctx.message.author)
        if "stats" not in self.profiles[user.id]:
            self.profiles[user.id]["stats"] = {}

        #need to parse the message again
        messStart = self.find_message_start(ctx, user, "plus1")

        #go through the keys to prevent duplicates and adjust stats accordingly
        for key in self.profiles[user.id]["stats"]:
            if key.lower() == ctx.message.content[messStart:].lower():
                self.profiles[user.id]["stats"][key] = self.profiles[user.id]["stats"][key] + 1
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`{} gets +1 to {}`".format(user.name, key))

        #create the stat if not already created
        self.profiles[user.id]["stats"][ctx.message.content[messStart:]] = 1
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return await self.bot.say("`{} gets +1 to {}`".format(user.name, ctx.message.content[messStart:]))

    @commands.command(pass_context=True)
    async def minus1(self, ctx, user : discord.Member=None):
        """Subtract a point to a stat on a given user

        Will give [user] the given stat if they didn't have it already, and then subtract 1 from it.
        This does not take your cheers points, but you may only do this once every few minutes
        """

        if not user:
            return await self.bot.say("`Need a user and a stat to subtract from`")

        #make sure the people involved have profiles
        if not self.profile_check(user.id):
            self.create_profile(user)
        if not self.profile_check(ctx.message.author.id):
            self.create_profile(ctx.message.author)
        if "stats" not in self.profiles[user.id]:
            self.profiles[user.id]["stats"] = {}

        #need to parse the message again
        messStart = self.find_message_start(ctx, user, "minus1")

        #go through the keys to prevent duplicates and adjust stats accordingly
        for key in self.profiles[user.id]["stats"]:
            if key.lower() == ctx.message.content[messStart:].lower():
                self.profiles[user.id]["stats"][key] = self.profiles[user.id]["stats"][key] - 1
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`{} subtracts 1 from {}`".format(user.name, key))

        #create the stat if not already created
        self.profiles[user.id]["stats"][ctx.message.content[messStart:]] = -1
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return await self.bot.say("`{} subtracts 1 from {}`".format(user.name, ctx.message.content[messStart:]))

    @commands.command(pass_context=True)
    async def fix1(self, ctx, user : discord.Member=None, word : str=""):
        """Allows you to update a selected quote for the given user

        [p]fix1 [user] <word> <newstat>
        Will pick the stat in [user]'s given stats with <word> in it and replace it with <newstat>
        Do not use quotes or spaces in the word key. It must be a single word or part of a word.
        """
        #first check to make sure the user exists and has quotes

        #make sure the people involved have profiles
        if not self.profile_check(user.id):
            self.create_profile(user)
            return await self.bot.say("`{} Didn't even have a profile! I have created one for them".format(user.name))
        if not self.profile_check(ctx.message.author.id):
            self.create_profile(ctx.message.author)
        if "stats" not in self.profiles[user.id]:
            self.profiles[user.id]["stats"] = {}
            return await self.bot.say("`{} Doesn't even have stats!".format(user.name))

        #get message start, add word length
        messStart = self.find_message_start(ctx, user, "fix1")

        messStart += len(word) + 1

        if messStart >= len(ctx.message.content):
            return await self.bot.say("`I can't fix a stat with nothing`")
        # add quotemarks to given quote as needed
        statStr = ctx.message.content[messStart:]

        #get keylist and check to see if they even have this stat, keeping track of case sensitivity
        keyList = list(self.profiles[user.id]["stats"].keys())
        for num in range(0, len(self.profiles[user.id]["stats"])):
            if word.lower() in keyList[num].lower():
                numInStat = self.profiles[user.id]["stats"][keyList[num]]
                del self.profiles[user.id]["stats"][keyList[num]]
                self.profiles[user.id]["stats"][ctx.message.content[messStart:]] = numInStat
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`Stat for " + user.name + " changed to`\n" + statStr)

        return await self.bot.say("`No stat containing {} found for {}`".format(word, user.name))

    @commands.command(pass_context=True)
    async def remove1(self, ctx, user : discord.Member=None, word : str=""):
        """Allows you to remove a selected stat for the given user

        [p]remove1 [user] <word>
        Will pick the stat in [user]'s stats with <word> in it and remove it
        """
        #first check to make sure the user exists and has stats
        if user is None:
            return await self.bot.say("`I need a user to remove a stat from!`")

        if not self.profile_check(user.id):
            self.create_profile(user)
            fileIO("data/ego/profiles.json", "save", self.profiles)
            return await self.bot.say("`User doesn't have a profile! I have made one for them`")
        if len(self.profiles[user.id]["stats"]) is 0:
            return await self.bot.say("`User doesn't have any stats saved!`")

        if word is "":
            return await self.bot.say("`I can't find a stat to remove without a key`")

        #get keylist and check to see if they even have this stat, keeping track of case sensitivity
        keyList = list(self.profiles[user.id]["stats"].keys())
        for num in range(0, len(self.profiles[user.id]["stats"])):
            if word.lower() in keyList[num].lower():
                del self.profiles[user.id]["stats"][keyList[num]]
                fileIO("data/ego/profiles.json", "save", self.profiles)
                return await self.bot.say("`Stat for " + user.name + " removed`\n")

        return await self.bot.say("`No stat containing {} found for {}`".format(word, user.name))

    @commands.command(pass_context=True)
    async def get1(self, ctx, user : discord.Member=None, word : str=""):
        """shows the given stat for the given user, a random stat for the given user, or a random stat for a random user

        [p]get1
        Will give a random stat from random user
        [p]get1 [user]
        Will give a random stat from the given [user]
        [p]get1 [user] <word>
        Will pick the stat in [user]'s stats with <word> in it and show how much they have in it
        """
        #with no parameters, this will select a completely random stat
        if not user:
            #randomly select a stat using weights to prevent favoring users
            totals = []
            currIndex = 0
            for userID in self.profiles.keys():
                currIndex += len(self.profiles[userID]["stats"])
                totals.append([currIndex, userID])

            # if there are no stat, there's nothing to do here
            if currIndex is 0:
                return await self.bot.say("`You have no stats saved! Use [p]plus1 [user] <stat> to add some!`")

            i = randint(0, currIndex - 1)
            temp = 0

            for num in range(0, len(totals)):
                if i < totals[num][0]:
                    index = random.choice(list(self.profiles[totals[num][1]]["stats"].keys()))
                    return await self.bot.say("`{} has {} in {}`".format( self.profiles[totals[num][1]]["name"], self.profiles[totals[num][1]]["stats"][index], index))
                temp += totals[num][0]

        if not self.profile_check(user.id):
            self.create_profile(user)
            fileIO("data/ego/profiles.json", "save", self.profiles)
            return await self.bot.say("`User doesn't have a profile! I have made one for them`")
        if len(self.profiles[user.id]["stats"]) is 0:
            return await self.bot.say("`User doesn't have any stats saved!`")

        #no word given, return a random stat from given user
        if word is "":
            randomkey = random.choice(list(self.profiles[user.id]["stats"].keys()))
            return await self.bot.say("`{} has {} in {}`".format(user.name, self.profiles[user.id]["stats"][randomkey], randomkey))

        #get keylist and check to see if they even have this stat, keeping track of case sensitivity
        keyList = list(self.profiles[user.id]["stats"].keys())
        for num in range(0, len(self.profiles[user.id]["stats"])):
            if word.lower() in keyList[num].lower():
                return await self.bot.say("`" + user.name + " has " + str(self.profiles[user.id]["stats"][keyList[num]]) + " in " + [keyList[num]] + "`\n")

        return await self.bot.say("`No stat containing {} found for {}`".format(word, user.name))

    @commands.command(pass_context=True)
    async def stats(self, ctx, user : discord.Member=None):
        """Provides Ego stats assigned to the user

        Will provide number of quotes, number of cheers point gained, cheers points remaining, and any misc. points given by other discord members"""

        if user.id in self.profiles:
            quotelist = self.profiles[user.id]["quotes"]
            message = "```{} has been cheered {} times and has a total of {} quotes attributed to them:\n".format(user.name, self.profiles[user.id]["props"], len(quotelist))
            for q in quotelist:
                message += q + "\n"
            if "stats" in self.profiles[user.id]:
                message += "\nAs for stats, {} has:\n".format(user.name)
                statlist = self.profiles[user.id]["stats"]
                for s in statlist.keys():
                    message += "{} in {}\n".format(statlist[s], s)
            message += "```"
            return await self.bot.say("{}".format(message))

        self.create_profile(user)
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return await self.bot.say("`Looks like {} doesn't have any info yet! I've created an empty profile for them.`".format(user.name))

    @commands.command(pass_context=True)
    async def quotesonly(self, ctx, user : discord.Member=None):
        """Provides all the quotes attributed to [user]"""
        if user.id in self.profiles:
            quotelist = self.profiles[user.id]["quotes"]
            message = "```{} has a total of {} quotes attributed to them:\n".format(user.name, len(quotelist))
            for q in quotelist:
                message += q + "\n"
            message += "```"
            return await self.bot.say("{}".format(message))

        self.create_profile(user)
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return await self.bot.say("`Looks like {} doesn't have any info yet! I've created an empty profile for them.`".format(user.name))

    @commands.command(pass_context=True)
    async def statsonly(self, ctx, user : discord.Member=None):
        """Provides the number of cheers and all given stats [user] has been given"""
        if user.id in self.profiles:
            message = "```{} has been cheered {} times and has these stats:\n".format(user.name, self.profiles[user.id]["props"])
            if "stats" in self.profiles[user.id]:
                statlist = self.profiles[user.id]["stats"]
                for s in statlist.keys():
                    message += "{} in {}\n".format(statlist[s], s)
            message += "```"
            return await self.bot.say("{}".format(message))

        self.create_profile(user)
        fileIO("data/ego/profiles.json", "save", self.profiles)
        return await self.bot.say("`Looks like {} doesn't have any info yet! I've created an empty profile for them.`".format(user.name))

    # Checks to see if the profile exists
    def profile_check(self, id):
        if id in self.profiles:
            return True
        else:
            return False

    # Checks to see if quotes exist in the given profiles
    def quotes_check(self, id):
        if id in self.profiles and "quotes" in self.profiles[id]:
            return True
        else:
            return False

    # Creates and saves a profile for the given user
    def create_profile(self, user):
        today = datetime.date.today()
        if user.id in self.profiles:
            return
        self.profiles[user.id] = {"name" : user.name, "cheers_points" : 3, "props" : 0, "refresh_time" : [today.day, today.month, today.year], "quotes" : [], "stats" : {}}

    # Gives the index of the start of the message in the given message after the username is called
    def find_message_start(self, ctx, user, commName):
        length = len(commName) + 3
        if str(user.id) in ctx.message.content:
            length += 3 + len(str(user.id)) 
        else:
            try:
                if user.display_name in ctx.message.content:
                    if " " in user.display_name:
                        length = ctx.message.content.find("\" ") + 2
                    else:
                        length += len(user.display_name)
                else:
                    if " " in user.name and ctx.message.content.find("\" ") != -1:
                        length = ctx.message.content.find("\" ") + 2 
                    else:
                        length += len(str(user.name))
            except:
                if " " in user.name and ctx.message.content.find("\" ") != -1:
                    length = ctx.message.content.find("\" ") + 2
                else:
                    length += len(str(user.name))

        return length


def setup(bot):
    bot.add_cog(Ego(bot))