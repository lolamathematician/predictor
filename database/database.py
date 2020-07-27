import sqlite3
from sqlite3 import Error, OperationalError, IntegrityError
from datetime import datetime, timedelta
from collections import defaultdict
import ast
import os

ONE_DAY = timedelta(days=1)
START_DATE = datetime(year=2019, month=1, day=1)
END_DATE = datetime(year=2020, month=7, day=25) #Minor change

class database:

	def __init__(self, database_file):
		self.conn = None
		self.database_file = database_file

	def create_connection(self):
		try:
			self.conn = sqlite3.connect(self.database_file)
		except Error as e:
			print(e)
	
	def create_table(self, schema_path):
		self.create_connection()
		with open(schema_path, 'r') as f:
			table_schema = f.read()
			sql = """CREATE TABLE IF NOT EXISTS {table_schema};""".format(table_schema=table_schema)
			try:
				curs = self.conn.cursor()
				curs.execute(sql)
			except Error as e:
				print(e)
		curs.close()
		self.conn.close()
		
	def create_tables(self, schema_directory):
		schemas = os.listdir(schema_directory)
		for schema in schemas:
			schema_path = '{schema_directory}/{schema}'.format(schema_directory=schema_directory, schema=schema)
			self.create_table(schema_path)

	# Main way to write to database
	# Input start_date and end_date as datetime objects
	# e.g. start_date = datetime(year=2020, month=1, day=1)
	#	   end_date   = datetime(year=2020, month=2, day=20)
	# Dates are inclusive
	def write_dates(self, start_date, end_date):
		batch_date = start_date
		while batch_date <= end_date:
			self.write_results_one_by_one('comment', batch_date)
			self.write_results_one_by_one('submission', batch_date)
			current_time = datetime.utcnow().strftime('%H:%M:%S')
			date_string = batch_date.strftime('%Y%m%d')
			print('{current_time} {date_string}'.format(current_time=current_time, date_string=date_string))
			batch_date = batch_date + ONE_DAY
		return

	def write_results_one_by_one(self, result_type, date):
		result_dictionaries = self.get_result_dicts(result_type, date)
		if result_type == 'comment':
			sql = """ INSERT INTO {result_type}s
						(all_awardings, associated_award, author, author_flair_background_color, author_flair_css_class, author_flair_richtext, author_flair_template_id, author_flair_text, author_flair_text_color, author_flair_type, author_fullname, author_patreon_flair, author_premium, awarders, body, collapsed_because_crowd_control, created_utc, gildings, id, is_submitter, link_id, locked, no_follow, parent_id, permalink, retrieved_on, score, send_replies, stickied, subreddit, subreddit_id, top_awarded_type, total_awards_received, treatment_tags, created)
					  VALUES
					  	(:all_awardings, :associated_award, :author, :author_flair_background_color, :author_flair_css_class, :author_flair_richtext, :author_flair_template_id, :author_flair_text, :author_flair_text_color, :author_flair_type, :author_fullname, :author_patreon_flair, :author_premium, :awarders, :body, :collapsed_because_crowd_control, :created_utc, :gildings, :id, :is_submitter, :link_id, :locked, :no_follow, :parent_id, :permalink, :retrieved_on, :score, :send_replies, :stickied, :subreddit, :subreddit_id, :top_awarded_type, :total_awards_received, :treatment_tags, :created)
				  """.format(result_type=result_type)
		elif result_type == 'submission':
			sql = """ INSERT INTO {result_type}s
						(_comments_by_id, _fetched, _reddit, all_awardings, allow_live_comments, approved_at_utc, approved_by, archived, author, author_flair_background_color, author_flair_css_class, author_flair_richtext, author_flair_template_id, author_flair_text, author_flair_text_color, author_flair_type, author_fullname, author_patreon_flair, author_premium, awarders, banned_at_utc, banned_by, can_gild, can_mod_post, category, clicked, comment_limit, comment_sort, content_categories, contest_mode, created, created_utc, discussion_type, distinguished, domain, downs, edited, gilded, gildings, hidden, hide_score, id, is_crosspostable, is_meta, is_original_content, is_reddit_media_domain, is_robot_indexable, is_self, is_video, likes, link_flair_background_color, link_flair_css_class, link_flair_richtext, link_flair_template_id, link_flair_text, link_flair_text_color, link_flair_type, locked, media, media_embed, media_only, mod_note, mod_reason_by, mod_reason_title, mod_reports, name, no_follow, num_comments, num_crossposts, num_reports, over_18, parent_whitelist_status, permalink, pinned, post_hint, pwls, quarantine, removal_reason, removed_by, removed_by_category, report_reasons, saved, score, secure_media, secure_media_embe, selftext, selftext_html, send_replies, spoiler, stickied, subreddit, subreddit_id, subreddit_name_prefixed, subreddit_subscribers, subreddit_type, suggested_sort, thumbnail, thumbnail_height, thumbnail_width, title, top_awarded_type, total_awards_received, treatment_tags, ups, upvote_ratio, url, url_overridden_by_dest, user_reports, view_count, visited, whitelist_status, wls)
					  VALUES
					  	(:_comments_by_id, :_fetched, :_reddit, :all_awardings, :allow_live_comments, :approved_at_utc, :approved_by, :archived, :author, :author_flair_background_color, :author_flair_css_class, :author_flair_richtext, :author_flair_template_id, :author_flair_text, :author_flair_text_color, :author_flair_type, :author_fullname, :author_patreon_flair, :author_premium, :awarders, :banned_at_utc, :banned_by, :can_gild, :can_mod_post, :category, :clicked, :comment_limit, :comment_sort, :content_categories, :contest_mode, :created, :created_utc, :discussion_type, :distinguished, :domain, :downs, :edited, :gilded, :gildings, :hidden, :hide_score, :id, :is_crosspostable, :is_meta, :is_original_content, :is_reddit_media_domain, :is_robot_indexable, :is_self, :is_video, :likes, :link_flair_background_color, :link_flair_css_class, :link_flair_richtext, :link_flair_template_id, :link_flair_text, :link_flair_text_color, :link_flair_type, :locked, :media, :media_embed, :media_only, :mod_note, :mod_reason_by, :mod_reason_title, :mod_reports, :name, :no_follow, :num_comments, :num_crossposts, :num_reports, :over_18, :parent_whitelist_status, :permalink, :pinned, :post_hint, :pwls, :quarantine, :removal_reason, :removed_by, :removed_by_category, :report_reasons, :saved, :score, :secure_media, :secure_media_embe, :selftext, :selftext_html, :send_replies, :spoiler, :stickied, :subreddit, :subreddit_id, :subreddit_name_prefixed, :subreddit_subscribers, :subreddit_type, :suggested_sort, :thumbnail, :thumbnail_height, :thumbnail_width, :title, :top_awarded_type, :total_awards_received, :treatment_tags, :ups, :upvote_ratio, :url, :url_overridden_by_dest, :user_reports, :view_count, :visited, :whitelist_status, :wls)
				  """.format(result_type=result_type)
		self.create_connection()
		curs = self.conn.cursor()
		for result_dictionary in result_dictionaries:
			try:
				curs.execute(sql, result_dictionary)
			except IntegrityError as e:
				if e == 'sqlite3.IntegrityError: UNIQUE constraint failed: comments.id':
					return
		self.conn.commit()
		curs.close()
		self.conn.close()
		return

	def write_results(self, result_type, date):
		result_dictionary = self.get_result_dicts(result_type, date)
		if result_type == 'comment':
			sql = """ INSERT INTO {result_type}s
						(all_awardings, associated_award, author, author_flair_background_color, author_flair_css_class, author_flair_richtext, author_flair_template_id, author_flair_text, author_flair_text_color, author_flair_type, author_fullname, author_patreon_flair, author_premium, awarders, body, collapsed_because_crowd_control, created_utc, gildings, id, is_submitter, link_id, locked, no_follow, parent_id, permalink, retrieved_on, score, send_replies, stickied, subreddit, subreddit_id, top_awarded_type, total_awards_received, treatment_tags, created)
					  VALUES
					  	(:all_awardings, :associated_award, :author, :author_flair_background_color, :author_flair_css_class, :author_flair_richtext, :author_flair_template_id, :author_flair_text, :author_flair_text_color, :author_flair_type, :author_fullname, :author_patreon_flair, :author_premium, :awarders, :body, :collapsed_because_crowd_control, :created_utc, :gildings, :id, :is_submitter, :link_id, :locked, :no_follow, :parent_id, :permalink, :retrieved_on, :score, :send_replies, :stickied, :subreddit, :subreddit_id, :top_awarded_type, :total_awards_received, :treatment_tags, :created)
				  """.format(result_type=result_type)
		elif result_type == 'submission':
			sql = """ INSERT INTO {result_type}s
						(_comments_by_id, _fetched, _reddit, all_awardings, allow_live_comments, approved_at_utc, approved_by, archived, author, author_flair_background_color, author_flair_css_class, author_flair_richtext, author_flair_template_id, author_flair_text, author_flair_text_color, author_flair_type, author_fullname, author_patreon_flair, author_premium, awarders, banned_at_utc, banned_by, can_gild, can_mod_post, category, clicked, comment_limit, comment_sort, content_categories, contest_mode, created, created_utc, discussion_type, distinguished, domain, downs, edited, gilded, gildings, hidden, hide_score, id, is_crosspostable, is_meta, is_original_content, is_reddit_media_domain, is_robot_indexable, is_self, is_video, likes, link_flair_background_color, link_flair_css_class, link_flair_richtext, link_flair_template_id, link_flair_text, link_flair_text_color, link_flair_type, locked, media, media_embed, media_only, mod_note, mod_reason_by, mod_reason_title, mod_reports, name, no_follow, num_comments, num_crossposts, num_reports, over_18, parent_whitelist_status, permalink, pinned, post_hint, pwls, quarantine, removal_reason, removed_by, removed_by_category, report_reasons, saved, score, secure_media, secure_media_embe, selftext, selftext_html, send_replies, spoiler, stickied, subreddit, subreddit_id, subreddit_name_prefixed, subreddit_subscribers, subreddit_type, suggested_sort, thumbnail, thumbnail_height, thumbnail_width, title, top_awarded_type, total_awards_received, treatment_tags, ups, upvote_ratio, url, url_overridden_by_dest, user_reports, view_count, visited, whitelist_status, wls)
					  VALUES
					  	(:_comments_by_id, :_fetched, :_reddit, :all_awardings, :allow_live_comments, :approved_at_utc, :approved_by, :archived, :author, :author_flair_background_color, :author_flair_css_class, :author_flair_richtext, :author_flair_template_id, :author_flair_text, :author_flair_text_color, :author_flair_type, :author_fullname, :author_patreon_flair, :author_premium, :awarders, :banned_at_utc, :banned_by, :can_gild, :can_mod_post, :category, :clicked, :comment_limit, :comment_sort, :content_categories, :contest_mode, :created, :created_utc, :discussion_type, :distinguished, :domain, :downs, :edited, :gilded, :gildings, :hidden, :hide_score, :id, :is_crosspostable, :is_meta, :is_original_content, :is_reddit_media_domain, :is_robot_indexable, :is_self, :is_video, :likes, :link_flair_background_color, :link_flair_css_class, :link_flair_richtext, :link_flair_template_id, :link_flair_text, :link_flair_text_color, :link_flair_type, :locked, :media, :media_embed, :media_only, :mod_note, :mod_reason_by, :mod_reason_title, :mod_reports, :name, :no_follow, :num_comments, :num_crossposts, :num_reports, :over_18, :parent_whitelist_status, :permalink, :pinned, :post_hint, :pwls, :quarantine, :removal_reason, :removed_by, :removed_by_category, :report_reasons, :saved, :score, :secure_media, :secure_media_embe, :selftext, :selftext_html, :send_replies, :spoiler, :stickied, :subreddit, :subreddit_id, :subreddit_name_prefixed, :subreddit_subscribers, :subreddit_type, :suggested_sort, :thumbnail, :thumbnail_height, :thumbnail_width, :title, :top_awarded_type, :total_awards_received, :treatment_tags, :ups, :upvote_ratio, :url, :url_overridden_by_dest, :user_reports, :view_count, :visited, :whitelist_status, :wls)
				  """.format(result_type=result_type)
		self.create_connection()
		curs = self.conn.cursor()
		curs.executemany(sql, result_dictionary)
		self.conn.commit()
		curs.close()
		self.conn.close()
		return

	def get_result_dicts(self, result_type, date):
		year = date.strftime('%Y')
		month = date.strftime('%m')
		date_string = date.strftime('%Y%m%d')
		file_path = '../get_data/reddit/data/{result_type}s/{year}/{month}/{date_string}-{result_type}s-unfiltered.{result_type}'.format(result_type=result_type, year=year, month=month, date_string=date_string)
		with open(file_path, 'r', encoding='utf-8') as f:
			dicts = [defaultdict(lambda: 'None', ast.literal_eval(result)) for result in f]
			for d in dicts:
				for key in d:
					d[key] = str(d[key])
		return dicts

if __name__ == '__main__':
	d = database('database.db')
	d.write_dates(START_DATE, END_DATE)