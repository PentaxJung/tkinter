import random

number_zone = 1251
file = open('./1250auto.in', 'w', encoding='utf8')
header = 't matrices\na matrix=mf01 2016auto\n'
file.write(header)

for i in range(1, number_zone):
    for j in range(1, number_zone):
        lines = '%d ,%d ,%f\n' % (i, j, random.randint(0, 100000))
        file.write(lines)
