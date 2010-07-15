#!/usr/bin/python

# Debug messaging
import cgitb
cgitb.enable()

import cgi

from string import Template

from whoosh.index import open_dir

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

    index = open_dir("indexes/actionchix")

    searcher = index.searcher()

    f = searcher.find("body", unicode(query))

    result = ""

    for k in f:
        result = result +
                 '<p><a target="mail" href="http://localhost/pipermail/actionchix/' +
                 k["period"] +
                 '/' +
                 k["filename"] +
                 '"><b>' +
                 k["subject"] +
                 '</b> - ' +
                 k["author"] +
                 '</a></p><hr/>'


    showForm(query, result)


if __name__ == "__main__":
    printHeaders()

    main()
