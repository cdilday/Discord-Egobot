import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
import datetime
import time
import aiohttp
import asyncio
import re

settings = {"POLL_DURATION" : 60}

class General:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.stopwatches = {}
        self.ball = ["As I see it, yes", "It is certain", "It is decidedly so", "Most likely", "Outlook good",
                     "Signs point to yes", "Without a doubt", "Yes", "Yes – definitely", "You may rely on it", "Reply hazy, try again",
                     "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
        self.poll_sessions = []

    @commands.command(hidden=True)
    async def ping(self):
        """Pong."""
        await self.bot.say("Pong.")

    @commands.command()
    async def choose(self, *choices):
        """Chooses between multiple choices.

        To denote multiple choices, you should use double quotes.
        """
        if len(choices) < 2:
            await self.bot.say('Not enough choices to pick from.')
        else:
            await self.bot.say(randchoice(choices))

    @commands.command(pass_context=True)
    async def roll(self, ctx, inputString : str = ""):
        """Rolls random number (between 1 and user choice)

        Defaults to 100.

        To roll and sum multiple dice at once, type #d# and any modifiers you want after it
        Ex: roll 5d6 + 5 - 8 will roll 5 six-sided dice, add 5 to the result, and subtract 7 from that
        Supports +, -, *, /, and modulo modifiers
        """
        author = ctx.message.author
        #format content to accept spaces
        if len(ctx.message.content) > 5:
            inputString = ctx.message.content[5:]
            while inputString[0] is ' ':
                inputString = inputString[1:]

        #standar roll 100 if they just roll
        if len(inputString) is 0:
            n = str(randint(1, 100))
            return await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, n))
        else:
            allNums = list(map(int, re.findall(r'\d+', inputString)))
            if len(allNums) is 0:
                n = str(randint(1, 100))
                return await self.bot.say("{} You didn't put any numbers so I'm going to just roll 100 :game_die: {} :game_die:".format(author.mention, n))
            elif len(allNums) is 1:
                n = str(randint(1, allNums[0]))
                return await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, n))
            else:
                #get each component of the command to parse accordingly
                components = []
                while len(inputString) > 0:
                    if inputString[0].isdigit():
                        n = list(map(int, re.findall(r'\d+', inputString)))[0]
                        components.append(n)
                        inputString = inputString[len(str(n)):]
                    elif inputString[0] in ['d','+','-','*','/','%']:
                        components += inputString[0]
                        inputString = inputString[1:]
                    else:
                        inputString = inputString[1:]

                results = ""
                total = 0
                # edge case: if they chose to not say d but still want to do math, roll the first number
                if 'd' not in components:
                    if isinstance(components[0], int ):
                        if components[0] < 1:
                            return await self.bot.say("{} Can't roll less than 1, that's not how dice work".format(author.mention))
                        n = randint(1, components[0])
                        results += str(n)
                        total += n
                for i in range(0, len(components)):
                    if components[i] is 'd':
                        numrolls = 1
                        diesize = 100
                        if i is not 0 and isinstance(components[i-1], int ):
                            numrolls = components[i-1]
                        if i + 1 < len(components) and isinstance(components[i+1], int ):
                            diesize = components[i+1]
                        else:
                            return await self.bot.say("Cannot roll; number of sides not specified (<number of dice>d<number of sides>)")
                        
                        for j in range(0, numrolls):
                            n = randint(1, diesize)
                            total += n;
                            results += str(n)
                            if j is not numrolls - 1:
                                results += " + "
                            elif numrolls is not 1:
                                results += " = " + str(total)

                    elif components[i] is'+':
                        if i + 1 < len(components) and isinstance(components[i+1], int ):
                            results += " + {} = {}".format(str(components[i+1]), str(total + components[i+1]))
                            total += components[i+1]
                        else:
                            return await self.bot.say("Cannot roll; no number to add after +")
                    elif components[i] is'-':
                        if i + 1 < len(components) and isinstance(components[i+1], int ):
                            results += " - {} = {}".format(str(components[i+1]), str(total - components[i+1]))
                            total -= components[i+1]
                        else:
                            return await self.bot.say("Cannot roll; no number to subtract with after -")
                    elif components[i] is'*':
                        if i + 1 < len(components) and isinstance(components[i+1], int ):
                            results += " * {} = {}".format(str(components[i+1]), str(total * components[i+1]))
                            total *= components[i+1]
                        else:
                            return await self.bot.say("Cannot roll; no number to multiply by after *")
                    elif components[i] is'/':
                        if i + 1 < len(components) and isinstance(components[i+1], int ):
                            results += " / {} = {}".format(str(components[i+1]), str(total / components[i+1]))
                            total /= components[i+1]
                        else:
                            return await self.bot.say("Cannot roll; no number to divide by after /")
                    elif components[i] is'%':
                        if i + 1 < len(components) and isinstance(components[i+1], int ):
                            results += " % {} = {}".format(str(components[i+1]), str(total % components[i+1]))
                            total %= components[i+1]
                        else:
                            return await self.bot.say("Cannot roll; no number to modulo with")

                return await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, results))

    @commands.command(pass_context=True)
    async def flip(self, ctx, user : discord.Member=None):
        """Flips a coin... or a user.

        Defaults to coin.
        """
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = "Nice try. You think this is funny? How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            return await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            return await self.bot.say("*flips a coin and... " + randchoice(["HEADS!*", "TAILS!*"]))

    @commands.command(pass_context=True)
    async def rps(self, ctx, choice : str):
        """Play rock paper scissors"""
        author = ctx.message.author
        rpsbot = {"rock" : ":moyai:",
           "paper": ":page_facing_up:",
           "scissors":":scissors:"}
        choice = choice.lower()
        if choice in rpsbot.keys():
            botchoice = randchoice(list(rpsbot.keys()))
            msgs = {
                "win": " You win {}!".format(author.mention),
                "square": " We're square {}!".format(author.mention),
                "lose": " You lose {}!".format(author.mention)
            }
            if choice == botchoice:
                await self.bot.say(rpsbot[botchoice] + msgs["square"])
            elif choice == "rock" and botchoice == "paper":
                await self.bot.say(rpsbot[botchoice] + msgs["lose"])
            elif choice == "rock" and botchoice == "scissors":
                await self.bot.say(rpsbot[botchoice] + msgs["win"])
            elif choice == "paper" and botchoice == "rock":
                await self.bot.say(rpsbot[botchoice] + msgs["win"])
            elif choice == "paper" and botchoice == "scissors":
                await self.bot.say(rpsbot[botchoice] + msgs["lose"])
            elif choice == "scissors" and botchoice == "rock":
                await self.bot.say(rpsbot[botchoice] + msgs["lose"])
            elif choice == "scissors" and botchoice == "paper":
                await self.bot.say(rpsbot[botchoice] + msgs["win"])
        else:
            await self.bot.say("Choose rock, paper or scissors.")

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, *question):
        """Ask 8 ball a question

        Question must end with a question mark.
        """
        question = " ".join(question)
        if question.endswith("?") and question != "?":
            return await self.bot.say("`" + randchoice(self.ball) + "`")
        else:
            return await self.bot.say("That doesn't look like a question.")

    @commands.command(aliases=["sw"], pass_context=True)
    async def stopwatch(self, ctx):
        """Starts/stops stopwatch"""
        author = ctx.message.author
        if not author.id in self.stopwatches:
            self.stopwatches[author.id] = int(time.perf_counter())
            await self.bot.say(author.mention + " Stopwatch started!")
        else:
            tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
            tmp = str(datetime.timedelta(seconds=tmp))
            await self.bot.say(author.mention + " Stopwatch stopped! Time: **" + str(tmp) + "**")
            self.stopwatches.pop(author.id, None)

    @commands.command()
    async def lmgtfy(self, *text):
        """Creates a lmgtfy link"""
        if text == ():
            await self.bot.say("lmgtfy [search terms]")
            return
        text = "+".join(text)
        await self.bot.say("http://lmgtfy.com/?q=" + text)

    @commands.command(no_pm=True, hidden=True)
    async def hug(self, user : discord.Member, intensity : int=1):
        """Because everyone likes hugs

        Up to 10 intensity levels."""
        name = " *" + user.name + "*"
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ" + name + " ⊂(´・ω・｀⊂)"
        await self.bot.say(msg)

    @commands.command(pass_context=True, no_pm=True)
    async def info(self, ctx, user : discord.Member = None):
        """Shows users's informations"""
        author = ctx.message.author
        if not user:
            user = author
        roles = []
        for m in user.roles:
            if m.name != "@everyone":
                roles.append('"' + m.name + '"') #.replace("@", "@\u200b")
        if not roles: roles = ["None"]
        data = "```python\n"
        data += "Name: " + user.name + "#{}\n".format(user.discriminator)
        data += "ID: " + user.id + "\n"
        data += "Created: " + str(user.created_at) + "\n"
        data += "Joined: " + str(user.joined_at) + "\n"
        data += "Roles: " + " ".join(roles) + "\n"
        data += "Avatar: " + user.avatar_url + "\n"
        data += "```"
        await self.bot.say(data)

    @commands.command(pass_context=True, no_pm=True)
    async def server(self, ctx):
        """Shows server's informations"""
        server = ctx.message.server
        online = str(len([m.status for m in server.members if str(m.status) == "online" or str(m.status) == "idle"]))
        total = str(len(server.members))

        data = "```\n"
        data += "Name: {}\n".format(server.name)
        data += "ID: {}\n".format(server.id)
        data += "Region: {}\n".format(str(server.region))
        data += "Users: {}/{}\n".format(online, total)
        data += "Channels: {}\n".format(str(len(server.channels)))
        data += "Roles: {}\n".format(str(len(server.roles)))
        data += "Created: {}\n".format(str(server.created_at))
        data += "Owner: {}#{}\n".format(server.owner.name, server.owner.discriminator)
        data += "Icon: {}\n".format(server.icon_url)
        data += "```"
        await self.bot.say(data)
        
    @commands.command()
    async def urban(self, *, search_terms : str):
        """Urban Dictionary search"""
        search_terms = search_terms.split(" ")
        search_terms = "+".join(search_terms)
        search = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.get(search) as r:
                result = await r.json()
            if result["list"] != []:
                definition = result['list'][0]['definition']
                example = result['list'][0]['example']
                await self.bot.say("**Definition:** " + definition + "\n\n" + "**Example:** " + example )
            else:
                await self.bot.say("Your search terms gave no results.")
        except:
            await self.bot.say("Error.")

    @commands.command(pass_context=True, no_pm=True)
    async def poll(self, ctx, *text):
        """Starts/stops a poll

        Usage example:
        poll Is this a poll?;Yes;No;Maybe
        poll stop"""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await self.bot.say("Nice try.")
                return
            p = NewPoll(message, self)
            if p.valid:
                self.poll_sessions.append(p)
                await p.start()
            else:
                await self.bot.say("poll question;option1;option2 (...)")
        else:
            await self.bot.say("A poll is already ongoing in this channel.")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id: # or isMemberAdmin(message)
                await self.getPollByChannel(message).endPoll()
            else:
                await self.bot.say("Only admins and the author can stop the poll.")
        else:
            await self.bot.say("There's no poll ongoing in this channel.")

    def getPollByChannel(self, message):
        for poll in self.poll_sessions:
            if poll.channel == message.channel:
                return poll
        return False

    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                    self.getPollByChannel(message).checkAnswer(message)


class NewPoll():
    def __init__(self, message, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_sessions = main.poll_sessions
        msg = message.content[6:]
        msg = msg.split(";")
        if len(msg) < 2: # Needs at least one question and 2 choices
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = []
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}
        i = 1
        for answer in msg: # {id : {answer, votes}}
            self.answers[i] = {"ANSWER" : answer, "VOTES" : 0}
            i += 1

    async def start(self):
        msg = "**POLL STARTED!**\n\n{}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "{}. *{}*\n".format(id, data["ANSWER"])
        msg += "\nType the number to vote!"
        await self.client.send_message(self.channel, msg)
        await asyncio.sleep(settings["POLL_DURATION"])
        if self.valid:
            await self.endPoll()

    async def endPoll(self):
        self.valid = False
        msg = "**POLL ENDED!**\n\n{}\n\n".format(self.question)
        for data in self.answers.values():
            msg += "*{}* - {} votes\n".format(data["ANSWER"], str(data["VOTES"]))
        await self.client.send_message(self.channel, msg)
        self.poll_sessions.remove(self)

    def checkAnswer(self, message):
        try:
            i = int(message.content)
            if i in self.answers.keys():
                if message.author.id not in self.already_voted:
                    data = self.answers[i]
                    data["VOTES"] += 1
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass


def setup(bot):
    n = General(bot)
    bot.add_listener(n.check_poll_votes, "on_message")
    bot.add_cog(n)
