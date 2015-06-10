import datetime
import os
import time

import pyshark

from ClientLocation import ClientLocation
from DataRepository import DataRepository
from ImportedHostnameFile import ImportedHostnameFile
from Network import Network
from NetworkClient import NetworkClient
from NetworkLocation import NetworkLocation
from ProbeRequest import ProbeRequest
from Utils import Utils

class HostnameImporter:
	def __init__(self, data_repository, ignore_already_imported_error):
		self.data_repository = data_repository
		self.ignore_already_imported_error = ignore_already_imported_error
	
	def import_files(self, paths):
		start_time = time.time()
		pcap_files = self.find_all_pcap_files(paths)
		if len(pcap_files) == 0:
			print "No pcap files found to import."
		else:
			print "%s file(s) found to import." % str(len(pcap_files))
			for pcap_file in pcap_files:
				file_name = os.path.basename(pcap_file)
				if self.ignore_already_imported_error == False and file_name in self.data_repository.imported_hostname_files:
					imported_file = self.data_repository.imported_hostname_files[file_name]
					print "Ignoring %s. It has already been imported on %s." % (pcap_file, str(imported_file.date_imported))
					continue
				print "Reading %s" % pcap_file
				self.parse_pcap_file(pcap_file)
				self.data_repository.imported_hostname_files[file_name] = ImportedHostnameFile(0, file_name, Utils.get_utc_date_time())
			self.data_repository.save_updated_items()
		end_time = time.time()
		processing_time = end_time - start_time
		print "Completed in %s secs." % str(round(processing_time,2))
	
	def parse_pcap_file(self, pcap_file):
		bootp_packets = pyshark.FileCapture(pcap_file, display_filter='(bootp.option.dhcp==1 || bootp.option.dhcp==3) && bootp.option.hostname && bootp.hw.mac_addr')
		for packet in bootp_packets:
			all_frame_fields = packet.frame_info.__dict__['_all_fields']
			frame_date = Utils.get_date_from_pyshark_string(all_frame_fields['frame.time'].show)
			all_bootp_fields = packet.bootp.__dict__['_all_fields']
			bootp_option_dhcp_layer_field = all_bootp_fields['bootp.option.dhcp']
			bootp_option_hostname_layer_field = all_bootp_fields['bootp.option.hostname']
			bootp_hw_mac_addr_layer_field = all_bootp_fields['bootp.hw.mac_addr']
			hostname = bootp_option_hostname_layer_field.show
			client_mac_address = bootp_hw_mac_addr_layer_field.show
			client = self.data_repository.get_or_create_client(client_mac_address.upper())
			client.update_hostname(hostname, frame_date)
	
	def find_pcap_files_from_directory(self, path):
		files = []
		for file in os.listdir(path):
			if file.endswith(".pcap") or file.endswith(".pcapdump") or file.endswith(".pcapng"):
				files.append(os.path.join(path,file))
		return files

	def find_all_pcap_files(self, paths):
		files = []
		if len(paths) == 0:
			return self.find_pcap_files_from_directory("./")
		for path in paths:
			if not os.path.exists(path):
				print "File or folder not found: %s." % path
			else:
				if os.path.isfile(path):
					files.append(path)
				else:
					files_from_directory = self.find_pcap_files_from_directory(path)
					files.extend(files_from_directory)
		return files