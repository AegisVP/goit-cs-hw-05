import asyncio
import aiohttp
import argparse
import re
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict


parser = argparse.ArgumentParser(description='Search for a string in files')
parser.add_argument('--url', '-u', type=str, required=True, help="URL to process")
url = (parser.parse_args()).url


def map_function(word):
    return word, 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

def map_reduce(text):
    words = text.split()

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def get_top_words(words, top=10):
    top_words = dict()
    cur_count = 0
    cur_word = None

    for _ in range(top):
        for word, count in words.items():
            count = int(count)
            # print(f"{word} - {count}")
            if word in top_words:
                continue

            if cur_count < count:    
                cur_word = word
                cur_count = count

        top_words[cur_word] = cur_count
        cur_count = 0
        cur_word = None
    return top_words

def sanitize_text(text):
    return re.sub(
        r'[^\w\s]',
        '',
        ' '.join(BeautifulSoup(text, "html.parser").stripped_strings)
    )


def visualize_top_words(words):
    fig, ax = plt.subplots()

    keys = list(words.keys())
    values = list(words.values())
    x_max = max(values)
    x_min = min(values)
    x_offset = (x_max - x_min) / 5

    ax.barh(keys, values)

    # ax.barh(words.keys(), words.values(), align='center')
    ax.set_yticks(keys, labels=keys)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_ylabel('Words')
    ax.set_xlabel('Count')
    ax.set_title('Top Most Frequent Words')

    plt.axis(xmin = x_min - x_offset, xmax = x_max + x_offset)
    plt.subplots_adjust(left=0.3)
    plt.show()
    



async def main():
    global url

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(f"Status: {resp.status}")
            if resp.status != 200:
                print(f"Error: {resp.status}")
                return
            text = sanitize_text(await resp.text())
            result = map_reduce(text)
            result = get_top_words(result)
            visualize_top_words(result)

if __name__ == "__main__":
    asyncio.run(main())