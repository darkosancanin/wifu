from NetworkEncryption import NetworkEncryption
from NetworkESSID import NetworkESSID
from Utils import Utils

class Network:
	SQL_SCHEMA = "CREATE TABLE 'networks' ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'network_bssid' TEXT NOT NULL, 'essid' TEXT, 'total_packets' TEXT NOT NULL, 'avg_lat' TEXT, 'avg_lon' TEXT, 'is_hidden' TEXT, 'max_rate' TEXT, 'seen_first_time' TEXT NOT NULL, 'seen_last_time' TEXT NOT NULL, 'max_metres_between_locations' TEXT NOT NULL, number_of_times_seen TEXT NOT NULL);"
	SQL_INSERT_STATEMENT = "INSERT INTO networks (network_bssid, essid, total_packets, avg_lat, avg_lon, is_hidden, max_rate, seen_first_time, seen_last_time, max_metres_between_locations, number_of_times_seen) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
	SQL_UPDATE_STATEMENT = "UPDATE networks set essid=?, total_packets=?, avg_lat=?, avg_lon=?, is_hidden=?, max_rate=?, seen_first_time=?, seen_last_time=?, max_metres_between_locations=?, number_of_times_seen=? where id=?"
	SQL_SELECT_ALL = "SELECT * FROM networks"
	SQL_SELECT_TOTAL_COUNT = "SELECT count(*) FROM networks"
	
	def __init__(self):
		self.id = 0
		self.bssid = None
		self.essid = None
		self.seen_first_time = None
		self.seen_last_time = None
		self.total_packets = 0
		self.is_hidden = None
		self.max_rate = None
		self.avg_lat = None
		self.avg_lon = None
		self.max_metres_between_locations = 0
		self.number_of_times_seen = 0
		self.encryptions = {}
		self.basic_encryption_names = []
		self.clients = {}
		self.essids = {}
		self.locations = []
		self.is_dirty = False
		
	@classmethod
	def from_sqlite_data_row(self, sqlite_data_row):
		id, network_bssid, essid, total_packets, avg_lat, avg_lon, is_hidden, max_rate, seen_first_time, seen_last_time, max_metres_between_locations, number_of_times_seen = sqlite_data_row
		network = Network()
		network.id = id
		network.bssid = network_bssid
		network.essid = essid
		network.total_packets = int(total_packets)
		if not avg_lat == None:
			network.avg_lat = float(avg_lat)
			network.avg_lon = float(avg_lon)
		network.is_hidden = is_hidden == "1"
		network.max_rate = max_rate
		network.seen_first_time = Utils.get_date_from_sqlite_string(seen_first_time)
		network.seen_last_time = Utils.get_date_from_sqlite_string(seen_last_time)
		network.max_metres_between_locations = int(max_metres_between_locations)
		network.number_of_times_seen = int(number_of_times_seen)
		return network
	
	def update_seen_first_time(self, seen_first_time):
		if self.seen_first_time == None or self.seen_first_time > seen_first_time:
			self.seen_first_time = seen_first_time
			
	def update_seen_last_time(self, seen_last_time):
		if self.seen_last_time == None or self.seen_last_time < seen_last_time:
			self.seen_last_time = seen_last_time
		
	def update_total_packets(self, total_packets):
		self.total_packets = self.total_packets + total_packets
	
	def update_max_rate(self, max_rate):
		if self.max_rate == None or self.max_rate <= max_rate:
			self.max_rate = max_rate
			
	def increment_number_of_times_seen(self):
		self.number_of_times_seen = self.number_of_times_seen + 1
	
	def update_gps(self, avg_lat, avg_lon, previous_total_packet_count, number_of_new_packets):
		(updated_avg_lat, updated_avg_lon, updated_max_metres_between_locations) = Utils.get_updated_avg_gps_coordinates(self.avg_lat, self.avg_lon, self.max_metres_between_locations, previous_total_packet_count, avg_lat, avg_lon, number_of_new_packets)
		self.avg_lat = updated_avg_lat
		self.avg_lon = updated_avg_lon
		self.max_metres_between_locations = updated_max_metres_between_locations
		
	def update_encryptions(self, encryptions):
		for encryption in encryptions:
			network_encryption = self.encryptions.get(encryption)
			if network_encryption == None:
				network_encryption = NetworkEncryption(0, self.bssid, encryption, self.seen_first_time, self.seen_last_time)
				self.encryptions[encryption] = network_encryption
			else:
				network_encryption.update_seen_first_time(self.seen_first_time)
				network_encryption.update_seen_last_time(self.seen_last_time)
				network_encryption.is_dirty = True
		
	def update_essids(self, essids):
		if len(essids) > 0:
			self.essid = essids[0]
		for essid in essids:
			network_essid = self.essids.get(essid)
			if network_essid == None:
				network_essid = NetworkESSID(0, self.bssid, essid, self.seen_first_time, self.seen_last_time)
				self.essids[essid] = network_essid
			else:
				network_essid.update_seen_first_time(self.seen_first_time)
				network_essid.update_seen_last_time(self.seen_last_time)
				network_essid.is_dirty = True
	
	def get_basic_encryption_names(self):
		if len(self.basic_encryption_names) > 0:
			return self.basic_encryption_names
		else:
			basic_encryption_values = ["WEP", "WPA", "None"]
			for encryption in self.encryptions.keys():
				for basic_encryption in basic_encryption_values:
					if basic_encryption in encryption and basic_encryption not in self.basic_encryption_names:
						self.basic_encryption_names.append(basic_encryption)
			return self.basic_encryption_names
		
	def get_object_for_sqlite_insert(self):
		return (self.bssid, self.essid, self.total_packets, self.avg_lat, self.avg_lon, self.is_hidden, self.max_rate, self.seen_first_time, self.seen_last_time, self.max_metres_between_locations, self.number_of_times_seen)
	
	def get_object_for_sqlite_update(self):
		return (self.essid, self.total_packets, self.avg_lat, self.avg_lon, self.is_hidden, self.max_rate, self.seen_first_time, self.seen_last_time, self.max_metres_between_locations, self.number_of_times_seen, self.id)
		
	def get_network_encryptions_to_insert_and_update(self):
		network_encryptions_to_insert = []
		network_encryptions_to_update = []
		for key in self.encryptions.keys():
			network_encryption = self.encryptions[key]
			if network_encryption.id == 0:
				network_encryptions_to_insert.append(network_encryption.get_object_for_sqlite_insert())
			elif network_encryption.is_dirty == True:
				network_encryptions_to_update.append(network_encryption.get_object_for_sqlite_update())
		return (network_encryptions_to_insert, network_encryptions_to_update)
		
	def get_network_essids_to_insert_and_update(self):
		network_essids_to_insert = []
		network_essids_to_update = []
		for key in self.essids.keys():
			network_essid = self.essids[key]
			if network_essid.id == 0:
				network_essids_to_insert.append(network_essid.get_object_for_sqlite_insert())
			elif network_essid.is_dirty == True:
				network_essids_to_update.append(network_essid.get_object_for_sqlite_update())
		return (network_essids_to_insert, network_essids_to_update)
		
	def get_network_clients_to_insert_and_update(self):
		network_clients_to_insert = []
		network_clients_to_update = []
		for key in self.clients.keys():
			network_client = self.clients[key]
			if network_client.id == 0:
				network_clients_to_insert.append(network_client.get_object_for_sqlite_insert())
			elif network_client.is_dirty == True:
				network_clients_to_update.append(network_client.get_object_for_sqlite_update())
		return (network_clients_to_insert, network_clients_to_update)
		
	def get_network_locations_to_insert(self):
		network_locations_to_insert = []
		for network_location in self.locations:
			if network_location.id == 0:
				network_locations_to_insert.append(network_location.get_object_for_sqlite_insert())
		return network_locations_to_insert