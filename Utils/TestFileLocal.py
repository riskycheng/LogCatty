filename = 'c:/test/logsTest.txt'

data = []
num_lines = 0
with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        num_lines += 1
        data.append(line)

print('file loading done with lines:', num_lines)

# crop slides of the array
print('line 100,0000 to line 100,1000')
for line in data[1000000: 1001000]:
    print(line)
