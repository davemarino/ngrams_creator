from __future__ import absolute_import

import os
import sys
import MySQLdb
import re

class ConnectDB(object):
	"""Connect to a DB using a configuration file"""
	configurations = {}
	db = None
	cr = None

	def __init__(self, conf_file):
		try:
			conf = {}
			with open(conf_file) as f:
				for line in f.readlines():
					elems = line.strip().partition('=')
					if elems[2].isdigit():
						conf[elems[0]] = int(elems[2])
					else:
						conf[elems[0]] = elems[2]
			self.configurations = conf
		except Exception, e:
			print "error: %s" % e

	def connect(self):
		try:
			db = MySQLdb.connect(**self.configurations)
			self.db = db
			self.cr = db.cursor()
		except Exception, e:
			print "It was impossible to connect to the db."
			raise SystemExit()

class NgramsCreator(object):
	db = None
	ngrams = {}

	def __init__(self, db):
		self.db = db

	def accurate_questions(self):
		# execute query
		query = self.db.cr.execute("select query from conversation_message where accuracy=1 or accuracy=2")
		return self.db.cr.fetchall()

	def show_accurate_questions(self):
		# show results
		for row in self.accurate_questions():
			print row[0]

	def strip_word_array(self, array):
		return [w for w in array if w]

	def create_ngrams(self, n=3):
		ngrams = {}
		for row in self.accurate_questions():
			words = re.findall("[\w']*", row[0])
			words = self.strip_word_array(words)
			for i in range(0, len(words)-n+1):
				key = ""
				for j in range(0, n):
					key = key + words[i+j]
					if j != n-1:
						key = key + "-"
			if key in ngrams:
				ngrams[key] += 1
			else:
				ngrams[key] = 1
		self.ngrams = ngrams

	def print_ngrams(self):
		for k,v in self.ngrams.items():
			print "%s: %s\n" % (k, v)

if __name__ == "__main__":
	print "Connection to DB in progress..."
	db = ConnectDB('./config_db')
	db.connect()
	print "Connected to DB. Analisys in progress..."
	creator = NgramsCreator(db)
	creator.create_ngrams(n=2)
	creator.print_ngrams()
