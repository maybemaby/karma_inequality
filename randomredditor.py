# Module to select random redditors with certain karma values.

import praw, prawcore.exceptions
from secrets import *
import numpy as np
import random, time
import pandas as pd
from pathlib import Path

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
    username=username,
    password=password,
)


def random_redditor(count: int, min_karma: int, max_karma: int) -> pd.DataFrame:
    """Looks for random redditors within a designated karma range and organizes them.

    Inputs
    ------
    count: Number of redditors you want retrieved.
    min_karma: Minimum karma they should have.
    max_karma: Maximum karma they should have.

    Returns
    ------
    pandas.Dataframe with columns: username, karma, karma range and shape: (count,3)
    """
    array = np.zeros((count, 3))
    redditor_df = pd.DataFrame(
        array,
        columns=["username", "karma", "karma range"],
    )
    count_gen = (i for i in range(count))
    while True:
        print(redditor_df)
        rand_subreddit = reddit.subreddit("random")
        hot_posts = (x for x in rand_subreddit.hot(limit=10) if not x.stickied)
        for index, post in enumerate(hot_posts):
            author = post.author
            # Check if the user is suspended.
            if author:
                try:
                    karma = int(post.author.link_karma) + int(post.author.comment_karma)
                except prawcore.exceptions.NotFound:  # Account deleted
                    continue
                except AttributeError:  # Account suspended
                    continue
                except prawcore.exceptions.ServerError:  # Reddit server overloaded
                    time.sleep(10)
                    continue
                if (
                    (karma >= min_karma)
                    and (karma <= max_karma)
                    # Check if we already have the user.
                    and (post.author.name not in redditor_df["username"].values)
                ):
                    # Try except to check if count_gen is empty.
                    try:
                        redditor_df.iloc[next(count_gen)] = [
                            post.author.name,
                            karma,
                            f"{min_karma}-{max_karma}",
                        ]
                    except StopIteration:
                        return redditor_df


if __name__ == "__main__":
    min_karma = 50000
    max_karma = 100000
    datapoints = random_redditor(1000, min_karma, max_karma)
    datapoints.to_csv(Path.cwd() / "data" / f"redditors_{min_karma}-{max_karma}.csv")
