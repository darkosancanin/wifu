from Utils import Utils

class Client:
	SQL_SCHEMA = "CREATE TABLE 'clients' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'client_mac' TEXT NOT NULL, 'hostname' TEXT NULL, 'total_packets' TEXT NOT NULL, 'last_seen_lat' TEXT, 'last_seen_lon' TEXT, 'seen_first_time' TEXT NOT NULL, 'seen_last_time' TEXT NOT NULL, 'max_metres_between_locations' TEXT NOT NULL, number_of_times_seen TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO clients (client_mac, hostname, total_packets, last_seen_lat, last_seen_lon, seen_first_time, seen_last_time, max_metres_between_locations, number_of_times_seen) VALUES (?,?,?,?,?,?,?,?,?)"
	SQL_UPDATE_STATEMENT = "UPDATE clients set hostname=?, total_packets=?, last_seen_lat=?, last_seen_lon=?, seen_first_time=?, seen_last_time=?, max_metres_between_locations=?, number_of_times_seen=? where id=?"
	SQL_SELECT_ALL = "SELECT * FROM clients"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM clients"
	
	def __init__(self, client_mac):
		self.id = 0
		self.client_mac = client_mac
		self.hostname = None
		self.max_metres_between_locations = 0
		self.seen_first_time = None
		self.seen_last_time = None
		self.total_packets = 0
		self.last_seen_lat = None
		self.last_seen_lon = None
		self.number_of_times_seen = 0
		self.is_dirty = False
		self.network_clients = {}
		self.probe_requests = {}
		self.locations = []
	
	@classmethod
	def from_sqlite_data_row(self, sqlite_data_row):
		id, client_mac, hostname, total_packets, last_seen_lat, last_seen_lon, seen_first_time, seen_last_time, max_metres_between_locations, number_of_times_seen = sqlite_data_row
		client = Client(client_mac)
		client.id = id
		client.hostname = hostname
		client.total_packets = int(total_packets)
		if not last_seen_lat == None:
			client.last_seen_lat = float(last_seen_lat)
			client.last_seen_lon = float(last_seen_lon)
		client.seen_first_time = Utils.get_date_from_sqlite_string(seen_first_time)
		client.seen_last_time = Utils.get_date_from_sqlite_string(seen_last_time)
		client.max_metres_between_locations = int(max_metres_between_locations)
		client.number_of_times_seen = int(number_of_times_seen)
		return client
		
	def get_object_for_sqlite_insert(self):
		return (self.client_mac, self.hostname, self.total_packets, self.last_seen_lat, self.last_seen_lon, self.seen_first_time, self.seen_last_time, self.max_metres_between_locations, self.number_of_times_seen)
	
	def get_object_for_sqlite_update(self):
		return (self.hostname, self.total_packets, self.last_seen_lat, self.last_seen_lon, self.seen_first_time, self.seen_last_time, self.max_metres_between_locations, self.number_of_times_seen, self.id)
		
	def update_details_from_network_client(self, network_client):
		self.is_dirty = True
		self.increment_number_of_times_seen()
		self.update_total_packets(network_client.total_packets)
		self.update_seen_first_time(network_client.seen_first_time)
		is_last_time_its_seen = self.update_seen_last_time(network_client.seen_last_time)
		has_location = network_client.avg_lat is not None
		if has_location:
			self.update_max_metres_between_locations(network_client.avg_lat, network_client.avg_lon)
			if is_last_time_its_seen:
				self.last_seen_lat = network_client.avg_lat
				self.last_seen_lon = network_client.avg_lon
				
	def update_hostname(self, hostname, seen_date):
		self.is_dirty = True
		self.update_seen_first_time(seen_date)
		self.update_seen_last_time(seen_date)
		self.hostname = hostname
			
	def update_details_from_probe_request(self, probe_request, avg_lat, avg_lon):
		self.is_dirty = True
		self.increment_number_of_times_seen()
		self.update_total_packets(probe_request.total_packets)
		self.update_seen_first_time(probe_request.seen_first_time)
		is_last_time_its_seen = self.update_seen_last_time(probe_request.seen_last_time)
		has_location = avg_lat is not None
		if has_location:
			self.update_max_metres_between_locations(avg_lat, avg_lon)
			if is_last_time_its_seen:
				self.last_seen_lat = avg_lat
				self.last_seen_lon = avg_lon
	
	def update_max_metres_between_locations(self, new_avg_lat, new_avg_lon):
		for location in self.locations:
			if new_avg_lat != location.avg_lat and new_avg_lon != location.avg_lon:
				metres_between_coordinates = Utils.distance_between_two_coordinates_in_metres(new_avg_lat, new_avg_lon, location.avg_lat, location.avg_lon)
				if metres_between_coordinates > self.max_metres_between_locations:
					self.max_metres_between_locations = metres_between_coordinates
	
	def update_total_packets(self, total_packets):
		self.total_packets = self.total_packets + total_packets
		
	def increment_number_of_times_seen(self):
		self.number_of_times_seen = self.number_of_times_seen + 1
		
	def update_seen_first_time(self, seen_first_time):
		if self.seen_first_time == None or self.seen_first_time > seen_first_time:
			self.seen_first_time = seen_first_time
			
	def update_seen_last_time(self, seen_last_time):
		if self.seen_last_time == None or self.seen_last_time < seen_last_time:
			self.seen_last_time = seen_last_time
			return True
		else:
			return False
			
	def get_probe_requests_to_insert_and_update(self):
		probe_requests_to_insert = []
		probe_requests_to_update = []
		for key in self.probe_requests.keys():
			probe_request = self.probe_requests[key]
			if probe_request.id == 0:
				probe_requests_to_insert.append(probe_request.get_object_for_sqlite_insert())
			elif probe_request.is_dirty == True:
				probe_requests_to_update.append(probe_request.get_object_for_sqlite_update())
		return (probe_requests_to_insert, probe_requests_to_update)
		
	def get_client_locations_to_insert(self):
		client_locations_to_insert = []
		for client_location in self.locations:
			if client_location.id == 0:
				client_locations_to_insert.append(client_location.get_object_for_sqlite_insert())
		return client_locations_to_insert