with open("game/hs.txt", "r") as f:
    hs = int(f.read())

print(hs)

with open("game/hs.txt", "w") as f:
    f.write(f"{hs+1}")



