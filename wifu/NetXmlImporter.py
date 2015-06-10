import datetime
import os
import time
import xml.etree.ElementTree as ElementTree

from ClientLocation import ClientLocation
from DataRepository import DataRepository
from ImportedFile import ImportedFile
from Network import Network
from NetworkClient import NetworkClient
from NetworkLocation import NetworkLocation
from ProbeRequest import ProbeRequest
from Utils import Utils

class NetXmlImporter:
	def __init__(self, data_repository, ignore_already_imported_error):
		self.data_repository = data_repository
		self.ignore_already_imported_error = ignore_already_imported_error
	
	def import_files(self, paths):
		start_time = time.time()
		netxml_files = self.find_all_netxml_files(paths)
		if len(netxml_files) == 0:
			print "No netxml files found to import."
		else:
			print "%s file(s) found to import." % str(len(netxml_files))
			for netxml_file in netxml_files:
				file_name = os.path.basename(netxml_file)
				if self.ignore_already_imported_error == False and file_name in self.data_repository.imported_files:
					imported_file = self.data_repository.imported_files[file_name]
					print "Ignoring %s. It has already been imported on %s." % (netxml_file, str(imported_file.date_imported))
					continue
				print "Reading %s" % netxml_file
				try:
					tree = ElementTree.parse(netxml_file)
				except:
					print "Ignoring %s. Failed to parse the xml." % netxml_file
					continue
				root = tree.getroot()
				self.parse_wireless_network_elements(root.findall("wireless-network"), file_name)
				self.data_repository.imported_files[file_name] = ImportedFile(0, file_name, Utils.get_utc_date_time())
			self.data_repository.save_updated_items()
		end_time = time.time()
		processing_time = end_time - start_time
		print "Completed in %s secs." % str(round(processing_time,2))
		
	def find_netxml_files_from_directory(self, path):
		files = []
		for file in os.listdir(path):
			if file.endswith(".netxml"):
				files.append(os.path.join(path,file))
		return files

	def find_all_netxml_files(self, paths):
		files = []
		if len(paths) == 0:
			return self.find_netxml_files_from_directory("./")
		for path in paths:
			if not os.path.exists(path):
				print "File or folder not found: %s." % path
			else:
				if os.path.isfile(path):
					files.append(path)
				else:
					files_from_directory = self.find_netxml_files_from_directory(path)
					files.extend(files_from_directory)
		return files

	def parse_wireless_network_elements(self, network_elements, file_name):
		for network_element in network_elements:
			if network_element.get("type") == "infrastructure":
				#parse the network
				network_bssid = network_element.find("BSSID").text
				network = self.data_repository.get_or_create_network(network_bssid)
				network.increment_number_of_times_seen()
				network.is_dirty = True
				network.bssid = network_bssid
				network.update_seen_first_time(self.get_date_from_kismet_string(network_element.get("first-time")))
				network.update_seen_last_time(self.get_date_from_kismet_string(network_element.get("last-time")))
				network_previous_total_packets = network.total_packets
				network_number_of_new_packets = network_element.find("packets").find("total").text
				network.update_total_packets(int(network_number_of_new_packets))
				(network_max_rate, network_is_hidden, network_essids, network_encryptions) = self.parse_network_ssid_elements(network_element.findall("SSID"))
				network.update_max_rate(network_max_rate)
				network.is_hidden = network_is_hidden
				network.update_essids(network_essids)
				network.update_encryptions(network_encryptions)
				network_gps_info_element = network_element.find("gps-info")
				if not network_gps_info_element == None:
					network_avg_lat = float(network_gps_info_element.find("avg-lat").text)
					network_avg_lon = float(network_gps_info_element.find("avg-lon").text)
					network_location_seen_time = self.get_date_from_kismet_string(network_element.get("last-time"))
					network.update_gps(network_avg_lat, network_avg_lon, network_previous_total_packets, network_number_of_new_packets)
					network.locations.append(NetworkLocation(0, network_bssid, network_avg_lat, network_avg_lon, network_location_seen_time, file_name))
				self.parse_wireless_client_elements(network, network_element.findall("wireless-client"), file_name)
			elif network_element.get("type") == "probe":
				wireless_client_element = network_element.find("wireless-client")
				client_mac = wireless_client_element.find("client-mac").text
				client = self.data_repository.get_or_create_client(client_mac)
				ssid_elements = wireless_client_element.findall("SSID")
				for ssid_element in ssid_elements:
					ssid = None
					ssid_name_element = ssid_element.find("ssid")
					if not ssid_name_element == None:
						ssid = ssid_name_element.text
					probe_request_total_packets = int(ssid_element.find("packets").text)
					probe_request_seen_first_time = self.get_date_from_kismet_string(ssid_element.get("first-time"))
					probe_request_seen_last_time = self.get_date_from_kismet_string(ssid_element.get("last-time"))
					if ssid in client.probe_requests:
						probe_request = client.probe_requests[ssid]
						probe_request.update_total_packets(probe_request_total_packets)
						probe_request.update_seen_first_time(probe_request_seen_first_time)
						probe_request.update_seen_last_time(probe_request_seen_last_time)
						probe_request.increment_number_of_times_seen()
						probe_request.is_dirty = True
					else:
						probe_request = ProbeRequest(0, client_mac, ssid, probe_request_total_packets, probe_request_seen_first_time, probe_request_seen_last_time, 1)
						client.probe_requests[probe_request.ssid] = probe_request
				probe_request_gps_info_element = wireless_client_element.find("gps-info")
				probe_request_avg_lat = None
				probe_request_avg_lon = None
				if not probe_request_gps_info_element == None:
					probe_request_avg_lat = float(probe_request_gps_info_element.find("avg-lat").text)
					probe_request_avg_lon = float(probe_request_gps_info_element.find("avg-lon").text)
					probe_request_seen_time = self.get_date_from_kismet_string(wireless_client_element.get("last-time"))
					client.locations.append(ClientLocation(0, client_mac, probe_request_avg_lat, probe_request_avg_lon, probe_request_seen_time, file_name))
				client.update_details_from_probe_request(probe_request, probe_request_avg_lat, probe_request_avg_lon)
				
	def parse_wireless_client_elements(self, network, wireless_client_elements, file_name):
		for wireless_client_element in wireless_client_elements:
			client_mac = wireless_client_element.find("client-mac").text
			network_client = network.clients.get(client_mac)
			if network_client == None:
				network_client = NetworkClient()
				network.clients[client_mac] = network_client
			network_client.is_dirty = True
			network_client.increment_number_of_times_seen()
			network_client.client_mac = client_mac
			network_client.network_bssid = network.bssid
			network_client.update_seen_first_time(self.get_date_from_kismet_string(wireless_client_element.get("first-time")))
			network_client.update_seen_last_time(self.get_date_from_kismet_string(wireless_client_element.get("last-time")))
			network_client_previous_total_packets = network_client.total_packets
			network_client_number_of_new_packets = int(wireless_client_element.find("packets").find("total").text)
			network_client.update_total_packets(network_client_number_of_new_packets)
			network_client_gps_info_element = wireless_client_element.find("gps-info")
			client = self.data_repository.get_or_create_client(client_mac)
			if network_client.network_bssid not in client.network_clients:
				client.network_clients[network_client.network_bssid] = network_client
			if not network_client_gps_info_element == None:
				network_client_avg_lat = float(network_client_gps_info_element.find("avg-lat").text)
				network_client_avg_lon = float(network_client_gps_info_element.find("avg-lon").text)
				network_client_location_seen_time = self.get_date_from_kismet_string(wireless_client_element.get("last-time"))
				network_client.update_gps(network_client_avg_lat, network_client_avg_lon, network_client_previous_total_packets, network_client_number_of_new_packets)
				client.locations.append(ClientLocation(0, client_mac, network_client_avg_lat, network_client_avg_lon, network_client_location_seen_time, file_name))
			client.update_details_from_network_client(network_client)
			
	def parse_network_ssid_elements(self, network_ssid_elements):
		network_max_rate = None
		network_is_hidden = None
		network_essids = []
		network_encryptions =[]
		for network_ssid_element in network_ssid_elements:
			if not network_ssid_element.find("type").text == "Cached SSID":
				network_max_rate = int(float(network_ssid_element.find("max-rate").text))
				network_essid_element = network_ssid_element.find("essid")
				if network_essid_element.text is not None and not network_essid_element.text == "":
					network_essids.append(network_essid_element.text)
				if network_is_hidden == None or network_is_hidden == False:
					network_is_hidden = network_essid_element.get("cloaked") == "true"
				for network_encryption_element in network_ssid_element.findall("encryption"):
					if network_encryption_element.text not in network_encryptions:
						network_encryptions.append(network_encryption_element.text)
		return (network_max_rate, network_is_hidden, network_essids, network_encryptions)

	def get_date_from_kismet_string(self, date_string):
			return datetime.datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y")