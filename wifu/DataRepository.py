import os
import sqlite3
import time

from Client import Client
from ClientLocation import ClientLocation
from ImportedHostnameFile import ImportedHostnameFile
from ImportedFile import ImportedFile
from Network import Network
from NetworkClient import NetworkClient
from NetworkEncryption import NetworkEncryption
from NetworkESSID import NetworkESSID
from NetworkLocation import NetworkLocation
from ProbeRequest import ProbeRequest
			
class DataRepository:
	def __init__(self, db_file_name, preload_data):
		self.networks = {}
		self.clients = {}
		self.imported_files = {}
		self.imported_hostname_files = {}
		if db_file_name is not None:
			self.db_file_name = os.path.abspath(db_file_name)
		else:
			self.db_file_name = os.path.abspath("wifu.sqlite")
		self.check_if_db_exists()
		if preload_data == True:
			self.load_data()
		
	def print_db_stats(self):
		print "%s networks" % str(self.execute_scalar(Network.SQL_SELECT_TOTAL_COUNT))
		print "%s network clients" % str(self.execute_scalar(NetworkClient.SQL_SELECT_TOTAL_COUNT))
		print "%s network encryptions" % str(self.execute_scalar(NetworkEncryption.SQL_SELECT_TOTAL_COUNT))
		print "%s network essids" % str(self.execute_scalar(NetworkESSID.SQL_SELECT_TOTAL_COUNT))
		print "%s network locations" % str(self.execute_scalar(NetworkLocation.SQL_SELECT_TOTAL_COUNT))
		print "%s clients" % str(self.execute_scalar(Client.SQL_SELECT_TOTAL_COUNT))
		print "%s client locations" % str(self.execute_scalar(ClientLocation.SQL_SELECT_TOTAL_COUNT))
		print "%s probe requests" % str(self.execute_scalar(ProbeRequest.SQL_SELECT_TOTAL_COUNT))
		print "%s imported files" % str(self.execute_scalar(ImportedFile.SQL_SELECT_TOTAL_COUNT))
		print "%s imported hostname files" % str(self.execute_scalar(ImportedHostnameFile.SQL_SELECT_TOTAL_COUNT))
			
	def execute_scalar(self, query):
		with sqlite3.connect(self.db_file_name) as conn:
			cursor = conn.cursor()
			return cursor.execute(query).fetchone()[0]
		
	def get_or_create_client(self, client_mac):
		if client_mac in self.clients:
			return self.clients[client_mac]
		else:
			client = Client(client_mac)
			self.clients[client_mac] = client
			return client
		
	def get_or_create_network(self, network_bssid):
		if network_bssid in self.networks:
			return self.networks[network_bssid]
		else:
			network = Network()
			self.networks[network_bssid] = network
			return network

	def load_data(self):
		print "Loading object cache."
		start_time = time.time()
		with sqlite3.connect(self.db_file_name) as conn:
			cursor = conn.cursor()
			cursor.execute(Network.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading networks. Found %i existing networks." % len(allrows)
			for row in allrows:
				network = Network.from_sqlite_data_row(row)
				self.networks[network.bssid] = network
			cursor.execute(NetworkEncryption.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading network encryptions. Found %i existing network encryptions." % len(allrows)
			for row in allrows:
				network_encryption = NetworkEncryption.from_sqlite_data_row(row)
				network = self.networks[network_encryption.network_bssid]
				network.encryptions[network_encryption.encryption] = network_encryption
			cursor.execute(NetworkESSID.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading network essids. Found %i existing network essids." % len(allrows)
			for row in allrows:
				network_essid = NetworkESSID.from_sqlite_data_row(row)
				network = self.networks[network_essid.network_bssid]
				network.essids[network_essid.essid] = network_essid
			cursor.execute(NetworkLocation.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading network locations. Found %i existing network locations." % len(allrows)
			for row in allrows:
				network_location = NetworkLocation.from_sqlite_data_row(row)
				network = self.networks[network_location.network_bssid]
				network.locations.append(network_location)
			cursor.execute(Client.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading clients. Found %i existing clients." % len(allrows)
			for row in allrows:
				client = Client.from_sqlite_data_row(row)
				self.clients[client.client_mac] = client
			cursor.execute(NetworkClient.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading network clients. Found %i existing network clients." % len(allrows)
			for row in allrows:
				network_client = NetworkClient.from_sqlite_data_row(row)
				network = self.networks[network_client.network_bssid]
				network.clients[network_client.client_mac] = network_client
				client = self.clients[network_client.client_mac]
				client.network_clients[network_client.network_bssid] = network_client
			cursor.execute(ProbeRequest.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading probe requests. Found %i existing probe requests." % len(allrows)
			for row in allrows:
				probe_request = ProbeRequest.from_sqlite_data_row(row)
				client = self.clients[probe_request.client_mac]
				client.probe_requests[probe_request.get_ssid_or_empty_string()] = probe_request
			cursor.execute(ClientLocation.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading client locations. Found %i existing client locations." % len(allrows)
			for row in allrows:
				client_location = ClientLocation.from_sqlite_data_row(row)
				client = self.clients[client_location.client_mac]
				client.locations.append(client_location)
			cursor.execute(ImportedFile.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading imported files. Found %i existing imported files." % len(allrows)
			for row in allrows:
				imported_file = ImportedFile.from_sqlite_data_row(row)
				self.imported_files[imported_file.file_name] = imported_file
			cursor.execute(ImportedHostnameFile.SQL_SELECT_ALL)
			allrows = cursor.fetchall()
			print "Loading imported hostname files. Found %i existing imported hostname files." % len(allrows)
			for row in allrows:
				imported_hostname_file = ImportedHostnameFile.from_sqlite_data_row(row)
				self.imported_hostname_files[imported_hostname_file.file_name] = imported_hostname_file
		end_time = time.time()
		processing_time = end_time - start_time
		print "Completed loading object cache in %s secs." % str(round(processing_time,2))
	
	def save_updated_items(self):
		print "Saving networks and clients."
		with sqlite3.connect(self.db_file_name) as conn:
			cursor = conn.cursor()
			networks_to_insert = []
			networks_to_update = []
			network_encryptions_to_insert = []
			network_encryptions_to_update = []
			network_essids_to_insert = []
			network_essids_to_update = []
			network_clients_to_insert = []
			network_clients_to_update = []
			network_locations_to_insert = []
			clients_to_insert = []
			clients_to_update = []
			client_probe_requests_to_insert = []
			network_encryptions_to_update = []
			network_essids_to_insert = []
			network_essids_to_update = []
			network_clients_to_insert = []
			network_clients_to_update = []
			clients_to_insert = []
			clients_to_update = []
			client_probe_requests_to_insert = []
			client_probe_requests_to_update = []
			client_locations_to_insert = []
			imported_files_to_insert = []
			imported_hostname_files_to_insert = []
			for key in self.networks.keys():
				network = self.networks[key]
				if network.is_dirty:
					if network.id == 0:
						networks_to_insert.append(network.get_object_for_sqlite_insert())
					else:
						networks_to_update.append(network.get_object_for_sqlite_update())
				(insert, update) = network.get_network_encryptions_to_insert_and_update()	
				network_encryptions_to_insert.extend(insert)	
				network_encryptions_to_update.extend(update)	
				(insert, update) = network.get_network_essids_to_insert_and_update()	
				network_essids_to_insert.extend(insert)	
				network_essids_to_update.extend(update)
				(insert, update) = network.get_network_clients_to_insert_and_update()	
				network_clients_to_insert.extend(insert)	
				network_clients_to_update.extend(update)
				(insert) = network.get_network_locations_to_insert()	
				network_locations_to_insert.extend(insert)
			for key in self.clients.keys():
				client = self.clients[key]
				if client.is_dirty:
					if client.id == 0:
						clients_to_insert.append(client.get_object_for_sqlite_insert())
					else:
						clients_to_update.append(client.get_object_for_sqlite_update())
				(insert, update) = client.get_probe_requests_to_insert_and_update()	
				client_probe_requests_to_insert.extend(insert)	
				client_probe_requests_to_update.extend(update)		
				(insert) = client.get_client_locations_to_insert()	
				client_locations_to_insert.extend(insert)
			for key in self.imported_files.keys():
				imported_file = self.imported_files[key]
				if imported_file.id == 0:
					imported_files_to_insert.append(imported_file.get_object_for_sqlite_insert())
			for key in self.imported_hostname_files.keys():
				imported_hostname_file = self.imported_hostname_files[key]
				if imported_hostname_file.id == 0:
					imported_hostname_files_to_insert.append(imported_hostname_file.get_object_for_sqlite_insert())
			print "%s networks to add." % str(len(networks_to_insert))
			print "%s networks to update." % str(len(networks_to_update))
			print "%s network encryptions to add." % str(len(network_encryptions_to_insert))
			print "%s network encryptions to update." % str(len(network_encryptions_to_update))
			print "%s network essids to add." % str(len(network_essids_to_insert))
			print "%s network essids to update." % str(len(network_essids_to_update))
			print "%s network clients to add." % str(len(network_clients_to_insert))
			print "%s network clients to update." % str(len(network_clients_to_update))
			print "%s network locations to add." % str(len(network_locations_to_insert))
			print "%s clients to add." % str(len(clients_to_insert))
			print "%s clients to update." % str(len(clients_to_update))
			print "%s probe requests to add." % str(len(client_probe_requests_to_insert))
			print "%s probe requests to update." % str(len(client_probe_requests_to_update))
			print "%s client locations to add." % str(len(client_locations_to_insert))
			print "%s imported files to add." % str(len(imported_files_to_insert))
			print "%s imported hostname files to add." % str(len(imported_hostname_files_to_insert))
			cursor.executemany(Network.SQL_INSERT_STATEMENT, networks_to_insert)
			cursor.executemany(Network.SQL_UPDATE_STATEMENT, networks_to_update)
			cursor.executemany(NetworkEncryption.SQL_INSERT_STATEMENT, network_encryptions_to_insert)
			cursor.executemany(NetworkEncryption.SQL_UPDATE_STATEMENT, network_encryptions_to_update)
			cursor.executemany(NetworkESSID.SQL_INSERT_STATEMENT, network_essids_to_insert)
			cursor.executemany(NetworkESSID.SQL_UPDATE_STATEMENT, network_essids_to_update)
			cursor.executemany(NetworkClient.SQL_INSERT_STATEMENT, network_clients_to_insert)
			cursor.executemany(NetworkClient.SQL_UPDATE_STATEMENT, network_clients_to_update)
			cursor.executemany(NetworkLocation.SQL_INSERT_STATEMENT, network_locations_to_insert)
			cursor.executemany(Client.SQL_INSERT_STATEMENT, clients_to_insert)
			cursor.executemany(Client.SQL_UPDATE_STATEMENT, clients_to_update)
			cursor.executemany(ProbeRequest.SQL_INSERT_STATEMENT, client_probe_requests_to_insert)
			cursor.executemany(ProbeRequest.SQL_UPDATE_STATEMENT, client_probe_requests_to_update)
			cursor.executemany(ClientLocation.SQL_INSERT_STATEMENT, client_locations_to_insert)
			cursor.executemany(ImportedFile.SQL_INSERT_STATEMENT, imported_files_to_insert)
			cursor.executemany(ImportedHostnameFile.SQL_INSERT_STATEMENT, imported_hostname_files_to_insert)
			print "Committing changes."
			conn.commit()
			print "Completed saving."
		
	def create_db_schema(self):
		with sqlite3.connect(self.db_file_name) as conn:
			print "Creating schema."
			conn.executescript(ClientLocation.SQL_SCHEMA)
			conn.executescript(ImportedFile.SQL_SCHEMA)
			conn.executescript(ImportedHostnameFile.SQL_SCHEMA)
			conn.executescript(Network.SQL_SCHEMA)
			conn.executescript(NetworkClient.SQL_SCHEMA)
			conn.executescript(NetworkEncryption.SQL_SCHEMA)
			conn.executescript(NetworkESSID.SQL_SCHEMA)
			conn.executescript(NetworkLocation.SQL_SCHEMA)
			conn.executescript(ProbeRequest.SQL_SCHEMA)
			conn.executescript(Client.SQL_SCHEMA)

	def check_if_db_exists(self):
		if not os.path.exists(self.db_file_name):
			print "No database found at %s. Creating database." % self.db_file_name
			open(self.db_file_name,'w')
			self.create_db_schema()	
		else:
			print "Using database at %s." % self.db_file_name