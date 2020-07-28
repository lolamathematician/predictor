import sqlite3
from sqlite3 import Error, OperationalError, IntegrityError
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import ast
import os

class database:

	def __init__(self):
		self.ONE_DAY = timedelta(days=1)
		self.conn = None
		self.database_file = None
		self.path = Path(__file__).parent
		self.schema_path = '{path}/schemas'.format(path=self.path)
		self.schema_fields = {}
		self.get_schema_fields()
		self.fields_sql_out = {}
		self.fields_sql_in = {}
		self.get_fields_for_sql()

	def set_database(self, database_file):
		self.database_file = '{path}/{database_file}'.format(path=self.path, database_file=database_file)

	def get_schema_fields(self):
		schemas = os.listdir(self.schema_path)
		for schema in schemas:
			full_schema_path = '{directory}/{schema}'.format(directory=self.schema_path, schema=schema)
			with open(full_schema_path, 'r') as f:
				key, fields = self.unpack_schema_fields(f)
				self.schema_fields[key] = fields

	def get_fields_for_sql(self):
		for schema in self.schema_fields:
			fields_sql_out = '('
			fields_sql_in = '('
			for field in self.schema_fields[schema]:
				fields_sql_out = fields_sql_out + '{field}, '.format(field=field)
				fields_sql_in = fields_sql_in + ':{field}, '.format(field=field)
			fields_sql_out = fields_sql_out[:-2] + ')'
			fields_sql_in = fields_sql_in[:-2] + ')'
			self.fields_sql_out[schema] = fields_sql_out
			self.fields_sql_in[schema] = fields_sql_in

	def unpack_schema_fields(self, file):
		first_line = True
		fields = []
		for line in file:
			line_split = line.split(' ')
			if first_line:
				key = line_split[0]
				first_line = False
			else:
				fields.append(line_split[0])
		fields.pop()
		return key, fields

	def create_connection(self):
		try:
			self.conn = sqlite3.connect(self.database_file)
		except Error as e:
			print(e)
	
	def create_table(self, full_schema_path):
		self.create_connection()
		with open(full_schema_path, 'r') as f:
			table_schema = f.read()
			sql = """CREATE TABLE IF NOT EXISTS {table_schema};""".format(table_schema=table_schema)
			try:
				curs = self.conn.cursor()
				curs.execute(sql)
			except Error as e:
				print(e)
		curs.close()
		self.conn.close()
		
	def create_tables(self):
		schemas = os.listdir(self.schema_path)
		for schema in schemas:
			full_schema_path = '{schema_directory}/{schema}'.format(schema_directory=self.schema_path, schema=schema)
			self.create_table(full_schema_path)

	# Main way to write to database
	# Input start_date and end_date as datetime objects
	# e.g. start_date = datetime(year=2020, month=1, day=1)
	#	   end_date   = datetime(year=2020, month=2, day=20)
	# Dates are inclusive
	def write_dates(self, start_date, end_date):
		batch_date = start_date
		while batch_date <= end_date:
			self.write_results('comments', batch_date)
			self.write_results('submissions', batch_date)
			current_time = datetime.utcnow().strftime('%H:%M:%S')
			date_string = batch_date.strftime('%Y%m%d')
			print('{current_time} {date_string}'.format(current_time=current_time, date_string=date_string))
			batch_date = batch_date + self.ONE_DAY
		return

	def write_results(self, result_type, date):
		result_dictionaries = self.get_result_dicts(result_type, date)
		sql = """
				INSERT INTO {result_type}
					{result_type_fields_out}
				VALUES
					{result_type_fields_in}
			  """.format(result_type=result_type, result_type_fields_out=self.fields_sql_out[result_type], result_type_fields_in=self.fields_sql_in[result_type])
		self.create_connection()
		curs = self.conn.cursor()
		for result_dictionary in result_dictionaries:
			try:
				curs.execute(sql, result_dictionary)
			except IntegrityError as e:
				if repr(e) in ("IntegrityError('UNIQUE constraint failed: comments.id')", "IntegrityError('UNIQUE constraint failed: submissions.id')"):
					print(repr(e))
					return
				else:
					print(e)
		self.conn.commit()
		curs.close()
		self.conn.close()
		return

	def get_result_dicts(self, result_type, date):
		year = date.strftime('%Y')
		month = date.strftime('%m')
		date_string = date.strftime('%Y%m%d')
		file_path = '{directory}/../get_data/reddit/data/{result_type}/{year}/{month}/{date_string}-{result_type}-unfiltered.{result_type}'.format(directory=self.path, result_type=result_type, year=year, month=month, date_string=date_string)[:-1]
		with open(file_path, 'r', encoding='utf-8') as f:
			dicts = [defaultdict(lambda: 'None', ast.literal_eval(result)) for result in f]
			for d in dicts:
				for key in d:
					d[key] = str(d[key])
		return dicts

	def read_results(self, schema, start_date, end_date, fields):
		start_date_utc = str(int(start_date.timestamp()))
		end_date_utc = str(int(end_date.timestamp()))
		print(start_date_utc)
		print(end_date_utc)
		field_string = ''
		for field in fields:
			field_string = field_string + '{field}, '.format(field=field)
		field_string = field_string[:-2]
		sql = """
				SELECT {field_string}
				FROM {schema}
				WHERE created_utc BETWEEN {start_date_utc} AND {end_date_utc}
			  """.format(field_string=field_string, schema=schema, start_date_utc=start_date_utc, end_date_utc=end_date_utc)
		self.create_connection()
		curs = self.conn.cursor()
		curs.execute(sql)
		rows = curs.fetchall()
		return rows

# if __name__ == '__main__':
# 	START_DATE = datetime(year=2020, month=1, day=1)
# 	END_DATE = datetime(year=2020, month=1, day=2)
# 	d = database()
# 	d.set_database('database.db')
# 	d.read_results('comments', START_DATE, END_DATE, ['id', 'body'])
