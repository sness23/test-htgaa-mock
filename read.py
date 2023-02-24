#!/usr/bin/env python3

import re

pattern = '^(\d+),(\d+): \(([0-9.]+).*$'

with open("marilyn.txt") as file:
    lines = [line.rstrip() for line in file]

coords = []
for line in lines:
    result = re.match(pattern, line)

    if result:
        x = result.group(1)
        y = result.group(2)
        a = result.group(3)
        coords.append([x,y,a])

print(coords)
