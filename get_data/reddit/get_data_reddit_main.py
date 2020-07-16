import praw
import pprint

user_agent="testscript by /u/SwagSorcerer420_API"
reddit = praw.Reddit(user_agent=user_agent)

for submission in reddit.subreddit("all").hot(limit=25):
	print(submission.title)
