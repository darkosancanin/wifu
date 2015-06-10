from Utils import Utils

class ProbeRequest:
	SQL_SCHEMA = "CREATE TABLE 'probe_requests' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'client_mac' TEXT NOT NULL, 'ssid' TEXT, 'total_packets' TEXT NOT NULL, 'seen_first_time' TEXT NOT NULL, 'seen_last_time' TEXT NOT NULL, number_of_times_seen TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO probe_requests (client_mac, ssid, total_packets, seen_first_time, seen_last_time, number_of_times_seen) VALUES (?,?,?,?,?,?)"
	SQL_UPDATE_STATEMENT = "UPDATE probe_requests set total_packets=?, seen_first_time=?, seen_last_time=?, number_of_times_seen=? where id=?"
	SQL_SELECT_ALL = "SELECT * FROM probe_requests"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM probe_requests"
	
	def __init__(self, id, client_mac, ssid, total_packets, seen_first_time, seen_last_time, number_of_times_seen):
		self.id = id
		self.client_mac = client_mac
		self.ssid = ssid
		self.total_packets = total_packets
		self.seen_first_time = seen_first_time
		self.seen_last_time = seen_last_time
		self.number_of_times_seen = number_of_times_seen
		self.is_dirty = False
	
	def update_seen_first_time(self, seen_first_time):
		if self.seen_first_time == None or self.seen_first_time > seen_first_time:
			self.seen_first_time = seen_first_time
			
	def update_seen_last_time(self, seen_last_time):
		if self.seen_last_time == None or self.seen_last_time < seen_last_time:
			self.seen_last_time = seen_last_time
			
	def increment_number_of_times_seen(self):
		self.number_of_times_seen = self.number_of_times_seen + 1
	
	def update_total_packets(self, total_packets):
		self.total_packets = self.total_packets + total_packets

	def get_ssid_or_empty_string(self):
		if self.ssid is None:
			return ""
		return self.ssid
	
	@classmethod
	def from_sqlite_data_row(cls, sqlite_data_row):
		id, client_mac, ssid, total_packets, seen_first_time, seen_last_time, number_of_times_seen = sqlite_data_row
		return ProbeRequest(id, client_mac, ssid, int(total_packets), Utils.get_date_from_sqlite_string(seen_first_time), Utils.get_date_from_sqlite_string(seen_last_time), int(number_of_times_seen))
		
	def get_object_for_sqlite_insert(self):
		return (self.client_mac, self.ssid, self.total_packets, self.seen_first_time, self.seen_last_time, self.number_of_times_seen)
	
	def get_object_for_sqlite_update(self):
		return (self.total_packets, self.seen_first_time, self.seen_last_time, self.number_of_times_seen, self.id)