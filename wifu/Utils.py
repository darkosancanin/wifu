import datetime
import math

class Utils:
	@staticmethod
	def get_updated_avg_gps_coordinates(current_lat, current_lon, current_max_metres_between_locations, current_total_packet_count, new_avg_lat, new_avg_lon, number_of_new_packets):
		if new_avg_lat == 0.0:
			return (None, None, 0)
		updated_avg_lat = new_avg_lat
		updated_avg_lon = new_avg_lon
		updated_max_metres_between_locations = current_max_metres_between_locations
		if current_lat != None and float(current_lat) != new_avg_lat:
			distance_between_previous_location = Utils.distance_between_two_coordinates_in_metres(float(current_lat), float(current_lon), new_avg_lat, new_avg_lon)
			if distance_between_previous_location > current_max_metres_between_locations:
				updated_max_metres_between_locations = distance_between_previous_location
			#if its too far from previous location then it must be a roaming network or has moved
			if distance_between_previous_location > 1000:
				updated_avg_lat = new_avg_lat
				updated_avg_lon = new_avg_lon
			else:
				total_packets = int(current_total_packet_count) + int(number_of_new_packets)
				updated_avg_lat = ((float(current_lat) * float(current_total_packet_count)) + (new_avg_lat * float(number_of_new_packets))) / total_packets
				updated_avg_lon = ((float(current_lon) * float(current_total_packet_count)) + (new_avg_lon * float(number_of_new_packets))) / total_packets
		return (updated_avg_lat, updated_avg_lon, updated_max_metres_between_locations)
	
	@staticmethod
	def distance_between_two_coordinates_in_metres(lat1, long1, lat2, long2):
		degrees_to_radians = math.pi/180.0
		phi1 = (90.0 - lat1)*degrees_to_radians
		phi2 = (90.0 - lat2)*degrees_to_radians
		theta1 = long1*degrees_to_radians
		theta2 = long2*degrees_to_radians
		cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
			   math.cos(phi1)*math.cos(phi2))
		arc = math.acos( cos )
		return int(float(arc * 6371000 ))
	
	@staticmethod
	def get_date_from_sqlite_string(date_string):
		return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
		
	@staticmethod
	def get_date_from_pyshark_string(date_string):
		date_string = date_string[0:date_string.index('.')]
		return datetime.datetime.strptime(date_string, "%b  %d, %Y %H:%M:%S")
		
	@staticmethod
	def get_utc_date_time():
		return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
		
	@staticmethod
	def get_date_from_viewer_querystring(date_string):
		if ":" not in date_string:
			date_string = date_string + ' 00:00'
		return datetime.datetime.strptime(date_string, "%d %b %Y %H:%M")
		
	@staticmethod
	def format_date_for_viewer(date_time):
		return date_time.strftime("%d %b %Y %H:%M")