#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import os
import codecs
import re
from datetime import datetime
import time
from operator import attrgetter
import yaml
from yaml import CLoader as Loader

class Day:
    """ Parse the content for one day and turn it into a elog entry """
    def __init__(self, year, month, day, content):
        # Get text and replace a invalid ISO-8859-1 char
        self.text = content["text"]
        self.text = self.text.replace("⁻", "-")
        # Test decoding
        try:
            self.text.encode("ISO-8859-1")
        except Exception:
            print("Cannot encode as ISO-8859-1")
            raise

        # Set time to 08:00
        self.date = datetime(int(year), int(month), int(day), 8)
        print("Day", self.date)
        self.techniques = []
        self.operator = None
        self._extract_details()
        self._replace_missing_items()

    def _extract_details(self):
        """Extract details"""
        if self.date > datetime(2012, 1, 1):
            self.operator = "Elisabeth Ulrikkeholm"
        else:
            self.operator = "Tobias Johansson"

        technique_defs = (
            ("xps", "XPS"),
            ("iss", "ISS"),
            ("tpd", "TPD"),
            ("plasma", "Plasma"),
            ("leed", "LEED"),
            ("deposition", "Deposition"),
        )

        for search_string, name in technique_defs:
            if search_string in self.text.lower():
                self.techniques.append(name)

        #print("Techniques:", self.techniques)


    def _replace_missing_items(self):
        """Replace images syntax"""
        image_re = r'\[""file:///(.*?)""(\..{2,3})\]'
        image_re_replace = r'MISSINGIMAGE:\1\2'
        if re.search(image_re, self.text):
            self.text = re.sub(image_re, image_re_replace, self.text)
            print("Replaced image in", self.date)

    def export(self):
        """Export text and metadata"""
        metadata = {
            'user': self.operator,
            'technique': ' | '.join(self.techniques),
        }
        return self.text, metadata


files = os.listdir("labbook/")
# Parse the input files and

days = []
files.sort()
for f in files:
    with codecs.open("labbook/" + f, "rb", encoding="utf-8") as month_file:
        if f.find(os.path.basename(__file__)) < 0 and f.find('.log') < 0:
            month_content = yaml.load(month_file, Loader=Loader)

            year, month = f.rstrip(".txt").split("-")

            for day in month_content.keys():
                days.append(Day(year, month, day, month_content[day]))
        else:
            print("Skipping file: {0}".format(f))

print("Parsed {} days".format(len(days)))

# Technique: XPS | TPD
# ISO-8859-1


# Sort the days
sortkey = attrgetter('date')
days_sorted = sorted(days, key=sortkey)

last = days[0]
for lower, upper in zip(days_sorted[:-1], days_sorted[1:]):
    assert lower.date < upper.date

current_file = 'None'

for n, day in enumerate(days_sorted):
    filename = day.date.strftime("%y%m%d") + "a.log"
    if filename != current_file:
        f = codecs.open('output/' + filename, "w", encoding='ISO-8859-1')
        current_file = filename

    data = {
        "number": n + 1,
        "record_date": int(time.mktime(day.date.timetuple())),
        "date": time.strftime("%a, %d %b %Y %H:%M:%S +0100"),
    }

    # strftime("%a, %d %b %Y %H:%M:%S +0100"),

    text, metadata = day.export()
    data.update(metadata)

    header = ("$@MID@$: {number}\n"
              "Date: {date}\n"
              "Record date: {record_date}\n"
              "Technique: {technique}\n"
              "Sample: Unknown\n"
              "User: {user}\n"
              "Attachment: \n"
              "Encoding: plain\n"
              "========================================\n")
    header = header.format(**data)
    #print("### HEADER\n", header, "\n### HEADER\n", sep="")
    f.write(header)
    f.write(text)


f.close()
