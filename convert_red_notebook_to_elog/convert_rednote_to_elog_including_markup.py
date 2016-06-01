#!/usr/bin/env python

import os
import codecs
import re
import cgi
from datetime import datetime
import time
import yaml
from yaml import CLoader as Loader
from tidylib import tidy_document

class Day:
    """ Parse the content for one day and turn it into a elog entry """
    def __init__(self, year, month, day, content):
        # Replace non-ascii characters with html codes
        self.text = content["text"]
        self.text_html = ""
        # Sets the entry time to 0800
        self.date = datetime(int(year), int(month), int(day), 8)
        if content.has_key("Tags"):
            self.tags = content["Tags"]

        # Variable used during the parsing
        self.list_active = False
        self.newline = '\r\n'

        self.html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            ">": "&gt;",
            "<": "&lt;",
            }

    def _html_escape(self, text):
        """Produce entities within text."""
        return "".join(self.html_escape_table.get(c,c) for c in text)

    def export(self):
        """ The export consist of:
        
        Iterate through lines to form lists
        Iterate through lines to substitute markup
        """

        # Convert the text to lines:
        lines = self.text.split("\n")
        
        for line in lines:
            # Get rid of carrige return
            l = line.rstrip("\r")
            # Escape html syntax characters
            l = self._html_escape(l)
            # Get rid of non-ascii characters
            l = l.encode("ascii", "xmlcharrefreplace")
            self.text_html += self._parse_line(l)

        if self.list_active:
            self.text_html += "</ul>" + self.newline
            self.list_active = False
        
        self.text_html = self.text_html.strip(day.newline) + '\n'
        return self.text_html

    def _parse_line(self, line):
        re_search_list = r'^( *- )(.*)$'
        ret = ""
        res = re.search(re_search_list, line)
        #print line
        try:
            list_match = res.groups()
            #print list_match
            # If the res.groups() call does not raise a exception, indent will
            # be > 1
            indent = len(list_match[0])/2
            # Output list starts and ends
            if indent > 0 and not self.list_active:
                ret += ("<ul>" + self.newline)
                self.list_active = True

            # Output list elements
            ret += "<li>{0}{1}</li>{2}".format(
                "INDENT-&gt;" * (indent - 1),
                self._replace_markup(list_match[1], True),
                self.newline
                )

        except AttributeError:
            if self.list_active:
                ret += ("</ul>" + self.newline)
                ret += self._replace_markup(line)
                self.list_active = False
            else:
                ret = self._replace_markup(line)

        #if ret == self.newline:
        #    ret = "<p>&nbsp;</p>" + self.newline
        return ret

    def _replace_markup(self, text, listitem=False):
        orig = text
        regs_full_line=[
            [r'====================', r'<hr />' + self.newline],
            [r'===(.*?)===', r'<h1>\1</h1>' + self.newline],
        ]
        for reg in regs_full_line:
            text = "{0}".format(re.sub(reg[0], reg[1], text))
        if text == orig:
            if not listitem:
                if len(text) > 0:
                    text = "<p>{0}</p>{1}".format(text, self.newline)
                else:
                    text = "<p>&nbsp;</p>{0}".format(self.newline)

        regs = [[r'\[&quot;&quot;file://(.*?)&quot;&quot;(\..{2,3})\]',
                 r'MISSINGIMAGE:\1\2'], # Images
                [r'\*\*(.*?)\*\*', r'<strong>\1</strong>'],  # Bold
                [r'//(.*?)//', r'<em>\1</em>'], # Italic
                #[r'--(.*?)--', r'<strike>\1</strike>'], # Strike through
                [r'__(.*?)__', r'<u>\1</u>'], # Underline
                ]

        for reg in regs:
            text = re.sub(reg[0], reg[1], text)

        return text

files = os.listdir(".")
# Parse the input files and

days = []
files.sort()
for f in files:
    with codecs.open(f, "rb", encoding="utf-8") as month_file:
        if f.find(os.path.basename(__file__)) < 0 and f.find('.log') < 0:
            month_content = yaml.load(month_file, Loader=Loader)

            year, month = f.rstrip(".txt").split("-")

            for day in month_content.keys():
                days.append(Day(year, month, day, month_content[day]))
        else:
            print "Skipping file: {0}".format(f)


filename = time.strftime("%y%m%d") + "a.log"

dummy_html_header = ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 "
                     "Transitional//EN\" "
                     "\"http://www.w3.org/TR/html4/loose.dtd\">\n"
                     "<html><head><title>dummy</title></head><body>")
dummy_html_footer = ("</body></html>")

err = 0

### EDIT HERE ### EDIT HERE ### EDIT HERE ###
chamber = "stm312"
### EDIT HERE ### EDIT HERE ### EDIT HERE ###

with open(filename, "w") as f:
    for n, day in enumerate(days):

        if chamber == "stm312":
            header = ("$@MID@$: {0}\n"
                      "Date: {1}\n"
                      "Headline: \n"
                      "Record date: {2}\n"
                      "Author: Import\n"
                      "Crystal: \n"
                      "Database ID: \n"
                      "Attachment: \n"
                      "Encoding: HTML\n"
                      "========================================\n")\
                      .format(n+1,
                              day.date.strftime("%a, %d %b %Y %H-%M-%S +0100"),
                              int(time.time())
                              )
        elif chamber == "microreactor":
            pass

        f.write(header)
        export = day.export()
        document, errors = tidy_document(dummy_html_header + export +
                                         dummy_html_footer)
        if len(errors) > 0:
            print errors
            err = err + 1
            print err
            print day.date.strftime("%a, %d %b %Y %H-%M-%S +0100")
            print export 
        f.write(export)
