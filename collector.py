#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
import argparse
import macadamia
import BaseHTTPServer

def run_as_server():
	PORT = 8080
	Server = BaseHTTPServer.HTTPServer
	httpd = Server(("", PORT), macadamia.MacadamiaServer)

	while True:
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			break

def run_instantly(keyword):
	Seeds = macadamia.Macadamia(keyword)

	# Retrieve torrent from seeder sites
	Seeds._from("tosarang2")

	# Export screen
	print Seeds._basket()
	# Export as a torrent files into the directory
	#Seeds.store_in("./example/")
	Seeds.store_in("./seeds/")
	# Export as a rss file
	Seeds.store_rss("example.rss")

options = argparse.ArgumentParser(description="Macadamia: Automatic torrent seed collector")
group = options.add_mutually_exclusive_group(required=True)
group.add_argument("--server", action="store_true", help="run collector as rss server")
group.add_argument("--keyword", action="store", help="instant search with given keyword")
args = options.parse_args()

if args.server == True:
	run_as_server()
elif len(args.keyword) > 0:
	run_instantly(args.keyword)
else:
	options.print_help()
