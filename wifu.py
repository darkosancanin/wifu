import argparse
import sys

from wifu.DataRepository import DataRepository
from wifu.HostnameImporter import HostnameImporter
from wifu.NetXmlImporter import NetXmlImporter
from wifu.ViewerDataRepository import ViewerDataRepository
from wifu.ViewerHttpServer import ViewerHttpServer

def get_argument_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--database", dest="path", help="path to sqlite database file")
	parser.add_argument("-x", dest="ignore_already_imported_error", help="ignore already imported error", action='store_true')
	parser.add_argument("-i", "--import", dest="import_path", help="import netxml files", nargs='*')
	parser.add_argument("-n", "--hostname", dest="hostnames_import_path", help="import hostnames", nargs='*')
	parser.add_argument("-v", "--viewer", help="start the web server to view the data", action='store_true')
	parser.add_argument("-p", "--port", help="port number on which to start the web server")
	parser.add_argument("-s", "--stats", help="show database statistics", action='store_true')
	return parser
	
def parse_arguments():
	parser = get_argument_parser()
	args = parser.parse_args()
	return args

def main():
	args = parse_arguments()
	option_selected = False
	if args.import_path is not None:
		data_repository = DataRepository(args.path, True)
		net_xml_importer = NetXmlImporter(data_repository, args.ignore_already_imported_error)
		net_xml_importer.import_files(args.import_path)
		option_selected = True
	if args.hostnames_import_path is not None:
		data_repository = DataRepository(args.path, True)
		hostname_importer = HostnameImporter(data_repository, args.ignore_already_imported_error)
		hostname_importer.import_files(args.hostnames_import_path)
		option_selected = True
	if args.stats == True:
		data_repository = DataRepository(args.path, False)
		data_repository.print_db_stats()
		option_selected = True
	if args.viewer == True:
		viewer_data_repository = ViewerDataRepository(args.path)
		viewer_http_server = ViewerHttpServer(viewer_data_repository)
		viewer_http_server.start(args.port)
		option_selected = True
	if option_selected == False:
		get_argument_parser().print_help()
	sys.exit(0)

if __name__ == '__main__':
    main()