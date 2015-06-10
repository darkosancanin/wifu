from BaseHTTPServer import BaseHTTPRequestHandler
import json
import os
import time
import urlparse

from ViewerClasses import ViewerOptions
from ViewerDataRepository import ViewerDataRepository

class ViewerHttpServer():
	def __init__(self, data_repository):
		self.data_repository = data_repository
		
	def start(self, port):
		if port == None:
			port = 8080
		from BaseHTTPServer import HTTPServer
		server = HTTPServer(('localhost', int(port)), ViewerHttpServerHandler)
		print 'Starting the analyzer web server on port %s, use <Ctrl-C> to stop' % str(port)
		server.data_repository = self.data_repository
		server.serve_forever()
	
class ViewerHttpServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		start_time = time.time()
		parsed_path = urlparse.urlparse(self.path)
		if parsed_path.path.startswith("index.html"):
			self.process_files_request(parsed_path.path[6:])
		elif parsed_path.path.startswith("/files"):
			self.process_files_request(parsed_path.path[6:])
		elif parsed_path.path.startswith("/api/"):
			self.process_api_request(parsed_path.path[5:], urlparse.parse_qs(parsed_path.query))
		else:
			self.process_files_request("index.html")
		end_time = time.time()
		processing_time = end_time - start_time
		print "Completed request in %s secs." % str(round(processing_time,3))
		return
	
	def process_api_request(self, path, querystring):
		if path.startswith("network_markers_with_client"):
			network_markers = self.server.data_repository.get_network_markers_for_client(self.get_value_from_querystring(querystring, "client_mac"))
			self.send_data_and_response(json.dumps(network_markers))
		elif path.startswith("network_details"):
			network_details = self.server.data_repository.get_network_details(self.get_value_from_querystring(querystring, "network_bssid"))
			self.send_data_and_response(json.dumps(network_details))
		elif path.startswith("network_markers"):
			network_markers = self.server.data_repository.get_network_markers(ViewerOptions(querystring))
			self.send_data_and_response(json.dumps(network_markers))
		elif path.startswith("network_marker"):
			network_marker = self.server.data_repository.get_network_marker(self.get_value_from_querystring(querystring, "network_bssid"))
			self.send_data_and_response(json.dumps(network_marker))
		elif path.startswith("client_markers_on_network"):
			client_markers = self.server.data_repository.get_client_markers_for_network(self.get_value_from_querystring(querystring, "network_bssid"))
			self.send_data_and_response(json.dumps(client_markers))
		elif path.startswith("client_details"):
			client_details = self.server.data_repository.get_client_details(self.get_value_from_querystring(querystring, "client_mac"), self.get_value_or_none_from_querystring(querystring, "network_bssid"))
			self.send_data_and_response(json.dumps(client_details))
		elif path.startswith("client_markers"):
			client_markers = self.server.data_repository.get_client_markers(ViewerOptions(querystring))
			self.send_data_and_response(json.dumps(client_markers))
		elif path.startswith("client_marker"):
			client_marker = self.server.data_repository.get_client_marker(self.get_value_from_querystring(querystring, "client_mac"), self.get_value_or_none_from_querystring(querystring, "network_bssid"))
			self.send_data_and_response(json.dumps(client_marker))
		else:
			self.send_response(404)
	
	def get_value_from_querystring(self, qs, parameter_name):
		return qs[parameter_name][0]
			
	def get_value_or_none_from_querystring(self, qs, parameter_name):
		if parameter_name in qs:
			return qs[parameter_name][0]
		else:
			return None
	
	def send_data_and_response(self, data):
		self.send_response(200)
		self.end_headers()
		self.wfile.write(data)
	
	def process_files_request(self, file_name):
		file_path = os.path.abspath("wifu/files/" + file_name)
		if not os.path.isfile(file_path) or not os.path.exists(file_path):
			self.send_response(404)
		else:
			if file_name.endswith("png"):
				with open (file_path, "rb") as myfile:
					message = myfile.read()
			else:
				with open (file_path, "r") as myfile:
					message = myfile.read()
			self.send_data_and_response(message)