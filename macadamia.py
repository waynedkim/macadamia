#!/usr/bin/python
#-*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.getcwd())

import string, re, base64
import bencode, hashlib
import urllib, pycurl
from sites import *
import BaseHTTPServer
from StringIO import StringIO
from bs4 import BeautifulSoup

class Macadamia:
	def __init__(self, keyword):
		self.BASKET = []
		self.KEYWORD = keyword

	def _from(self, siteName):
		print "Searching in " + siteName + " ..."
		eval(siteName).do(self)

	def retrieve(self, url):
		buffer = StringIO()
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, url)
		curl.setopt(pycurl.WRITEDATA, buffer)
		curl.setopt(pycurl.FOLLOWLOCATION, 1)
		curl.setopt(pycurl.COOKIEJAR, '/tmp/cookie.txt')
		curl.setopt(pycurl.COOKIEFILE, '/tmp/cookie.txt')
		curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 Safari/537.36")
		curl.perform()
		curl.close()
		return buffer.getvalue()

	def tor2magnet(self, seed):
		try:
			meta = bencode.bdecode(seed)
			contents_hash = bencode.bencode(meta['info'])
			digest = hashlib.sha1(contents_hash).digest()
			b32hash = base64.b32encode(digest)
			params = {'xt': 'urn:btih:%s' % b32hash,
				  'dn': meta['info']['name']}

			announces = ''
			for announce in meta['announce-list']:
				announces += '&' + urllib.urlencode({'tr': announce[0]})

			params = urllib.urlencode(params) + announces
			magnet = "magnet:?%s" % params
			return {"name": meta['info']['name'],
					"magnet": magnet}
		except:
			return {"name": "", "magnet": ""}

	def checkTorrent(self, seed):
		magicCode = seed[0:2]
		if magicCode == "d8":
			return True
		else:
			return False

	def addTorrent(self, host, title, seed):
		torrentInfo = self.tor2magnet(seed)
		torrentInfo["title"] = title
		torrentInfo["binary"] = seed
		torrentInfo["hostedBy"] = host
		if torrentInfo["name"] == "":
			torrentInfo["name"] = "".join(i for i in title if i not in "\/:*?<>|")

		self.BASKET.append(torrentInfo)

	def getHostedSites(self):
		sites = set()
		for entry in self.BASKET:
			sites.add(entry["hostedBy"])

		return string.join(sites, ", ")

	def _basket(self):
		return self.exportRss()

	def store_rss(self, rss):
		fd = open(rss, "w")
		fd.write(self.exportRss().encode("utf8"))
		fd.close()

	def store_in(self, here):
		if os.path.isdir(here) == False:
			print "Invalid exporting directory ..."
			return False

		for entry in self.BASKET:
			fd = open(here + entry["name"] + ".torrent", "wb")
			fd.write(entry["binary"])
			fd.close()

	def exportRss(self):
		print "Transforming in RSS ..."
		doc = BeautifulSoup("<rss version=\"2.0\"></rss>", "xml")
		doc.rss.append(doc.new_tag("channel"))
		doc.rss.channel.append(doc.new_tag("title"))
		doc.rss.channel.append(doc.new_tag("description"))
		doc.rss.channel.title.insert(0, "Macadamia: RSS for \"" + self.KEYWORD + "\"")
		doc.rss.channel.description.insert(0, "Macadamia generated RSS for \"" + self.KEYWORD + "\" searched from " + self.getHostedSites())

		for entry in self.BASKET:
			item = doc.new_tag("item");
			item.append(doc.new_tag("title"))
			item.append(doc.new_tag("link"))
			item.append(doc.new_tag("description"))
			item.title.insert(0, entry["name"])
			item.link.insert(0, entry["magnet"])
			item.description.insert(0, "Torrent from " + entry["hostedBy"])
			doc.rss.channel.append(item)

		rssData = doc.prettify()
		return rssData

class MacadamiaServer(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		keyword = self.path[1:]

		if keyword == "favicon.ico":
			self.send_response(404)
			self.end_headers()
		elif len(keyword) < 1:
			self.send_response(403)
			self.end_headers()
		else:
			self.send_response(200)
			self.end_headers()
			keyword = urllib.unquote(keyword)

			# FIXME: Wanna do this job at class outside
			Seeds = Macadamia(keyword)
			# Retrieve torrent from seeder sites
			Seeds._from("gwtorrent")
			Seeds._from("torrentbest")

			self.wfile.write(Seeds._basket().encode("utf8"))
