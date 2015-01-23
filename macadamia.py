#!/usr/bin/python
#-*- coding: utf-8 -*-
import os, sys
import string, re, base64
import bencode, hashlib
import urllib, pycurl
from StringIO import StringIO
from sites import *
from bs4 import BeautifulSoup

class Macadamia:
	def __init__(self, keyword):
		self.MAGNETS = []
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

	def addTorrent(self, host, title, seed):
		torrentInfo = self.tor2magnet(seed)
		torrentInfo["title"] = title
		torrentInfo["binary"] = seed
		torrentInfo["hostedBy"] = host
		if torrentInfo["name"] == "":
			torrentInfo["name"] = "".join(i for i in title if i not in "\/:*?<>|")

		self.MAGNETS.append(torrentInfo)

	def getHostedSites(self):
		sites = set()
		for entry in self.MAGNETS:
			sites.add(entry["hostedBy"])

		return string.join(sites, ", ")

	def export(self, argument):
		if len(argument) == 0 :
			self.exportRss("")
		elif len(argument) - argument.rfind(".rss") == 3 :
			self.exportRss(argument)
		elif len(argument) - argument.rfind("/") == 1 :
			for entry in self.MAGNETS:
				fd = open(argument + entry["name"] + ".torrent", "wb")
				fd.write(entry["binary"])
				fd.close()
		else :
			self.exportRss("")

	def exportRss(self, rssFile):
		print "Exporting ..."
		doc = BeautifulSoup("<rss version=\"2.0\"></rss>", "xml")
		doc.rss.append(doc.new_tag("channel"))
		doc.rss.channel.append(doc.new_tag("title"))
		doc.rss.channel.append(doc.new_tag("description"))
		doc.rss.channel.title.insert(0, "Macadamia: RSS for \"" + self.KEYWORD + "\"")
		doc.rss.channel.description.insert(0, "Macadamia generated RSS for \"" + self.KEYWORD + "\" searched from " + self.getHostedSites())

		for entry in self.MAGNETS:
			item = doc.new_tag("item");
			item.append(doc.new_tag("title"))
			item.append(doc.new_tag("link"))
			item.append(doc.new_tag("description"))
			item.title.insert(0, entry["name"])
			item.link.insert(0, entry["magnet"])
			item.description.insert(0, "Torrent from " + entry["hostedBy"])
			doc.rss.channel.append(item)

		rssData = doc.prettify()

		if rssFile == "" :
			print rssData
		else :
			fd = open(rssFile, "w")
			fd.write(rssData.encode("utf8"))
			fd.close()
