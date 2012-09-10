#! /usr/bin/env python
# requres libraries requests lxml

import requests, os
from lxml import etree

def log(logString, debug=False):
	if (not debug) or Config.DEBUG:
		print logString

class Config:
	ROOTPATH = "."
	DEBUG = True
	
class User:
	_changesetDataString = ''
	_changesetXmlRoot = ''
	_uid = ''
	_user = ''
	
	def loadChangesetFromString(self, dataString):
		self._changesetXmlRoot = etree.fromstring(dataString)

	def loadValuesFromChangeset(self):
		changesetCount = len(self._changesetXmlRoot)
		if changesetCount > 0: # not what happens if there are no edits at all
			log("User XML contains {0} changeset Elements".format(changesetCount))
			firstChangesetElement = self._changesetXmlRoot[0]
			self._uid = firstChangesetElement.get('uid')
			self._user = firstChangesetElement.get('user')
		else:
			log("User XML contains no changeset Element", debug=True)


class UserFile:
	_isLoaded = False
	_dataFolder = "userdata"
	_data = ''
	_name = ''
	_user = ''
	_userChangeSetUrl = "http://api.openstreetmap.org/api/0.6/changesets?display_name={0}"

	def __init__(self, name, update=False):
		self._name = name

	def loadData(self):
		dataPath = Config.ROOTPATH + "/" + self._dataFolder + "/" + self._name + ".xml"
		if not os.path.exists(dataPath):
			log(dataPath + " does not exist. Downloading")
			r = requests.get(self._userChangeSetUrl.format(self._name))
			if r.status_code == 200:
				f = open(dataPath, "w")
				f.write(r.text)
				self._data = r.text
				self._isLoaded = True
		else:
			log(dataPath + " exists already. Skipping Download")
			f = open(dataPath, "r")
			self._data = f.read()
			self._isLoaded = True

		if self._isLoaded:
			self._user = User()
			self._user.loadChangesetFromString(self._data)
			self._user.loadValuesFromChangeset()
			print self._user._uid
			print self._user._user

	def updateData(self):
		if self._isLoaded:
			pass


	def getLastChangeDate(self):
		pass
		# TODO

def main():
	# test = UserFile("bimal(Adyota)")
	test = UserFile("prabhasp")
	test.loadData();

if __name__ == '__main__':
	main()