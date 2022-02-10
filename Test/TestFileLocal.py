import re

filename = 'H:/test/huge_logFiles/logs_short.txt'

data = []
num_lines = 0
# non-space but not including \n
pattern = re.compile(r'[^\S\x0a\x0d]')
with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        num_lines += 1
        data.append(pattern.sub('\t', line))

print('file loading done with lines:', num_lines)

# crop slides of the array
for line in data:
    print(line)