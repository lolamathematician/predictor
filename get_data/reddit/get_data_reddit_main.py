import praw
from datetime import datetime

def print_limits(reddit_instance):
	limit_info = reddit_instance.auth.limits
	limit_info['reset_timestamp'] = '{}{}{}'.format(str(limit_info['reset_timestamp']), ' | ', str(datetime.utcfromtimestamp(limit_info['reset_timestamp']).strftime('%Y-%m-%d %H:%M:%S')))
	print(limit_info)


user_agent= "testscript by /u/SwagSorcerer420_API"
reddit = praw.Reddit(user_agent=user_agent)

submission_id = "hsctzt"
submission = reddit.submission(id=submission_id)

submission.comments.replace_more(limit=None)
comment_count = 0
for comment in submission.comments.list():
	print(comment.body)
	print(comment_count)
	comment_count += 1

print_limits(reddit)
