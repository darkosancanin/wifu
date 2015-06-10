from Utils import Utils

class NetworkESSID:
	SQL_SCHEMA = "CREATE TABLE 'network_essids' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'network_bssid' TEXT NOT NULL, 'essid' TEXT NOT NULL, 'seen_first_time' TEXT NOT NULL, 'seen_last_time' TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO network_essids (network_bssid, essid, seen_first_time, seen_last_time) VALUES (?,?,?,?)"
	SQL_UPDATE_STATEMENT = "UPDATE network_essids set seen_first_time=?, seen_last_time=? where id=?"
	SQL_SELECT_ALL = "SELECT * FROM network_essids"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM network_essids"
	
	def __init__(self, id, network_bssid, essid, seen_first_time, seen_last_time):
		self.id = id
		self.network_bssid = network_bssid
		self.essid = essid
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
		id, network_bssid, essid, seen_first_time, seen_last_time = sqlite_data_row
		return NetworkESSID(id, network_bssid, essid, Utils.get_date_from_sqlite_string(seen_first_time), Utils.get_date_from_sqlite_string(seen_last_time))
		
	def get_object_for_sqlite_insert(self):
		return (self.network_bssid, self.essid, self.seen_first_time, self.seen_last_time)
	
	def get_object_for_sqlite_update(self):
		return (self.seen_first_time, self.seen_last_time, self.id)