from psaw import PushshiftAPI
from datetime import datetime, timedelta
import time

# NUMBER_OF_COMMENTS_TO_RETRIEVE = 10 # DEPRECATED
START_DATE = datetime(year=2020, month=2, day=1)
END_DATE = datetime(year=2020, month=2, day=29) # Inclusive
ONE_DAY = timedelta(days=1)

def convert_utc_to_readable_time(utc_time):
	readable_time = datetime.utcfromtimestamp(utc_time).strftime('%Y-%m-%d %H:%M:%S')
	return readable_time

def get_date_string(batch_date):
	date_string = batch_date.strftime('%Y%m%d')
	return date_string

def retrieve_results(api, batch_date):
	date_string = get_date_string(batch_date)
	print('{date} Retrieving results.'.format(date=date_string))
	batch_end_date = batch_date + ONE_DAY
	batch_start_epoch = int(batch_date.timestamp())
	batch_end_epoch = int(batch_end_date.timestamp())
	comment_results = api.search_comments(subreddit='wallstreetbets',
								  after=batch_start_epoch,
								  before=batch_end_epoch)
	submission_results = api.search_submissions(subreddit='wallstreetbets',
								  after=batch_start_epoch,
								  before=batch_end_epoch)
	comment_results = [comment_result.d_ for comment_result in comment_results]
	submission_results = [submission_result.d_ for submission_result in submission_results]
	print('{date} Results retrieved.'.format(date=date_string))
	return comment_results, submission_results

# filter_results replaced with the filter argument from psaw
"""
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
"""

def write_results(result_type, results_list, batch_date):
	date_string = get_date_string(batch_date)
	print('{date_string} Writing {result_type}s.'.format(date_string=date_string, result_type=result_type))
	file_name = 'data/{result_type}s/{date_string}-{result_type}s-unfiltered.{result_type}'.format(date_string=date_string, result_type=result_type)
	with open(file_name, 'w', encoding='utf8') as f:
		for result in results_list:
			try:
				f.write(str(result) + '\n')
			except UnicodeEncodeError as error:
				print('Character error (should no longer be an emoji causing this):\n' + str(error))
	print('{date_string} {result_type}s written to {file_name}.'.format(date_string=date_string, result_type=result_type, file_name=file_name))


def retrieve_batch(api, batch_date):
	batch_run_start_time = time.time()
	comments, submissions = retrieve_results(api, batch_date)
	# filtered_results = filter_results(comments) DEPRECATED now we filter on result retrieval
	write_results('comment', comments, batch_date)
	write_results('submission', submissions, batch_date)

# records times taken to retrieve one month's worth of data
def check_time(start_time, batch_date, month_times):
	next_day = (batch_date + ONE_DAY).day
	if next_day == 1:
		time_since_start = round(time.time()-start_time, 2)
		print('Time taken: {time_since_start}'.format(time_since_start=time_since_start))
		month_times.append(str(time_since_start))

def record_times(month_times, start_date, end_date):
	start_date_string  = get_date_string(start_date)
	end_date_string = get_date_string(end_date)
	time_period_string = '{start_date_string}-{end_date_string}'.format(start_date=start_date_string, end_date=end_date_string)
	times_file = "retrieval_times/{time_period_string}-times.time".format(time_period_string=time_period_string)
	with open(times_file, 'a') as f:
		output_string = time_period_string
		for month_time in month_times:
			output_string += ' {month_time}'.format(month_time=month_time)
		f.write(output_string + '\n')

def main():
	start_time = time.time()
	month_times = []
	api = PushshiftAPI()
	batch_date = START_DATE
	# Do them in daily batches
	while batch_date <= END_DATE:
		check_time(start_time, batch_date, month_times)
		retrieve_batch(api, batch_date)
		batch_date = batch_date + ONE_DAY
	record_times(month_times, START_DATE, END_DATE)

if __name__ == '__main__':
	main()
