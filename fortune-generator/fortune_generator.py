import requests
import json
import argparse
import os


def get_top_posts(subreddit, per_request_limit, next_link=None):
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    titles = []

    querystring = {"sort": "top", "t": "all", "limit": per_request_limit}
    if next_link != None:
        querystring["after"] = next_link

    headers = {
        'User-Agent': "/u/username",
        'Accept': "*/*",
        'Host': "www.reddit.com",
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    response_dict = response.json()["data"]
    results_dict = response_dict["children"]
    for result in results_dict:
        data = f"{result['data']['title']} (r/{subreddit})"
        titles.append(data)

    return titles, response_dict["after"]


def get_all_top_posts(subreddit, total_items, per_request_limit):
    next_link = None
    titles = []
    while len(titles) < total_items:
        new_titles, next_link = get_top_posts(
            subreddit, per_request_limit, next_link=next_link)
        titles.extend(new_titles)
        print(f"Downloaded {len(titles)}/{total_items} objects", end="\r")
    print()
    return titles


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate fortunes files from subreddits..')
    parser.add_argument('--subreddit', help='name of the subreddit',
                        default='showerthoughts', type=str)
    parser.add_argument(
        '--limit', help='number of fortunes', default=10, type=int)

    args = parser.parse_args()

    subreddit = args.subreddit
    total_requested = args.limit
    per_request = 10
    titles = get_all_top_posts(subreddit, total_requested, per_request)

    with open(subreddit, "w") as f:
        print(*titles, sep="\n%\n", file=f)
    print(f"File saved as {subreddit}")
    print(f"Attempting to generate data file")
    os.system(f"strfile {subreddit} {subreddit}.dat")
    print("Data file saved... Copy both files to /usr/share/games/fortunes or similar directory")
