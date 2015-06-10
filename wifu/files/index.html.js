var WIFU = (function ($){
	var map;
	var first_load_completed = false;
	var marker_index_map = {};
	
	function init(){
		map = new GMaps({
			div: '#map',
			zoom: 16,
			//SYDNEY - lat: -33.865143, lng:151.209900,
			lat: -33.746477, lng: 151.109194, 
			bounds_changed: function(e){
				if (first_load_completed == true) 
					return; 
				GMaps.geolocate({ success: function(position) { 
					//map.setCenter(position.coords.latitude, position.coords.longitude); 
					refresh_map(); 
				}});
				first_load_completed = true;
			},
			dragend: function(e){
				if (WIFU.OPTIONS.get_mode() == WIFU.OPTIONS.BROWSE)
					refresh_map();;
			}
		});
		
		WIFU.DETAILS.hide();
		
		$('#go_to_address_button').click(function (){
			WIFU.go_to_address($('#address').val());
		});
		
		$('#address').keypress(function (e) {
			var code = e.keyCode || e.which;
			if (code === 13) {
				WIFU.go_to_address($('#address').val());
			};
		});
	}
	
	function show_client_location_marker(client_location_marker){
		var marker_index_map_key = "cl" + client_location_marker.client_mac + client_location_marker.seen_time;
		if (!(marker_index_map_key in marker_index_map)){
			var content = document.createElement("div");
			content.className = "nowrap";
			content.innerHTML = client_location_marker.client_mac + "<br>Seen Time: " + client_location_marker.seen_time;
			var gmap_marker = {
				lat: client_location_marker.lat,
				lng: client_location_marker.lon,
				title: client_location_marker.essid,
				infoWindow: { content: content },
				icon  : '/files/blue.png',
				details: { client_mac: client_location_marker.client_mac },
				click: function(e){
					load_and_show_client(e.details.client_mac);
				}
			}
			map.addMarker(gmap_marker);
			add_to_marker_index_map(marker_index_map_key, map.markers.length - 1);
		}
		show_info_window(marker_index_map_key);
	}
	
	function show_network_location_marker(network_location_marker){
		var marker_index_map_key = "nl" + network_location_marker.network_bssid + network_location_marker.seen_time;
		if (!(marker_index_map_key in marker_index_map)){
			var content = document.createElement("div");
			content.innerHTML = network_location_marker.essid + "<br>Seen Time: " + network_location_marker.seen_time;
			var gmap_marker = {
				lat: network_location_marker.lat,
				lng: network_location_marker.lon,
				title: network_location_marker.essid,
				infoWindow: { content: content },
				icon  : '/files/purple.png',
				details: { network_bssid: network_location_marker.network_bssid },
				click: function(e){
					load_and_show_network(e.details.network_bssid);
				}
			}
			map.addMarker(gmap_marker);
			add_to_marker_index_map(marker_index_map_key, map.markers.length - 1);
		}
		show_info_window(marker_index_map_key);
	}
	
	function load_and_show_client(client_mac){
		load_and_show_client_marker(client_mac)
		var url = "/api/client_details?client_mac=" + client_mac
		$.ajax({url:url,success:function(result){
			var client_details = $.parseJSON(result);
			WIFU.DETAILS.show_client_details(client_details);
		}});
	}
	
	function load_and_show_network(network_bssid){
		load_and_show_network_marker(network_bssid)
		var url = "/api/network_details?network_bssid=" + network_bssid
		$.ajax({url:url,success:function(result){
			var network_details = $.parseJSON(result);
			WIFU.DETAILS.show_network_details(network_details);
		}});
	}
	
	function show_info_window(key){
		for (i = 0; i < map.markers.length; i++){
			map.markers[i].infoWindow.close();
		}
		if (key in marker_index_map) {
			var marker_index = marker_index_map[key];
			map.markers[marker_index].infoWindow.open(map.map,map.markers[marker_index]);
		}
	}
	
	function removeMarkers(){
		map.removeMarkers();
		marker_index_map = {};
	}
	
	function add_to_marker_index_map(key, marker){
		marker_index_map[key] = marker;
	}
	
	function refresh_map(){
		removeMarkers();
		WIFU.RESULTS.clear();
		WIFU.DETAILS.hide();
		if (WIFU.OPTIONS.get_type() == WIFU.OPTIONS.NETWORKS) {
			load_and_show_network_markers(WIFU.OPTIONS.get_mode() == WIFU.OPTIONS.BROWSE, false)
		}
		else {
			load_and_show_client_markers(WIFU.OPTIONS.get_mode() == WIFU.OPTIONS.BROWSE, false)
		}
	}
	
	function get_map_bounds_querystring(){
		var ne_lat = map.map.getBounds().getNorthEast().lat();
		var ne_lon = map.map.getBounds().getNorthEast().lng();
		var sw_lat = map.map.getBounds().getSouthWest().lat();
		var sw_lon = map.map.getBounds().getSouthWest().lng();
		var qs = "&ne_lat=" + ne_lat + "&ne_lon=" + ne_lon + "&sw_lat=" + sw_lat + "&sw_lon=" + sw_lon;
		return qs;
	}
	
	function load_and_show_client_markers(restrict_to_map_bounds){
		var url = "/api/client_markers?" + WIFU.OPTIONS.get_querystring_from_options();
		if (restrict_to_map_bounds) {
			url += get_map_bounds_querystring();
		}
		$.ajax({url:url, success:function(result){
			var client_markers_result = $.parseJSON(result);
			var client_markers = client_markers_result.data;
			WIFU.RESULTS.set_results_found(client_markers_result.count, client_markers_result.total_count);
			for (i = 0; i < client_markers.length; i++) { 
				client_marker = client_markers[i];
				show_client_marker(client_marker, false);
				WIFU.RESULTS.add_client_marker(client_marker);
			}
		}});
	}
	
	function load_and_show_client_marker(client_mac){
		var marker_index_map_key = 'c' + client_mac;
		if (!(marker_index_map_key in marker_index_map)){
			var url = "/api/client_marker?client_mac=" + client_mac;
			$.ajax({url:url, success:function(result){
				var client_marker = $.parseJSON(result);
				show_client_marker(client_marker, true);
			}});
		}
		else{
			show_info_window(marker_index_map_key);
		}
	}
	
	function show_client_marker(client_marker, show_info_window_immediately){
		var marker_index_map_key = "c" + client_marker.client_mac;
		if (!(marker_index_map_key in marker_index_map)){
			var content = document.createElement("div");
			content.innerHTML = client_marker.client_mac;
			var gmap_marker = {
				lat: client_marker.lat,
				lng: client_marker.lon,
				title: client_marker.client_mac,
				infoWindow: { content: content },
				icon: '/files/client_map_icon.png',
				details: { client_mac: client_marker.client_mac },
				click: function(e){
					load_and_show_client(e.details.client_mac);
				}
			}
			map.addMarker(gmap_marker);
			add_to_marker_index_map(marker_index_map_key, i);
		}
		if (show_info_window_immediately) { show_info_window(marker_index_map_key); }
	}
	
	function load_and_show_network_markers(restrict_to_map_bounds){
		var url = "/api/network_markers?" + WIFU.OPTIONS.get_querystring_from_options();
		if (restrict_to_map_bounds) {
			url += get_map_bounds_querystring();
		}
		$.ajax({url:url, success:function(result){
			var network_markers_result = $.parseJSON(result);
			var network_markers = network_markers_result.data;
			WIFU.RESULTS.set_results_found(network_markers_result.count, network_markers_result.total_count);
			for (i = 0; i < network_markers.length; i++) { 
				network_marker = network_markers[i];
				show_network_marker(network_marker, false);
				WIFU.RESULTS.add_network_marker(network_marker);
			}
		}});
	}
	
	function load_and_show_network_marker(network_bssid){
		var marker_index_map_key = 'n' + network_bssid;
		if (!(marker_index_map_key in marker_index_map)){
			var url = "/api/network_marker?network_bssid=" + network_bssid;
			$.ajax({url:url, success:function(result){
				var network_marker = $.parseJSON(result);
				show_network_marker(network_marker, true);
			}});
		}
		else{
			show_info_window(marker_index_map_key);
		}
	}
	
	function show_network_marker(network_marker, show_info_window_immediately){
		var marker_index_map_key = "n" + network_marker.network_bssid;
		if (!(marker_index_map_key in marker_index_map)){
			var content = document.createElement("div");
			content.innerHTML = network_marker.essid;
			var icon = '/files/ap_secured_map_icon.png';
			if(network_marker.encryptions.indexOf("None") > -1){
				icon = '/files/ap_unsecured_none_map_icon.png';
			}
			else if(network_marker.encryptions.indexOf("WEP") > -1){
				icon = '/files/ap_unsecured_wep_map_icon.png';
			}
			var gmap_marker = {
				lat: network_marker.lat,
				lng: network_marker.lon,
				title: network_marker.essid,
				color: 'black',
				infoWindow: { content: content },
				icon: icon,
				details: { network_bssid: network_marker.network_bssid },
				click: function(e){
					load_and_show_network(e.details.network_bssid);
				}
			}
			map.addMarker(gmap_marker);
			add_to_marker_index_map(marker_index_map_key, map.markers.length - 1);
		}
		if (show_info_window_immediately) { show_info_window(marker_index_map_key); }
	}
	
	function go_to_address(address){
		GMaps.geocode({
			address: address,
			callback: function(results, status) {
				if (status == 'OK') {
					var latlng = results[0].geometry.location;
					map.setCenter(latlng.lat(), latlng.lng());
					refresh_map();
				}
			}
		});
	}

	return {
		init: init,
		go_to_address: go_to_address,
		refresh_map: refresh_map,
		load_and_show_client: load_and_show_client,
		load_and_show_network: load_and_show_network,
		show_client_location_marker: show_client_location_marker,
		show_network_location_marker: show_network_location_marker,
		load_and_show_network_marker: load_and_show_network_marker
	};
}(jQuery));

WIFU.OPTIONS = (function ($){
	var BROWSE = 0;
	var SEARCH = 1;
	var mode = BROWSE;
	var NETWORKS = 0;
	var CLIENTS = 1;
	var type = NETWORKS;
	
	function init(){
		$('#options_pane_mode_browse').click(function(){ mode_changed(BROWSE) });
		$('#options_pane_mode_search').click(function(){ mode_changed(SEARCH) });
		
		$('input[name=options_type]:radio').click(function (){
			if ($('input:radio[name=options_type]:checked').val() == "NETWORKS")
				type = NETWORKS;
			else
				type = CLIENTS;
			show_fields_for_type();
			WIFU.refresh_map();
		});
		
		$('#options_search').click(function (){
			WIFU.refresh_map();
		});
		
		$('#options_reset').click(function (){
			$("#options_form")[0].reset();
		});
		
		show_fields_for_type();
		
		$('#options_pane').keypress(function (e) {
			var code = e.keyCode || e.which;
			if (code === 13) {
				WIFU.refresh_map();
			};
		});
	}
	
	function mode_changed(new_mode){
		mode = new_mode;
		if (mode == BROWSE){
			$('#options_pane_mode_browse').addClass("options_pane_mode_selected");
			$('#options_pane_mode_search').removeClass("options_pane_mode_selected");
		}
		else{
			$('#options_pane_mode_browse').removeClass("options_pane_mode_selected");
			$('#options_pane_mode_search').addClass("options_pane_mode_selected");
		}
		show_fields_for_type();
		WIFU.refresh_map();
	}
	
	function get_mode(){
		return mode;
	}
	
	function get_type(){
		return type;
	}
	
	function show_fields_for_type(){
		if(type == NETWORKS){
			$('#options_network_specific').show();
			$("#sort_by_property option[value='length_probe_requests']").hide();
			$('#options_client_specific').hide();
			$("#sort_by_property option[value='essid']").show();
			$("#sort_by_property option[value='length_clients']").show();
			$("#sort_by_property option[value='hostname']").hide();
		}
		else{
			$('#options_network_specific').hide();
			$("#sort_by_property option[value='length_probe_requests']").show();
			$('#options_client_specific').show();
			$("#sort_by_property option[value='essid']").hide();
			$("#sort_by_property option[value='length_clients']").hide();
			$("#sort_by_property option[value='hostname']").show();
		}
	}
	
	function get_querystring_from_options(){
		var qs = "";
		if($('#options_essid').val().length > 0) { qs += "&essid=" + $('#options_essid').val(); }
		if($('#options_bssid').val().length > 0) { qs += "&bssid=" + $('#options_bssid').val(); }
		if($('#options_probing_for_ssid').val().length > 0) { qs += "&probing_for_ssid=" + $('#options_probing_for_ssid').val(); }
		if($('#options_has_hostname').is(':checked')) { qs += "&has_hostname=yes"; }
		if($('#options_hostname').val().length > 0) { qs += "&hostname=" + $('#options_hostname').val(); }
		if($('#options_encryption_none').is(':checked')) { qs += "&encryption=None"; }
		if($('#options_encryption_wep').is(':checked')) { qs += "&encryption=WEP"; }
		if($('#options_encryption_wpa').is(':checked')) { qs += "&encryption=WPA"; }
		if($('#options_essid_id_hidden').val().length > 0) { qs += "&essid_is_hidden=" + $('#options_essid_id_hidden').val(); }
		if($('#options_client_mac').val().length > 0) { qs += "&client_mac=" + $('#options_client_mac').val(); }
		if($('#options_seen_after_date').val().length > 0) { qs += "&seen_after_date=" + $('#options_seen_after_date').val(); }
		if($('#options_seen_before_date').val().length > 0) { qs += "&seen_before_date=" + $('#options_seen_before_date').val(); }
		if($('#options_max_metres_greater_than').val().length > 0) { qs += "&max_metres_greater_than=" + $('#options_max_metres_greater_than').val(); }
		if($('#options_max_metres_less_than').val().length > 0) { qs += "&max_metres_less_than=" + $('#options_max_metres_less_than').val(); }
		if($('#options_number_of_times_seen_greater_than').val().length > 0) { qs += "&times_seen_greater_than=" + $('#options_number_of_times_seen_greater_than').val(); }
		if($('#options_number_of_times_seen_less_than').val().length > 0) { qs += "&times_seen_less_than=" + $('#options_number_of_times_seen_less_than').val(); }
		if($('#sort_by_property').val().length > 0) { 
			qs += "&sort_by_property=" + $('#sort_by_property').val(); 
			qs += "&sort_by_direction=" + $('#sort_by_direction').val(); 
		}
		if($('#options_max_records').val().length > 0) { qs += "&max_records=" + $('#options_max_records').val(); }
		return qs;
	}

	return {
		init: init,
		get_mode: get_mode,
		BROWSE: BROWSE,
		SEARCH: SEARCH,
		get_type: get_type,
		NETWORKS: NETWORKS,
		CLIENTS: CLIENTS,
		get_querystring_from_options: get_querystring_from_options
	};
}(jQuery));

WIFU.RESULTS = (function ($){
	function clear(){
		$('#results_pane ul').empty();
	}
	
	function set_results_found(count, total_count){
		$('#results_found').text(count + '/' + total_count);
	}
	
	function add_network_marker(network_marker){
		var li_html = "<li><span class='result_title'>" + network_marker.essid + '</span>';
		if(network_marker.number_of_clients > 1){
			li_html += '<br>Clients:' + network_marker.number_of_clients;
		}
		li_html += '</li>';
		var li = $(li_html);
		var actual_listitem = li.get(0);
		$.data(actual_listitem, 'network_marker', network_marker);
		$('#results_pane ul').append(li);
		$(li).click(function (){
			WIFU.load_and_show_network($(this).data('network_marker').network_bssid);
		});
	}
	
	function add_client_marker(client_marker){
		var title = client_marker.hostname;
		if (!client_marker.hostname){
			title = client_marker.client_mac;
		}
		var li_html = "<li><span class='result_title'>" + title + '</span>';
		if(client_marker.hostname){
			li_html += '<br>' + client_marker.client_mac;
		}
		if(client_marker.number_of_networks > 1){
			li_html += '<br>Networks:' + client_marker.number_of_networks;
		}
		if(client_marker.number_of_probe_requests > 1){
			li_html += '<br>Probe Requests:' + client_marker.number_of_probe_requests;
		}
		li_html += '</li>';
		var li = $(li_html);
		var actual_listitem = li.get(0);
		$.data(actual_listitem, 'client_marker', client_marker);
		$('#results_pane ul').append(li);
		$(li).click(function (){
			WIFU.load_and_show_client($(this).data('client_marker').client_mac);
		});
	}
	
	return {
		clear: clear,
		add_client_marker: add_client_marker,
		add_network_marker: add_network_marker,
		set_results_found: set_results_found
	};
}(jQuery));

WIFU.DETAILS = (function ($){
	function init(){
		$('#client_details_close_window').click(function (){
			hide();
		});
		
		$('#network_details_close_window').click(function (){
			hide();
		});
	}
	
	function show_network_details(network_details){
		hide();
		var actual_details_pane = $('#network_details_pane').get(0);
		$.data(actual_details_pane, 'network_details', network_details);
		$('#network_details_essid').text(network_details.essid);
		$('#network_details_bssid').text(network_details.network_bssid);
		$('#network_details_is_hidden').text(network_details.is_hidden ? "Yes" : "No");
		$('#network_details_encryptions').text(network_details.encryptions);
		$('#network_details_seen_first_time').text(network_details.seen_first_time);
		$('#network_details_seen_last_time').text(network_details.seen_last_time);
		$('#network_details_total_packets').text(network_details.total_packets);
		$('#network_details_number_of_times_seen').text(network_details.number_of_times_seen);
		$('#network_details_max_metres_between_locations').text(network_details.max_metres_between_locations);
		$('#network_details_location').text(network_details.lat.toFixed(5) + ", " + network_details.lon.toFixed(5));
		$('#network_details_clients').empty();
		network_details.clients.forEach(function (client){
			var title = client.hostname;
			if (!client.hostname){
				title = client.client_mac;
			}
			var li_html = '<li>' + title;
			if(client.number_of_probe_requests > 0){
				li_html += "<br><span class='details_sub_detail'>Probe Requests: " + client.number_of_probe_requests + '</span>';
			}
			if(client.number_of_networks > 1){
				li_html += "<br><span class='details_sub_detail'>Networks: " + client.number_of_networks + '</span>';
			}
			li_html += '</li>';
			var client_li = $(li_html);
			$('#network_details_clients').append(client_li);
			client_li.click(function (){
				WIFU.load_and_show_client(client.client_mac);
			});
		});
		$('#network_details_locations').empty();
		network_details.location_markers.forEach(function (location_marker){
			var location_marker_li = $('<li>' + location_marker.seen_time + '</li>');
			$('#network_details_locations').append(location_marker_li);
			location_marker_li.click(function (){
				WIFU.show_network_location_marker(location_marker);
			});
		});
		$('#network_details_pane').show();
	}
	
	function show_client_details(client_details){
		hide();
		var actual_details_pane = $('#client_details_pane').get(0);
		$.data(actual_details_pane, 'client_details', client_details);
		if (!client_details.hostname){
			$('#client_details_hostname_section').hide();
			$('#client_details_hostname').text('');
		} else {
			$('#client_details_hostname_section').show();
			$('#client_details_hostname').text(client_details.hostname);
		}
		$('#client_details_client_mac').text(client_details.client_mac);
		$('#client_details_seen_first_time').text(client_details.seen_first_time);
		$('#client_details_seen_last_time').text(client_details.seen_last_time);
		$('#client_details_total_packets').text(client_details.total_packets);
		$('#client_details_number_of_times_seen').text(client_details.number_of_times_seen);
		$('#client_details_max_metres_between_locations').text(client_details.max_metres_between_locations);
		$('#client_details_networks').empty();
		var client_details_networks_section = $('#client_details_networks_section');
		if(client_details.networks.length > 0) { client_details_networks_section.show(); } else { client_details_networks_section.hide(); }
		client_details.networks.forEach(function (network){
			var network_li = $('<li>' + network.essid + '</li>');
			$('#client_details_networks').append(network_li);
			network_li.click(function (){
				WIFU.load_and_show_network(network.bssid);
			});
		});
		$('#client_details_probe_requests').empty();
		var client_details_probe_requests_section = $('#client_details_probe_requests_section');
		if(client_details.probe_requests.length > 0) { client_details_probe_requests_section.show(); } else { client_details_probe_requests_section.hide(); }
		client_details.probe_requests.forEach(function (probe_request){
			var li_html = '<li>' + probe_request.ssid;
			if (probe_request.number_of_times_seen > 1){
				li_html += ' (' + probe_request.number_of_times_seen + ')';
			}
			li_html += '</li>';
			$('#client_details_probe_requests').append(li_html);
		});
		$('#client_details_locations').empty();
		var client_details_locations_section = $('#client_details_locations_section');
		if(client_details.location_markers.length > 0) { client_details_locations_section.show(); } else { client_details_locations_section.hide(); }
		client_details.location_markers.forEach(function (location_marker){
			var location_marker_li = $('<li>' + location_marker.seen_time + '</li>');
			$('#client_details_locations').append(location_marker_li);
			location_marker_li.click(function (){
				WIFU.show_client_location_marker(location_marker);
			});
		});
		$('#client_details_pane').show();
	}
	
	function hide(){
		$('#client_details_pane').hide();
		$('#network_details_pane').hide();
	}
	
	return {
		init: init,
		hide: hide,
		show_client_details: show_client_details,
		show_network_details: show_network_details
	};
}(jQuery));

$(document).ready(function(){
	WIFU.init();
	WIFU.OPTIONS.init();
	WIFU.DETAILS.init();
});