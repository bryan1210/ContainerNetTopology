import os

def read():
    with os.scandir("reports") as entries:
        for entry in entries:
            if entry.is_file():
                with open(entry.path) as f:
                    print(f.read())

def write():
    for i in range(10):
        with open(f"reports/{str(i)}.txt", "w") as f:
            for j in range(10):
                f.write(f"{str(j)}\n")
read()