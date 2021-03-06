#!/usr/bin/python3

import re
import os
import sys
import datetime

class RTXConfiguration:

	#### Constructor
	def __init__(self):
		self.version = "RTX 0.5.4"

		# This is the flag/property to switch between the two containers
		self.live = "Production"
		#self.live = "KG2"
		#self.live = "rtxdev"
		#self.live = "staging"

		if self.live == "Production":
			self.bolt = "bolt://rtx.ncats.io:7687"
			self.database = "rtx.ncats.io:7474/db/data"

		if self.live == "KG2":
			self.bolt = "bolt://rtx.ncats.io:7787"
			self.database = "rtx.ncats.io:7574/db/data"

		if self.live == "rtxdev":
			self.bolt = "bolt://rtxdev.saramsey.org:7887"
			self.database = "rtxdev.saramsey.org:7674/db/data"

		if self.live == "staging":
			self.bolt = "bolt://steveneo4j.saramsey.org:7687"
			self.database = "steveneo4j.saramsey.org:7474/db/data"


	#### Define attribute version
	@property
	def version(self) -> str:
		return self._version

	@version.setter
	def version(self, version: str):
		self._version = version

	@property
	def live(self) -> str:
		return self._live

	@live.setter
	def live(self, live: str):
		self._live = live

	@property
	def bolt(self) -> str:
		return self._bolt

	@bolt.setter
	def bolt(self, bolt: str):
		self._bolt = bolt

	@property
	def database(self) -> str:
		return self._database

	@database.setter
	def database(self, database: str):
		self._database = database


def main():
	rtxConfig = RTXConfiguration()
	print("RTX Version string: " + rtxConfig.version)
	print("live version: %s" % rtxConfig.live)
	print("bolt protocol: %s" % rtxConfig.bolt)
	print("database: %s" % rtxConfig.database)


if __name__ == "__main__": main()
