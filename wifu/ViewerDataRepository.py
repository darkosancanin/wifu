import sqlite3

from DataRepository import DataRepository
from ViewerClasses import ViewerClientMarker
from ViewerClasses import ViewerClientDetails
from ViewerClasses import ViewerNetworkMarker
from ViewerClasses import ViewerNetworkDetails
from ViewerClasses import ViewerResults
from Utils import Utils
		
class ViewerDataRepository(DataRepository):
	def __init__(self, db_file_name):
		DataRepository.__init__(self, db_file_name, True)
		
	def get_network_markers(self, viewer_options):
		networks = []
		total_record_count = 0
		for key in self.networks.keys():
			network = self.networks[key]
			if network.avg_lat is None:
				continue
			if viewer_options.filter_by_essid_is_hidden:
				if network.is_hidden != viewer_options.essid_is_hidden:
					continue
			if viewer_options.filter_by_seen_before_date:
				if network.seen_first_time > viewer_options.seen_before_date:
					continue
			if viewer_options.filter_by_seen_after_date:
				if network.seen_last_time < viewer_options.seen_after_date:
					continue
			if viewer_options.filter_by_bssid:
				if viewer_options.bssid.lower() not in network.bssid.lower():
					continue
			if viewer_options.filter_by_essid:
				if network.essid is None or viewer_options.essid.lower() not in network.essid.lower():
					continue
			if viewer_options.filter_by_max_metres_greater_than:
				if network.max_metres_between_locations < viewer_options.max_metres_greater_than:
					continue
			if viewer_options.filter_by_max_metres_less_than:
				if network.max_metres_between_locations > viewer_options.max_metres_less_than:
					continue
			if viewer_options.filter_by_times_seen_greater_than:
				if network.number_of_times_seen < viewer_options.times_seen_greater_than:
					continue
			if viewer_options.filter_by_times_seen_less_than:
				if network.number_of_times_seen > viewer_options.times_seen_less_than:
					continue
			if viewer_options.filter_by_encryption:
				encryption_matches = False
				for encryption in viewer_options.encryptions:
					if encryption in network.get_basic_encryption_names():
						encryption_matches = True
						continue
				if encryption_matches == False:
					continue
			if viewer_options.filter_by_distance_from_location:
				if Utils.distance_between_two_coordinates_in_metres(viewer_options.lat, viewer_options.lon, network.avg_lat, network.avg_lon) > viewer_options.within_metres:
					continue
			if viewer_options.filter_by_map_bounds:
				if network.avg_lat < viewer_options.sw_lat or network.avg_lat > viewer_options.ne_lat or network.avg_lon < viewer_options.sw_lon or network.avg_lon > viewer_options.ne_lon:
					continue
			networks.append(network)
			total_record_count = total_record_count + 1
		if viewer_options.sort_by_property:
			networks.sort(key=lambda x: self.get_sort_value(x, viewer_options.sort_by_property_name), reverse=viewer_options.sort_by_desc)
		if total_record_count >= viewer_options.max_records:
			networks = networks[0:viewer_options.max_records]
		viewer_networks = []
		for network in networks:
			viewer_networks.append(ViewerNetworkMarker(network).__dict__)
		return ViewerResults(viewer_networks, len(viewer_networks), total_record_count).__dict__
	
	def get_sort_value(self, obj, property_name):
		if property_name.startswith("length_"):
			return len(getattr(obj, property_name[7:]))
		value = getattr(obj, property_name)
		if type(value) is str:
			return value.lower()
		else:
			return value
	
	def get_network_marker(self, network_bssid):
		network_marker = self.networks[network_bssid]
		return ViewerNetworkMarker(network_marker).__dict__
		
	def get_network_details(self, network_bssid):
		network = self.networks[network_bssid]
		viewer_network_details = ViewerNetworkDetails(network)
		viewer_network_details.load_clients(network, self.clients)
		return viewer_network_details.__dict__
	
	def get_network_markers_for_client(self, client_mac):
		client = self.clients[client_mac]
		network_markers = []
		for key in client.network_clients.keys():
			network_client = client.network_clients[key]
			network = self.networks[network_client.network_bssid]
			network_markers.append(ViewerNetworkMarker(network).__dict__)
		return network_markers
	
	def get_client_markers(self, viewer_options):
		clients = []
		total_record_count = 0
		for key in self.clients.keys():
			client = self.clients[key]
			if client.last_seen_lat is None:
				continue
			if viewer_options.filter_by_seen_before_date:
				if client.seen_first_time.date() > viewer_options.seen_before_date:
					continue
			if viewer_options.filter_by_seen_after_date:
				if client.seen_last_time.date() < viewer_options.seen_after_date:
					continue
			if viewer_options.filter_by_client_mac:
				if viewer_options.client_mac.lower() not in client.client_mac.lower():
					continue
			if viewer_options.filter_by_hostname:
				if client.hostname is None or viewer_options.hostname.lower() not in client.hostname.lower():
					continue
			if viewer_options.filter_by_has_hostname:
				if (client.hostname is None) == viewer_options.has_hostname:
					continue
			if viewer_options.filter_by_probing_for_ssid:
				probing_for_ssid_matches = False
				for key in client.probe_requests.keys():
					probe_request = client.probe_requests[key]
					if probe_request.ssid is not None and viewer_options.probing_for_ssid.lower() in probe_request.ssid.lower():
						probing_for_ssid_matches = True
						continue
				if probing_for_ssid_matches == False:
					continue
			if viewer_options.filter_by_max_metres_greater_than:
				if client.max_metres_between_locations < viewer_options.max_metres_greater_than:
					continue
			if viewer_options.filter_by_max_metres_less_than:
				if client.max_metres_between_locations > viewer_options.max_metres_less_than:
					continue
			if viewer_options.filter_by_times_seen_greater_than:
				if client.number_of_times_seen < viewer_options.times_seen_greater_than:
					continue
			if viewer_options.filter_by_times_seen_less_than:
				if client.number_of_times_seen > viewer_options.times_seen_less_than:
					continue
			if viewer_options.filter_by_distance_from_location:
				if Utils.distance_between_two_coordinates_in_metres(viewer_options.lat, viewer_options.lon, client.last_seen_lat, client.last_seen_lon) > viewer_options.within_metres:
					continue
			if viewer_options.filter_by_map_bounds:
				if client.last_seen_lat < viewer_options.sw_lat or client.last_seen_lat > viewer_options.ne_lat or client.last_seen_lon < viewer_options.sw_lon or client.last_seen_lon > viewer_options.ne_lon:
					continue
			clients.append(client)
			total_record_count = total_record_count + 1
		if viewer_options.sort_by_property:
			clients.sort(key=lambda x: self.get_sort_value(x, viewer_options.sort_by_property_name), reverse=viewer_options.sort_by_desc)
		if total_record_count >= viewer_options.max_records:
			clients = clients[0:viewer_options.max_records]
		viewer_clients = []
		for client in clients:
			viewer_clients.append(ViewerClientMarker(client, None).__dict__)
		return ViewerResults(viewer_clients, len(viewer_clients), total_record_count).__dict__
		
	def get_client_markers_for_network(self, network_bssid):
		network = self.networks[network_bssid]
		client_markers = []
		for key in network.clients.keys():
			network_client = network.clients[key]
			client = self.clients[network_client.client_mac]
			client_markers.append(ViewerClientMarker(client).__dict__)
		return client_markers
		
	def get_client_marker(self, client_mac, network_bssid):
		client = self.clients[client_mac]
		network = None
		if network_bssid is not None:
			network = self.networks[network_bssid]
		return ViewerClientMarker(client, network).__dict__
		
	def get_client_details(self, client_mac, network_bssid):
		network = None
		if network_bssid is not None:
			network = self.networks[network_bssid]
		client = self.clients[client_mac]
		client_details = ViewerClientDetails(client, network)
		client_details.load_networks(client, self.networks)
		return client_details.__dict__