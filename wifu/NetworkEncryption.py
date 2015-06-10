from Utils import Utils

class NetworkEncryption:
	SQL_SCHEMA = "CREATE TABLE 'network_encryptions' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'network_bssid' TEXT NOT NULL, 'encryption' TEXT NOT NULL, 'seen_first_time' TEXT NOT NULL, 'seen_last_time' TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO network_encryptions (network_bssid, encryption, seen_first_time, seen_last_time) VALUES (?,?,?,?)"
	SQL_UPDATE_STATEMENT = "UPDATE network_encryptions set seen_first_time=?, seen_last_time=? where id=?"
	SQL_SELECT_ALL = "SELECT * FROM network_encryptions"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM network_encryptions"
	
	def __init__(self, id, network_bssid, encryption, seen_first_time, seen_last_time):
		self.id = id
		self.network_bssid = network_bssid
		self.encryption = encryption
		self.seen_first_time = seen_first_time
		self.seen_last_time = seen_last_time
		self.is_dirty = False
	
	def update_seen_first_time(self, seen_first_time):
		if self.seen_first_time == None or self.seen_first_time > seen_first_time:
			self.seen_first_time = seen_first_time
			
	def update_seen_last_time(self, seen_last_time):
		if self.seen_last_time == None or self.seen_last_time < seen_last_time:
			self.seen_last_time = seen_last_time
			
	@classmethod
	def from_sqlite_data_row(cls, sqlite_data_row):
		id, network_bssid, encryption, seen_first_time, seen_last_time = sqlite_data_row
		return NetworkEncryption(id, network_bssid, encryption, Utils.get_date_from_sqlite_string(seen_first_time), Utils.get_date_from_sqlite_string(seen_last_time))
		
	def get_object_for_sqlite_insert(self):
		return (self.network_bssid, self.encryption, self.seen_first_time, self.seen_last_time)
	
	def get_object_for_sqlite_update(self):
		return (self.seen_first_time, self.seen_last_time, self.id)