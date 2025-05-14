
from includes import *

data = []

row1 = {}
row1["one"] = "ichi"
row1["two"] = "ni"
row1["three"] = "san"

row2 = {}
row2["zero"] = "nol"
row2["one"] = "odin"
row2["two"] = "dva"

row3 = {}
row3["two"] = "ar"

data.append(row1)
data.append(row2)
# data.append(row3)

print(data)
print()
res = show_map_table(data)
print(res)



