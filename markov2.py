#!/usr/bin/python

#adapted from
#https://github.com/coleifer/irc/blob/master/bots/markov.py

import os
import pickle
import random
import re
import sys


class MarkovBot():
    messages_to_generate = 15
    max_words = 50
    chain_length = 2
    stop_word = '\n'
    filename = 'markov.db'
    last = None 
    
    def __init__(self, *args, **kwargs):
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            fh = open(self.filename, 'rb')
            self.word_table = pickle.loads(fh.read())
            fh.close()
        else:
            self.word_table = {}
    
    def save_data(self):
        fh = open(self.filename, 'wb')
        fh.write(pickle.dumps(self.word_table))
        fh.close()

    def split_message(self, message):
        words = message.split()
        if len(words) > self.chain_length:
            words.extend([self.stop_word] * self.chain_length)
            for i in range(len(words) - self.chain_length):
                yield (words[i:i + self.chain_length + 1])

    def generate_message(self, size=15, seed_key=None):
        if not seed_key:
            seed_key = random.choice(self.word_table.keys())
			
        message = []
        for i in xrange(self.messages_to_generate):
            words = seed_key
            gen_words = []
            for i in xrange(size):
                if words[0] == self.stop_word:
                    break

                gen_words.append(words[0])
                try:
                    words = words[1:] + (random.choice(self.word_table[words]),)
                except KeyError:
                    break

            if len(gen_words) > len(message):
                message = list(gen_words)
        
        return ' '.join(message)

    def imitate(self, sender, message, channel):
        person = message.replace('imitate ', '').strip()[:10]
        if person != self.conn.nick:
            return self.generate_message(person)

    def cite(self, sender, message, channel):
        if self.last:
            return self.last
    
    def sanitize_message(self, message):
        """Convert to lower-case and strip out all quotation marks"""
        return re.sub('[\"\']', '', message.lower())

    def log(self, message):
        if message.startswith('/'):
            return
		
        say_something = True
        messages = []
        seed_key = None
        best_message = ''
        for words in self.split_message(self.sanitize_message(message)):
            key = tuple(words[:-1])
            if key in self.word_table:
                self.word_table[key].append(words[-1])
            else:
                self.word_table[key] = [words[-1]]

            if(key in self.word_table):
                generated = self.generate_message(seed_key=key)
                if len(generated) > len(best_message):
                    best_message = generated
                #if generated:
                #    messages.append(generated)
				
        if len(best_message):
            self.save_data()
            #message = random.choice(messages)
            return best_message


    def load_log_file(self, filename):
        fh = open(filename, 'r')
        logline_re = re.compile('<\s*(\w+)>[^\]]+\]\s([^\r\n]+)[\r\n]')
        for line in fh.readlines():
            match = logline_re.search(line)
            if match:
                sender, message = match.groups()
                self.log(sender, message, '', False, None)

    def load_text_file(self, filename, sender):
        fh = open(filename, 'r')
        for line in fh.readlines():
            self.log(sender, line, '', False, None)
    
    def command_patterns(self):
        return (
            self.ping('^imitate \S+', self.imitate),
            self.ping('^cite', self.cite),
            ('.*', self.log),
        )