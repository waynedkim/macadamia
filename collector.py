#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys, macadamia

if len(sys.argv) != 2 :
	print " * Usage: " + sys.argv[0] + " KEYWORD\n"
	sys.exit(1)

myMagnets = macadamia.Macadamia(sys.argv[1])

# Retrieve torrent from seeder sites
myMagnets._from("gwtorrent")
myMagnets._from("torrentbest")

# Export as a torrent files into the directory
myMagnets.export("./example/")
# Export as a rss file
myMagnets.export("example.rss")
# Export screen
myMagnets.export("")
