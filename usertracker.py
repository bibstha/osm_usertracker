#! /usr/bin/env python
# requres libraries requests lxml

import requests, os
from lxml import etree

def log(logString, debug=False):
	if (not debug) or Config.DEBUG:
		print(logString)

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

	def getLastElement(self):
		lastElement = False
		if len(self._changesetXmlRoot) > 0:
			lastElement = self._changesetXmlRoot[0]
		return lastElement

	def getChangeSetIdList(self):
		changesetIdList = []
		for changesetElement in self._changesetXmlRoot:
			changesetIdList.append(changesetElement.get('id'))
		return changesetIdList

class FileDownloader:
	_isLoaded = False
	_dataFolder = "userdata"
	_fileName = ""
	_url = ""
	_data = ""

	def __init__(self, fileName, url, dataFolder = None):
		if (dataFolder):
			self._dataFolder = dataFolder
		self._fileName = fileName
		self._url = url

	def download(self):
		dataPath = self._dataFolder + "/" + self._fileName
		if not os.path.exists(dataPath):
			log(dataPath + " does not exist. Downloading")
			r = requests.get(self._url)
			if r.status_code == 200:
				f = open(dataPath, "w")
				f.write(r.text.encode('utf-8'))
				self._data = r.text.encode('utf-8')
				self._isLoaded = True
		else:
			log(dataPath + " exists already. Skipping Download")
			f = open(dataPath, "r")
			self._data = f.read().encode('utf-8')
			self._isLoaded = True

	def isLoaded(self):
		return self._isLoaded


class UserChangeFile(FileDownloader):
	_fileName = ""
	_urlTemplate = "http://api.openstreetmap.org/api/0.6/changeset/{0}/download"
	_url = ""

	def __init__(self, changesetId):
		self._fileName = changesetId + ".xml"
		self._url = self._urlTemplate.format(changesetId)



class UserFile(FileDownloader):
	_name = ''
	_user = ''
	_urlTemplate = "http://api.openstreetmap.org/api/0.6/changesets?display_name={0}"

	def __init__(self, name, update=False):
		self._name = name
		self._url = self._urlTemplate.format(name)
		self._fileName = name + ".xml"

	def loadData(self):
		self.download()

		if self._isLoaded:
			self._user = User()
			self._user.loadChangesetFromString(self._data)
			self._user.loadValuesFromChangeset()
			print(self._user._uid)
			print(self._user._user)
			changesetIdList = self._user.getChangeSetIdList()
			for changesetId in changesetIdList:
				changesetFile = UserChangeFile(changesetId)
				changesetFile.download()

	def updateData(self):
		if self._isLoaded:
			pass


	def getLastChangeDate(self):
		pass
		# TODO

def main():
	#test = UserFile("bimal(Adyota)")
	test = UserFile("prabhasp")
	test.loadData();

if __name__ == '__main__':
	main()