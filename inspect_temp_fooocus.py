import os, glob

temp_dir = r"C:\Users\nstra\AppData\Local\Temp\fooocus"
pngs = glob.glob(os.path.join(temp_dir, "**", "*.png"), recursive=True)
print(f"Total generated PNG files in Fooocus temp dir: {len(pngs)}")
for p in sorted(pngs, key=os.path.getmtime, reverse=True)[:5]:
    print(f" - {p} | size = {os.path.getsize(p)} bytes | mtime = {os.path.getmtime(p)}")
