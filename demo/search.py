#!/usr/bin/python

# Debug messaging
import cgitb
cgitb.enable()

import cgi

import sys

from string import Template


sys.path.append("/usr/lib/mailman")

from whoosh.lang.porter import stem

from Mailman import mm_cfg
from Mailman import Utils
from Mailman import MailList
from Mailman import Errors
from Mailman import i18n
from Mailman.htmlformat import *
from Mailman.Logging.Syslog import syslog

from Mailman.Searcher import Mailocate


# Set up i18n
_ = i18n._
i18n.set_language(mm_cfg.DEFAULT_SERVER_LANGUAGE)


def printHeaders():
    # Required header that tells the browser how to render the text.
    print "Content-Type: text/html"
    # One blank line
    print


def showForm(search_string, results):
    formHTML = Template(open("form.html", "r").read())

    print formHTML.substitute(search_string=search_string, results=results)


def fetchResults():
    pass


def main():
    form = cgi.FieldStorage()

    if "q" not in form:
        showForm("", "<p>Type keywords in the search box and hit enter</p>")
        return

    query = form["q"].value

    mailocate = Mailocate.Mailocate("/var/lib/mailman/archives/private/actionchix/actionchix.index")
    
    f = mailocate.search(query)
        
    result = ""
    
    # print f
    
    if len(f['documents']) == 0:
        result = "<p>No Results found.<br /><br />"
        
        result += "Did you mean: <br />"
        
        result += '<a href="search.py?q='
        
        if (f['search_mode'] == "author") or (f['search_mode'] == "subject"):
            result += f['search_mode'] + ":"
        
        for word in f['base_string'].split(' '):
            if word in f['spelling']:
                if len(f['spelling'][word]):
                    result += f['spelling'][word][0]
                    result += '+'
                else:
                    result += word
                    result += '+'
            else:
                result += word
                result += '+'
            
        result = result[0:(len(result)-1)]
        
        result += '">'
 
        if (f['search_mode'] == "author") or (f['search_mode'] == "subject"):
            result += f['search_mode'] + ":"                   
 
        for word in f['base_string'].split(' '):
            if word in f['spelling']:
                if len(f['spelling'][word]):
                    result += '<b>' + f['spelling'][word][0] + '</b>'
                    result += ' '
                else:
                    result += word
                    result += ' '
            else:
                result += word
                result += ' '


        result = result[0:(len(result)-1)]
            
        result += '</a></p>'
       
        
    else:
        for k in f['documents']:
            result += '<p><a target="mail" '
            result += 'href="http://localhost/pipermail/actionchix/'
            result += k["period"] + '/' + k["filename"] +'"><b>'+k["subject"]
            result += '</b></a> - <span class="author">' + k['author'] + '</span>'
            result += '</p>'
            result += '<p class="body">' + k['unstemmed_body'][0:100] + ' ...</p>'
            result += '<hr/>\n'
           
    query = query.replace('"', '&quot;')
    
    showForm(query, result)

    if len(f['documents']) == 0:
        print "DEBUG: "
        print f

if __name__ == "__main__":
    printHeaders()

    main()
