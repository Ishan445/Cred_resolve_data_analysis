import os
import shutil

src = r"data/raw"
dst = os.path.join("data", "raw")

if os.path.exists(src):
    if not os.path.exists("data"):
        os.makedirs("data")
    shutil.move(src, dst)
    print(f"Successfully moved {src} -> {dst}")
else:
    print(f"Source {src} does not exist. Checking {dst}: {os.path.exists(dst)}")

if os.path.exists(dst):
    files = os.listdir(dst)
    print(f"Total files in {dst}: {len(files)}")
