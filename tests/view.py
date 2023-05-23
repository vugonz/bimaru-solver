import sys

def print_table(table, rows, col):
    res = ""
    i = 0
    for row in table:
        for cell in row:
            res += f"{cell} "
        res += f" {rows[i]}\n"
        i += 1

    for val in col:
        res += f"{val} "

    return res

row, col, _, *hints = sys.stdin.readlines()

row = list(map(int, row.split()[1:]))
col = list(map(int, col.split()[1:]))

table = [["." for _ in range(10)] for _ in range(10)] 

for hint in hints:
    x, y, z = hint.split()[1:]
    table[int(x)][int(y)] = z

print(print_table(table, row, col))
