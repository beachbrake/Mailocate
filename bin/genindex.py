#!/usr/bin/env python

import os
import re
import sys
import pprint
import pickle
import marshal

sys.path.append("/var/lib/mailman")

from Mailman.Archiver import HyperArch
import Mailman

from whoosh.index import create_in
from whoosh.fields import *

from htmlentitydefs import name2codepoint

class progressBar:
	def __init__(self, minValue = 0, maxValue = 10, totalWidth=12):
		self.progBar = "[]"   # This holds the progress bar string
		self.min = minValue
		self.max = maxValue
		self.span = maxValue - minValue
		self.width = totalWidth
		self.amount = 0       # When amount == max, we are 100% done
		self.updateAmount(0)  # Build progress bar string

	def updateAmount(self, newAmount = 0):
		if newAmount < self.min: newAmount = self.min
		if newAmount > self.max: newAmount = self.max
		self.amount = newAmount

		# Figure out the new percent done, round to an integer
		diffFromMin = float(self.amount - self.min)
		percentDone = (diffFromMin / float(self.span)) * 100.0
		percentDone = round(percentDone)
		percentDone = int(percentDone)

		# Figure out how many hash bars the percentage should be
		allFull = self.width - 2
		numHashes = (percentDone / 100.0) * allFull
		numHashes = int(round(numHashes))

		# build a progress bar with hashes and spaces
		self.progBar = "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"

		# figure out where to put the percentage, roughly centered
		percentPlace = (len(self.progBar) / 2) - len(str(percentDone))
		percentString = str(percentDone) + "%"

		# slice the percentage into the bar
		self.progBar = self.progBar[0:percentPlace] + percentString + self.progBar[percentPlace+len(percentString):]

	def __str__(self):
		return str(self.progBar)



def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)


def openArticleFile(listPath, article):

    fp = open(listPath + "/database/" + article)
    d = marshal.load(fp)

    return d


def main(listName):

    listPath = "/var/lib/mailman/archives/private/" + listName

    if not os.path.isdir(listPath):
        print "Archives not found! Make sure the list exists."
        sys.exit()

    print "Generating search index for " + listName
    print

    archives = os.listdir(listPath + "/database/")

    i = 0

    prog = progressBar(0, len(archives), 77)

    schema = Schema(msgid=TEXT(stored=True),
                    author=TEXT(stored=True),
                    date=TEXT(stored=True),
                    email=TEXT(stored=True),
                    subject=TEXT(stored=True),
                    body=TEXT(stored=True),
                    filename=TEXT(stored=True),
                    period=TEXT(stored=True))

    os.mkdir(listName)

    ix = create_in(listName, schema)


    writer = ix.writer()

    for a in archives:
        if a.endswith("article"):
            d = openArticleFile(listPath, a)

            period = a.replace("-article", "")

            article = {}

            for entry in d:
                f = pickle.loads(d[entry])

                #print f.sequence
                #print f.subject
                #print f.datestr
                #print f.date
                #print f.headers
                #print f.author
                #print f.email
                #print f.msgid
                #print f.in_reply_to
                #print f.references
                #print "Body = "
                #print f.body
                #print f.filename

                html = open(listPath + "/" + period + "/" + f.filename, "r").read()

                r = re.findall(r"<!--beginarticle-->.*<!--endarticle-->", html, re.DOTALL)[0]

                r = r.replace("<!--beginarticle-->", "")
                r = r.replace("<!--endarticle-->", "")

                p = re.compile(r'<.*?>')
                r = p.sub('', r)

                #print unescape(r)

                article["msgid"] = f.msgid
                article["author"] = f.author
                article["date"] = f.date
                article["email"] = f.email
                article["subject"] = f.subject
                article["body"] = r
                article["filename"] = f.filename

                writer.add_document(msgid=unicode(f.msgid),
                                    author=unicode(f.author),
                                    date=unicode(f.date),
                                    email=unicode(f.email),
                                    subject=unicode(f.subject),
                                    body=unicode(r),
                                    filename=unicode(f.filename),
                                    period=unicode(period))

            prog.updateAmount(i)
            print prog, "\r",

        i = i + 1

    writer.commit()

    print
    print
    print "Search Index Generated!"

    print i


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:"
        print "    " + sys.argv[0] + " listname"
        sys.exit()

    main(sys.argv[1])
