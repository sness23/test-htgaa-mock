#!/usr/bin/env python3

#!/usr/bin/env python3

import re

pattern = '^(\d+),(\d+): \((\d+).*$'
test_string = '38,39: (0,0,0)  #000000  black'
result = re.match(pattern, test_string)

x = result.group(1)
y = result.group(2)
a = result.group(3)

print(x)
print(y)
print(a)

if result:
  print("Search successful.")
else:
  print("Search unsuccessful.")

#with open("marilyn.txt") as file:
#    lines = [line.rstrip() for line in file]
#    print(lines)
