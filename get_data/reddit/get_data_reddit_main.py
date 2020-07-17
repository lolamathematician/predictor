from psaw import PushshiftAPI
from datetime import datetime, timedelta
import time

# NUMBER_OF_COMMENTS_TO_RETRIEVE = 10 # DEPRECATED
START_DATE = datetime(year=2020, month=1, day=1)
END_DATE = datetime(year=2020, month=1, day=1) # Inclusive
ONE_DAY = timedelta(days=1)

def convert_utc_to_readable_time(utc_time):
	return datetime.utcfromtimestamp(utc_time).strftime('%Y-%m-%d %H:%M:%S')

def retrieve_comments(api, batch_date):
	print('Retrieving results.')
	batch_end_date = batch_date + ONE_DAY
	batch_start_epoch = int(batch_date.timestamp())
	batch_end_epoch = int(batch_end_date.timestamp())
	results = api.search_comments(subreddit='wallstreetbets',
								  after=batch_start_epoch,
								  before=batch_end_epoch)
	print('Results retrieved.'.format(year=batch_date.year, month=batch_date.month, day=batch_date.day))
	return results

def filter_results(results):
	print('Filtering results.')
	filtered_results = [{'created_utc': result.d_['created_utc'],
						 'created_datetime': convert_utc_to_readable_time(result.d_['created_utc']),
						 'permalink': result.d_['permalink'],
						 'body': result.d_['body'],
						 'retrieved_on': result.d_['retrieved_on'],
						 'retrieved_on_datetime': convert_utc_to_readable_time(result.d_['retrieved_on']),
						 'subreddit': result.d_['subreddit'],
						 'id': result.d_['id'],
						 'is_submitter': result.d_['is_submitter'],
						 'link_id': result.d_['link_id'],
						 'parent_id': result.d_['parent_id'],
						 'score': result.d_['score'],
						 'subreddit_id': result.d_['subreddit_id']}
						 for result in results]
	number_of_results = len(filtered_results)
	print('Results filtered. Total results: {number_of_results}'.format(number_of_results=number_of_results))
	return filtered_results

def write_comments(comment_list, batch_date):
	print('Writing results.')
	file_name = 'comments/{year}-{month}-{day}-comments.comment'.format(year=batch_date.year, month=batch_date.month, day=batch_date.day)
	with open(file_name, 'w', encoding='utf8') as f:
		for comment in comment_list:
			try:
				f.write(str(comment) + '\n')
			except UnicodeEncodeError as error:
				print('Character error (should no longer be an emoji causing this):\n' + str(error))
	print('Results written to {file_name}.'.format(file_name=file_name))


def retrieve_batch(api, batch_date):
	batch_run_start_time = time.time()
	comments = retrieve_comments(api, batch_date)
	filtered_results = filter_results(comments)
	write_comments(filtered_results, batch_date)

def main():
	api = PushshiftAPI()
	batch_date = START_DATE
	# Do them in daily batches
	while batch_date <= END_DATE:
		retrieve_batch(api, batch_date)
		batch_date = batch_date + ONE_DAY

if __name__ == '__main__':
	main()
