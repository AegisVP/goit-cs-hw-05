import argparse
import asyncio
import logging
from timeit import default_timer
from pathlib import Path
from shutil import copyfile


parser = argparse.ArgumentParser(description='Search for a string in files')
parser.add_argument('--source', '-s', required=True, help="Source directory")
parser.add_argument('--destination', '-d', help="Ourput directory", default="dest")
args = parser.parse_args()

source = Path(args.source)
dest = Path(args.destination)
count = 0


async def get_folders(path):
    queue = []
    for item in path.iterdir():
        if item.is_dir():
            if item.name == dest.name: # skip the dest dir
                continue
            queue.append(get_folders(item))
        elif (item.is_file()):
            queue.append(copy_file(item))
    await asyncio.gather(*queue)


async def copy_file(file):
    global count
    output = dest / file.suffix[1:]
    try:
        output.mkdir(exist_ok=True, parents=True)
        copyfile(file, output / file.name)
        count += 1
    except Exception as e:
        logging.error(e)


async def main():
    await asyncio.sleep(0)
    await get_folders(source)
    # await asyncio.gather(*[copy_files(f) for f in folders])


if __name__ == "__main__":
    # logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.DEBUG, datefmt="%H:%M:%S")
    start = default_timer()
    asyncio.run(main())
    end = default_timer()
    print(f"Copied {count} files in {round(end - start, 6)} seconds")  # default_timer() - start)