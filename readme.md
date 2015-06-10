## Overview 
Wifu is a wifi data analysis tool written in Python, it is based on the output of Kismet (https://www.kismetwireless.net/) files.

Wifu parses the data from Kismet .netxml output files and stores the data in a structured SQLite database for analysis. A simple HTTP viewer can be spun up to browse the data in a browser via Google Maps. Note: the viewer only displays networks and clients with GPS location data. The viewer has also only been tested on Chrome.

Hostnames of clients can also be imported from any .pcap files (specifically from DHCP packets).

The tool was created to better understand wireless networks and traffic around me and is helpful in answering the following questions:  

- What are the most common network names?  
`SELECT essid AS [Network Name], COUNT(*) AS [Number of Networks] FROM networks GROUP BY essid ORDER BY COUNT(*) DESC`

- What are the networks most probed for by clients?  
`SELECT ssid AS [Network Name], COUNT(*) AS [Number of Probe Requests] FROM probe_requests GROUP BY ssid ORDER BY COUNT(*) DESC`

- What is most common access point encryption used? How prevalent is WEP?  
`SELECT encryption AS [Encryption], COUNT(*) AS [Number of Networks] FROM network_encryptions GROUP BY encryption ORDER BY COUNT(*) DESC`

- How many times have you seen the same client?  
`SELECT client_mac, hostname, number_of_times_seen, seen_first_time, seen_last_time FROM clients ORDER BY number_of_times_seen DESC`

- What is the furthest distance apart that you have seen the same client?  
`SELECT client_mac, max_metres_between_locations, number_of_times_seen, seen_first_time, seen_last_time FROM clients ORDER BY CAST(max_metres_between_locations AS INT) DESC`

- What networks have the most clients?  
`SELECT N.essid AS [Network Name], N.network_bssid AS [Network BSSID], COUNT(*) AS [Number of Clients] from network_clients NC INNER JOIN networks N ON N.network_bssid = NC.network_bssid GROUP BY N.network_bssid ORDER BY COUNT(*) DESC`

- How many networks have changed their name?  
`SELECT N.essid AS [Current Network Name], N.network_bssid AS [Network BSSID], COUNT(*) AS [Number of Name Changes] FROM network_essids NE INNER JOIN networks N ON n.network_bssid = NE.network_bssid GROUP BY NE.network_bssid ORDER BY COUNT(*) DESC`

## Instructions/Usage
Install python requirements - `pip install -r requirements.txt`.

Importing Kismet output files (.netxml) into the database - `python wifu.py --import C:\PathToKismetNetXmlFiles\`.  
Note: the database is created automatically if it does not exist (wifu.sqlite). By default it is created in the same directory or the path can be specified using the `--database` argument.

Importing client hostname data from pcaps into the database - `python wifu.py --hostname C:\PathToPcapFiles\`.

View statistics about data in the database - `python wifu.py --stats`.

Start the HTTP viewer (defaults to port 8080) - `python wifu.py --viewer`.

Start the HTTP viewer on a specific port - `python wifu.py --viewer --port 9000`.

## Screenshots
![Importing Data](https://raw.githubusercontent.com/darkosancanin/wifu/master/images/console_importing_data.png)

![Viewing Statistics](https://raw.githubusercontent.com/darkosancanin/wifu/master/images/console_stats.png)

![HTTP Viewer](https://raw.githubusercontent.com/darkosancanin/wifu/master/images/console_viewer.png)

![Networks](https://raw.githubusercontent.com/darkosancanin/wifu/master/images/networks.png)

![Clients](https://raw.githubusercontent.com/darkosancanin/wifu/master/images/clients.png)

## Database Schema
###client_locations
- id [INTEGER] - Primary key for the table.
- client_mac [TEXT] - MAC address of the client.
- avg_lat [TEXT] - Average latitude of where they client was seen.
- avg_lon [TEXT] - Average longitude of where they client was seen.
- seen_time [TEXT] - Date/time when the client was seen at this location.
- seen_in_file_name [TEXT] - What file the location was imported from.

###clients
- id [INTEGER] - Primary key for the table.
- client_mac [TEXT] - MAC address of the client.
- hostname [TEXT] - The computer hostname of the client (retrieved from DHCP packets).
- total_packets [TEXT] - Total number of packets seen from this user (includes network client packets and probe requests).
- last_seen_lat [TEXT] - Average latitude where the client was last seen.
- last_seen_lon [TEXT] - Average longitude where the client was last seen.
- seen_first_time [TEXT] - Date/time when the client was first seen.
- seen_last_time [TEXT] - Date/time when the client was last seen.
- max_metres_between_locations [TEXT] - The furthest distance (in metres) where the client has been seen.
- number_of_times_seen [TEXT] - The total number of times the client has been seen.

###imported_files
- id [INTEGER] - Primary key for the table.
- file_name [TEXT] - The name of the file.
- date_imported [TEXT] - Date/time when the file was imported.

###imported_hostname_files
- id [INTEGER] - Primary key for the table.
- file_name [TEXT] - The name of the file.
- date_imported [TEXT] - Date/time when the file was imported.

###network_clients
- id [INTEGER] - Primary key for the table.
- client_mac [TEXT] - MAC address of the client.
- network_bssid [TEXT] - The bssid of the network that the client was connected to.
- total_packets [TEXT] - Total number of packets seen from this user (includes network client packets and probe requests).
- last_seen_lat [TEXT] - Average latitude where the client was last seen.
- last_seen_lon [TEXT] - Average longitude where the client was last seen.
- seen_first_time [TEXT] - Date/time when the client was first seen.
- seen_last_time [TEXT] - Date/time when the client was last seen.
- max_metres_between_locations [TEXT] - The furthest distance (in metres) where the client has been seen.
- number_of_times_seen [TEXT] - The total number of times the client has been seen.

###network_encryptions
- id [INTEGER] - Primary key for the table.
- network_bssid [TEXT] - The bssid of the network.
- encryption [TEXT] - The encryption that the network is advertising.
- seen_first_time [TEXT] - Date/time when the encryption was first seen for that network.
- seen_last_time [TEXT] - Date/time when the encryption was last seen for that network.

###network_essids
- id [INTEGER] - Primary key for the table.
- network_bssid [TEXT] - The bssid of the network.
- essid [TEXT] - The essid that the network is advertising.
- seen_first_time [TEXT] - Date/time when the essid was first seen for that network.
- seen_last_time [TEXT] - Date/time when the essid was last seen for that network.

###network_locations
- id [INTEGER] - Primary key for the table.
- network_bssid [TEXT] - The bssid of the network.
- avg_lat [TEXT] - Average latitude of where the network was seen.
- avg_lon [TEXT] - Average longitude of where the network was seen.
- seen_time [TEXT] - Date/time when the network was seen at this location.
- seen_in_file_name [TEXT] - What file the location was imported from.

###networks
- id [INTEGER] - Primary key for the table.
- network_bssid [TEXT] - The bssid of the network.
- essid [TEXT] - The latest essid that the network is advertising.
- total_packets [TEXT] - Total number of packets seen from this network.
- avg_lat [TEXT] - Average latitude of where the network was seen.
- avg_lon [TEXT] - Average longitude of where the network was seen.
- is_hidden [TEXT] - Whether the network is hidden (i.e. not broadcasting its essid).
- max_rate [TEXT] - Maximum data rate that the network supports.
- seen_first_time [TEXT] - Date/time when the network was first seen.
- seen_last_time [TEXT] - Date/time when the network was last seen.
- max_metres_between_locations [TEXT] - The furthest distance (in metres) where the network has been seen.
- number_of_times_seen [TEXT] - The total number of times the network has been seen.

###probe_requests
- id [INTEGER] - Primary key for the table.
- client_mac [TEXT] - MAC address of the client.
- ssid [TEXT] - The ssid of the network that the client was probing for.
- total_packets [TEXT] - Total number of packets seen from this user probing for this network.
- seen_first_time [TEXT] - Date/time when the client was first seen probing for this network.
- seen_last_time [TEXT] - Date/time when the client was last seen probing for this network.
- number_of_times_seen [TEXT] - The total number of times the client has been seen probing for this network.
