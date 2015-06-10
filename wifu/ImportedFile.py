from Utils import Utils

class ImportedFile:
	SQL_SCHEMA = "CREATE TABLE 'imported_files' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'file_name' TEXT NOT NULL, 'date_imported' TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO imported_files (file_name, date_imported) VALUES (?,?)"
	SQL_SELECT_ALL = "SELECT * FROM imported_files"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM imported_files"
	
	def __init__(self, id, file_name, date_imported):
		self.id = id
		self.file_name = file_name
		self.date_imported = date_imported
			
	@classmethod
	def from_sqlite_data_row(cls, sqlite_data_row):
		id, file_name, date_imported = sqlite_data_row
		return ImportedFile(id, file_name, Utils.get_date_from_sqlite_string(date_imported))
		
	def get_object_for_sqlite_insert(self):
		return (self.file_name, self.date_imported)