from Utils import Utils

class ClientLocation:
	SQL_SCHEMA = "CREATE TABLE 'client_locations' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'client_mac' TEXT NOT NULL, 'avg_lat' TEXT NOT NULL, 'avg_lon' TEXT NOT NULL, 'seen_time' TEXT NOT NULL, 'seen_in_file_name' TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO client_locations (client_mac, avg_lat, avg_lon, seen_time, seen_in_file_name) VALUES (?,?,?,?,?)"
	SQL_SELECT_ALL = "SELECT * FROM client_locations"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM client_locations"
	
	def __init__(self, id, client_mac, avg_lat, avg_lon, seen_time, seen_in_file_name):
		self.id = id
		self.client_mac = client_mac
		self.avg_lat = avg_lat
		self.avg_lon = avg_lon
		self.seen_time = seen_time
		self.seen_in_file_name = seen_in_file_name
		
	@classmethod
	def from_sqlite_data_row(cls, sqlite_data_row):
		id, client_mac, avg_lat, avg_lon, seen_time, seen_in_file_name = sqlite_data_row
		return ClientLocation(id, client_mac, float(avg_lat), float(avg_lon), Utils.get_date_from_sqlite_string(seen_time), seen_in_file_name)
	
	def get_object_for_sqlite_insert(self):
		return (self.client_mac, self.avg_lat, self.avg_lon, self.seen_time, self.seen_in_file_name)