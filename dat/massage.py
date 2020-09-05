#!/usr/bin/env python3

import dataset

TIP_TYPES = {"text": 0, "snippet": 1}

db = dataset.connect("sqlite:///tips.db")

contents = ""
with open("tips.txt") as f:
    contents = f.read()

db.begin()

line_i = 0
lines = contents.split("\n")
while line_i < len(lines):
    line = lines[line_i]
    if len(line) < 1:
        line_i += 1
        continue

    if line[0] == "\t":
        description = lines[line_i + 1]
        snippet = line[1:]
        db["tips"].insert(
            dict(
                date=0,
                author_nick=None,
                author_account=None,
                author_username="Vim Tips Wiki",
                tiptype=TIP_TYPES["snippet"],
                snippet=snippet,
                snippet_desc=description,
            )
        )
        line_i += 1
    else:
        db["tips"].insert(
            dict(
                date=0,
                author_nick=None,
                author_account=None,
                author_username="Vim Tips Wiki",
                tiptype=TIP_TYPES["text"],
                text=line,
            )
        )
    line_i += 1

db.commit()
