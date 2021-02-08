import praw
from datetime import datetime
from secrets import *
import pandas as pd
from pathlib import Path

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
        "timestamp (UTC)": [],
        "id": [],
        "karma": [],
        "subreddit": [],
        "submissionOP": [],
        "account_name": [],
        "type": [],
    }
    for comment in comments:
        activitydata["timestamp (UTC)"].append(comment.created_utc)
        activitydata["id"].append(comment.id)
        activitydata["karma"].append(comment.score)
        activitydata["subreddit"].append(comment.subreddit.display_name)
        activitydata["submissionOP"].append(comment.is_submitter)
        activitydata["account_name"].append(comment.author.name)
        activitydata["type"].append("Comment")
    for post in posts:
        activitydata["timestamp (UTC)"].append(post.created_utc)
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


def save_to_pickle(activitydf: pd.DataFrame, karmadf: pd.DataFrame):
    """Save given pandas dataframe args to a pickle file in data directory."""
    check = input(
        "Are you sure you would like to save the pkl files? (overwrites existing files) (Y/N)"
    )
    if check == "Y":
        activitydf.to_pickle(Path.cwd() / "data" / "activity_data.pkl")
        karmadf.to_pickle(Path.cwd() / "data" / "karmatracker.pkl")
    else:
        return


def save_to_csv(activitydf: pd.DataFrame, karmadf: pd.DataFrame):
    """Save given pandas dataframe args to a csv file in data directory."""
    check = input(
        "Are you sure you would like to save the csv files? (overwrites existing files) (Y/N)"
    )
    if check == "Y":
        activitydf.to_csv(Path.cwd() / "data" / "activity_data.csv")
        karmadf.to_csv(Path.cwd() / "data" / "karmatracker.csv")
    else:
        return


def update_pickle(activitydf: pd.DataFrame, karmadf: pd.DataFrame):
    """Update existing pickle files with new dataframes."""
    activitydf_0 = pd.read_pickle(Path.cwd() / "data" / "activity_data.pkl")
    karmadf_0 = pd.read_pickle(Path.cwd() / "data" / "karmatracker.pkl")
    activitydf_0.append(activitydf, ignore_index=True)
    karmadf_0.append(karmadf, ignore_index=True)
    check = input("Are you sure you would like to update the pkl files? (Y/N)")
    if check == "Y":
        activitydf_0.to_pickle(Path.cwd() / "data" / "activity_data.pkl")
        karmadf_0.to_pickle(Path.cwd() / "data" / "karmatracker.pkl")
    else:
        return


def update_csv(activitydf: pd.DataFrame, karmadf: pd.DataFrame):
    """Update exisiting csv files with new dataframes."""
    activitydf_0 = pd.read_csv(Path.cwd() / "data" / "activity_data.csv", index_col=0)
    karmadf_0 = pd.read_csv(Path.cwd() / "data" / "karmatracker.csv", index_col=0)
    activitydf_0 = activitydf_0.append(activitydf, ignore_index=True)
    karma_df_0 = karmadf_0.append(karmadf, ignore_index=True)
    check = input("Are you sure you would like to update the csv files? (Y/N)")
    if check == "Y":
        activitydf_0.to_csv(Path.cwd() / "data" / "activity_data.csv")
        karmadf_0.to_csv(Path.cwd() / "data" / "karmatracker.csv")
    else:
        return


if __name__ == "__main__":
    # accounts = ["mohiemen", "KingPZe"]
    accounts = ["orchid_breeder", "DurovCode"]
    user_info = []
    for account in accounts:
        user = retrieve_account(account)
        user_info.append(user["account_info"])
        try:
            activitydf = activitydf.append(
                retrieve_activity(user["object"].name), ignore_index=True
            )
        except NameError:
            activitydf = retrieve_activity(user["object"].name)
    karmadf = pd.DataFrame(
        user_info, columns=["account_name", "post_karma", "comment_karma", "timestamp"]
    )
    print(activitydf)
    print(karmadf)

    # Only uncomment these commands when you are first saving or you want to overwrite old files.
    # save_to_pickle(activitydf, karmadf)
    # save_to_csv(activitydf, karmadf)

    # Functions to update existing files.
    # update_pickle(activitydf, karmadf)
    # update_csv(activitydf, karmadf)
