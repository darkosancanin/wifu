from Utils import Utils

class NetworkLocation:
	SQL_SCHEMA = "CREATE TABLE 'network_locations' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'network_bssid' TEXT NOT NULL, 'avg_lat' TEXT NOT NULL, 'avg_lon' TEXT NOT NULL, 'seen_time' TEXT NOT NULL, 'seen_in_file_name' TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO network_locations (network_bssid, avg_lat, avg_lon, seen_time, seen_in_file_name) VALUES (?,?,?,?,?)"
	SQL_SELECT_ALL = "SELECT * FROM network_locations"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM network_locations"
	TYPE_NETWORK_CLIENT = 1
	TYPE_PROBE_REQUEST = 2
	
	def __init__(self, id, network_bssid, avg_lat, avg_lon, seen_time, seen_in_file_name):
		self.id = id
		self.network_bssid = network_bssid
		self.avg_lat = avg_lat
		self.avg_lon = avg_lon
		self.seen_time = seen_time
		self.seen_in_file_name = seen_in_file_name
			
	@classmethod
	def from_sqlite_data_row(cls, sqlite_data_row):
		id, network_bssid, avg_lat, avg_lon, seen_time, seen_in_file_name = sqlite_data_row
		return NetworkLocation(id, network_bssid, float(avg_lat), float(avg_lon), Utils.get_date_from_sqlite_string(seen_time), seen_in_file_name)
	
	def get_object_for_sqlite_insert(self):
		return (self.network_bssid, self.avg_lat, self.avg_lon, self.seen_time, self.seen_in_file_name)