from sopel import module
import random
import markov2
import sys

#read in the swears
swears = [line.rstrip('\n').rstrip('\r') for line in open('swears.txt', 'r')]
brain = markov2.MarkovBot()

def containsswear(input):
	try:
		words = input.split()
		for word in words:
			for swear in swears:
				#i know this is gross, but input coming from irccloud seems to be
				#all unicode funky
				if str(word) == str(swear):
					return True
		return False
	except:
		return "i don't know man"

#give nahmal status to all things		
@module.commands('(.+)status')
def commandresponse(bot, trigger):
	bot.say(trigger.group(2).upper().strip() + ' NAHMAL')
	
#respond to YAH NAHMAL in any message
@module.rule('(.*)YAH NAHMAL(.*)')
def ruleresponse(bot, trigger):
	bot.say('YAH NAHMAL!')

#respond to messages to you
@module.nickname_commands('(.*)')
def nickresponse(bot, trigger):
	#check for swears
	if containsswear(trigger.group(1)):
		bot.reply("i don't know man")
	else:
		response = brain.log(trigger.group(1))
		if response == None:
			bot.reply('What?')
		else:
			bot.reply(response)
	