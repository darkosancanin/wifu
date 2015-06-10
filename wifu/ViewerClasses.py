from Network import Network
from Utils import Utils

class ViewerOptions():
	def __init__(self, querystring):
		self.querystring = querystring
		self.sort_by_property = False
		self.sort_by_desc = False
		self.filter_by_seen_after_date = False
		self.filter_by_seen_before_date = False
		self.filter_by_client_mac = False
		self.filter_by_has_hostname = False
		self.filter_by_hostname = False
		self.filter_by_probing_for_ssid = False
		self.filter_by_bssid = False
		self.filter_by_essid = False
		self.filter_by_essid_is_hidden = False
		self.filter_by_max_metres_greater_than = False
		self.filter_by_max_metres_less_than = False
		self.filter_by_times_seen_greater_than = False
		self.filter_by_times_seen_less_than = False
		self.filter_by_encryption = False
		self.filter_by_distance_from_location = False
		self.filter_by_map_bounds = False
		self.max_records = 0
		if self.has_value_in_querystring("within_metres"):
			self.filter_by_distance_from_location = True
			self.within_metres = int(self.get_string_from_querystring("within_metres"))
			self.lat = float(self.get_string_from_querystring("lat"))
			self.lon = float(self.get_string_from_querystring("lon"))
		if self.has_value_in_querystring("ne_lat"):
			self.filter_by_map_bounds = True
			self.ne_lat = float(self.get_string_from_querystring("ne_lat"))
			self.ne_lon = float(self.get_string_from_querystring("ne_lon"))
			self.sw_lat = float(self.get_string_from_querystring("sw_lat"))
			self.sw_lon = float(self.get_string_from_querystring("sw_lon"))
		if self.has_value_in_querystring("seen_before_date"):
			self.filter_by_seen_before_date = True
			self.seen_before_date = self.get_date_from_querystring("seen_before_date")
		if self.has_value_in_querystring("seen_after_date"):
			self.filter_by_seen_after_date = True
			self.seen_after_date = self.get_date_from_querystring("seen_after_date")
		if self.has_value_in_querystring("bssid"):
			self.filter_by_bssid = True
			self.bssid = self.get_string_from_querystring("bssid")
		if self.has_value_in_querystring("client_mac"):
			self.filter_by_client_mac = True
			self.client_mac = self.get_string_from_querystring("client_mac")
		if self.has_value_in_querystring("has_hostname"):
			self.filter_by_has_hostname = True
			self.has_hostname = self.get_bool_from_querystring("has_hostname")
		if self.has_value_in_querystring("hostname"):
			self.filter_by_hostname = True
			self.hostname = self.get_string_from_querystring("hostname")
		if self.has_value_in_querystring("probing_for_ssid"):
			self.filter_by_probing_for_ssid = True
			self.probing_for_ssid = self.get_string_from_querystring("probing_for_ssid")
		if self.has_value_in_querystring("essid"):
			self.filter_by_essid = True
			self.essid = self.get_string_from_querystring("essid")
		if self.has_value_in_querystring("essid_is_hidden"):
			self.filter_by_essid_is_hidden = True
			self.essid_is_hidden = self.get_bool_from_querystring("essid_is_hidden")
		if self.has_value_in_querystring("encryption"):
			self.filter_by_encryption = True
			self.encryptions = self.get_values_from_querystring("encryption")
		if self.has_value_in_querystring("max_metres_greater_than"):
			self.filter_by_max_metres_greater_than = True
			self.max_metres_greater_than = self.get_int_from_querystring("max_metres_greater_than")
		if self.has_value_in_querystring("max_metres_less_than"):
			self.filter_by_max_metres_less_than = True
			self.max_metres_less_than = self.get_int_from_querystring("max_metres_less_than")
		if self.has_value_in_querystring("times_seen_greater_than"):
			self.filter_by_times_seen_greater_than = True
			self.times_seen_greater_than = self.get_int_from_querystring("times_seen_greater_than")
		if self.has_value_in_querystring("times_seen_less_than"):
			self.filter_by_times_seen_less_than = True
			self.times_seen_less_than = self.get_int_from_querystring("times_seen_less_than")
		if self.has_value_in_querystring("sort_by_property"):
			self.sort_by_property = True
			self.sort_by_property_name = self.get_string_from_querystring("sort_by_property")
			if self.has_value_in_querystring("sort_by_direction"):
				self.sort_by_desc = (self.get_string_from_querystring("sort_by_direction") == "desc")
		if self.has_value_in_querystring("max_records"):
			self.max_records = self.get_int_from_querystring("max_records")
			
	def has_value_in_querystring(self, parameter_name):
		return parameter_name in self.querystring
		
	def get_string_from_querystring(self, parameter_name):
		return self.querystring[parameter_name][0]
	
	def get_int_from_querystring(self, parameter_name):
		return int(self.querystring[parameter_name][0])
		
	def get_bool_from_querystring(self, parameter_name):
		value = self.get_string_from_querystring(parameter_name)
		if value == "yes":
			return True
		else:
			return False
		
	def get_boolean_value_from_querystring(self, parameter_name):
		return self.querystring[parameter_name][0] == "true"
		
	def get_date_from_querystring(self, parameter_name):
		return Utils.get_date_from_viewer_querystring(self.querystring[parameter_name][0])
		
	def get_values_from_querystring(self, parameter_name):
		values = self.querystring[parameter_name]
		return values
		
class ViewerNetworkMarker:
	def __init__(self, network):
		self.network_bssid = network.bssid
		if network.essid == None:
			self.essid = "-- hidden --"
		else:
			self.essid = network.essid
		self.lat = network.avg_lat
		self.lon = network.avg_lon
		#self.seen_first_time = Utils.format_date_for_viewer(network.seen_first_time)
		#self.seen_last_time = Utils.format_date_for_viewer(network.seen_last_time)
		#self.number_of_times_seen = network.number_of_times_seen
		self.encryptions = network.get_basic_encryption_names()
		self.number_of_clients = len(network.clients)

class ViewerNetworkDetails:
	def __init__(self, network):
		self.network_bssid = network.bssid
		if network.essid == None:
			self.essid = "-- hidden --"
		else:
			self.essid = network.essid
		self.is_hidden = network.is_hidden
		self.lat = network.avg_lat
		self.lon = network.avg_lon
		self.seen_first_time = Utils.format_date_for_viewer(network.seen_first_time)
		self.seen_last_time = Utils.format_date_for_viewer(network.seen_last_time)
		self.number_of_times_seen = network.number_of_times_seen
		self.total_packets = network.total_packets
		self.max_metres_between_locations = network.max_metres_between_locations
		self.encryptions = network.encryptions.keys()
		self.location_markers = []
		for network_location in network.locations:
			self.location_markers.append(ViewerNetworkLocationMarker(network_location, network.essid).__dict__)
		self.clients = []
			
	def load_clients(self, network, clients):
		for key in network.clients.keys():
			network_client = network.clients[key]
			client = clients[network_client.client_mac]
			self.clients.append(ViewerNetworkDetailsClients(client).__dict__)

class ViewerNetworkDetailsClients:
	def __init__(self, client):
		self.client_mac = client.client_mac
		self.hostname = client.hostname
		self.number_of_probe_requests = len(client.probe_requests)
		self.number_of_networks = len(client.network_clients)
		
class ViewerNetworkLocationMarker:
	def __init__(self, network_location, network_essid):
		self.essid = network_essid
		self.network_bssid = network_location.network_bssid
		self.seen_time = Utils.format_date_for_viewer(network_location.seen_time)
		self.lat = network_location.avg_lat
		self.lon = network_location.avg_lon
		
class ViewerClientMarker:
	def __init__(self, client, network):
		self.client_mac = client.client_mac
		self.hostname = client.hostname
		self.lat = client.last_seen_lat
		self.lon = client.last_seen_lon
		#self.seen_first_time = Utils.format_date_for_viewer(client.seen_first_time)
		#self.seen_last_time = Utils.format_date_for_viewer(client.seen_last_time)
		#self.number_of_times_seen = client.number_of_times_seen
		self.number_of_probe_requests = len(client.probe_requests)
		self.number_of_networks = len(client.network_clients)
		
class ViewerClientDetails:
	def __init__(self, client, network):
		self.client_mac = client.client_mac
		self.hostname = client.hostname
		self.lat = client.last_seen_lat
		self.lon = client.last_seen_lon
		self.seen_first_time = Utils.format_date_for_viewer(client.seen_first_time)
		self.seen_last_time = Utils.format_date_for_viewer(client.seen_last_time)
		self.number_of_times_seen = client.number_of_times_seen
		self.max_metres_between_locations = client.max_metres_between_locations
		self.total_packets = client.total_packets
		self.location_markers = []
		for client_location in client.locations:
			self.location_markers.append(ViewerClientLocationMarker(client_location).__dict__)
		self.probe_requests = []
		for key in client.probe_requests.keys():
			self.probe_requests.append(ViewerClientDetailsProbeRequests(client.probe_requests[key]).__dict__)
		self.networks = []
		
	def load_networks(self, client, networks):
		for key in client.network_clients.keys():
			network_client = client.network_clients[key]
			network = networks[network_client.network_bssid]
			self.networks.append(ViewerClientDetailsNetworks(network).__dict__)

class ViewerClientDetailsNetworks:
	def __init__(self, network):
		self.essid = network.essid
		self.bssid = network.bssid
		
class ViewerClientDetailsProbeRequests:
	def __init__(self, probe_request):
		self.ssid = probe_request.get_ssid_or_empty_string()
		self.number_of_times_seen = probe_request.number_of_times_seen
			
class ViewerClientLocationMarker:
	def __init__(self, client_location):
		self.client_mac = client_location.client_mac
		self.seen_time = Utils.format_date_for_viewer(client_location.seen_time)
		self.lat = client_location.avg_lat
		self.lon = client_location.avg_lon
		
class ViewerResults:
	def __init__(self, data, count, total_count):
		self.data = data
		self.count = count
		self.total_count = total_count