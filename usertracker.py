#! /usr/bin/env python
# requres libraries requests lxml

import requests, os, time, sys
from lxml import etree

class Config:
	ROOTPATH = "."
	DEBUG = True

def log(logString, debug=False):
	if (not debug) or Config.DEBUG:
		print(logString)
	
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
			log("User XML contains {0} changeset Elements".format(changesetCount), debug=True)
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

	def getChangesetIdList(self):
		changesetIdList = []
		for changesetElement in self._changesetXmlRoot:
			changesetIdList.append(changesetElement.get('id'))
		return changesetIdList

	def printData(self):
		userData = {}

		# organize by date
		for changesetElement in self._changesetXmlRoot: # considering the data is generated date wize
			createdAtDateStr = changesetElement.get("created_at")
			createdAtDate = time.strptime(changesetElement.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
			createdAtDateOnlyStr = time.strftime('%Y-%m-%d', createdAtDate)
			
			if not userData.has_key(createdAtDateOnlyStr):
				userData[createdAtDateOnlyStr] = {}
				createCount = {'node':0, 'relation':0, 'way':0}
				modifyCount = {'node':0, 'relation':0, 'way':0}
			
			changeFile = UserChangeFile(changesetElement.get("id"))
			changeFile.loadFileData()
			changeFileXmlRoot = etree.fromstring(changeFile.getData())
			
			g = lambda x:x.get('id')
			create = {}
			create['node'] = map(g, changeFileXmlRoot.xpath('/osmChange/create/node'))
			create['way'] = map(g, changeFileXmlRoot.xpath('/osmChange/create/way'))
			create['relation'] = map(g, changeFileXmlRoot.xpath('/osmChange/create/relation'))

			modify = {}
			modify['node'] = map(g, changeFileXmlRoot.xpath('/osmChange/modify/node'))
			modify['way'] = map(g, changeFileXmlRoot.xpath('/osmChange/modify/way'))
			modify['relation'] = map(g, changeFileXmlRoot.xpath('/osmChange/modify/relation'))

			userData[createdAtDateOnlyStr][changesetElement.get("id")] = {'create':create, 'modify':modify}

			createCount['node'] = createCount['node'] + len(create['node'])
			createCount['way'] += len(create['way'])
			createCount['relation'] += len(create['relation'])

			modifyCount['node'] += len(modify['node'])
			modifyCount['way'] += len(modify['way'])
			modifyCount['relation'] += len(modify['relation'])

			userData[createdAtDateOnlyStr]['createCount'] = createCount
			userData[createdAtDateOnlyStr]['modifyCount'] = modifyCount

		for day in sorted(userData.keys()):
			print day
			print "CreateCount ::", userData[day]['createCount']
			print "ModifyCount ::", userData[day]['modifyCount']

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
				f.close()
				self._data = r.text.encode('utf-8')
				self._isLoaded = True
		else:
			self.loadFileData()

	def loadFileData(self):
		dataPath = self._dataFolder + "/" + self._fileName
		if os.path.exists(dataPath):
			f = open(dataPath, "r")
			self._data = f.read()
			self._isLoaded = True

	def isLoaded(self):
		return self._isLoaded

	def getData(self):
		return self._data


class UserChangeFile(FileDownloader):
	_fileName = ""
	_dataFolder = "userdata/changesets"
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

	def loadChangesetData(self):
		if self._isLoaded:
			self._user = User()
			self._user.loadChangesetFromString(self._data)
			self._user.loadValuesFromChangeset()
			print(self._user._uid)
			print(self._user._user)
			changesetIdList = self._user.getChangesetIdList()
			for changesetId in changesetIdList:
				changesetFile = UserChangeFile(changesetId)
				changesetFile.download()

	def updateData(self):
		if self._isLoaded:
			pass

	def printData(self):
		self._user.printData()

	

def main():
	if len(sys.argv) < 2:
		print "Usage: usertracker.py osm_username"
		exit(-1)

	username = sys.argv[1]
	log("Downloading data for {0}".format(username))

	userFile = UserFile(username)
	userFile.loadData()
	userFile.loadChangesetData()
	userFile.printData()

if __name__ == '__main__':
	main()