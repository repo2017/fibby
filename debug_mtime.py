import time, glob, os, re

start_time = time.time()
print("start_time:", start_time)

OUTPUT_SEARCH_DIRS = [
    r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\Fooocus\outputs",
    r"C:\Users\nstra\AppData\Local\Temp\fooocus"
]

for s_dir in OUTPUT_SEARCH_DIRS:
    pngs = glob.glob(os.path.join(s_dir, "**", "*.png"), recursive=True)
    for p in pngs:
        filename = os.path.basename(p)
        mtime = os.path.getmtime(p)
        if re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', filename):
            print(f"File: {filename} | mtime: {mtime} | mtime >= start_time-5: {mtime >= start_time - 5} | size: {os.path.getsize(p)}")
