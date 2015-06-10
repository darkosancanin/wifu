from Utils import Utils

class NetworkClient:
	SQL_SCHEMA = "CREATE TABLE 'network_clients' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'client_mac' TEXT NOT NULL, 'network_bssid' TEXT NOT NULL, 'total_packets' TEXT NOT NULL, 'avg_lat' TEXT, 'avg_lon' TEXT, 'seen_first_time' TEXT NOT NULL, 'seen_last_time' TEXT NOT NULL, 'max_metres_between_locations' TEXT NOT NULL, number_of_times_seen TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO network_clients (client_mac, network_bssid, total_packets, avg_lat, avg_lon, seen_first_time, seen_last_time, max_metres_between_locations, number_of_times_seen) VALUES (?,?,?,?,?,?,?,?,?)"
	SQL_UPDATE_STATEMENT = "UPDATE network_clients set total_packets=?, avg_lat=?, avg_lon=?, seen_first_time=?, seen_last_time=?, max_metres_between_locations=?, number_of_times_seen=? where id=?"
	SQL_SELECT_ALL = "SELECT * FROM network_clients"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM network_clients"
	
	def __init__(self):
		self.id = 0
		self.client_mac = None
		self.network_bssid = None
		self.seen_first_time = None
		self.seen_last_time = None
		self.total_packets = 0
		self.avg_lat = None
		self.avg_lon = None
		self.max_metres_between_locations = 0
		self.number_of_times_seen = 0
		self.is_dirty = False
		
	@classmethod
	def from_sqlite_data_row(cls, sqlite_data_row):
		id, client_mac, network_bssid, total_packets, avg_lat, avg_lon, seen_first_time, seen_last_time, max_metres_between_locations, number_of_times_seen = sqlite_data_row
		network_client = NetworkClient()
		network_client.id = id
		network_client.client_mac = client_mac
		network_client.network_bssid = network_bssid
		network_client.total_packets = int(total_packets)
		if not avg_lat == None:
			network_client.avg_lat = float(avg_lat)
			network_client.avg_lon = float(avg_lon)
		network_client.seen_first_time = Utils.get_date_from_sqlite_string(seen_first_time)
		network_client.seen_last_time = Utils.get_date_from_sqlite_string(seen_last_time)
		network_client.max_metres_between_locations = int(max_metres_between_locations)
		network_client.number_of_times_seen = int(number_of_times_seen)
		return network_client
		
	def update_seen_first_time(self, seen_first_time):
		if self.seen_first_time == None or self.seen_first_time > seen_first_time:
			self.seen_first_time = seen_first_time
			
	def update_seen_last_time(self, seen_last_time):
		if self.seen_last_time == None or self.seen_last_time < seen_last_time:
			self.seen_last_time = seen_last_time
		
	def update_total_packets(self,total_packets):
		self.total_packets = self.total_packets + total_packets
		
	def increment_number_of_times_seen(self):
		self.number_of_times_seen = self.number_of_times_seen + 1
	
	def update_gps(self, avg_lat, avg_lon, previous_total_packet_count, number_of_new_packets):
		(updated_avg_lat, updated_avg_lon, updated_max_metres_between_locations) = Utils.get_updated_avg_gps_coordinates(self.avg_lat, self.avg_lon, self.max_metres_between_locations, previous_total_packet_count, avg_lat, avg_lon, number_of_new_packets)
		self.avg_lat = updated_avg_lat
		self.avg_lon = updated_avg_lon
		self.max_metres_between_locations = updated_max_metres_between_locations
	
	def get_object_for_sqlite_insert(self):
		return (self.client_mac, self.network_bssid, self.total_packets, self.avg_lat, self.avg_lon, self.seen_first_time, self.seen_last_time, self.max_metres_between_locations, self.number_of_times_seen)
	
	def get_object_for_sqlite_update(self):
		return (self.total_packets, self.avg_lat, self.avg_lon, self.seen_first_time, self.seen_last_time, self.max_metres_between_locations, self.number_of_times_seen, self.id)