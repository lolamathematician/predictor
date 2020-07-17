import praw
from datetime import datetime

def utc_timestamp_to_datetime_string(utc_timestamp):
	return str(datetime.utcfromtimestamp(utc_timestamp).strftime('%Y-%m-%d %H:%M:%S'))

def print_limits(reddit_instance):
	limit_info = reddit_instance.auth.limits
	limit_info['reset_timestamp'] = '{}{}{}'.format(str(limit_info['reset_timestamp']), ' | ', utc_timestamp_to_datetime_string(limit_info['reset_timestamp']))
	print(limit_info)


user_agent= "testscript by /u/SwagSorcerer420_API"
reddit = praw.Reddit(user_agent=user_agent)

subreddit = reddit.subreddit("wallstreetbets")

for submission in subreddit.new(limit=100):
	submission_info = '{}{}{}'.format(utc_timestamp_to_datetime_string(submission.created_utc), ' | ', submission.title)
	print(submission_info)
# submission_id = "hsctzt"
# submission = reddit.submission(id=submission_id)

# submission.comments.replace_more(limit=None)
# comment_count = 0
# for comment in submission.comments.list():
# 	print(comment.body)
# 	print(comment_count)
# 	comment_count += 1

print_limits(reddit)
