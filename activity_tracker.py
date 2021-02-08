import praw
from datetime import datetime
from secrets import *
import pandas as pd

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
    username=username,
    password=password,
)


def retrieve_account(name: str) -> dict:
    """Get the requested praw account object and other basic info."""
    account = reddit.redditor(name)
    account_name = account.name
    post_karma = account.link_karma
    comment_karma = account.comment_karma
    current_date = datetime.now()
    return {
        "object": account,
        "account_info": (account_name, post_karma, comment_karma, current_date),
    }


def retrieve_activity(name: str) -> tuple:
    """Get the posting and commenting activity of the account for the last day."""
    account = reddit.redditor(name)
    comments = account.comments.top(time_filter="day")
    posts = account.submissions.top(time_filter="day")
    df = activity_to_df(comments, posts)
    return df


def activity_to_df(comments, posts):
    """Function to create a dataframe from the praw comments and posts sublistings."""
    activitydata = {
        "timestamp": [],
        "id": [],
        "karma": [],
        "subreddit": [],
        "submissionOP": [],
        "account_name": [],
        "type": [],
    }
    for comment in comments:
        activitydata["timestamp"].append(comment.created_utc)
        activitydata["id"].append(comment.id)
        activitydata["karma"].append(comment.score)
        activitydata["subreddit"].append(comment.subreddit.display_name)
        activitydata["submissionOP"].append(comment.is_submitter)
        activitydata["account_name"].append(comment.author.name)
        activitydata["type"].append("Comment")
    for post in posts:
        activitydata["timestamp"].append(post.created_utc)
        activitydata["id"].append(post.id)
        activitydata["karma"].append(post.score)
        activitydata["subreddit"].append(post.subreddit.display_name)
        activitydata["submissionOP"].append("NaN")
        activitydata["account_name"].append(post.author.name)
        activitydata["type"].append("Post")

    activitydf = pd.DataFrame.from_dict(
        activitydata,
    )
    return activitydf


accounts = ["mohiemen", "KingPZe"]

for account in accounts:
    user = retrieve_account(account)
    try:
        df = df.append(retrieve_activity(user["object"].name), ignore_index=True)
    except NameError:
        df = retrieve_activity(user["object"].name)
    print(df)
