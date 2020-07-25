import sys
sys.path.insert(0, "./c++/")
import predictor
from psaw import PushshiftAPI
import configparser
from datetime import datetime, timedelta
import time

# NUMBER_OF_COMMENTS_TO_RETRIEVE = 10 # DEPRECATED
START_DATE = datetime(year=2020, month=3, day=20)
END_DATE = datetime(year=2020, month=3, day=20) # Inclusive
ONE_DAY = timedelta(days=1)


def convert_utc_to_readable_time(utc_time):
	readable_time = datetime.utcfromtimestamp(utc_time).strftime('%Y-%m-%d %H:%M:%S')
	return readable_time


def get_date_string(batch_date):
	date_string = batch_date.strftime('%Y%m%d')
	return date_string


def get_current_time():
	current_time = datetime.utcnow().strftime('%H:%M:%S')
	return current_time	


def retrieve_results(api, batch_date):
	date_string = get_date_string(batch_date)
	current_time = get_current_time()
	print('{current_time} {results_date} Retrieving results.'.format(current_time=current_time, results_date=date_string))
	batch_end_date = batch_date + ONE_DAY
	batch_start_epoch = int(batch_date.timestamp())
	batch_end_epoch = int(batch_end_date.timestamp())
	comment_results = api.search_comments(subreddit='wallstreetbets', after=batch_start_epoch, before=batch_end_epoch)
	submission_results = api.search_submissions(subreddit='wallstreetbets', after=batch_start_epoch, before=batch_end_epoch)
	comment_results = [comment_result.d_ for comment_result in comment_results]
	submission_results = [submission_result.d_ for submission_result in submission_results]
	print('{current_time} {results_date} Results retrieved.'.format(current_time=current_time, results_date=date_string))
	return comment_results, submission_results


def write_results(result_type, results_list, batch_date):
	date_string = get_date_string(batch_date)
	current_time = get_current_time()
	year = batch_date.strftime('%Y')
	month = batch_date.strftime('%m')
	print('{current_time} {results_date} Writing {result_type}s.'.format(current_time=current_time, results_date=date_string, result_type=result_type))
	file_name = 'data/{result_type}s/{year}/{month}/{date_string}-{result_type}s-unfiltered.{result_type}'.format(result_type=result_type, year=year, month=month, date_string=date_string)
	with open(file_name, 'w', encoding='utf8') as f:
		for result in results_list:
			try:
				f.write(str(result) + '\n')
			except UnicodeEncodeError as error:
				print('Character error (should no longer be an emoji causing this):\n' + str(error))
	capitalised_result_type = result_type.capitalize()
	print('{current_time} {results_date} {capitalised_result_type}s written to {file_name}.'.format(current_time=current_time, results_date=date_string, capitalised_result_type=capitalised_result_type, file_name=file_name))


def retrieve_batch(api, batch_date):
	batch_start_time = datetime.utcnow()
	batch_run_start_time = time.time()
	comments, submissions = retrieve_results(api, batch_date)
	write_results('comment', comments, batch_date)
	write_results('submission', submissions, batch_date)
	number_of_comments = len(comments)
	number_of_submissions = len(submissions)
	record_batch_time(batch_date, batch_start_time, number_of_comments, number_of_submissions)


def record_batch_time(batch_date, batch_start_time, number_of_comments, number_of_submissions):
	batch_finish_time = datetime.utcnow()
	date_string = get_date_string(batch_date)
	current_time = get_current_time()
	run_time = batch_finish_time - batch_start_time
	print('{current_time} {results_date} Batch run time {run_time}.'.format(current_time=current_time, results_date=date_string, run_time=run_time))
	with open('data/batch_statistics/batch_statistics.stats', 'a') as f:
		batch_time_record = '{results_date} {run_time} {number_of_comments} {number_of_submissions}\n'.format(results_date=date_string, run_time=run_time, number_of_comments=number_of_comments, number_of_submissions=number_of_submissions)
		f.write(batch_time_record)


# Reads config and creates list of desired fields.
def load_fields_to_keep():
	config = configparser.ConfigParser()
	config.read('./resources/config.ini')
	fields, bools = zip(*config.items("COMMENT_FILTERING_FIELDS_TO_KEEP"))
	return [fields[i] for i in range(len(fields)) if bools[i] == "True"]


class CommentFilter():
	def __init__(self):
		self.fields_to_keep = None

	def configure(self, fields_to_keep):
		self.fields_to_keep = fields_to_keep

	def filter(self, comments):
		if isinstance(comments, dict):
			comments = [comments]
		return [self._filter_one(comment) for comment in comments]

	def _filter_one(self, comment):
		return {field_we_want: comment[field_we_want] for field_we_want in self.fields_to_keep}


# Creates CommentFilter object and configures it with desired fields.
def load_comment_filter():
	cf = CommentFilter()
	fields_to_keep = load_fields_to_keep()
	cf.configure(fields_to_keep)
	return cf


# Requires pre-configured CommentFilter object and batch of comments.
# Batch of comments should be provided as list of dicts, or dict if one result.
# Filters said comments.
def filter_comments(comment_filter, comments):
	return comment_filter.filter(comments)


def main():
	api = PushshiftAPI()
	batch_date = START_DATE
	# Do them in daily batches
	while batch_date <= END_DATE:
		# batch_start_time = datetime.utcnow()
		retrieve_batch(api, batch_date)
		# record_batch_time(batch_date, batch_start_time)
		batch_date = batch_date + ONE_DAY


if __name__ == '__main__':
	main()
