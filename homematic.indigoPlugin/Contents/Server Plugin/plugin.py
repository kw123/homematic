#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# homematic Plugin
# Developed by Karl Wachs
# karlwachs@me.com

import datetime
import json

import subprocess
import os 
import sys
import pwd
import time
import platform
import codecs

import getNumber as GT
import threading
import logging
import copy
import requests
from checkIndigoPluginName import checkIndigoPluginName 

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


# left to be done:
#  
#  check curl -> request for variable action does not work with requests !! works with devices
# 
#
#
#


_dataVersion = 1.0
_defaultName ="Homematic"
## Static parameters, not changed in pgm

#from params-user import *
from params import *


_defaultDateStampFormat = "%Y-%m-%d %H:%M:%S"

######### set new  pluginconfig defaults
# this needs to be updated for each new property added to pluginProps. 
# indigo ignores the defaults of new properties after first load of the plugin 
kDefaultPluginPrefs = {
	"MSG":										"please enter values",
	"portNumber":								"2121",
	"ipNumber":									"192.168.1.x",
	"ShowGeneral":								True,
	"tempUnit":									"C",
	"ignoreNewDevices":							False,
	"folderNameDevices":						_defaultName,
	"ShowDevices":								False,
	"accept_HEATING":							True,
	"accept_SYSVAR":							True,
	"accept_WatchDog":							True,
	"accept_DutyCycle":							True,
	"ShowDebug":								False,
	"writeInfoToFile":							False,
	"showLoginTest":							True,
	"debugLogic":								False,
	"debugConnect":								False,
	"debugGetData":								False,
	"debugGetData":								False,
	"debugActions":								False,
	"debugDigest":								False,
	"debugUpdateStates":						False,
	"debugTime":								False,
	"debugSpecial":								False,
	"debugAll":									False,
	"ShowExpert":								False,
	"requestTimeout":							"10",
	"delayOffForButtons":						"2",
	"getCompleteUpdateEvery":					"120",
	"getValuesEvery":							"3000" # in millisecs
}

_defaultAllHomematic = { "type":"", "title":"", "indigoId":0, "indigoDevType":"deviceTypeId", "lastErrorMsg":0, "lastmessageFromHomematic":0, "indigoStatus":"active", "homemtaticStatus":"active", "childInfo":{} }

_debugAreas = {}
for kk in kDefaultPluginPrefs:
	if kk.find("debug") == 0:
		_debugAreas[kk.split("debug")[1]] = False


################################################################################
# noinspection PyUnresolvedReferences,PySimplifyBooleanCheck,PySimplifyBooleanCheck
class Plugin(indigo.PluginBase):
	####-----------------			  ---------
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

	
###############  common for all plugins ############
		self.pluginShortName 			= _defaultName
		self.quitNOW					= ""
		self.delayedAction				= {}
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split("Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split("."))
		self.indigoVersion 				= float(major)+float(minor)/10.
		self.indigoRelease 				= release

		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= "init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser("~")
		self.userIndigoDir				= self.MAChome + "/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+"Preferences/Plugins/"+self.pluginId+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +"/plugin.log"

		formats=	{   logging.THREADDEBUG: "%(asctime)s %(msg)s",
						logging.DEBUG:       "%(asctime)s %(msg)s",
						logging.INFO:        "%(asctime)s %(msg)s",
						logging.WARNING:     "%(asctime)s %(msg)s",
						logging.ERROR:       "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:    "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: "%Y-%m-%d %H:%M:%S",		# 5
						logging.DEBUG:       "%Y-%m-%d %H:%M:%S",		# 10
						logging.INFO:        "%Y-%m-%d %H:%M:%S",		# 20
						logging.WARNING:     "%Y-%m-%d %H:%M:%S",		# 30
						logging.ERROR:       "%Y-%m-%d %H:%M:%S",		# 40
						logging.CRITICAL:    "%Y-%m-%d %H:%M:%S" }		# 50
		formatter = LevelFormatter(fmt="%(msg)s", datefmt="%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger("Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.INFO)

		logging.getLogger("requests").setLevel(logging.WARNING)
		logging.getLogger("urllib3").setLevel(logging.WARNING)


		self.indiLOG.log(20,"initializing  ...")
		self.indiLOG.log(20,"path To files:          =================")
		self.indiLOG.log(10,"indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(10,"installFolder           {}".format(self.indigoPath))
		self.indiLOG.log(10,"plugin.py               {}".format(self.pathToPlugin))
		self.indiLOG.log(10,"indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(20,"detailed logging in     {}".format(self.PluginLogFile))
		if self.pluginPrefs.get('showLoginTest', True):
			self.indiLOG.log(20,"testing logging levels, for info only: ")
			self.indiLOG.log( 0,"logger  enabled for     0 ==> TEST ONLY ")
			self.indiLOG.log( 5,"logger  enabled for     THREADDEBUG    ==> TEST ONLY ")
			self.indiLOG.log(10,"logger  enabled for     DEBUG          ==> TEST ONLY ")
			self.indiLOG.log(20,"logger  enabled for     INFO           ==> TEST ONLY ")
			self.indiLOG.log(30,"logger  enabled for     WARNING        ==> TEST ONLY ")
			self.indiLOG.log(40,"logger  enabled for     ERROR          ==> TEST ONLY ")
			self.indiLOG.log(50,"logger  enabled for     CRITICAL       ==> TEST ONLY ")
			self.indiLOG.log(10,"Plugin short Name       {}".format(self.pluginShortName))
		self.indiLOG.log(10,"my PID                  {}".format(self.myPID))	 
		self.indiLOG.log(10,"Achitecture             {}".format(platform.platform()))	 
		self.indiLOG.log(10,"OS                      {}".format(platform.mac_ver()[0]))	 
		self.indiLOG.log(10,"indigo V                {}".format(indigo.server.version))	 
		self.indiLOG.log(10,"python V                {}.{}.{}".format(sys.version_info[0], sys.version_info[1] , sys.version_info[2]))	 

		self.pythonPath = ""
		if os.path.isfile("/Library/Frameworks/Python.framework/Versions/Current/bin/python3"):
				self.pythonPath				= "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
		self.indiLOG.log(20,"using '{}' for utily programs".format(self.pythonPath))

		self.initFileDir()
			

###############  END common for all plugins ############
		#self.sleep(0)
		return
		
####

	####-----------------			  ---------
	def __del__(self):
		indigo.PluginBase.__del__(self)

	###########################		INIT	## START ########################

	####----------------- @ startup set global parameters, create directories etc ---------
	def startup(self):
		if not checkIndigoPluginName(self, indigo): 
			self.sleep(20000)
			exit() 

		try:
			self.initSelfVariables()

			self.currentVersion	= self.readJson(self.indigoPreferencesPluginDir+"dataVersion",defReturn={}).get("currentVersion",{})

			self.setDebugFromPrefs(self.pluginPrefs)

			self.getFolderId()

			self.pluginStartTime = time.time()


		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			exit(0)

		#self.sleep(0)
		return


	###########################		util functions	## START ########################


	####----------------- @ startup set global parameters, create directories etc ---------
	def initSelfVariables(self):
		try:
			self.writeToLogAfter 								= 180 # secs 
			self.useCurlForVar 									= True
			self.curlPath 										= "/usr/bin/curl"
			self.variablesToDevicesLast							= {}
			self.variablesToDevices 							= {}
			self.checkOnThreads 								= time.time()
			self.autosaveChangedValues							= 0
			self.dayReset 										= -1
			self.averagesCounts									= {}
			self.nextFullStateCheck 							= 0 # do a full one at start
			self.nextFullStateCheckAfter						= 251 # secs
			self.oneCycleComplete								= False
			self.lastDevStates									= {} # save execution time, only check those tha have chnaged w/o reading the states
			self.hostDevId										= 0
			self.homematicIdtoTitle								= {}
			self.numberOfRooms									= -1
			self.numberOfDevices								= -1
			self.numberOfVariables								= -1
			self.listOfprograms									= ""
			self.listOfEvents 									= ""
			self.lastSucessfullHostContact						= 0
			self.devStateChangeList								= {}
			self.devNeedsUpdate									= {}
			self.pendingCommand									= {}
			self.requestSession									= ""
			self.getcompleteUpdateLast							= 0
			self.getCompleteUpdateEvery 						= float(self.pluginPrefs.get("getCompleteUpdateEvery", "90"))
			self.getValuesEvery 								= float(self.pluginPrefs.get("getValuesEvery", "10"))/1000.
			self.getValuesLast									= 0
			self.requestTimeout									= float(self.pluginPrefs.get("requestTimeout", "10"))
			self.portNumber										= self.pluginPrefs.get("portNumber", "")
			self.ipNumber										= self.pluginPrefs.get("ipNumber", "")
			self.restartHomematicClass							= {}
			self.folderNameDevicesID							= 0
			self.roomMembers									= {}
			self.allDataFromHomematic							= self.readJson(fName=self.indigoPreferencesPluginDir + "allData.json")
			self.getDataNow										= time.time() + 9999999999
			self.devsWithenabledChildren						= []
			self.newDevice										= False
			self.fillDevStatesErrorLog 							= 0
			self.firstReadAll 									= False
			try: 	self.homematicAllDevices					= self.readJson(self.indigoPreferencesPluginDir+"homematicAllDevices",defReturn={})
			except:	self.homematicAllDevices					= {}
			self.fixAllhomematic()
			
#			self.indiLOG.log(20,"k_supportedDeviceTypesFromHomematicToIndigo :\n{}".format(k_supportedDeviceTypesFromHomematicToIndigo))
#			self.indiLOG.log(20,"k_indigoToHomaticeDevices :\n{}".format(k_indigoToHomaticeDevices))
			#self.indiLOG.log(20,"k_mapHomematicToIndigoDevTypeStateChannelProps :\n{}".format(json.dumps(k_mapHomematicToIndigoDevTypeStateChannelProps, sort_keys=True, indent=2)))
			#self.indiLOG.log(20,"\n\n\nafter  k_mapHomematicToIndigoDevTypeStateChannelProps :\n{}".format(json.dumps(k_mapHomematicToIndigoDevTypeStateChannelProps, sort_keys=True, indent=2)))
			#self.indiLOG.log(20,"k_createStates:\n{}".format(json.dumps(k_createStates, sort_keys=True, indent=2)))


			#time.sleep(1000)
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			exit(0)


		return


	####-----------------	 ---------
	def fixAllhomematic(self, address=""):
		if address == "":
			latestV = "address-vC"
			if latestV not in self.homematicAllDevices:
				self.homematicAllDevices = {}
				self.homematicAllDevices[latestV] = copy.copy(_defaultAllHomematic )
				self.homematicAllDevices[latestV]["indigoStatus"] = "active/comDisabled/deleted"
				self.homematicAllDevices[latestV]["homemtaticStatus"] ="active/gone"
				self.homematicAllDevices[latestV]["childInfo"] = {"homematicStateName1":"indigoId1","homematicStateName2":"indigoId2"} 

	
			for addr in self.homematicAllDevices:
				for dd in _defaultAllHomematic:
					if dd not in self.homematicAllDevices[addr]:
						self.homematicAllDevices[addr][dd] = copy.copy(_defaultAllHomematic[dd] )
		else:
			if address not in self.homematicAllDevices: 
				self.homematicAllDevices[address] = {}
				for dd in _defaultAllHomematic:
					if dd not in self.homematicAllDevices[address]:
						self.homematicAllDevices[address][dd] = copy.copy(_defaultAllHomematic[dd] )

#																																				indigoStatus: active, normal state, comDisabled  igored and dev exists  --  or dev deleted, must be reenabled ]

	####-----------------	 ---------
	def initFileDir(self):

			if not os.path.exists(self.indigoPreferencesPluginDir):
				os.mkdir(self.indigoPreferencesPluginDir)
			if not os.path.exists(self.indigoPreferencesPluginDir):
				self.indiLOG.log(50,"error creating the plugin data dir did not work, can not create: {}".format(self.indigoPreferencesPluginDir)  )
				self.sleep(1000)
				exit()

	####-----------------	 ---------
	def setDebugFromPrefs(self, theDict, writeToLog=True):
		self.debugAreas = []
		try:
			for d in _debugAreas:
				if theDict.get("debug"+d, False): self.debugAreas.append(d)
			if writeToLog: self.indiLOG.log(20,"debug areas: {} ".format(self.debugAreas))
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####-----------------	 ---------
	def isValidIP(self, ip0):
		if ip0 == "localhost": 							return True

		ipx = ip0.split(".")
		if len(ipx) != 4:								return False

		else:
			for ip in ipx:
				try:
					if int(ip) < 0 or  int(ip) > 255: 	return False
				except:
														return False
		return True


	####-----------------	 ---------
	def isValidMAC(self, mac):
		xxx = mac.split(":")
		if len(xxx) != 6:			return False
		else:
			for xx in xxx:
				if len(xx) != 2: 	return False
				try: 	int(xx, 16)
				except: 			return False
		return True
#

	####-------------------------------------------------------------------------####
	def testPing(self, ipN):
		try:
			ss = time.time()
			ret = subprocess.call("/sbin/ping  -c 1 -W 40 -o " + ipN, shell=True) # send max 2 packets, wait 40 msec   if one gets back stop

			#indigo.server.log(  ipN+"-1  {}".format(ret) +"  {}".format(time.time() - ss)  )

			if int(ret) == 0:  return 0
			if self.decideMyLog("Connect"): self.indiLOG.log(10," sbin/ping  -c 1 -W 40 -o {} return-code: {}".format(ipN, ret) )
			self.sleep(0.1)
			ret = subprocess.call("/sbin/ping  -c 1 -W 400 -o " + ipN, shell=True)
			if self.decideMyLog("Connect"): self.indiLOG.log(10,"/sbin/ping  -c 1 -W 400 -o {} ret-code: ".format(ipN, ret) )

			#indigo.server.log(  ipN+"-2  {}".format(ret) +"  {}".format(time.time() - ss)  )

			if int(ret) == 0:  return 0
			return 1
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"ping error", exc_info=True)

		#indigo.server.log(  ipN+"-3  {}".format(ret) +"  {}".format(time.time() - ss)  )
		return 1



	####-------------------------------------------------------------------------####
	def writeJson(self, data, fName="", sort = True, doFormat=True, singleLines= False ):
		try:

			if self.decideMyLog("Logic"): self.indiLOG.log(10,"writeJson: fname:{}, sort:{}, doFormat:{}, singleLines:{}, data:{} ".format(fName, sort, doFormat, singleLines, str(data)[0:100]) )
	
			out = ""
			if data == "": return ""
			if data == {} : return ""
			if data is None: return ""

			if doFormat:
				if singleLines:
					out = ""
					for xx in data:
						out += "\n{}:{}".format(xx, data[xx])
				else:
					try: out = json.dumps(data, sort_keys=sort, indent=2)
					except: pass
			else:
					try: out = json.dumps(data, sort_keys=sort)
					except: pass

			if fName !="":
				f = self.openEncoding(fName,"w")
				f.write(out)
				f.close()
			return out

		except	Exception as e:
			self.indiLOG.log(40,"", exc_info=True)
			self.indiLOG.log(20,"writeJson error for fname:{} ".format(fName))
		return ""




	####-------------------------------------------------------------------------####
	def readJson(self, fName, defReturn={}):
		try:
			if os.path.isfile(fName):
				f = self.openEncoding(fName,"r")
				data = json.loads(f.read())
				f.close()
				return data
			else:
				return defReturn

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.indiLOG.log(20,"readJson error for fName:{} ".format(fName))
		return defReturn



	####-----------------	 ---------
	def getFolderId(self):
		try:
			try:
				self.folderNameDevicesID = indigo.devices.folders.getId(self.pluginPrefs.get("folderNameDevices", _defaultName))
			except:
				pass
			if self.folderNameDevicesID == 0:
				try:
					ff = indigo.devices.folder.create(self.pluginPrefs.get("folderNameDevices", _defaultName))
					self.folderNameDevicesID = ff.id
				except:
					self.folderNameDevicesID = 0
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		return


	####-----------------	 ---------
	def completePath(self,inPath):
		if len(inPath) == 0: return ""
		if inPath == " ":	 return ""
		if inPath[-1] !="/": inPath +="/"
		return inPath

	####-----------------	 ---------
	def printConfigMenu(self,  valuesDict=None, typeId=""):
		try:
			out =  "\n"
			out += "\n "
			out += "\n{}   =============plugin config Parameters========".format(_defaultName)

			out += "\ndebugAreas".ljust(40)								+	"{}".format(self.debugAreas)
			out += "\nlogFile".ljust(40)								+	self.PluginLogFile
			out += "\nipNumber".ljust(40)								+	self.ipNumber
			out += "\nport#".ljust(40)									+	self.portNumber
			out += "\nread values every".ljust(40)						+	"{}".format(self.getValuesEvery)
			out += "\nread complete info every".ljust(40)				+	"{}".format(self.getCompleteUpdateEvery)
			out += "\nrequestTimeout".ljust(40)							+	"{}".format(self.requestTimeout)

			out += "\n{}    =============plugin config Parameters========  END\n".format(_defaultName)

			out += self.listOfprograms
			out += self.listOfEvents

			out += "\n     Homematic address -> indigo id, name  =================="
			header = "\nnn  HomematicAddr ----- indigoState HM_state Title-----------------------------------------   IndigoId devType ---------  Indigo name -----------------------------------------------------   child info --------------------------------------------"
			out += header
			sList = []
			addList =[]
			for address in self.homematicAllDevices:
				if address.find("__") >-1: continue
				if len(address) < 2: continue
				sList.append(( self.homematicAllDevices[address]["type"], self.homematicAllDevices[address]["title"], self.homematicAllDevices[address]["indigoId"], address, self.homematicAllDevices[address]["lastErrorMsg"], self.homematicAllDevices[address]["childInfo"], self.homematicAllDevices[address]["indigoStatus"], self.homematicAllDevices[address]["homemtaticStatus"]))
				addList.append(address)

			for address in self.homematicAllDevices:
				if address in addList: continue
				if len(address) < 2: continue
				devId = self.homematicAllDevices[address]["indigoId"]
				if devId not in indigo.devices: continue
				dev = indigo.devices[devId]
				dType  = dev.deviceTypeId
				aname  = dev.states["title"]
				sList.append(( dType, aname, devId, address,""))

			nn = 0
			for items in sorted(sList):
				nn +=1 
				dType 		= items[0]
				htitle 		= items[1]
				indigoId 	= items[2]
				address 	= items[3]
				status		= items[6]
				HMstatus	= items[7]
				if address.find("address") == 0: continue
				iname		= "-----"
				child 		= str(items[5])
				if len(child) < 5: 
					chOut = "no child"
				else:
					chOut = ""
					maxL = 80
					chOut = child[0:maxL]
					if len(child) > maxL:
						for i in range(maxL, len(child), maxL):
							chOut += "\n{:190}{:}".format(" ",child[i:i+maxL])
					
				if address in self.homematicAllDevices:
					indigoId = self.homematicAllDevices[address]["indigoId"]
				if indigoId in indigo.devices:
					try:	
							dev = indigo.devices[indigoId]
							iname = dev.name
							devTypeId = dev.deviceTypeId
							htitle = dev.states.get("title"," no title")
					except: 
							iname = "no indigo name"
							devTypeId = "no devtype"
							htitle = "no title"
				out += "\n{:<4}{:20}{:12}{:9}{:45}{:12} {:19}{:68}{:}".format(nn, address, status, HMstatus, htitle, indigoId, dType, iname, chOut)
 
			out += header
			out += '\n'
			out += '\n'
			out += '\n'
			out += '================================ HELP ===========================\n'
			out += 'to install correctly: \n'
			out += '1. install CCU-jack on the raspberry pi \n'
			out += '2. in config set ip # , and if wanted chage folder name etc. For the rest the default should be ok\n'
			out += 'after ~ 10 seconds after config the new devcies should appear in indigo \n'
			out += 'You can configure some devices eg \n'
			out += '   if min/max average.. states should be created\n'
			out += '   if certain child devices should be created eg how many valves are used etc\n'
			out += 'In the plugin menue you can set some devcies to be ignored or used again.\n'
			out += 'Radiators and thermostats are fully supported and can be set\n'
			out += 'You can switch on/off relays, dimmers, set sound and lights in actions\n'
			out += '\n'
			out += '\n'
			out += '\n'
			out += '\n'
			out += '========== For device type ASIR alarm action to work you need to\n'
			out += '   (a) create a system variable on homematic eg "alarmInput" type string\n'
			out += '   (b) add a program with a "Bedingung: Wenn"  "Systemzustand"   alarmInput    "bei": blank, select "bei Aktualisierung ausloesen"  \n'
			out += '       "Aktivitaet dann" leave empty;\n'
			out += '       "Aktivitaet Sonst" "Skript"  <<then put the script here>>    /  and select "sofort"  then save and activate\n'
			out += '   (c) In indigo menu or action you can create an action that will trigger the optical or acustical output.\n'
			out += '        select the ASIR device and the variable you just created.\n'
			out += '\n'
			out += 'start of script   ! are comments --------<<<\n'
			out += '! reads variable alarmInput\n'
			out += '! must be "address/dur unit/durationvalue/acoustic alarm/optical alarm\n'
			out += '! eg 00245F29B40C63/0/10/0/4\n'
			out += '! then send commands to device ASIR to start alarm\n'
			out += '\n'
			out += 'var inp = dom.GetObject("alarmInput").Variable();\n'
			out += 'var debug = false;\n'
			out += 'if (debug){WriteLine(inp)};\n'
			out += '\n'
			out += 'var address = inp.StrValueByIndex("/", 0);\n'
			out += 'var DURATION_UNIT = inp.StrValueByIndex("/", 1);\n'
			out += 'var DURATION_VALUE = inp.StrValueByIndex("/", 2);\n'
			out += 'var ACOUSTIC_ALARM_SELECTION = inp.StrValueByIndex("/", 3);\n'
			out += 'var OPTICAL_ALARM_SELECTION = inp.StrValueByIndex("/", 4);\n'
			out += '\n'
			out += 'if (debug){WriteLine("address:                    "+ address+                  " len:"+ address.Length());}\n'
			out += 'if (address.Length() < 5){quit;};\n'
			out += '\n'
			out += 'if (debug){WriteLine("DURATION_UNIT:              "+ DURATION_UNIT+             " len:"+ DURATION_UNIT.Length().ToString());}\n'
			out += 'if ((DURATION_UNIT.Length() != 1) && (DURATION_UNIT.ToInteger() > 2) ){quit;};   ! = 0,1,2\n'
			out += '\n'
			out += 'if (debug){WriteLine("DURATION_VALUE:             "+ DURATION_VALUE+            " len:"+ DURATION_VALUE.Length());}\n'
			out += 'if ((DURATION_VALUE.Length() >2) && (DURATION_VALUE.ToInteger() > 60)){quit;}; ! = 0-60\n'
			out += '\n'
			out += 'if (debug){WriteLine("ACOUSTIC_ALARM_SELECTION:   "+ ACOUSTIC_ALARM_SELECTION+  " len:"+ ACOUSTIC_ALARM_SELECTION.Length());}\n'
			out += 'if ((ACOUSTIC_ALARM_SELECTION.Length() > 1) && (ACOUSTIC_ALARM_SELECTION.ToInteger() > 7)){quit;}; ! 0,1,2,3,4,5,6,7\n'
			out += '\n'
			out += 'if (debug){WriteLine("OPTICAL_ALARM_SELECTION:    "+ OPTICAL_ALARM_SELECTION+   " len:"+ OPTICAL_ALARM_SELECTION.Length());}\n'
			out += 'if ((OPTICAL_ALARM_SELECTION.Length() > 1) && (OPTICAL_ALARM_SELECTION.ToInteger() > 7)){quit;}; ! 0,1,2,3,4,5,6,7\n'
			out += '\n'
			out += 'dom.GetObject("HmIP-RF."+address+":3.DURATION_UNIT").State(DURATION_UNIT);\n'
			out += 'dom.GetObject("HmIP-RF."+address+":3.DURATION_VALUE").State(DURATION_VALUE);\n'
			out += 'dom.GetObject("HmIP-RF."+address+":3.ACOUSTIC_ALARM_SELECTION").State(ACOUSTIC_ALARM_SELECTION);\n'
			out += 'dom.GetObject("HmIP-RF."+address+":3.OPTICAL_ALARM_SELECTION").State(OPTICAL_ALARM_SELECTION);\n'
			out += ' >>> end of script ------------- \n\n'
			out += '\n'
			out += '\n'
			out += '================================ HELP END =======================\n'

			self.indiLOG.log(20,out)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return

	####-----------------	 ---------
	def padDisplay(self,status):
		if	 status == "up":		 return status.ljust(11)
		elif status == "expired":	 return status.ljust(8)
		elif status == "down":		 return status.ljust(9)
		elif status == "susp":		 return status.ljust(9)
		elif status == "changed":	 return status.ljust(8)
		elif status == "double":	 return status.ljust(8)
		elif status == "ignored":	 return status.ljust(8)
		elif status == "off":		 return status.ljust(11)
		elif status == "REC":		 return status.ljust(9)
		elif status == "ON":		 return status.ljust(10)
		else:						 return status.ljust(10)
		return

	
	####-------------------------------------------------------------------------####
	def readPopen(self, cmd):
		try:
			ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			return ret.decode('utf-8'), err.decode('utf-8')

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	####-------------------------------------------------------------------------####
	def openEncoding(self, fName, readOrWrite, showError=True):

		try:
			if readOrWrite.find("b") >-1:
				return open( fName, readOrWrite)

			if sys.version_info[0]  > 2:
				return open( fName, readOrWrite, encoding="utf-8")

			else:
				return codecs.open( fName, readOrWrite, "utf-8")

		except	Exception as e:
			self.indiLOG.log(20,"openEncoding error w r/w:{}, fname:".format(readOrWrite, fName))
			self.indiLOG.log(40,"", exc_info=True)


	####-----------------	 ---------
	def inpDummy(self, valuesDict=None, typeId="", devId=""):
		return valuesDict



	###########################		util functions	## END  ########################


	###########################		ACTIONS START  ########################
	def getAllDataCallback(self, filter="", valuesDict="", typeId=""):

		self.getcompleteUpdateLast = 0.

		return 
	####-------------action filters  -----------
	def filterDevices(self, filter="", valuesDict="", typeId="", xxx=""):

		try:
			ret = []
			devTypes = k_actionTypes.get(filter,"")
			#self.indiLOG.log(20,"filterDevices: filter given.. filter:{}, devTypes:{}, valuesDict:{}".format(filter, devTypes, valuesDict))
			if devTypes == []: 
				self.indiLOG.log(20,"filterDevices: no proper filter given.. filter:{}, devType:{}".format(filter, devType))
				return ret

			for dev in indigo.devices.iter(self.pluginId):
				#self.indiLOG.log(20,"filterDevices: comparing. devType:{}".format(dev.deviceTypeId))
				if dev.deviceTypeId in devTypes: 
					#self.indiLOG.log(20,"filterDevices: accepted: {}".format(dev.name))
					ret.append([dev.id, dev.name])

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return ret

	####-------------ignore / unignore devices  -----------
	def filterHomematicAllDevices(self, filter="", valuesDict={}, typeId="",xxx=""):

		try:
			retUse = []
			retEna = []
			retIgn = []
			sList = []
			for address in self.homematicAllDevices:
				if address.find("address-") >-1: continue
				if self.homematicAllDevices[address]["type"] in ["RPI-RF-MOD",""," "]: continue  #["STRING","ALARM","ROOM","FLOAT","BOOL",
				sList.append(( self.homematicAllDevices[address]["type"], self.homematicAllDevices[address]["title"], address))


			for items in sorted(sList):
				enabled = False
				exists = False
				try:
					address 	= items[2]
					dType 		= self.homematicAllDevices[address]["type"]
					name 		= self.homematicAllDevices[address]["title"]
					indigoId 	= int(self.homematicAllDevices[address]["indigoId"])
					if indigoId in indigo.devices: 
						enabled = indigo.devices[indigoId].enabled
					else:
						indigoId = 0
						self.homematicAllDevices[address]["indigoId"] = 0
						if self.homematicAllDevices[address]["indigoStatus"] != "create":
							self.homematicAllDevices[address]["indigoStatus"] =  "deleted"
				except:
					self.indiLOG.log(20,"filterDevices: items:{}".format(items))
					continue

				
				if   indigoId > 0 and (self.homematicAllDevices[address]["indigoStatus"] == "active" and enabled):
					retUse.append((address,"{:10s}::{}::{}  ACTIVE".format(dType, name, address)))

				elif  indigoId > 0 and  self.homematicAllDevices[address]["indigoStatus"] in ["comDisabled"]:
					retIgn.append((address,"{:10s}::{}::{}  IGNORED-EXISTING".format(dType, name, address)))

				elif  indigoId == 0 and self.homematicAllDevices[address]["indigoStatus"] in ["deleted"]:
					retIgn.append((address,"{:10s}::{}::{}  IGNORED-DELETED".format(dType, name, address)))

				else:
					retEna.append((address,"{:10s}::{}::{}  ENABLED".format(dType, name, address)))

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return retUse+retEna+retIgn


	####-------------
	def ignoreDevicesButton(self, valuesDict, typeId=""):

		try:
			address = valuesDict["address"]
			if address not in self.homematicAllDevices: return valuesDict

			name = ""
			if address in self.homematicAllDevices and self.homematicAllDevices[address]["indigoId"] in indigo.devices:
				dev = indigo.devices[self.homematicAllDevices[address]["indigoId"]]
				name = dev.name
				indigo.device.enable(dev, value=False)

			elif address in self.homematicAllDevices :
				name = self.homematicAllDevices[address]["title"]

			self.homematicAllDevices[address]["indigoStatus"] = "comDisabled"
			if self.homematicAllDevices[address]["indigoId"] not in indigo.devices:
				self.homematicAllDevices[address]["indigoStatus"] = "deleted"
				self.homematicAllDevices[address]["indigoId"] = 0
			self.writeJson(self.homematicAllDevices, fName=self.indigoPreferencesPluginDir + "homematicAllDevices.json", doFormat=True, singleLines=False )
			self.indiLOG.log(20,"ignoreDevicesButton  set  {}::{}::{}  to IGNORE".format(address, name, self.homematicAllDevices.get(address,{})))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return valuesDict


	####-------------
	def useDevicesButton(self, valuesDict, typeId=""):

		try:
			address = valuesDict["address"]
			if len(address) < 5: return valuesDicts
			if address not in self.homematicAllDevices: return 

			name = ""
			indigoId = self.homematicAllDevices[address]["indigoId"] 
			if indigoId in indigo.devices:
				dev= indigo.devices[indigoId]
				name = dev.name
				indigo.device.enable(dev, value=True)
				self.homematicAllDevices[address]["indigoStatus"] = "active" 

			else:
				name = self.homematicAllDevices[address]["title"]
				self.homematicAllDevices[address]["indigoId"]  = 0
				self.getcompleteUpdateLast = 1
				self.indiLOG.log(20,"useDevicesButton  set  getcompleteUpdateLast = 0")
				self.homematicAllDevices[address]["indigoStatus"] = "create" 

			self.indiLOG.log(20,"useDevicesButton  set  {}::{}::{}  to USE".format(address, name, self.homematicAllDevices.get(address,"")))
			self.writeJson(self.homematicAllDevices, fName=self.indigoPreferencesPluginDir + "homematicAllDevices.json", doFormat=True, singleLines=False )
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return valuesDict


	####-------------
	def removeFromListDevicesButton(self, valuesDict, typeId=""):

		try:
			address = valuesDict["address"]
			if len(address) < 5: return valuesDicts
			if address not in self.homematicAllDevices: return 
			self.indiLOG.log(20,"useDevicesButton  remove   {}::{}  to USE".format(address, self.homematicAllDevices[address]))
			del  self.homematicAllDevices[address]
			self.writeJson(self.homematicAllDevices, fName=self.indigoPreferencesPluginDir + "homematicAllDevices.json", doFormat=True, singleLines=False )
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return valuesDict


	####-------------ignore / unignore devices  ----------- END




	#  ---------- thermostat action  boost
	def boostThermostatAction(self, action, typeId):
		return self.boostThermostat(action.props, typeId)

	def boostThermostat(self, action, typeId=""):

		try:
			
			if self.decideMyLog("Actions"): self.indiLOG.log(20,"boostThermostat action:{}".format(str(action).replace("\n",", ")))

			if not self.isValidIP(self.ipNumber): return 

			dev = indigo.devices[int(action["deviceId"])]

			address = dev.states["address"]

			if dev.deviceTypeId not in k_mapHomematicToIndigoDevTypeStateChannelProps: return 
			acp = k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId].get("actionParams",{})

			props = dev.pluginProps
			dj = json.dumps({"v": action.get("OnOff","on") == "on" })

			if "states" not in acp: return
			state = acp["states"].get("BOOST_MODE","BOOST_MODE")
			channels = acp["channels"].get("BOOST_MODE","1")
			self.doSendAction( channels, address, state, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	# Main thermostat action set target temp called by Indigo Server.
	####-------------
	def boostThermostatAction(self, action, typeId):
		return self.boostThermostat(action.props, typeId)

	####-------------
	def actionControlThermostat(self, action, typeId=""):

		try:
			dev = indigo.devices[action.deviceId]
			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlThermostat  action:{}".format( str(action).replace("\n",", ")))
			if action.thermostatAction == indigo.kThermostatAction.SetHeatSetpoint: 
				value = action.actionValue
			elif action.thermostatAction == indigo.kThermostatAction.DecreaseHeatSetpoint: 
				value = dev.states["setpointHeat"] - action.actionValue
			elif action.thermostatAction == indigo.kThermostatAction.IncreaseHeatSetpoint: 
				value = dev.states["setpointHeat"] + action.actionValue
			else:
				value = 18

			if not self.isValidIP(self.ipNumber): return 

			address = dev.states["address"]

			props = dev.pluginProps
			dj = json.dumps({"v": value })

			if dev.deviceTypeId not in k_mapHomematicToIndigoDevTypeStateChannelProps: return
			acp = k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId].get("actionParams",{})

			if "states" not in acp: return
			state =	acp["states"].get("SET_POINT_TEMPERATURE","SET_POINT_TEMPERATURE")
			channels = acp["channels"].get("SET_POINT_TEMPERATURE",["1"])

			self.doSendAction( channels, address, state, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####-------------
	def sendStringToDisplayAction(self, action, typeId):
		return self.sendStringToDisplay(action.props, typeId)

	####-------------
	def sendStringToDisplay(self, valuesDict, typeId):
		try:
#
#  send something like this 
# curl  -X PUT -d '{"v":"{DDBC=WHITE,DDTC=BLACK,DDA=CENTER,DDS=abc,DDI=2,DDID=1},{DDBC=WHITE,DDTC=BLACK,DDI=1,DDA=CENTER,DDS=def,DDID=2},{DDBC=WHITE,DDTC=BLACK,DDI=3,DDA=CENTER,DDS=Zeile3,DDID=3},{DDBC=WHITE,DDTC=BLACK,DDI=5,DDA=CENTER,DDS=Zeile4,DDID=4},{DDBC=WHITE,DDTC=BLACK,DDI=3,DDA=CENTER,DDS=Zeile5,DDID=5,DDC=true},{R=1,IN=5,ANS=4}"}'  http://192.168.1.49:2121/device/002A60C9950CB5/3/COMBINED_PARAMETER/~pv
#
#
			address = indigo.devices[int(valuesDict["devId"])].states["address"]

			lines = ["","","","",""]
			for ii in range(5):
				jj = str(ii+1)
				for item in ["DDBC","DDTC","DDA","DDS","DDI"]:
					xx =  item+"-"+jj 
					if xx not in valuesDict: # all items must be present 
						lines[ii] = ""
						break
					if item != "DDS" and valuesDict[xx] == "":  # reject lines w empty props, but  accept empty text line = 1 space 
						lines[ii] = ""
						break
					if item == "DDI" and valuesDict[xx] == "0": continue # no icon
						
					lines[ii] +=  item +"="+valuesDict[xx]+","

				if lines[ii] != "": lines[ii] += "DDID="+jj

			#if self.decideMyLog("Actions"): self.indiLOG.log(20,"sendStringToDisplay lines:{}".format(lines))
			outLines = ""
			for nn in range(len(lines)):
				if lines[nn] == "": continue
				outLines += "{"+lines[nn]+"}"+","

			sound = ""
			if "ANS" in valuesDict and valuesDict["ANS"] not in ["","-1"]:
				R = valuesDict.get("ANS","1")
				IN = valuesDict.get("IN","1")
				sound = ",{R="+R+",IN="+IN+",ANS="+valuesDict["ANS"]+"}"

			outLines = outLines.strip(",").strip("}") + ',DDC=true}' +sound
			#if self.decideMyLog("Actions"): self.indiLOG.log(20,"sendStringToDisplay outLines:{}".format(outLines))

			dj = json.dumps({"v":outLines })
			self.doSendAction( ["3"], address, "COMBINED_PARAMETER", dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####- set alarm on ASIR
	def alarmSIRENaction(self, action, typeId):
		return self.alarmSIREN(action.props, typeId)

	def alarmSIREN(self, action, typeId):
		try:
			if self.decideMyLog("Actions"): self.indiLOG.log(20,"alarmASIR action:{}".format(action))

			addressDev = indigo.devices[int(action["alarmDevId"])].states["address"]
			addressVar = indigo.devices[int(action["alarmVarId"])].states["address"]

			DURATION = int(action["DURATION"])
			unit = 0
			if DURATION >= 60:
				DURATION //= 60
				unit = 1
						#address/unit/length/acoust/optical
			dj = { "v":"{}/{}/{}/{}/{}".format(addressDev, unit, DURATION, action["ACOUSTIC_ALARM_SELECTION"], action["OPTICAL_ALARM_SELECTION"]) }
	
			self.doSendActionVariable( addressVar, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)





	####- door lock/unlock 
	####-------------
	def doorLockUnLockAction(self, action, typeId):
		return self.doorLockUnLock(action.props, typeId)

	####-------------
	def doorLockUnLock(self, action, typeId):
		try:


			if self.decideMyLog("Actions"): self.indiLOG.log(20,"doorLockUnLock  action:{}".format( str(action).replace("\n",", ")))

			if not self.isValidIP(self.ipNumber): 
				self.indiLOG.log(30,"doorLockUnLock {}  device:{}, bad IP number:{} ".format(action,self.ipNumber) )
				return 


			address = dev.states["address"].split("-")[0]
			channels = []

			if dev.deviceTypeId not in k_mapHomematicToIndigoDevTypeStateChannelProps: 
				self.indiLOG.log(30,"doorLockUnLock {}  device:{}, bad deviceTypeId:{} ".format(dev.name, action, dev.deviceTypeId) )
				return

			acp =  k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId].get("actionParams",{})


			if self.decideMyLog("Actions"): self.indiLOG.log(20,"doorLockUnLock acp:{}".format(acp))

			if "states" not in acp: 
				self.indiLOG.log(30,"doorLockUnLock {}  device:{}, states not in acp:{} ".format(dev.name, action, acp) )
				return

			dj = "{}"
			for ch in acp["channels"]:
				channels.append(ch) # turn off all channels
			if action["value"] == "lock":
				dj =json.dumps({"v":acp["OnOffValues"]["On"]})
			else:
				dj =json.dumps({"v":acp["OnOffValues"]["Off"]})
			state =	acp["states"].get("OnOff","LOCK_TARGET_LEVEL")

			self.doSendAction( channels, address, state, dj )
								

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		

	####- dimmer relay actions
	####-------------
	def actionControlDimmerRelay(self, action, dev):
		try:


			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay dev:{}, action:{}".format(dev.name, str(action).replace("\n",", ")))

			if not self.isValidIP(self.ipNumber): 
				self.indiLOG.log(30,"actionControlDimmerRelay {}  device:{}, bad IP number:{} ".format(dev.name, action, self.ipNumber) )
				return 


			address = dev.states["address"].split("-")[0]
			channels = []

			if dev.deviceTypeId not in k_mapHomematicToIndigoDevTypeStateChannelProps: 
				self.indiLOG.log(30,"actionControlDimmerRelay {}  device:{}, bad deviceTypeId:{} ".format(dev.name, action, dev.deviceTypeId) )
				return

			acp = k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId].get("actionParams",{})

			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay acp:\n{}".format(acp))

			if "states" not in acp: 
				self.indiLOG.log(30,"actionControlDimmerRelay {}  device:{}, states not in acp:{} ".format(dev.name, action, acp) )
				return

			dj = "{}"

			if action.deviceAction == indigo.kDeviceAction.TurnOn:
				if "mult" in acp:
					dj = json.dumps({"v": round(100* acp["mult"]["Dimm"],2)})
					state =		acp["states"].get("Dimm","")
					for ch in acp["channels"].get("Dimm",["1"]):
						channels.append(ch)	
						break	
				else:
					dj = json.dumps({"v":True })
					state =		acp["states"].get("OnOff","")
					for ch in acp["channels"].get("OnOff",["1"]):
						channels.append(ch)	# turn on only one channel
						break	

			elif action.deviceAction == indigo.kDeviceAction.TurnOff:
				if "mult" in acp:
					dj = json.dumps({"v":0.})
					state =		acp["states"].get("Dimm","")
					for ch in acp["channels"].get("Dimm",["1"]):
						channels.append(ch)	
				else:
					dj = json.dumps({"v":False })
					state =		acp["states"].get("OnOff","")
					for ch in acp["channels"].get("OnOff",["1"]):
						channels.append(ch) # turn off all channels

			elif action.deviceAction == indigo.kDeviceAction.Toggle:
				if "onOffState" in dev.states:
					state =		acp["states"].get("OnOff","")
					if dev.states["onOffState"]:
						dj = json.dumps({"v":False})
						for ch in acp["channels"].get("OnOff",["1"]):
							channels.append(ch) # turn off all channels
					else:
						dj = json.dumps({"v":True})
						for ch in acp["channels"].get("OnOff",["1"]):
							channels.append(ch) # turn only ch 1
							break


			elif action.deviceAction == indigo.kDeviceAction.SetBrightness:
				if action.actionValue == 0:	
					dj = json.dumps({"v":0 })
					state =		acp["states"].get("Dimm","")
					for ch in acp["channels"].get("Dimm",["1"]):
						channels.append(ch) # turn off all channels
				else:
					state =		acp["states"].get("Dimm","")
					if "mult" in acp:
						dj = json.dumps({"v": round(action.actionValue*acp["mult"]["Dimm"] ,2)})
					else:
						dj = json.dumps({"v":action.actionValue})
					for ch in acp["channels"].get("Dimm",["1"]):
						channels.append(ch)	# dimm only one channel
						break
			elif action.deviceAction == indigo.kDeviceAction.SetColorLevels:
				colorCode = 0
				if "whiteLevel"  in action.actionValue:	
					dj = json.dumps({"v":7})
					state = "COLOR"
					evalChannels = [str(eval(acp["channels"].get("Dimm",["1"])[0]))]
					self.doSendAction( evalChannels, address, state, dj )

					state = "LEVEL"
					dj = json.dumps({"v":action.actionValue["whiteLevel"]*acp["mult"].get("Dimm",1)})
					channels = [acp["channels"].get("Dimm",["1"])[0]]

				else:
					minLevel =  (action.actionValue["blueLevel"]  + action.actionValue["greenLevel"]  + action.actionValue["redLevel"])*0.2
					if action.actionValue["blueLevel"]  > minLevel: colorCode +=1
					if action.actionValue["greenLevel"] > minLevel: colorCode +=2
					if action.actionValue["redLevel"]   > minLevel: colorCode +=4
					dj = json.dumps({"v":colorCode})
					channels = [acp["channels"].get("Dimm",["1"])[0]]
					state = "COLOR"

			else:
				self.indiLOG.log(30,"actionControlDimmerRelay  {}  action not suppported  {}".format(dev.name, action))
				state =	acp["states"].get("Dimm","")


			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay channels:{}".format(channels))
			evalChannels = []
			for xx in channels:
				evalChannels.append(str(eval(xx)))
			self.doSendAction( evalChannels, address, state, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,f"{dev.name:}, States\n{dev.states:}\n actionV:{action:}", exc_info=True)

		return 


	####- exec send 
	####-------------
	def doSendAction(self, channels, address, state, dj ):
		try:
			thisRequestSession = requests.Session()
			for ch in channels:	
				html = "http://{}:{}/device/{}/{}/{}/~pv".format(self.ipNumber ,self.portNumber, address, ch, state )
				r = "error"
				if self.decideMyLog("Actions"): self.indiLOG.log(20,"doSendAction html:{}, dj:{}<<".format(html, dj))

				try:
					r = thisRequestSession.put(html, data=dj, timeout=self.requestTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
				except Exception as e:
					self.indiLOG.log(30,"doSendActionVariable  bad return for html:{}, dj:{} ==> {}, err:{}".format(html, dj, r, e))

				if self.decideMyLog("Actions"): self.indiLOG.log(20,"doSendAction ret:{}".format(r))
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		# force refresh of data from homematic
		self.getDataNow = time.time() + min(3.5,self.getValuesEvery)  # it takes ~ 3.5 secs after set to get new value back from homematic
		#if self.decideMyLog("Special"): self.indiLOG.log(20,"setting getDataNow")

		return 

		## exec update variale
	####-------------
	def doSendActionVariable(self, address, dj ):
		try:
			thisRequestSession = requests.Session()
			html = "http://{}:{}/sysvar/{}/~pv".format(self.ipNumber ,self.portNumber, address)
			r = "error"

			if self.useCurlForVar:
				cmd = self.curlPath + " -X PUT -d '" +json.dumps(dj)+"' " + html
				ret = self.readPopen(cmd)
				if self.decideMyLog("Actions"): self.indiLOG.log(20,"doSendActionVariable cmd:{},\nret:{}".format(cmd, ret))

			else:
				if self.decideMyLog("Actions"): self.indiLOG.log(20,"doSendActionVariable html:{}, dj:{}<<".format(html, dj))
				try:
					r = thisRequestSession.put(html, data=dj, timeout=self.requestTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
				except Exception as e:
					self.indiLOG.log(30,"doSendActionVariable  bad return for html:{}, dj:{} ==> {}, err:{}".format(html, dj, r, e))
	
				if self.decideMyLog("Actions"): self.indiLOG.log(20,"doSendActionVariable ret:{}".format(r))
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		# force refresh of data from homematic
		self.getDataNow = time.time() + min(3.5,self.getValuesEvery)  # it takes ~ 3.5 secs after set to get new value back from homematic
		#if self.decideMyLog("Special"): self.indiLOG.log(20,"setting getDataNow")

		return 


	###########################		ACTIONS END  ########################





	###########################		DEVICE	#################################
	####-------------
	def deviceStartComm(self, dev):
		try:
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"starting device:  {}  {} ".format(dev.name, dev.id))
	
			if	self.pluginState == "init":
				dev.stateListOrDisplayStateIdChanged()
				props = dev.pluginProps
				updateProp = True
				if dev.deviceTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps:
					for prop in k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId]["props"]:
						if prop != "" and  props.get(prop,"") == "":
							props[prop] = k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId]["props"][prop]
							updateProp = True
							if self.decideMyLog("Logic"): self.indiLOG.log(10,"starting device:{}  uodating prop from  {}  to {} ".format(dev.name, props[prop], defaultProps[devTdev.deviceTypeIdypeId][prop]))
				if updateProp:
					dev.replacePluginPropsOnServer(props)
	
				if "created" in dev.states and len(dev.states["created"]) < 5:
					self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
	
	
			if "address" in dev.states:
				address = dev.states["address"]
				if len(address) < 2:
					#self.indiLOG.log(20,"starting device:  {}  {}  address empty, states:{}".format(dev.name, dev.id, dev.states))
					if len(dev.address) > 1: 
						address = dev.address
						self.addToStatesUpdateDict(dev, "address", address)
	
				if not  dev.pluginProps.get("isChild", False):
					if address not in self.homematicAllDevices:
						self.fixAllhomematic(address=address)
						self.homematicAllDevices[address]["type"]				= dev.states.get("homematicType","")
						self.homematicAllDevices[address]["title"]				= dev.states.get("title","")
						self.homematicAllDevices[address]["indigoId"]			= dev.id
						self.homematicAllDevices[address]["indigoDevType"]		= dev.deviceTypeId
	
						if dev.states.get("childInfo","") != "":
							try:	
								chId , chn, childDevType  =  json.loads(childInfo)
								if childDevType  in k_mapHomematicToIndigoDevTypeStateChannelProps: 
									if "states"  in k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]: 
										homematicStateNames = k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]["states"]
		
										if chn not in  self.homematicAllDevices[address]["childInfo"]:
											self.homematicAllDevices[address]["childInfo"][chn] = {}
										for homematicStateName in homematicStateNames:
											if homematicStateName not in k_dontUseStatesForOverAllList:
												self.homematicAllDevices[address]["childInfo"][chn][homematicStateName] = chId
										self.homematicAllDevices[address]["childInfo"] = json.loads(dev.states["childInfo"])
							except: pass
	
					try:
						if dev.enabled:
							self.homematicAllDevices[address]["indigoStatus"] = "active"
						else:
							self.homematicAllDevices[address]["indigoStatus"] = "comDisabled"
					except Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"deviceStartComm: homematicAllDevices= {}".format(self.homematicAllDevices[address]), exc_info=True)
	
			if self.pluginState == "run":
				self.devNeedsUpdate[dev.id] = True
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,f"{dev.name:}, States\n{dev.states:}\n actionV:{action:}", exc_info=True)

		return

	####-----------------	 ---------
	def deviceStopComm(self, dev):
		if	self.pluginState != "stop":
			self.devNeedsUpdate[dev.id] = True
			if not dev.enabled and dev.pluginProps.get("isChild",False):
				self.homematicAllDevices[address]["indigoStatus"]	= "comDisabled"
				
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"stopping device:  {}  {}".format(dev.name, dev.id) )

	####-----------------	 ---------
	def deviceDeleted(self, dev):  ### indigo calls this
		if dev.deviceTypeId == "Homematic-Host":
			self.hostDevId = 0
		elif "address" in dev.states:
			address = dev.states["address"]
			if address in self.homematicAllDevices and dev.states.get("childOf","") == "":
				self.homematicAllDevices[address]["indigoId"] = 0
				self.homematicAllDevices[address]["indigoStatus"] = "deleted"
				self.indiLOG.log(30,"removing dev w address:{}, and indigo id:{}, from internal list, indigo device was deleted, setting to ignored, reallow in menu (un)Ignore.. ".format(address, self.homematicAllDevices[address]["indigoId"] ))
		return 


	####-----------------	 ---------
	def xxxdidDeviceCommPropertyChange(self, origDev, newDev):
		#if origDev.pluginProps['xxx'] != newDev.pluginProps['address']:
		#	 return True
		return False


	####-------------------------------------------------------------------------####
	def getDeviceConfigUiValues(self, pluginProps, typeId, devId):
		try:
			theDictList =  super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)

			if typeId == "Homematic-Host":
				theDictList[0]["ipNumber"] = self.pluginPrefs.get("ipNumber","192.168.1.99")
				theDictList[0]["portNumber"] = self.pluginPrefs.get("portNumber","2121")

			return theDictList
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)


	####-----------------	 ---------
	def validateDeviceConfigUi(self, valuesDict=None, typeId="", devId=0):
		try:
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"Validate Device dict:, devId:{}  vdict:{}".format(devId,valuesDict) )
			self.devNeedsUpdate[int(devId)] = True
			errorDict = indigo.Dict()

			if devId != 0:
				dev = indigo.devices[devId]
	
				props = dev.pluginProps	
				if typeId == "Homematic-Host":
					if not self.isValidIP(valuesDict["ipNumber"]):
						errorDict["ipNumber"] = "bad ip number"
						return (False, valuesDict, errorDict)
	
					if devId != 0:
						self.hostDevId = devId
						dev = indigo.devices[devId]
						if 	props.get("ipNumber","") != valuesDict["ipNumber"]:
							self.pluginPrefs["ipNumber"] = valuesDict["ipNumber"]
							self.ipNumber = valuesDict["ipNumber"]
							self.pendingCommand["restartHomematicClass"] = True
	
						if 	props.get("portNumber","") != valuesDict["portNumber"]:
							self.pluginPrefs["portNumber"] = valuesDict["portNumber"]
							self.portNumber = valuesDict["portNumber"]
							self.pendingCommand["restartHomematicClass"] = True
		
						if len(dev.states["created"]) < 10:
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
	
						valuesDict["address"] = valuesDict["ipNumber"]+":"+valuesDict["portNumber"]





			return (True, valuesDict)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		errorDict = valuesDict
		return (False, valuesDict, errorDict)

	###########################		update States start  ########################

	###########################		changed Values Start  ########################
	####-------------------------------------------------------------------------####
	def readChangedValues(self):
		try:
			self.changedValues = {}
			version = "-2"
			## cleanup from older version
			if  os.path.isfile(self.indigoPreferencesPluginDir+"changedValues.json"):
				f = open(self.indigoPreferencesPluginDir + "changedValues.json", "r")
				self.changedValues = json.loads(f.read())
				f.close()
				# check for -Version#, if not correct:  rest storage 
				if version  not in self.changedValues: 
					self.changedValues = {version:"version .. format is: indigoId:{stateList:[[timestamp:value],[timestamp:value],...]}"}

				for devId in copy.copy(self.changedValues):
					if devId.find("-") > -1: continue
					if  int(devId) not in indigo.devices:
						del self.changedValues[devId]
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.saveChangedValues()

	####-------------------------------------------------------------------------####
	def saveChangedValues(self):
		try:
			self.writeJson(self.changedValues, fName=self.indigoPreferencesPluginDir + "changedValues")
		except Exception as e:
			self.exceptionHandler(40, e)




	####-------------------------------------------------------------------------####
	## this will update the states xxxChangeXXMinutes / Hours eg TemperatureChange10Minutes TemperatureChange1Hour TemperatureChange6Hour
	## has problems when there are no updates, values can be  stale over days
	def updateChangedValuesInLastXXMinutes(self,dev, value, stateToUpdate, localCopy,  decimalPlaces=1):
		try:
			if stateToUpdate not in dev.states:
				self.indiLOG.log(10,"updateChangedValuesInLastXXMinutes: {}, state {}   not defined".format(dev.name, stateToUpdate))
				return 

			#self.indiLOG.log(20,"updateChangedValuesInLastXXMinutes: {}, state {}, updateListStates:{}".format(dev.name, stateToUpdate, dev.pluginProps.get("isMememberOfChangedValues","")))
			if stateToUpdate +"_"+ k_testIfmemberOfStateMeasures not in dev.states:
				return 

			doPrint = False

			updateList = []

			devIdS = str(dev.id)

			# create the measurement time stamps in minutes
			for state in dev.states:
				## state  eg =  "temperatureChange1Hour"
				if state.find(stateToUpdate+"_Change") == 0:
					if state.find(".ui") > 8: continue
					if state.find("_ui") > 8: continue
					upU = state.split("Change")[1]
					if len(upU) < 2: continue
					if upU.find("Hours") > -1:     updateN = "Hours";   updateMinutes = 3600
					elif upU.find("Minutes") > -1: updateN = "Minutes"; updateMinutes = 60
					else: continue
					amount = int(upU.split(updateN)[1])
					updateList.append( {"state":state, "unit":updateN, "deltaSecs":updateMinutes * amount, "pointer":0, "changed":0} )

			if len(updateList) < 1: 
				#self.indiLOG.log(10,"updateChangedValuesInLastXXMinutes:{},  state:{}Changexx value:{} \nnot in states: {}".format(dev.name, stateToUpdate, value, dev.states))
				return

			## get last list
			if devIdS not in self.changedValues:
				self.changedValues[devIdS] = {}



			updateList = sorted(updateList, key = lambda x: x["deltaSecs"])
			if doPrint: self.indiLOG.log(20,"{}: {}, = {}  updateList:{},  ".format(dev.name, stateToUpdate, value, updateList))
			#if doPrint: self.indiLOG.log(20,"{}: start changedValues:{},  ".format(dev.name, self.changedValues[devIdS][stateToUpdate+"list"]))


			if stateToUpdate+"list" in self.changedValues[devIdS]:
				valueList = self.changedValues[devIdS][stateToUpdate+"list"]
			else:
				valueList = [(0,0),(0,0)]


			try: decimalPlaces = int(decimalPlaces)
			except: 
				self.indiLOG.log(20,"updateChangedValuesInLastXXMinutes dev{}: bad decimalPlaces {}: type:{}  must be >=0 and integer ".format(dev.name, decimalPlaces, type(decimalPlaces)))
				return

			if decimalPlaces == 0: 
				valueList.append([int(time.time()),int(value)])
			elif decimalPlaces > 0: 
				valueList.append([int(time.time()), round(value,decimalPlaces)])
			else:  
				self.indiLOG.log(20,"updateChangedValuesInLastXXMinutes dev{}: bad decimalPlaces {}: type:{}  must be >=0 and integer ".format(dev.name, decimalPlaces, type(decimalPlaces)))
				return

			jj 		= len(updateList)
			cutMax	= updateList[-1]["deltaSecs"] # this is for 172800 secs = 48 hours
			ll		= len(valueList)
			for ii in range(ll):
				if len(valueList) <= 2: break
				if (valueList[-1][0] - valueList[0][0]) > cutMax: valueList.pop(0)
				else: 				    break


			ll = len(valueList)
			if ll > 1:
				for kk in range(jj):
					cut = updateList[kk]["deltaSecs"] # = 5 min = 300, 10 min = 600, 20 min=1200, 1 hour = 3600 ... 48hours = 172800 secs
					updateList[kk]["pointer"] = 0
					if cut != cutMax: # we can skip the largest, must be first and last entry
						for ii in range(ll-1,-1,-1):
							if (valueList[-1][0] - valueList[ii][0]) <= cut:
								updateList[kk]["pointer"] = ii
							else:
								break

					if decimalPlaces == "":
						changed			 = round(( valueList[-1][1] - valueList[updateList[kk]["pointer"]][1] ))
					elif decimalPlaces == 0:
						changed			 = int(valueList[-1][1] - valueList[updateList[kk]["pointer"]][1] )
					else:
						changed			 = round(( valueList[-1][1] - valueList[updateList[kk]["pointer"]][1] ), decimalPlaces)

					
					localCopy[ updateList[kk]["state"] ] = [changed,""]
					if doPrint: self.indiLOG.log(20,"{}:  updateList:{}, changed:{}, dec:{} ".format(dev.name, updateList[kk]["state"], changed, decimalPlaces))

			self.changedValues[devIdS][stateToUpdate+"list"] = valueList

			return 

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	###########################		changed Values END  ########################


	###########################		averages  Start  ########################
	####----------------------reset sensor min max at midnight -----------------------------------####
	def moveAveragesToLastDay(self):
		try:
			if self.dayReset == datetime.datetime.now().day or datetime.datetime.now().hour != 0: return 
			self.dayReset = datetime.datetime.now().day
			#self.indiLOG.log(20,"moveAveragesToLastDay resetting averages" )
			self.averagesCounts = {}
			for dev in indigo.devices.iter(self.pluginId):
					self.averagesCounts[dev.id] = {}
					if dev.enabled:
						try:
							for ttx in k_statesWithfillMinMax:
								#self.indiLOG.log(20,f"moveAveragesToLastDay etsting ttx:{ttx:}" )
								if ttx in dev.states and ttx+"_MaxToday" in dev.states:
									val = dev.states[ttx]
									self.addToStatesUpdateDict(dev,ttx+"_MaxYesterday",	dev.states[ttx+"_MaxToday"])
									self.addToStatesUpdateDict(dev,ttx+"_MinYesterday",	dev.states[ttx+"_MinToday"])
									self.addToStatesUpdateDict(dev,ttx+"_MaxToday",		dev.states[ttx]	)
									self.addToStatesUpdateDict(dev,ttx+"_MinToday",		dev.states[ttx])
									self.addToStatesUpdateDict(dev,ttx+"_AveYesterday",	dev.states[ttx+"_AveToday"])
									self.addToStatesUpdateDict(dev,ttx+"_AveToday",		dev.states[ttx])
									self.addToStatesUpdateDict(dev,ttx+"_MeasurementsYesterday",		dev.states[ttx+"_MeasurementsToday"])
									self.addToStatesUpdateDict(dev,ttx+"_MeasurementsToday", 1)

						except	Exception as e:
							if len("{}".format(e))	> 5 :
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

			self.executeUpdateStatesList()					
		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	####----------------------fill min max, ave-----------------------------------####
	def fillMinMaxSensors(self, dev, stateName, value, decimalPlaces, localCopy):
		try:
			if value == "": return
			if stateName in dev.states and stateName+"_MaxToday" in dev.states:
				val = float(value)
				if val > float(dev.states[stateName+"_MaxToday"]):
					localCopy[stateName+"_MaxToday"] = [val,""]
				if val < float(dev.states[stateName+"_MinToday"]):
					localCopy[stateName+"_MinToday"] = [val,""]

				if stateName+"_AveToday" in dev.states and stateName+"_MeasurementsToday" in dev.states:
						if dev.id not in self.averagesCounts: self.averagesCounts[dev.id] = {}
						if stateName+"_MeasurementsToday"  not in self.averagesCounts[dev.id]: 
							self.averagesCounts[dev.id][stateName+"_MeasurementsToday"] = [dev.states[stateName+"_MeasurementsToday"], 0]
						currentAve = dev.states[stateName+"_AveToday"]
						nMeas = max(0,self.averagesCounts[dev.id][stateName+"_MeasurementsToday"][0])
						newAve = ( currentAve*nMeas + val )/ (nMeas+1)
						if decimalPlaces == 0: newAve = int(newAve)
						else: newAve = round(newAve, decimalPlaces)
						localCopy[stateName+"_AveToday"] = [newAve,""]
						self.averagesCounts[dev.id][stateName+"_MeasurementsToday"][0] += 1
						if time.time() - self.averagesCounts[dev.id][stateName+"_MeasurementsToday"][1] > 63.1:
							self.averagesCounts[dev.id][stateName+"_MeasurementsToday"][1] = time.time()
							localCopy[stateName+"_MeasurementsToday"] = [nMeas+1,""]
			return localCopy				


		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

	###########################		averages  END  ########################

	####-----------------	 ---------
	def addToStatesUpdateDict(self, dev, key, value, uiValue=""):
		try:

			keyLocal = copy.copy(key)
			if dev.states.get("address","")  == "xx001860C98C9E3E":
				self.indiLOG.log(20,"addToStatesUpdateDict (2) dev:{:35s}, key:{}; value:{}".format(dev.name, keyLocal, value) )

			localCopy = copy.deepcopy(self.devStateChangeList)
			if dev.id not in localCopy:
				localCopy[dev.id] = {}

			localCopy[dev.id][keyLocal] = [value, uiValue]

			doprint = False
			if keyLocal in k_doubleState:
				keyLocal = k_doubleState[keyLocal]
				localCopy[dev.id][keyLocal] = [value, uiValue]

			if keyLocal in k_statesThatHaveMinMaxReal:
				self.fillMinMaxSensors( dev, keyLocal, value, 1, localCopy[dev.id])
				self.updateChangedValuesInLastXXMinutes(dev, value, keyLocal, localCopy[dev.id],  decimalPlaces=1)
				doprint = True
			if keyLocal in k_statesThatHaveMinMaxInteger:
				self.fillMinMaxSensors( dev, keyLocal, value, 0, localCopy[dev.id])
				self.updateChangedValuesInLastXXMinutes(dev, value, keyLocal, localCopy[dev.id], decimalPlaces=0)
				doprint = True

			self.devStateChangeList = copy.deepcopy(localCopy)
			#f	doprint: self.indiLOG.log(20,"addToStatesUpdateDict (2) dev:{:35s}, key:{}; devStateChangeList:{}".format(dev.name, key, self.devStateChangeList) )


		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def executeUpdateStatesList(self):
		devId = ""
		key = ""
		local = ""
		checkAddress = "xxx001860C98C9E3E"
		try:
			if len(self.devStateChangeList) == 0: return
			local = copy.deepcopy(self.devStateChangeList)
			self.devStateChangeList = {}
			trigList = []
			for devId in  local:
				lastSensorChangeFound = False
				onlyIfChanged = []
				try: int(devId)
				except: continue
				if len( local[devId]) > 0:
					try: 	dev = indigo.devices[int(devId)]
					except: continue
					props = dev.pluginProps
					#if  dev.deviceTypeId == "HMIP-ROOM": self.indiLOG.log(10,"executeUpdateStatesList :{},".format(dev.name))

					keyAlreadyInList = []
					for key in local[devId]:
						#if  dev.deviceTypeId == "HMIP-ROOM": self.indiLOG.log(10,"executeUpdateStatesList :{}, key:{}".format(dev.name,key))
						if key not in dev.states: 
							self.indiLOG.log(20,"executeUpdateStatesList :{}, key:{} not in states".format(dev.name,key))
							continue
						if key in keyAlreadyInList: continue
						value = local[devId][key][0]
						uiValue = local[devId][key][1]
						# excude from update old=new or if  new =="" and old =0.
						nv = "{}".format(value).strip()
						ov = "{}".format(dev.states[key]).strip()
						ov0 = ov.replace(".0","") 
						ouiv = dev.states.get(state+".ui", uiValue)
						#if dev.id == 1488939244: self.indiLOG.log(10,"executeUpdateStatesList :{},key:{}, nv:{}, ov:{}, ov0:{}".format(dev.name, key, value, nv, ov, ov0))

						if   key.find("RSSI") == 0 			and abs(dev.states[key] - value) < 1:   continue
						elif key == "humidityInput1"		and abs(dev.states[key] - value) < 1:   continue
						elif key == "HUMIDITY" 				and abs(dev.states[key] - value) < 2:   continue
						elif key == "humidityInput1" 		and abs(dev.states[key] - value) < 2:   continue
						elif key == "ILLUMINATION" 			and abs(dev.states[key] - value) < 3:   continue
						elif key == "Temperature" 			and abs(dev.states[key] - value) < 0.1: continue
						elif key == "temperatureInput1" 	and abs(dev.states[key] - value) < 0.1: continue
						elif key == "brightnessLevel" 		and abs(dev.states[key] - value) < 1:   continue
						#if dev.id == 1488939244: self.indiLOG.log(10,"executeUpdateStatesList pass 1")

						addValue = False
						if (
							( nv == ov) or (nv == "" and ov0 == "0") or (nv == "0" and ov0 == "0")  or 	( uiValue != "" and uiValue !=  ouiv)
							): continue

						keyAlreadyInList.append(key)
						addValue = True
						if uiValue != "":
							onlyIfChanged.append({"key":key,"value":value,"uiValue":uiValue})
						else:
							onlyIfChanged.append({"key":key,"value":value})

						#if dev.id == 1488939244: self.indiLOG.log(10,"executeUpdateStatesList : t/f {}  {}  {}  {}  {} state:{} in?{}".format("lastSensorChange" in dev.states ,lastSensorChangeFound , key == "sensorValue" , key == "onOffState" , key in k_stateThatTriggersLastSensorChange.get(dev.deviceTypeId,[]), key, k_stateThatTriggersLastSensorChange.get(dev.deviceTypeId,[]) ))
						if 	(
								("lastSensorChange" in dev.states) and 
								(not lastSensorChangeFound) and 
								(key == "sensorValue" or key == "onOffState" or (dev.deviceTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps and  "triggerLastSensorChange" in k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId] and  key in k_mapHomematicToIndigoDevTypeStateChannelProps[dev.deviceTypeId]["triggerLastSensorChange"]) 	)
							):
							#if dev.id == 1488939244: self.indiLOG.log(10,"executeUpdateStatesList pass 2")
							onlyIfChanged.append({"key":"lastSensorChange","value":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
							lastSensorChangeFound = True # only add lastSensorChange once per dev.

						# show in status field if .. 
						if props.get("displayStateId","xxx") == "displayStatus" and key == props.get("displayS",""):
							onlyIfChanged.append({"key":"displayStatus","value":value,"uiValue":uiValue})
							



				if onlyIfChanged != []:
					if False and  dev.states.get("address","")  == "xx001860C98C9E3E":
						self.indiLOG.log(20,f"update device:{dev.name:30}, keys/values:{onlyIfChanged:} ")
					try:
						#if True or dev.id == 1518189768: self.indiLOG.log(20,f"update device:{dev.name:30}, keys/values:{onlyIfChanged:} ")
						dev.updateStatesOnServer(onlyIfChanged)
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				try:
					self.indiLOG.log(40,"{}     {}  {};  devStateChangeList:\n{}".format(dev.name, devId , key, local) )
				except:pass

		return
	###########################		update States END   ########################



	###########################		DEVICE	## END ############################

	"""
	###########################		Prefs	## Start ############################
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the XML for the PluginConfig.xml by default; you probably don't
	# want to use this unless you have a need to customize the XML (again, uncommon)
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetPrefsConfigUiXml(self):
		return super(Plugin, self).getPrefsConfigUiXml()



	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the UI values for the configuration dialog; the default is to
	# simply return the self.pluginPrefs dictionary. It can be used to dynamically set
	# defaults at run time
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getPrefsConfigUiValues(self):
		try:
			(valuesDict, errorsDict) = super(Plugin, self).getPrefsConfigUiValues()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return (valuesDict, errorsDict)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine is called once the user has exited the preferences dialog
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def closedPrefsConfigUi(self, valuesDict , userCancelled):
		# if the user saved his/her preferences, update our member variables now
		if userCancelled == False:
			pass
		return
	"""

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine is called once the user has exited the preferences dialog
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------  set the geneeral config parameters---------
	def validatePrefsConfigUi(self, valuesDict):

		errorDict = indigo.Dict()
		try:
			valuesDict["MSG"]								= "ok"
			self.getCompleteUpdateEvery =					float(valuesDict.get("getCompleteUpdateEvery", "180"))
			self.getValuesEvery =							float(valuesDict.get("getValuesEvery", "3000"))/1000.
			self.requestTimeout =							float(valuesDict.get("requestTimeout", "10"))
			if ( 
				valuesDict["ipNumber"] != self.pluginPrefs.get("ipNumber","") or
				valuesDict["portNumber"] != self.pluginPrefs.get("portNumber","") or
				 "{}".format(self.requestTimeout) != "{}".format(self.pluginPrefs.get("requestTimeout",0))
				):
				self.ipNumber = valuesDict["ipNumber"]
				self.portNumber = valuesDict["portNumber"]
				self.pendingCommand["restartHomematicClass"] = True

			if not self.isValidIP(valuesDict["ipNumber"]):
				valuesDict["MSG"] = "bad IP number"
				return (False, errorDict, valuesDict)

			self.ipNumber =									valuesDict["ipNumber"]

			self.pendingCommand["getFolderId"] = True
			self.pendingCommand["setDebugFromPrefs"] = True

			found = False
			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId == "Homematic-Host":
					found = True
					if dev.deviceTypeId == "Homematic-Host":
						found = True
						props = dev.pluginProps
						upd = False
						if props.get("ipNumber") != valuesDict["ipNumber"]:
							props["ipNumber"] = valuesDict["ipNumber"]
							upd = True
						if props.get("portNumber") != valuesDict["portNumber"]:
							props["portNumber"] = valuesDict["portNumber"]
							upd = True
						if upd:
							props["address"] = valuesDict["ipNumber"] + ":" + valuesDict["portNumber"]
							dev.replacePluginPropsOnServer(props)
						break

			if not found:
				self.pendingCommand["createHometicHostDev"] = True

			return True, valuesDict

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		errorDict["MSG"]  = "error please check indigo eventlog"
		valuesDict["MSG"] =	"error please check indigo eventlog"
		return (False, errorDict, valuesDict)

	###########################		Prefs	## END ############################


	####-------------action  -----------
	def filterThermostat():
		try:
			ret = []
			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId not in ["HMIP-ETRV"]: continue
				ret.append([dev.id,dev.name])

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return ret

	####-----------------	 ---------
	def doGetDevStateType(self,  deviceTypeId, statesToCreate, dev = ""):
	
		checkStates = []
		nch = 99
		for state in statesToCreate:
			stateType = statesToCreate[state]

			for xx in [state]:
				if xx != "" and xx not in k_alreadyDefinedStatesInIndigo:
					ignore = False
					if dev != "":
						for chkState in  k_checkIfPresentInValues:
							#if dev.name == "HmIP-DRSI1-0029DD89A1358F": self.indiLOG.log(20,"doGetDevStateType testing:{:35},  state:{:22}, chkState:{:15},  stTest:{:2} T?; prop:{:} T?, value:{}".format(dev.name, xx,  chkState, xx.upper().find(chkState) , chkState+"_Ignore" in dev.pluginProps ,dev.pluginProps.get(chkState +"_Ignore","not present")  ))
							if xx.upper().find(chkState) == 0 and chkState+"_Ignore" in dev.pluginProps:
								if dev.pluginProps.get(chkState +"_Ignore",True): 
									ignore = True
									break
					if ignore: continue
					if   stateType == "real":			self.newStateList.append(self.getDeviceStateDictForRealType(xx, xx, xx))
					elif stateType == "integer":		self.newStateList.append(self.getDeviceStateDictForIntegerType(xx, xx, xx))
					elif stateType == "number":			self.newStateList.append(self.getDeviceStateDictForNumberType(xx, xx, xx))
					elif stateType == "string":			self.newStateList.append(self.getDeviceStateDictForStringType(xx, xx, xx))
					elif stateType == "booltruefalse":	self.newStateList.append(self.getDeviceStateDictForBoolTrueFalseType(xx, xx, xx))
					elif stateType == "boolonezero":	self.newStateList.append(self.getDeviceStateDictForBoolOneZeroType(xx, xx, xx))
					elif stateType == "boolonoff":		self.newStateList.append(self.getDeviceStateDictForBoolOnOffType(xx, xx, xx))
					elif stateType == "boolyesno":		self.newStateList.append(self.getDeviceStateDictForBoolYesNoType(xx, xx, xx))
					elif stateType == "enum":			self.newStateList.append(self.getDeviceStateDictForEnumType(xx, xx, xx))
					elif stateType == "separator":		self.newStateList.append(self.getDeviceStateDictForSeparatorType(xx, xx, xx))

				if True:
					## add min/max etc if designed
					if state in k_statesWithfillMinMax and dev !="" and dev.pluginProps.get("minMaxEnable-"+state,True):
					
						if state in k_statesThatHaveMinMaxReal:
							for yy in k_stateMeasures:
								self.newStateList.append(self.getDeviceStateDictForRealType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
							for yy in k_stateMeasuresCount:
								self.newStateList.append(self.getDeviceStateDictForIntegerType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
						if state in k_statesThatHaveMinMaxInteger: 
							for yy in k_stateMeasures:
								self.newStateList.append(self.getDeviceStateDictForIntegerType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
							for yy in k_stateMeasuresCount:
								self.newStateList.append(self.getDeviceStateDictForIntegerType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
	

		return 

	####-----------------	 ---------
	def getDeviceStateList(self, dev):

		try:
	
			self.newStateList  = super(Plugin, self).getDeviceStateList(dev)

			self.doGetDevStateType(dev.deviceTypeId, k_allDevicesHaveTheseStates, dev=dev)

			self.doGetDevStateType(dev.deviceTypeId, k_createStates[dev.deviceTypeId], dev=dev)

			if dev.deviceTypeId.find("Homematic") == -1 and dev.deviceTypeId.find("HMIP-SYSVAR-") == -1:
				if  dev.deviceTypeId not in k_isNotRealDevice and  dev.deviceTypeId not in k_devsThatAreChildDevices and dev.deviceTypeId.find("child") == -1 and not dev.pluginProps.get("isChild",False):
						self.doGetDevStateType(dev.deviceTypeId, k_statesToCreateisRealDevice, dev=dev)

				if  dev.pluginProps.get("isChild",False):
						self.doGetDevStateType(dev.deviceTypeId, k_ChildrenHaveTheseStates, dev=dev)

		except	Exception as e:
			self.indiLOG.log(20,"deviceTypeId:{}, {}".format(dev.deviceTypeId, dev.name))
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return self.newStateList 

	####-----------------	 ---------
	def getDeviceDisplayStateId(self, dev):
			displayStateId  = super(Plugin, self).getDeviceDisplayStateId(dev)
			newd = ""
			deviceTypeId = dev.deviceTypeId

			if deviceTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps:
				newd =  k_mapHomematicToIndigoDevTypeStateChannelProps[deviceTypeId]["props"].get("displayStateId","")
				if newd != "": return newd

			return displayStateId



	####-------------
	def getDeviceConfigUiXml(self, typeId, devId):
		dev = indigo.devices[devId]
		#self.indiLOG.log(20,"getDeviceConfigUiXml typeId:{}, devId:{}  0 ".format(typeId, devId))
		if typeId not in k_mapHomematicToIndigoDevTypeStateChannelProps: 
			#self.indiLOG.log(20,"typeId:{}, not pass 1 ".format(typeId, devId))
			return super(Plugin, self).getDeviceConfigUiXml(typeId, devId)

		if "deviceXML" not in k_mapHomematicToIndigoDevTypeStateChannelProps[typeId]: 
			#self.indiLOG.log(20,"typeId:{}, not pass 2 ".format(typeId, devId))
			return super(Plugin, self).getDeviceConfigUiXml(typeId, devId)

		if k_mapHomematicToIndigoDevTypeStateChannelProps[typeId]["deviceXML"] == "":
			#self.indiLOG.log(20,"typeId:{}, not pass 3 ".format(typeId, devId))
			return super(Plugin, self).getDeviceConfigUiXml(typeId, devId)

		#self.indiLOG.log(20,"typeId:{}, :{} new:{} ".format(typeId, dev.name, k_mapHomematicToIndigoDevTypeStateChannelProps[typeId]["deviceXML"]))
		return k_mapHomematicToIndigoDevTypeStateChannelProps[typeId]["deviceXML"] 



######## set defaults for action and menu screens
	#/////////////////////////////////////////////////////////////////////////////////////
	# Actions Configuration
	#/////////////////////////////////////////////////////////////////////////////////////
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the actions for the plugin; you normally don't need to
	# override this as the base class returns the actions from the Actions.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetActionsDict(self):
		return super(Plugin, self).getActionsDict()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine obtains the callback method to execute when the action executes; it
	# normally just returns the action callback specified in the Actions.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetActionCallbackMethod(self, typeId):
		return super(Plugin, self).getActionCallbackMethod(typeId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the configuration XML for the given action; normally this is
	# pulled from the Actions.xml file definition and you need not override it
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetActionConfigUiXml(self, typeId, devId):
		return super(Plugin, self).getActionConfigUiXml(typeId, devId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the UI values for the action configuration screen prior to it
	# being shown to the user
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------	 ---------
	def xxgetActionConfigUiValues(self, pluginProps, typeId, devId):
		return super(Plugin, self).getActionConfigUiValues(pluginProps, typeId, devId)


	#/////////////////////////////////////////////////////////////////////////////////////
	# Menu Item Configuration
	#/////////////////////////////////////////////////////////////////////////////////////
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the menu items for the plugin; you normally don't need to
	# override this as the base class returns the menu items from the MenuItems.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetMenuItemsList(self):
		return super(Plugin, self).getMenuItemsList()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the configuration XML for the given menu item; normally this is
	# pulled from the MenuItems.xml file definition and you need not override it
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetMenuActionConfigUiXml(self, menuId):
		return super(Plugin, self).getMenuActionConfigUiXml(menuId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the initial values for the menu action config dialog, if you
	# need to set them prior to the GUI showing
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------	 ---------
	def getMenuActionConfigUiValues(self, menuId):
		valuesDict = indigo.Dict()
		self.menuXML = {}
		self.menuXML["MSG"] = ""
		

		for item in self.menuXML:
			valuesDict[item] = self.menuXML[item]
		errorsDict = indigo.Dict()
		#self.indiLOG.log(20,"getMenuActionConfigUiValues - menuId:{}".format(menuId))
		return (valuesDict, errorsDict)



######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

	####-----------------	 ---------
	def triggerStartProcessing(self, trigger):
		self.triggerList.append(trigger.id)

	####-----------------	 ---------
	def triggerStopProcessing(self, trigger):
		if trigger.id in self.triggerList:
			self.triggerList.remove(trigger.id)

	#def triggerUpdated(self, origDev, newDev):
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

	####-----------------	 ---------
	def triggerEvent(self, eventId):
		for trigId in self.triggerList:
			trigger = indigo.triggers[trigId]
			if trigger.pluginTypeId == eventId:
				indigo.trigger.execute(trigger)
		return




	###########################	   MAIN LOOP  ############################
	###########################	   MAIN LOOP  ############################
	###########################	   MAIN LOOP  ############################
	###########################	   MAIN LOOP  ############################
	####-----------------init  main loop ---------
	def fixBeforeRunConcurrentThread(self):

		nowDT = datetime.datetime.now()
		self.lastMinute		= nowDT.minute
		self.lastHour		= nowDT.hour
		self.writeJson({"version":_dataVersion}, fName=self.indigoPreferencesPluginDir + "dataVersion")

		self.threads = {}
		self.threads["getDeviceData"] = {}
		self.threads["getDeviceData"]["thread"]  = threading.Thread(name='getDeviceData', target=self.getDeviceData)
		self.threads["getDeviceData"]["thread"].start()

		self.threads["getCompleteupdate"] = {}
		self.threads["getCompleteupdate"]["thread"]  = threading.Thread(name='getCompleteupdate', target=self.getCompleteupdate)
		self.threads["getCompleteupdate"]["thread"].start()


		self.pluginStartTime = time.time()

		for dev in indigo.devices.iter(self.pluginId):
			if dev.deviceTypeId == "Homematic-Host":
				self.hostDevId = dev.id
				break

		try:
			# ceck if we have some old devices with the same address in our environment
			devList = []
			for dev in indigo.devices.iter(self.pluginId):
				if "address" in dev.states:
					devList.append((dev.id, dev.states["address"]))
			for nn in range(len(devList)):
				for kk in range(nn+1,len(devList)):
					if devList[nn][1] == devList[kk][1]:
						dev1 = indigo.devices[devList[nn][0]]
						dev2 = indigo.devices[devList[kk][0]]
						dev1ChildID = dev1.states.get("childOf","")
						dev2ChildID= dev2.states.get("childOf","")
						if dev1ChildID != "" and dev2.id == dev1ChildID:
							xx= "fixme"
							try:	xx = dev1.name.split(" ")[0].split("-child-")[-1]
							except	Exception as e:
								self.indiLOG.log(40,"", exc_info=True)
							self.indiLOG.log(30,"doing  fix #1 adding: :{} to address".format(xx)) 
							dev1.updateStateOnServer("address", dev1.states["address"]+"-child-"+xx)
							continue
						elif dev2ChildID != "" and dev1.id == dev2ChildID:
							xx = "fixme"
							try: 	xx = dev2.name.split(" ")[0].split("-child-")[-1]
							except	Exception as e:
								self.indiLOG.log(40,"", exc_info=True)
							self.indiLOG.log(30,"doing  fix #2  adding: {} to address ".format(xx)) 
							dev2.updateStateOnServer("address", dev2.states["address"]+"-child-"+xx)
							continue

						self.indiLOG.log(30,"device with same address:{}, delete one and restart plugin:\ndev1 == {:12} {:12} {:12} {:55s}- type:{:12}, created:{}\ndev2 == {:12} {:12} {:12} {:55s}- type:{:12}, created:{}\n".format( devList[nn][1], 
																										dev1.states["address"], dev1.id, dev1ChildID, dev1.name, dev1.states["homematicType"], dev1.states["created"],    
																										dev2.states["address"], dev2.id, dev2ChildID, dev2.name, dev2.states["homematicType"], dev2.states["created"] ))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.pluginState   = "run"
		self.readChangedValues()
		

		return True

	####-----------------   main loop          ---------
	def runConcurrentThread(self):

		if not self.fixBeforeRunConcurrentThread():
			self.indiLOG.log(40,"..error in startup")
			self.sleep(10)
			return

		self.indiLOG.log(10,"runConcurrentThread.....")

		self.dorunConcurrentThread()

		self.sleep(1)
		if self.quitNOW !="":
			self.indiLOG.log(20, "runConcurrentThread stopping plugin due to:  ::::: {} :::::".format(self.quitNOW))
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)
		return

	####-----------------   main loop            ---------
	def dorunConcurrentThread(self):

		self.indiLOG.log(10," start   runConcurrentThread, initializing loop settings and threads ..")


		indigo.server.savePluginPrefs()
		self.lastDayCheck				= -1
		self.lastHourCheck				= datetime.datetime.now().hour
		self.lastMinuteCheck			= datetime.datetime.now().minute
		self.pluginStartTime 			= time.time()
		self.countLoop					= 0
		self.indiLOG.log(20,"initialized ... looping")
		indigo.server.savePluginPrefs()	
		self.lastSecCheck = time.time()

		self.sleep(1)
		try:
			while True:
				self.countLoop += 1
				ret = self.doTheLoop()

				if ret != "ok":
					self.indiLOG.log(20,"LOOP   return break: >>{}<<".format(ret) )
				for ii in range(2):
					if self.quitNOW != "": 
						break
					self.sleep(1)

				if self.quitNOW != "": 
					break
	 
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.indiLOG.log(20,"after loop , quitNow= >>{}<<".format(self.quitNOW ) )

		self.postLoop()

		return


	###########################	   exec the loop  ############################
	####-----------------	 ---------
	def doTheLoop(self):


		if self.quitNOW != "": return "break"

		try:

			self.periodCheck()
			self.executeUpdateStatesList()

			if self.quitNOW != "": return "break"

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return "ok"


	###########################	   after the loop  ############################
	####-----------------	 ---------
	def postLoop(self):

		self.pluginState   = "stop"
		self.threads["getDeviceData"]["status"] = "stop" 
		self.threads["getCompleteupdate"]["status"] = "stop" 

		self.saveChangedValues()
		self.writeJson(self.homematicAllDevices, fName=self.indigoPreferencesPluginDir + "homematicAllDevices.json", doFormat=True, singleLines=False )

		indigo.server.savePluginPrefs()	

		if self.quitNOW == "config changed":
			pass
		if self.quitNOW == "": self.quitNOW = " restart / stop requested "
		self.sleep(1)

		return 


	####-----------------	 ---------
	def periodCheck(self):
		try:

			if	self.countLoop < 2:						return
			if time.time() - self.pluginStartTime < 5: return
			changed = False
			self.processPendingCommands()
			self.checkOnDelayedActions()

			if time.time() - self.lastSecCheck  > 27:
				if self.hostDevId > 0:
					if  self.numberOfVariables >= 0:
						dev = indigo.devices[self.hostDevId]
						self.addToStatesUpdateDict(dev, "numberOfVariables", self.numberOfVariables)
						self.addToStatesUpdateDict(dev, "numberOfDevices", self.numberOfDevices)
						self.addToStatesUpdateDict(dev, "numberOfRooms", self.numberOfRooms)

						if time.time() - self.lastSucessfullHostContact  > 100:
							if self.hostDevId != 0 and  dev.states["onOffState"]:
								self.addToStatesUpdateDict(indigo.devices[self.hostDevId], "onOffState", False, uiValue="offline")

				self.moveAveragesToLastDay()
				if time.time() - self.autosaveChangedValues > 20: 
					self.saveChangedValues()
					self.autosaveChangedValues = time.time()

				if time.time() - self.checkOnThreads > 20: 
					for xx in self.threads:
						if self.threads[xx]["status"] != "running":
							if xx == "getDeviceData":
								self.threads[xx]["thread"]  = threading.Thread(name=xx, target=self.getDeviceData)
								self.threads[xx]["thread"].start()
							elif xx == "getCompleteupdate":
								self.threads[xx]["thread"]  = threading.Thread(name=xx, target=self.getCompleteupdate)
								self.threads[xx]["thread"].start()
					self.checkOnThreads = time.time()

				if self.devsWithenabledChildren == []:
					for dev in indigo.devices.iter(self.pluginId):
						for st in dev.states:
							if st.find("enabledChildren") > -1:
								self.devsWithenabledChildren.append(dev.id)
								#self.indiLOG.log(20,"enabledChildren:name:{}".format(dev.name ))
								break

				newL = []
				for devId in self.devsWithenabledChildren:
					if devId not in indigo.devices:
						continue
					dev = indigo.devices[devId]
					if not dev.enabled: continue
					if  "enabledChildren" not in dev.states:
						continue
					props = dev.pluginProps
					enabledChildren = ""
					for ii in range(100):
						if props.get("enable-"+str(ii), False ):
							enabledChildren += str(ii)+","
					enabledChildren = enabledChildren.strip(",")	
					enList= enabledChildren.split(",")
					for pr in props:
						if pr.find("enable-") == 0:
							etype = pr.split("-")[1]
							try: 
								int(etype)
								continue
							except: pass
							enabledChildren += etype+","
					enabledChildren = enabledChildren.strip(",")	
					#self.indiLOG.log(20,"periodCheck: {},  enabledChildren:{}".format(dev.name, enabledChildren))
					self.addToStatesUpdateDict(dev, "enabledChildren", enabledChildren)
					if props.get("displayS","") == "enabledChildren" and "sensorValue" in dev.states:
						self.addToStatesUpdateDict(dev, "sensorValue", 1, uiValue="channels:"+enabledChildren.strip(","))
					newL.append(devId)
				self.devsWithenabledChildren = newL
				self.writeJson(self.homematicAllDevices, fName=self.indigoPreferencesPluginDir + "homematicAllDevices.json", doFormat=True, singleLines=False )

				self.lastSecCheck = time.time()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return	changed


	####-----------------	 ---------
	def fillDevStates(self, dev, props, address, homematicStateName, channelNumber, iChannelNumber, v, doInverse, vInverse, dt, checkCH=True, doprint=False):
		try:
			doPrint = doprint
			devTypeId = dev.deviceTypeId
			if False and dev.id == 1488939244: doPrint = True
			if doPrint: self.indiLOG.log(20,"fillDevStates: ---0-- {}: devTypeId:{}, channelNumber:{}, homematicStateName:{:30}, test1:{}, test2:{} checkCH:{}".format(dev.name, devTypeId, channelNumber,  homematicStateName,  devTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps, homematicStateName in  k_mapHomematicToIndigoDevTypeStateChannelProps[devTypeId]["states"],checkCH))
			if False and doPrint: self.indiLOG.log(20,"fillDevStates: ---0-1  homematicStateName:{} , states:{}".format( homematicStateName , k_mapHomematicToIndigoDevTypeStateChannelProps[devTypeId]["states"]))
			if devTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps and homematicStateName in  k_mapHomematicToIndigoDevTypeStateChannelProps[devTypeId]["states"]:
					indigoInfo 	= k_mapHomematicToIndigoDevTypeStateChannelProps[devTypeId]["states"][homematicStateName]

					if checkCH:
						ich = int( indigoInfo.get("channelNumber","1"))
						if  	ich < 0: chn = "-1" 
						elif 	ich == iChannelNumber: 	chn = channelNumber
						else: 
							if doPrint: self.indiLOG.log(20,"fillDevStates: ---1-1               test3 false:ich:{}  ".format(ich))
							return False
					else:
						chn = channelNumber; ich = iChannelNumber

					#if doPrint: self.indiLOG.log(20,"fillDevStates: ---1---ich:{}, indigoInfo:{}".format(homematicStateName, v , channelNumber, devTypeId, ich, indigoInfo))

					state 		= indigoInfo.get("indigoState",homematicStateName)
					mult		= indigoInfo.get("mult",1)
					dType		= indigoInfo.get("dType","integer")
					uiForm		= indigoInfo.get("format","{}")
					if doPrint: self.indiLOG.log(20,"fillDevStates: ---2 ====>      OK      state:{}, mult:{}, dType:{}, v:{},  devTypeId:{}, ich:{},".format( state,  mult, dType, v,  devTypeId, ich))

					if mult != 1: v *= mult

					if dType == "integer": 
						try:
							v = int(v)
						except:
							self.writeErrorToLog(address, "fillDevStates: {} st:{} ch#:{} has error, not an integer>{}<".format(dev.name, homematicStateName, channelNumber, v ))
							v = 0
							
						#if address == "00325D89BB3F6A": self.indiLOG.log(20,"fillDevStates- 9   state:{}, v:{} ===========".format( state, v))
						self.addToStatesUpdateDict(dev, state, v, uiValue= uiForm.format(v))
						#if doPrint: self.indiLOG.log(20,"fillDevStates:  ---3---- displayS:{}, SupportsSensorValue:{}".format( props.get("displayS","--"), props.get("SupportsSensorValue",False)))
						if props.get("displayS","--") == state and "sensorValue" in dev.states and props.get("SupportsSensorValue",False):
							if doPrint: self.indiLOG.log(20,"fillDevStates {}:  add sensorvalue".format(dev.name))
							self.addToStatesUpdateDict(dev, "sensorValue", round(float(v),0), uiValue= uiForm.format(v))
						if state in dev.states:
							if True or dev.states[state] != v:
								self.addToStatesUpdateDict(dev, state, v, uiValue= uiForm.format(v))

					elif dType == "real":
						try:
							v = float(v)
						except:
							self.writeErrorToLog(address, "fillDevStates: {} adr:{} st:{} has error not a float>{}<".format(dev.name, homematicStateName, channelNumber, v ))
							v = 0. 
						if props.get("displayS","--") == state and "sensorValue" in dev.states and props.get("SupportsSensorValue",False):
							if dev.states["sensorValue"] != v:
								self.addToStatesUpdateDict(dev, "sensorValue", v, uiValue=uiForm.format(v))

						if state in dev.states:
							if True or dev.states[state] != v:
								self.addToStatesUpdateDict(dev, state, v, uiValue= uiForm.format(v))

					elif dType == "booltruefalse":
							TF = self.isBool2(v, doInverse, vInverse)
							UIF = "on" if TF else "off" 
							if props.get("displayS","--") == state and "onOffState" in dev.states and props.get("SupportsOnState",False):
								if dev.states["onOffState"] != TF:
									self.addToStatesUpdateDict(dev, "onOffState", TF, uiValue=UIF)
									if "lastEvent" in dev.states:
										if TF:
											self.addToStatesUpdateDict(dev, "lastEventOn", dtNow)
										else:
											self.addToStatesUpdateDict(dev, "lastEventOff", dtNow)
							if state in dev.states:
								TF = self.isBool2(v, False, v)
								UIF = "on" if TF else "off" 
								if True or dev.states[state] != v:
									self.addToStatesUpdateDict(dev, state, v, uiValue=UIF)

					elif dType == "string":
						#if doPrint:	self.indiLOG.log(20,"fillDevStates,--3--  dev:{}, key:{}, value:{}, intToState:{}".format(dev.name, homematicStateName, v , indigoInfo.get("intToState",False) ) )
						if indigoInfo.get("intToState",False):
							#if doPrint:	self.indiLOG.log(20,"fillDevStates - 4- ,  t1:{}, t2:{}".format(dev.name, homematicStateName in dev.states , homematicStateName in k_stateValueNumbersToTextInIndigo ) )
							if state in dev.states: 				use = state
							elif homematicStateName in dev.states: 	use = homematicStateName
							if use in dev.states and use in k_stateValueNumbersToTextInIndigo:
								stautusReplacementList = k_stateValueNumbersToTextInIndigo[use]
								vui = "{}".format( stautusReplacementList[ max(0, min(len(stautusReplacementList)-1, v)) ])
								self.addToStatesUpdateDict(dev, use, "{}".format(vui))

								if homematicStateName == "COLOR" and devTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps and k_mapHomematicToIndigoDevTypeStateChannelProps[devTypeId]["props"].get("isSimpleColorDevice",False): self.setRGB07(dev, v)

					elif dType == "datetime":
							self.addToStatesUpdateDict(dev, state, dt)

					else:
							self.addToStatesUpdateDict(dev, state, v )

					return True

		except	Exception as e:
			self.indiLOG.log(20,"{}, :{}".format(dev.name, homematicStateName))
			if "{}".format(e).find("None") == -1: self.indiLOG.log(30,"", exc_info=True)
			time.sleep(2)

		return False


	####-----------------	 ---------
	def setRGB07(self, dev, v):
		if   v == 0: r=0  ;g=0  ;b=0
		elif v == 7: r=33 ;g=33 ;b=33
		elif v == 6: r=50 ;g=50 ;b=0
		elif v == 5: r=50 ;g=0  ;b=50
		elif v == 4: r=100;g=0  ;b=0
		elif v == 3: r=0  ;g=50 ;b=50
		elif v == 2: r=0  ;g=100;b=0
		elif v == 1: r=0  ;g=0  ;b=100
		self.addToStatesUpdateDict(dev, 'redLevel',   r )
		self.addToStatesUpdateDict(dev, 'greenLevel', g )
		self.addToStatesUpdateDict(dev, 'blueLevel',  b )

	####-----------------	 ---------
	def fillDevStatesKeypad(self, dev, s, homematicStateName, channelNumber, chState, v, tso, vHomatic, dt):
		try:
				if s > 0: return 
				#self.indiLOG.log(20," upDateDeviceData address:{},  homematicStateName:{}, v:{}, t:{}".format(address,  chState, v, tso))
				#v = ts # button press always has true after first press, never goes to false, the info is the time stamp
				state = "keyPadAction"
				key = v
				v = tso
				# anything valid here?
						# get last values:
				if self.lastKeyDev == 0 or self.lastInfo == {} :
					lastValuesText = dev.states.get("lastValuesText","")
					try: 	self.lastInfo = json.loads(lastValuesText)
					except: self.lastInfo = {}
					if dev.id not in self.delayedAction:
						self.delayedAction[dev.id] = []
					self.USER_AUTHORIZATION = dev.states["USER_AUTHORIZATION"].split(",")
				self.lastKeyDev = dev.id

				if channelNumber == "0": 
					if homematicStateName.find("USER_AUTHORIZATION_") == 0:
						NumberOfUsersMax = int(dev.pluginProps.get("NumberOfUsersMax",8))
						if  len(self.USER_AUTHORIZATION) != NumberOfUsersMax:
							self.USER_AUTHORIZATION =  ["0" for i in range(NumberOfUsersMax)]
						nn = min(10,max(1,int(homematicStateName.split("_")[2])))-1

						if vHomatic != (self.USER_AUTHORIZATION[nn] == "1"):
							if vHomatic: self.USER_AUTHORIZATION[nn] = "1"
							else:		self.USER_AUTHORIZATION[nn] = "0"
							self.addToStatesUpdateDict(dev, "USER_AUTHORIZATION", ",".join(self.USER_AUTHORIZATION))

				if channelNumber == "0" and homematicStateName == "CODE_ID" and tso != 0 and vHomatic and s == 0: 
					if self.lastInfo.get(chState, -1) != tso:
						self.addToStatesUpdateDict(dev, "userPrevious", dev.states.get("user"))
						self.addToStatesUpdateDict(dev, "userTimePrevious", dev.states.get("userTime"))
						if int(key) > 8: 
							key = "bad code entered"
						else:
							self.addToStatesUpdateDict(dev, "onOffState", True)
							if dev.id not in self.delayedAction:
								self.delayedAction[dev.id] = []
							self.delayedAction[dev.id].append(["updateState", time.time() + float(self.pluginPrefs.get("delayOffForButtons",5)), "onOffState",False] )
						self.addToStatesUpdateDict(dev, "user", key)
						self.addToStatesUpdateDict(dev, "userTime", dt)
						self.lastInfo[chState] = tso
						self.addToStatesUpdateDict(dev, "lastValuesText", json.dumps(self.lastInfo))

		except	Exception as e:
			self.indiLOG.log(20,"{}, :{}".format(dev.name, homematicStateName))
			if "{}".format(e).find("None") == -1: self.indiLOG.log(30,"", exc_info=True)
			time.sleep(2)
		return 


	####-----------------	 ---------
	def fillDevStatesButton(self, dev, chState, homematicStateName, channelNumber, vHomatic, tso, dt,doPrint=False):
		try:
			state = "buttonAction"

			if channelNumber != "0" and tso != 0: #homematicStateName in k_buttonPressStates:
					lastValuesText = dev.states.get("lastValuesText","")
					try: 	lastInfo = json.loads(lastValuesText)
					except: lastInfo = {}
					if doPrint: self.indiLOG.log(20," fillDevStatesButton pass 1      tso:{}, lastInfo.chState:{}, TF:{}<".format( tso, lastInfo.get(chState, -1) , lastInfo.get(chState, -1) != tso))

					if lastInfo.get(chState, -1) != tso:
						if doPrint: self.indiLOG.log(20," fillDevStatesButton pass 2     updateing states for chn:{},".format( channelNumber))
						self.addToStatesUpdateDict(dev, "buttonPressedPrevious", dev.states.get("buttonPressed"))
						self.addToStatesUpdateDict(dev, "buttonPressedTimePrevious", dev.states.get("buttonPressedTime"))
						self.addToStatesUpdateDict(dev, "buttonPressedTypePrevious", dev.states.get("buttonPressedType"))
						self.addToStatesUpdateDict(dev, "buttonPressed", channelNumber)
						self.addToStatesUpdateDict(dev, "buttonPressedTime", dt)
						self.addToStatesUpdateDict(dev, "buttonPressedType", homematicStateName)
						self.addToStatesUpdateDict(dev, "onOffState", True)
						if dev.id not in self.delayedAction:
							self.delayedAction[dev.id] = []
						if doPrint: self.indiLOG.log(20," fillDevStatesButton pass 3     adding delay action  after {} secs".format( float(self.pluginPrefs.get("delayOffForButtons",5))))
						self.delayedAction[dev.id].append(["updateState", time.time() + float(self.pluginPrefs.get("delayOffForButtons",5)), "onOffState",False] )
						lastInfo[chState] = tso
						self.addToStatesUpdateDict(dev, "lastValuesText", json.dumps(lastInfo))
								
		except	Exception as e:
			self.indiLOG.log(20,"{}, :{}".format(dev.name, homematicStateName))
			if "{}".format(e).find("None") == -1: self.indiLOG.log(30,"", exc_info=True)
			time.sleep(2)
		return 


	####-----------------	 ---------
	def fillDevStatesLeftRight(self, dev, state, v, channelNumber, dt):
		try:

			if v != dev.states[state]:		
				self.addToStatesUpdateDict(dev, state, v) 
				self.addToStatesUpdateDict(dev, "lastSensorChange", dt)
				self.addToStatesUpdateDict(dev, "onOffState", True)
				if dev.id not in self.delayedAction:
					self.delayedAction[dev.id] = []
				self.delayedAction[dev.id].append(["updateState", time.time() + float(self.pluginPrefs.get("delayOffForButtons",5)), "onOffState", False] )

				if channelNumber == "2":
					self.addToStatesUpdateDict(dev, "direction", "left")
					self.addToStatesUpdateDict(dev, "PPREVIUOS_PASSAGE-left", dev.states["LAST_PASSAGE-left"])
					self.addToStatesUpdateDict(dev, "LAST_PASSAGE-left", dt)
				elif channelNumber == "3":
					self.addToStatesUpdateDict(dev, "direction", "right")
					self.addToStatesUpdateDict(dev, "PPREVIUOS_PASSAGE-right", dev.states["LAST_PASSAGE-right"])
					self.addToStatesUpdateDict(dev, "LAST_PASSAGE-right", dt)

		except	Exception as e:
			self.indiLOG.log(20,"{}, :{}".format(dev.name, homematicStateName))
			if "{}".format(e).find("None") == -1: self.indiLOG.log(30,"", exc_info=True)
			time.sleep(2)
		return 

	####-----------------	 ---------
	def upDateDeviceData(self, allValues, NumberOfhttpcalls):

			#self.indiLOG.log(10,"all Values:{}".format(json.dumps(allValues, sort_keys=True, indent=2)))
		## this for saving execution time. there are several states for each device, we dont need to reload the device multile times
		devChild = ""
		devTypeChild = ""
		devCurrent = ""
		devIdCurrent = -1
		devButtonCurrent = ""
		devButtonIdCurrent = -1
		indigoIdforChild = -1
		tStart = time.time()
		dtimes = []
		self.USER_AUTHORIZATION = []
		self.devCounter +=1
		self.lastKeydev = 0
		self.lastInfo = {}
		lastAddress = 0
		chId = -1
		dtNow = datetime.datetime.now().strftime(_defaultDateStampFormat)
		if allValues == {} or allValues == "": return 
		if allValues is None: return 

		updsystodev = False
		for link in allValues:
			if link == "": continue
			try:
				lStart = time.time()
				
				address, channelNumber, homematicStateName, homematicType = "",-1,"value", ""

				if time.time() - self.lastSucessfullHostContact  > 10:
					if self.hostDevId != 0:
						devHost = indigo.devices[self.hostDevId]
						if not devHost.states.get("onOffState",False):
							self.addToStatesUpdateDict( devHost, "onOffState", True, uiValue="online")
						self.lastSucessfullHostContact = time.time()

				if link.find("/sysvar/") > -1: 
					#if link.find("/3392") > -1: self.indiLOG.log(20,"upDateDeviceData: found 3392: link:{}, data:{}".format(link, allValues[link]) )
					updsystodev = updsystodev or self.upDateSysvar( link, allValues, dtNow)


				### devices ----------------------------------
				elif link.find("/device/") > -1: 
					try:	
						dummy, dd, address, channelNumber, homematicStateName  = link.split("/") 
						homematicType =  "device"
					except: continue

				if address not in self.homematicAllDevices: continue
				if self.homematicAllDevices[address].get("indigoId",-1) > 0:
					if self.homematicAllDevices[address]["indigoStatus"] != "active": continue
					# get data:
					if lastAddress != address:
						self.lastKeyDev = 0
						self.lastInfo = {}
					lastAddress = address

					try: iChannelNumber = int(channelNumber)
					except: iChannelNumber  = -1
					chState = channelNumber+"-"+homematicStateName
					stateCh = homematicStateName+"-"+channelNumber
					state  = homematicStateName

					vHomatic = allValues[link].get("v","")
					v = vHomatic
					vui = ""
					tso = allValues[link].get("ts",0)
					ts = tso/1000.
					s = allValues[link].get("s",100)
					try:	dt = datetime.datetime.fromtimestamp(ts).strftime(_defaultDateStampFormat)
					except: dt = ""

					#if address == "002E1F2991EB72": self.indiLOG.log(20," upDateDeviceData address:{}, chState:{:30}, v:{:5}, tso:{}".format(address,  chState , v, tso))

					# now check how to use this 

					newdevTypeId = self.homematicAllDevices[address]["indigoDevType"] 
					
					devIdNew = self.homematicAllDevices[address]["indigoId"] 
					if devIdNew < 1: continue

					if devIdNew not in self.lastDevStates:
						 self.lastDevStates[devIdNew] = {}

					 # test if same value as last time, if yes skip, but do a fulll one every 100 secs anyway
					if time.time() > self.nextFullStateCheck: # dont do this check if last full is xx secs ago
						self.lastDevStates[devIdNew][chState] = [v, tso] 

					else:
						if chState not in self.lastDevStates[devIdNew]:
							self.lastDevStates[devIdNew][chState] = [v, tso]
						else:
							if self.lastDevStates[devIdNew][chState][0] == v and self.lastDevStates[devIdNew][chState][1] == tso: 
								continue
							else:
								#self.indiLOG.log(20," upDateDeviceData address:{},  devId:{}, chState: {}, old:{}, v:{}, tso:{}".format(address,  devIdNew, chState , self.lastDevStates[devIdNew][chState] , v, tso))
								self.lastDevStates[devIdNew][chState] = [v, tso] 

					# data accepted, now load it into indigo states
					if devIdCurrent == devIdNew:
						dev = devCurrent
					else:
						try:
							dev = indigo.devices[self.homematicAllDevices[address]["indigoId"] ]
							if dev.id not in self.lastDevStates: 	self.lastDevStates[dev.id] = {}
							devCurrent = dev
							devIdCurrent = dev.id
							devTypeId = dev.deviceTypeId
							self.lastKeyDev = 0
						except	Exception as e:
							self.indiLOG.log(30,"removing dev w address:{}, and indigo id:{}, from internal list, indigo device was deleted, setting to ignored, reallow in menu (un)Ignore.. ".format(address, self.homematicAllDevices[address]["indigoId"] ))
							self.homematicAllDevices[address]["indigoId"] = 0
							self.homematicAllDevices[address]["indigoStatus"] = "deleted"

							continue
					#if address == "002E1F2991EB72": self.indiLOG.log(20," upDateDeviceData address:{}, enabled:{} 3".format(address,  dev.enabled , v))

					if not dev.enabled: continue
					props = dev.pluginProps
					#if address == "002E1F2991EB72": self.indiLOG.log(20," upDateDeviceData address:{},4".format(address,  chState , v))

					if homematicStateName.lower().find("temperature"):
						if "Temperature" in dev.states and not "temperatureStatesEnabled" in props:
							props["temperatureStatesEnabled"] = True 
							dev.replacePluginPropsOnServer(props)

					doInverse = False
					vInverse = v
					if (newdevTypeId in k_mapHomematicToIndigoDevTypeStateChannelProps and 
						homematicStateName in k_mapHomematicToIndigoDevTypeStateChannelProps[newdevTypeId]["states"] and 
						k_mapHomematicToIndigoDevTypeStateChannelProps[newdevTypeId]["states"][homematicStateName].get("inverse",False)
						):			
							doInverse = True
							try: 	
								if type(v) == type(1):
									vInverse = - v + 1
								elif type(v) == type(True):
									if v: vInverse = False
									else: vInverse = True
							except:	pass

					if newdevTypeId in k_deviceTypesWithButtonPress and (homematicStateName in k_buttonPressStates ) and vHomatic and s==0:
						self.fillDevStatesButton(dev, chState, homematicStateName, channelNumber, vHomatic, tso, dt, doPrint= False)
						continue

					if  newdevTypeId in k_deviceTypesParentWithButtonPressChild and  (homematicStateName in k_buttonPressStates ) and vHomatic and s==0:
						try:
							xx = dev.states.get("childInfo","{}")
							childInfo = json.loads(xx)
						except:
							childInfo = {}
						for mtype in k_deviceTypesWithButtonPress:
							for chIndex in childInfo:
								chIdnew, chn, childDevType = childInfo[chIndex]
								if mtype  == childDevType and chIdnew > 0:
									if chId != chIdnew:
										try:
											devChild = indigo.devices[chIdnew]
											chId = chIdnew
											if chIdnew >0: self.fillDevStatesButton(devChild, chState, homematicStateName, channelNumber, vHomatic, tso, dt, doPrint= False) # = address == "xx00251D89BBD7FC")
										except: 
											self.indiLOG.log(30," upDateDeviceData address:{},  devtype:{}  removing child device from listing, does not exist?!".format(address,  childDevType ))
											chIdnew = 0
											childInfo[chI] = [chIdnew, chn, childDevType ]
											self.addToStatesUpdateDict(dev, "childInfo", json.dumps(childInfo))
						continue

					if newdevTypeId in k_deviceTypesWithKeyPad and (homematicStateName in k_keyPressStates  or homematicStateName[:19] in k_keyPressStates):
						self.fillDevStatesKeypad( dev, s, homematicStateName, channelNumber, chState, v, tso, vHomatic, dt)
						continue

					if newdevTypeId == "HMIP-SPDR" and state.find("PASSAGE_COUNTER_VALUE") == 0:
							if channelNumber in ["2","3"]:
								if   channelNumber == "2": state = state+"-left"
								elif channelNumber == "3": state = state+"-right"
								self.fillDevStatesLeftRight( dev, state, v,  channelNumber, dt)
								continue

					if devTypeId in ["HMIP-DLD"] and state == "LOCK_STATE":
						self.addToStatesUpdateDict(dev, "lastSensorChange", dt)
						self.addToStatesUpdateDict(dev, "onOffState", v > 1, uiValue=2 )
						continue


					#if address == "001860C98C9E3E": self.indiLOG.log(20," upDateDeviceData address:{},  newdevTypeId:{},chState:{}".format(address,  newdevTypeId, chState ))
					# normal types of  children
					childAction = False
					if devTypeId in k_devTypeHasChildren:
						if channelNumber in self.homematicAllDevices[address]["childInfo"]:
							if homematicStateName in self.homematicAllDevices[address]["childInfo"][channelNumber] and self.homematicAllDevices[address]["childInfo"][channelNumber][homematicStateName] > 0:
								chIdNew = self.homematicAllDevices[address]["childInfo"][channelNumber][homematicStateName]
								if chIdNew != chId:
									try:
										devChild = indigo.devices[chIdNew]
										devTypeChild = devChild.deviceTypeId
									except:
											self.indiLOG.log(30," upDateDeviceData address:{},  homematicStateName:{}  channelNumber:{} childIndigoId:{}, please remove child device from listing, does not exist?!".format(address,  homematicStateName, channelNumber, chIdNew))

								chId = chIdNew
								if 	devTypeChild  in k_mapHomematicToIndigoDevTypeStateChannelProps and homematicStateName in  k_mapHomematicToIndigoDevTypeStateChannelProps[devTypeChild]["states"]: 
									childAction = self.fillDevStates( devChild, devChild.pluginProps, address, homematicStateName, channelNumber, iChannelNumber, v, doInverse, vInverse, dt, checkCH=False,  doprint= False) #doprint=address=="002820C9ABB461" and homematicStateName=="ACTUAL_TEMPERATURE" )

					if not childAction:
						if self.fillDevStates(dev, props, address, homematicStateName, channelNumber, iChannelNumber, v, doInverse, vInverse, dt,  doprint= False ):continue

					# and here the rest: UNREACH, CONFIG_PENDING, RSSI_DEVICE, LOW_BAT, RSSI_PEER
					if state in dev.states:
							self.addToStatesUpdateDict(dev, state, v, uiValue=vui)
						
				if self.decideMyLog("Time"): dtimes.append(time.time() - lStart)

				
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		if self.decideMyLog("Time"):  tMain = time.time() - tStart

		if time.time() > self.nextFullStateCheck:  
			self.nextFullStateCheck  = time.time() + self.nextFullStateCheckAfter

		self.doallVarToDev(updsystodev)
		self.executeUpdateStatesList()
		if self.decideMyLog("Time"):  
			tAve = 0
			for x in dtimes:
				tAve += x
			tAve = tAve / max(1,len(dtimes))
			self.indiLOG.log(20,"upDateDeviceData, counter:{} elapsed times - tot:{:.3f}, tMain:{:.3f}   per state ave:{:.5f},  N-States:{:}  NumberOfhttpcalls:{}".format(self.devCounter, time.time() - tStart, tMain, tAve, len(dtimes), NumberOfhttpcalls ) )

		return 





	####-----------------	 ---------
	def makeListOfallPrograms(self, doit):
		try:
			if doit and "address" in self.allDataFromHomematic["allProgram"]: 
				self.listOfprograms = "\nPrograms on host ====================\n"
				self.listOfprograms += "Address Title                                    TS                    s Value\n"
				for address in self.allDataFromHomematic["allProgram"]["address"]:
					xx = self.allDataFromHomematic["allProgram"]["address"][address]
					val = xx.get("value",{})
					self.listOfprograms += "{:6}  {:40} {:19} {:3} {:}\n".format(
						address,  
						xx.get("title",""), 
						datetime.datetime.fromtimestamp(val.get("ts",0.)/1000. ).strftime(_defaultDateStampFormat), 
						val.get("s",0.), val.get("v","")
						)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return

	####-----------------	 ---------
	def makeListOfallVendors(self, doit):
		try:
			if doit and "address" in self.allDataFromHomematic["allVendor"]: 
				self.listOfEvents = "\nEvents on host ========================\n"
				self.listOfEvents += "TS                   Type     Event ---------\n"
				xx = self.allDataFromHomematic["allVendor"]["address"]
				if "diagnostics" in xx:
					yy = xx["diagnostics"]
					if "value" in yy and "v" in yy["value"]:
						zz = yy["value"]["v"]
						if "Log" in zz:
							for event in zz["Log"]:
									self.listOfEvents += "{:19}  {:8} {:}\n".format(event[0], event[1], event[3][0:150])
				#self.indiLOG.log(20,self.listOfEvents)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return



	####-----------------	 ---------
	def doallRooms(self, doit):
		try:
			if doit and "address" in self.allDataFromHomematic["allRoom"]: 
				#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, rooms :{}; :{} .. all:{}".format( doRooms, "address" in self.allDataFromHomematic["allRoom"], str(self.allDataFromHomematic["allRoom"]["address"])[0:100]) )
 
				self.numberOfRooms = 0
				homematicType = "ROOM"
				self.roomMembers = {}
				for address in self.allDataFromHomematic["allRoom"]["address"]:
					try:
						self.lastSucessfullHostContact = time.time()
						if self.hostDevId  > 0 and time.time() - self.lastSucessfullHostContact  > 20:
							devHost = indigo.devices[self.hostDevId]
							if not devHost.states.get("onOffState",False):
								self.addToStatesUpdateDict(devHost, "onOffState", True, uiValue="online")


						thisDev = self.allDataFromHomematic["allRoom"]["address"][address]
						self.numberOfRooms += 1

						indigoType = "HMIP-ROOM" 
						devFound = False
						for dev in indigo.devices.iter(self.pluginId):
							if dev.deviceTypeId != indigoType: continue
							if dev.states["address"] == address: 
								devFound = True
								break
						#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, theType:{}, devFound:{};  address:{}".format(theType, devFound, address) )

						title = thisDev.get("title","")
						name = "room-"+title +"-"+	address		
	
						if not devFound:
							try: 
								dev = indigo.devices[name]
								devFound = True
							except: pass

						newprops = {}
						if indigoType in k_mapHomematicToIndigoDevTypeStateChannelProps:
							newprops = k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["props"]
						nDevices = 0
						roomListIDs = ""
						roomListNames = ""
						for devD in thisDev["devices"]:
							link = devD.get("link", "").split("/")
							if len(link) != 4: continue
							homematicAddress = link[2]
							if homematicAddress in roomListIDs: continue
							roomListIDs += homematicAddress+";"
								
							nDevices += 1
							tt = devD.get("title", "")
							if tt.rfind(":") == len(tt) -2:
								tt = tt[:-2]
							roomListNames += tt+";"
							try:
								if homematicAddress not in self.roomMembers:
									self.roomMembers[homematicAddress] = []
								if address not in self.roomMembers[homematicAddress]: 
									self.roomMembers[homematicAddress].append(address)
							except: pass

						if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate,  devFound:{};  address:{}, ndevs:{}, room list:{} == {}".format( devFound, address, nDevices, roomListNames, roomListIDs) )
						roomListNames = roomListNames.strip(";")
						roomListIDs = roomListIDs.strip(";")
						newprops["roomListIDs"] = roomListIDs
						newprops["roomListNames"] = roomListNames
						if not devFound:
							if self.pluginPrefs.get("ignoreNewDevices", False): continue
							self.newDevice	= True							
							dev = indigo.device.create(
								protocol		= indigo.kProtocol.Plugin,
								address			= address,
								name			= name,
								description		= "",
								pluginId		= self.pluginId,
								deviceTypeId	= indigoType,
								folder			= self.folderNameDevicesID,
								props			= newprops
								)
							self.newDevice	= False							
							self.lastDevStates[dev.id] = {}
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
							self.addToStatesUpdateDict(dev, "address", address)
						if not dev.enabled: continue

						self.homematicAllDevices[address]["indigoId"] 	= dev.id
						self.homematicAllDevices[address]["indigoDevType"] 	=dev.deviceTypeId

						props = dev.pluginProps
						uiValue = uiValue="{} devices".format(nDevices)
						self.addToStatesUpdateDict(dev, "title", title)
						self.addToStatesUpdateDict(dev, "roomListIDs", roomListIDs)
						self.addToStatesUpdateDict(dev, "homematicType", homematicType)
						self.addToStatesUpdateDict(dev, "roomListNames", roomListNames)
						if nDevices != dev.states["NumberOfDevices"]:
							self.addToStatesUpdateDict(dev, "sensorValue", nDevices,uiValue = f"Devs :{nDevices:0d}")
							self.addToStatesUpdateDict(dev, "NumberOfDevices", nDevices)
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.newDevice = False
		return



	####-----------------	 ---------
	def upDateSysvar(self, link, allValues, dtNow):
				### sysvar ----------------------------------
			try:	
				#if link.find("/3392") > -1: self.indiLOG.log(20,"upDateSysvar:     found 3392: link:{}, data:{}".format(link, allValues[link]) )

				address   = link.split("/")[-1]
				if allValues[link].get("s",0) > 0: return  # not valid
				homematicType =  "sysvar"
				if address not in self.homematicAllDevices: return 
				newdevTypeId = self.homematicAllDevices[address]["indigoDevType"] 
				devIdNew = self.homematicAllDevices[address]["indigoId"] 
				chState = "value"
				updsystodev = False
				newValue = allValues[link].get("v","")
				if devIdNew > 0: 
					tso = allValues[link].get("ts",0)

					## check if we need to update:
					upd = False
					if devIdNew not in self.lastDevStates:
						 self.lastDevStates[devIdNew] = {}
					if chState not in self.lastDevStates[devIdNew]:
						self.lastDevStates[devIdNew][chState] = [newValue, tso]
						upd = True
					else:
						if self.lastDevStates[devIdNew][chState][0] != newValue or self.lastDevStates[devIdNew][chState][1] != tso: 
							self.lastDevStates[devIdNew][chState] = [newValue, tso] 
							upd = True

					if upd:
						dev = indigo.devices[devIdNew]
						#if address == "14739": self.indiLOG.log(20," upDateDeviceData  sysvar  address:{:5s}, dev:{},{} , states:{} allValues:{},".format(address,  devIdNew, dev.name, dev.states, allValues[link]) )
						if   "sensorValue" 			in dev.states:	
							unit = dev.states.get("unit","")
							if unit !="":
								self.addToStatesUpdateDict(dev, "sensorValue", round(newValue,1), f"{newValue:.1f}{unit:}")
							else:
								self.addToStatesUpdateDict(dev, "sensorValue", round(newValue,1), f"{newValue:.1f}")

						elif "onOffState" 			in dev.states:
							self.addToStatesUpdateDict(dev, "onOffState", newValue)

						elif "value" 				in dev.states:
							self.addToStatesUpdateDict(dev, "value", newValue)

						if   "lastSensorChange" 	in dev.states:
							self.addToStatesUpdateDict(dev, "lastSensorChange", dtNow)

				# fill syvar to dev/state dict , then do updsystodev if any change
				found = 0
				for linkAdr in self.variablesToDevices:
					if linkAdr not in self.variablesToDevicesLast: break
					if found: break
					devInfo = self.variablesToDevices[linkAdr]
					for stateType in devInfo["type"]:
						if found: break
						for typeCounter in devInfo["type"][stateType]["values"]:
							try:
								oldValue , sysAddress = devInfo["type"][stateType]["values"][typeCounter]
							except:
								self.indiLOG.log(20,"upDateSysvar  error sysvar  address:{:5s}, typeCounter:{},".format(address,  devInfo["type"][stateType]["values"]) )
								break
							#if address == "3392": self.indiLOG.log(20," upDateSysvar sysAddress:{}, address:{}<".format(sysAddress, address ))
							if  sysAddress == address: 
								if oldValue != newValue: updsystodev = True
								devInfo["type"][stateType]["updateSource"] 	= "upDateSysvar"
								#if address == "3392": self.indiLOG.log(20," upDateSysvar  sysvar  address:{:5s}, stateType:{:15},  value:{:5}, new:{:5}, typeCounter:{}<,  updsystodev:{}".format(address, stateType,  newValue, oldValue, updsystodev, updsystodev))
								devInfo["type"][stateType]["values"][typeCounter][0] = newValue
								found = True
								break
							
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			return updsystodev




	####-----------------	 ---------
	def doallSysVar(self, doit):
		try:
			if not self.pluginPrefs.get("accept_SYSVAR",True): return 

			if doit and "address" in self.allDataFromHomematic["allSysvar"]:  
				doDutyCycle = self.pluginPrefs.get("accept_DutyCycle",True)
				doWatchDog = self.pluginPrefs.get("accept_WatchDog",True)

				self.numberOfVariables = 0
				#self.indiLOG.log(20,"createDevicesFromCompleteUpdate,  variablesToDevices:{}".format( json.dumps(self.variablesToDevices,sort_keys=True, indent=2) ))
				for address in self.allDataFromHomematic["allSysvar"]["address"]:
					try:
						thisDev = self.allDataFromHomematic["allSysvar"]["address"][address]
						self.numberOfVariables +=1

						
						vType = thisDev.get("type","string")
						indigoType = "HMIP-SYSVAR-"+vType
						title = thisDev.get("title","")
						unit = thisDev.get("unit","")

						if not doWatchDog and title.find("WatchDog") == 0: continue
						if not doDutyCycle and title.find("DutyCycle") == 0: continue


						if title.find("OldVal") >= 0: continue

						if address not in self.homematicAllDevices: 
							self.fixAllhomematic(address=address)
						self.homematicAllDevices[address]["homemtaticStatus"] 			= "active"
						self.homematicAllDevices[address]["lastmessageFromHomematic"] 	= time.time()
	
						if self.homematicAllDevices[address]["indigoStatus"] not in ["active","create"]: continue


						if title.find("sv") == 0:  #  fill sysvar to dev/state dict, this info should go into dev/states not into variables
							# eg: "svEnergyCounter_3375_0034DF29B93F79:6",
							useThis = title.strip("sv").strip("HmiIP").split("_")
							if len(useThis) == 3: 	linkedDevAddress = useThis[2].split(":") #== 0034DF29B93F79:6
							else:					linkedDevAddress = []
							linkAdr = useThis[1]											 #== 3375
							stateType = useThis[0].split("Counter")[0]						 #== Energy

							# k_mapTheseVariablesToDevices = {"Energy": {"Counter":["EnergyTotal", 1., "{:.1f}[mm]"],"CounterToday":["EnergyToday", 1., "{:.1f}[mm]"],"CounterYesterday":["EnergyYesterday", 1., "{:.1f}[mm]"]...
							if stateType in k_mapTheseVariablesToDevices:
								if linkAdr not in self.variablesToDevices:
									self.variablesToDevices[linkAdr]    = {"devAddress":"","type":{}}
									self.variablesToDevicesLast[linkAdr] = {"devAddress":"","type":{}}

								devInfo = self.variablesToDevices[linkAdr]
								typeCounter = useThis[0].split(stateType)[1] # == EnergyCounter
								if stateType not in devInfo["type"]:	#  [] = [value, sysVar address]
									devInfo["type"][stateType]                              = {"values":{"CounterToday":[-999,""], "CounterYesterday": [-999,""], "Counter":[-999,""]}, "updateSource":"doallSysVar"}
									self.variablesToDevicesLast[linkAdr]["type"][stateType] = {"values":{"CounterToday":[-999,""], "CounterYesterday": [-999,""], "Counter":[-999,""]}, "updateSource":"doallSysVar"}
								devInfo["type"][stateType] ["values"][typeCounter][0] 	= thisDev["value"].get("v",0)
								devInfo["type"][stateType] ["values"][typeCounter][1] 	= address
								devInfo["type"][stateType] ["updateSource"] = "doallSysVar"

								if linkAdr in self.variablesToDevices and linkedDevAddress != []:		
									if devInfo["devAddress"] == "":			
										devInfo["devAddress"] 				= linkedDevAddress[0]
									devInfo["type"][stateType] ["channel"] 	= linkedDevAddress[1]
							continue

							#if linkAdr == "6568": self.indiLOG.log(20,"createDevicesFromCompleteUpdate,  title:{:45};  linkAdr:{}, stateType:{}; variablesToDevices:{}".format( title, linkAdr, stateType, self.variablesToDevices[linkAdr]))

						name = "Sysvar-"+title +"-"+ address		
						value = thisDev["value"].get("v",0)

						devFound = False
						try:
							dev = indigo.devices[self.homematicAllDevices[address]["indigoId"]]
							devFound = True
						except: pass

						if not devFound:
							for dev in indigo.devices.iter(self.pluginId):
								if self.pluginState == "stop": return theDict 
								if dev.deviceTypeId != indigoType: continue
								if dev.states["address"] == address: 
									devFound = True
									break

							if not devFound:
								try: 
									dev = indigo.devices[name]
									devFound = True
								except: pass

						newprops = {}
						if indigoType in k_mapHomematicToIndigoDevTypeStateChannelProps:
							newprops = k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["props"]

						if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate,  devFound:{};  address:{}, desc:{}, htype:{}, thisdev:\n{}".format( devFound, address, thisDev.get("description"), thisDev.get("type",""), thisDev ))
						if not devFound:
							if self.pluginPrefs.get("ignoreNewDevices", False): continue
							self.newDevice	= True							
							dev = indigo.device.create(
								protocol		= indigo.kProtocol.Plugin,
								address			= address,
								name			= name,
								description		= "",
								pluginId		= self.pluginId,
								deviceTypeId	= indigoType,
								folder			= self.folderNameDevicesID,
								props			= newprops
								)
							self.newDevice	= False							
							self.lastDevStates[dev.id] = {}
						if not dev.enabled: continue
						
						self.fixAllhomematic(address=address)
						self.homematicAllDevices[address]["type"]			= vType
						self.homematicAllDevices[address]["title"]			= "Sysvar-"+title
						self.homematicAllDevices[address]["indigoId"]		= dev.id
						self.homematicAllDevices[address]["indigoDevType"]	= dev.deviceTypeId

						if len(dev.states["created"]) < 5:
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
						if len(dev.states["address"]) < 5:
							self.addToStatesUpdateDict(dev, "address", address)
						self.addToStatesUpdateDict(dev, "title", title)
						if "unit" in dev.states:
							self.addToStatesUpdateDict(dev, "unit",unit)
						self.addToStatesUpdateDict(dev, "description", thisDev.get("description",""))
						self.addToStatesUpdateDict(dev, "homematicType", thisDev.get("type",""))
						if vType == "FLOAT":
							if unit !="":
								self.addToStatesUpdateDict(dev, "sensorValue", round(value,1), f"{value:.1f}{unit:}")
							else:
								self.addToStatesUpdateDict(dev, "sensorValue", round(value,1), f"{value:.1f}")

						elif vType == "BOOL":
							self.addToStatesUpdateDict(dev, "onOffState", value)
						elif vType == "ALARM":
							self.addToStatesUpdateDict(dev, "onOffState", value)
						elif vType == "STRING":
							self.addToStatesUpdateDict(dev, "value", value)

					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.newDevice = False
		return


	####-----------------	 ---------
	def doallVarToDev(self, doit):
		# soem dev states are calculated on hometic and stored in avriables, thsi will take the info from teh sys vars and update the indigo dev/states
		try:
			if not doit: return 
			devChild = {}
			dev = {}
			
			for linkAdr in self.variablesToDevices:
				changed = 0
				devInfo = self.variablesToDevices[linkAdr]
				if linkAdr  not in self.variablesToDevicesLast: changed += 1; self.variablesToDevicesLast[linkAdr] = {}
				address = devInfo["devAddress"]
				if address not in self.homematicAllDevices: continue
				if self.homematicAllDevices[address]["indigoId"] < 1 or self.homematicAllDevices[address]["indigoStatus"]  != "active": continue

				for stateType in devInfo["type"]:
					if stateType not in k_mapTheseVariablesToDevices: continue
						
					for typeCounter in devInfo["type"][stateType]["values"]:

						if devInfo["type"][stateType]["values"][typeCounter][0] == -999: continue
						if typeCounter in k_mapTheseVariablesToDevices[stateType]:
							key = k_mapTheseVariablesToDevices[stateType][typeCounter][0]
							norm = k_mapTheseVariablesToDevices[stateType][typeCounter][1]
							form = k_mapTheseVariablesToDevices[stateType][typeCounter][2]
							value0, varAddress = devInfo["type"][stateType]["values"][typeCounter]
							updateSource = devInfo["type"][stateType]["updateSource"]
							
							if self.variablesToDevicesLast[linkAdr] != {} and value0 != self.variablesToDevicesLast[linkAdr]["type"][stateType]["values"][typeCounter][0]: 
								changed += 2

							if changed > 0:
								value = round(value0/norm,1) 
								if devInfo["devAddress"]  not in dev:
									dev[address] = indigo.devices[self.homematicAllDevices[address]["indigoId"]]	

								if dev[address].states.get("enabledChildren","") != "": # check if child 
									enabledChildren = dev[address].states.get("enabledChildren","").split(",")
									childInfo = json.loads(dev[address].states.get("childInfo","{}"))

									if stateType in childInfo: #   right child ?
										devId = childInfo[stateType][0]
										if devId > 1 and devId in indigo.devices: # exists?

											if devId not in devChild:  # did we get it already, some have multiple state to update, only get once 
												devChild[devId] = indigo.devices[devId]

											if key in devChild[devId].states: # update child  now 
												self.addToStatesUpdateDict(devChild[devId], key, value, uiValue=form.format(value))
												if devChild[devId].pluginProps.get("displayS","--") == key and "sensorValue" in devChild[devId].states:
													self.addToStatesUpdateDict(devChild[devId], "sensorValue", value, uiValue= form.format(value))
												continue	
										
								if key in dev[address].states: # update parent if it was not child 
									self.addToStatesUpdateDict(dev[address], key, value, uiValue= form.format(value))
								
			self.variablesToDevicesLast = copy.deepcopy(self.variablesToDevices)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return





	####-----------------	 ---------
	def doallDevices(self, doit):
		try:
			if not doit: return 
			startTime = time.time()
			if  "allDevice" not in self.allDataFromHomematic:  return 
			if  "address" not in self.allDataFromHomematic["allDevice"]:  return 
			doHeating = self.pluginPrefs.get("accept_HEATING",True)
			deviceFound = {}
			self.numberOfDevices = 0
			allValueLinks = self.allDataFromHomematic["allDevice"].get("allValueLinks",{})
			#self.indiLOG.log(20,"doallDevices, valuelinks: {}...<".format( str(allValueLinks)[0:100] ) )
			for address in self.allDataFromHomematic["allDevice"]["address"]:
				if self.pluginState == "stop": return theDict 
				if len(address) < 2: continue
				devinfoForChild = {}
				deviceFound[address] = True
				try:
					thisDev = self.allDataFromHomematic["allDevice"]["address"][address]

					if "type" not in thisDev: continue
					thisType = thisDev["type"].upper()
					title = thisDev.get("title","")

					if address not in self.homematicAllDevices: 
						self.fixAllhomematic(address=address)
						self.homematicAllDevices[address]["type"]	= thisType
					if self.homematicAllDevices[address]["homemtaticStatus"] == "deleted":
						if self.homematicAllDevices[address]["indigoId"] in indigo.devices:
							self.indiLOG.log(20,"doallDevices, #:{};  title:{}, enabling device in indigo, was added back on homematic".format( address, title) )
							dev = indigo.devices[self.homematicAllDevices[address]["indigoId"]]
							indigo.device.enable(dev, value=True)
						
	
					self.homematicAllDevices[address]["homemtaticStatus"] = "active"
					self.homematicAllDevices[address]["lastmessageFromHomematic"] = time.time()

					if self.homematicAllDevices[address]["indigoStatus"] not in ["active","create"]: continue
					#if address =="002EA0C98EEE0B":  self.indiLOG.log(20,"doallDevices, :{};  title:{}, aldev:{}".format( address, title, self.homematicAllDevices[address] ) )

					name = title 
					if name.find(address) == -1:
						name += "-"+ address	
	
					self.numberOfDevices += 1

					homematicType = thisDev.get("type","").split()[0]
					homematicTypeUpper = homematicType.upper()
					firmware = thisDev.get("firmware","")
					availableFirmware = thisDev.get("availableFirmware","")

					indigoType = ""
					for xx in k_supportedDeviceTypesFromHomematicToIndigo:
						if "||" in xx:  # must be exactely homematic == indigo  w/o any extra characters like -2 abc V2 ... || is at the end
							if homematicTypeUpper+"||" == xx:  # ad || to the end and check if it matches.
								indigoType =  k_supportedDeviceTypesFromHomematicToIndigo[xx]
								break
						else: # this is do the characters appear in 
							if homematicTypeUpper.find(xx) == 0:
								indigoType =  k_supportedDeviceTypesFromHomematicToIndigo[xx]
								break
					#if address =="002EA0C98EEE0B":  self.indiLOG.log(20,"doallDevices, :{};  pass 1".format( address) )

					if k_createStates.get(indigoType,"") =="": continue 
					#if address =="002EA0C98EEE0B":  self.indiLOG.log(20,"doallDevices, :{};  pass 2".format( address) )

					devFound = False
					if address in self.homematicAllDevices and self.homematicAllDevices[address]["indigoId"] != 0:
						try:
							dev = indigo.devices[self.homematicAllDevices[address]["indigoId"] ]
							props = dev.pluginProps
							devFound = True
							self.fixAllhomematic(address=address)
							self.homematicAllDevices[address]["type"] 			= homematicType
							self.homematicAllDevices[address]["title"] 			= title
							self.homematicAllDevices[address]["indigoId"] 		= dev.id
							self.homematicAllDevices[address]["indigoDevType"] 	= dev.deviceTypeId
						except: pass

					if not devFound:
						for dev in indigo.devices.iter(self.pluginId):
							if self.pluginState == "stop": return  
							if dev.deviceTypeId != indigoType: continue
							if "address" not in dev.states:
								continue
							if dev.states["address"] == address: 
								devFound = True
								self.fixAllhomematic(address=address)
								self.homematicAllDevices[address]["type"] 			= homematicType
								self.homematicAllDevices[address]["title"] 			= title
								self.homematicAllDevices[address]["indigoId"] 		= dev.id
								self.homematicAllDevices[address]["indigoDevType"]	= dev.deviceTypeId
								break
					#if address =="001F20C98F2D3D":  self.indiLOG.log(20,"doallDevices, :{};  pass 3".format( address) )

					if not devFound:
						try: 
							dev = indigo.devices[name]
							props = dev.pluginProps
							devFound = True
							self.fixAllhomematic(address=address)
							self.homematicAllDevices[address]["type"] 			= homematicType
							self.homematicAllDevices[address]["title"]			= title
							self.homematicAllDevices[address]["indigoId"] 		= dev.id
							self.homematicAllDevices[address]["indigoDevType"] 	= dev.deviceTypeId
						except: pass

					#if address =="00251F299A4815":  self.indiLOG.log(20,"doallDevices, :{};  pass 4".format( address) )

					if not devFound and not self.pluginPrefs.get("ignoreNewDevices", False): 
							if indigoType not in k_mapHomematicToIndigoDevTypeStateChannelProps: continue

							newprops = {}
							if indigoType in k_mapHomematicToIndigoDevTypeStateChannelProps:
								newprops = k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["props"]
							if "numberOfPhysicalChannels" in newprops:
								Nch = homematicTypeUpper.split("-C")[1]
								newprops["numberOfPhysicalChannels"] = Nch

					
							indigoStates = k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["states"]

							testStates = []
							for st in indigoStates:
								for chkIf in k_checkIfPresentInValues: 
									if st.upper().find(chkIf) > -1: 
										testStates.append( chkIf)
										break

							#if name == "HmIP-DRSI1-0029DD89A1358F": self.indiLOG.log(20,"doallDevices, 000 testStates:{}" .format(testStates))
							if testStates != []:
								for chkIf in testStates:
									for test in allValueLinks:
										if test.find(address) == -1: continue
		
										if test.find(chkIf) > -1: 
											#if name == "HmIP-DRSI1-0029DD89A1358F": self.indiLOG.log(20,"doallDevices, pass 2, chkIf:{},  links:{}" .format(chkIf,  test))
											newprops[chkIf+"_Ignore"] = False
											break
										newprops[chkIf+"_Ignore"] = True

							if indigoType in k_indigoDeviceisThermostatDevice:
								newprops["heatIsOn"] = True

							#if address =="00251F299A4815":  self.indiLOG.log(20,"doallDevices, :{};  pass 5".format( address) )
							if self.pluginPrefs.get("ignoreNewDevices", False): continue
							self.newDevice	= True							
							#self.indiLOG.log(20,"doallDevices, :{}; indigoType:{}, addr:{}, \nprops:{}, \nstates:{}".format( name, indigoType, address, newprops, k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["states"]) )
							dev = indigo.device.create(
								protocol		= indigo.kProtocol.Plugin,
								address			= address,
								name			= name,
								description		= "",
								pluginId		= self.pluginId,
								deviceTypeId	= indigoType,
								folder			= self.folderNameDevicesID,
								props			= newprops
								)
							self.newDevice	= False							
							self.homematicAllDevices[address]["indigoId"] = dev.id
							self.lastDevStates[dev.id] = {}
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
							self.addToStatesUpdateDict(dev, "address", address)
							if dev.deviceTypeId in k_indigoDeviceisThermostatDevice and dev.hvacMode == indigo.kHvacMode.Off:
								indigo.thermostat.setHvacMode(dev, indigo.kHvacMode.Heat)
	
							if indigoType in k_mapHomematicToIndigoDevTypeStateChannelProps:
								for zz in k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["states"]:
									yy = k_mapHomematicToIndigoDevTypeStateChannelProps[indigoType]["states"][zz]
									#if indigoType.find("SCTH") > -1: self.indiLOG.log(20,"created Device:{}; ==> map info:{}".format( dev.name, yy ) )
									#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, :{};  zz:{} - yy:{}".format( dev.name, zz, yy) )
									if "init" in yy:
										self.addToStatesUpdateDict(dev, yy["indigoState"], yy["init"])
							self.executeUpdateStatesList()
							dev = indigo.devices[dev.id]
							props = dev.pluginProps
							devFound = True
							self.fixAllhomematic(address=address)
							self.homematicAllDevices[address]["type"] = homematicType
							self.homematicAllDevices[address]["title"] = title
							self.homematicAllDevices[address]["indigoId"] =dev.id
							self.homematicAllDevices[address]["indigoDevType"] = dev.deviceTypeId
							for st in dev.states:
								if st.find("enabledChildren"):
									if dev.id not in self.devsWithenabledChildren: self.devsWithenabledChildren.append(dev.id)
									break

					if not devFound: continue

					#if address =="002EA0C98EEE0B":  self.indiLOG.log(20,"doallDevices, :{};  pass 6".format( address) )

					if not dev.enabled: continue
					self.homematicAllDevices[address]["indigoId"]	= dev.id
					self.homematicAllDevices[address]["indigoDevType"]	= dev.deviceTypeId

					if indigoType in k_systemAP: continue

					#if address =="002EA0C98EEE0B":  self.indiLOG.log(20,"doallDevices, :{};  pass 7, t:{}, id:{}, name:{}, homematicType:{} ".format( address, title, dev.id, dev.name, homematicType) )
					self.addToStatesUpdateDict(dev, "roomId", str(sorted(self.roomMembers.get(address,""))).strip("[").strip("]").replace("'",'') )
					self.addToStatesUpdateDict(dev, "title", title)
					self.addToStatesUpdateDict(dev, "firmware", firmware)
					self.addToStatesUpdateDict(dev, "availableFirmware", availableFirmware)
					self.addToStatesUpdateDict(dev, "homematicType", homematicType)


					if indigoType in k_devTypeHasChildren and devFound:

						childInfo0 = dev.states.get("childInfo", "{}")
						try:	
							childInfo = json.loads(childInfo0)
						except:
							self.indiLOG.log(20,"createDevicesFromCompleteUpdate, error in json decoding for 1 {}; childInfo0:>>{}<<".format( dev.name, childInfo0))
							continue
						enabledChildren = ""
						#if indigoType.find("INT000") > -1: self.indiLOG.log(20,"createDevicesFromCompleteUpdate,1 {}; childInfo:{}".format( dev.name, childInfo))
						anyChange = False
						if childInfo != {}: 
							parentProps = dev.pluginProps
							for mType in copy.copy(childInfo):
								#  {childInfo = childInfo:{'Temperature': [429389644, '4', 'HMIP-Temperature'], 'Humidity': [1093019429, '4', 'HMIP-Humidity'], 'Relay': [1422531914, '7', 'HMIP-Relay'], 'Dimmer': [738580295, '11', 'HMIP-Dimmer']}
								if mType not in childInfo:
									continue
								try:
									chId, chn, childDevType = childInfo[mType]
								except:
									childInfo[mType] = [0,"-99",mType] # set to default channel =-99 = all 
									continue
								if not parentProps.get("enable-"+mType, False): 
									if chId > 0:
										if chId in indigo.devices:
											delDev = indigo.devices[chId]
											indigo.device.delete(delDev)
											childInfo[mType] = [0, chn, childInfo[mType][2]]
									anyChange = True
									continue
								if chId > 0: 
									try:
										#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, :{}; exists: chId:{}".format( dev.name, chId ))
										dev1 = indigo.devices[chId]
										chId = dev1.id
									except:
										#self.indiLOG.log(30,"createDevicesFromCompleteUpdate, 3 {}; child w channel:{} , id:{}  does not exist, recreating ".format( dev.name, chn, chId ))
										chId = 0 
										del childInfo[mType]
										anyChange = True
								if chId == 0: 
									try: 	ii = int(mType)
									except: ii = -1
									self.indiLOG.log(20,"createDevicesFromCompleteUpdate, 4 :{};  address:{}-child, indigoType:{}, mType:{}, childDevType:{}".format( dev.name, address, indigoType, mType, childDevType  ) )
									self.newDevice	= True
									if name+"-child-{} of {}".format(mType, dev.id) in indigo.devices:
										dev1 = indigo.devices[name+"-child-{} of {}".format(mType, dev.id) ]
									else:
										if childDevType not in k_mapHomematicToIndigoDevTypeStateChannelProps:
											self.indiLOG.log(20,"createDevicesFromCompleteUpdate, 5 childDevType:{} not in k_mapHomematicToIndigoDevTypeStateChannelProps".format( childDevType  ) )
											continue

										props			 = k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]["props"]
										states			 = k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]["states"]
	
										for pp in parentProps:
											for vv in k_checkIfPresentInValues:
												if pp.upper().find(vv+"_IGNORE") == 0:
													props[pp] = parentProps[pp]
			
										props["isChild"] = True					
										dev1 = indigo.device.create(
											protocol		= indigo.kProtocol.Plugin,
											address			= address,
											name			= name+"-child-{} of {}".format(mType, dev.id),
											description		= "",
											pluginId		= self.pluginId,
											deviceTypeId	= childDevType,
											folder			= self.folderNameDevicesID,
											props			= k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]["props"]
											)
										self.newDevice	= False							
										self.addToStatesUpdateDict(dev1, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
										self.addToStatesUpdateDict(dev1, "address", address+"-child-"+mType)
										anyChange = True
										childInfo[mType] = [dev1.id, chn, childDevType]
										enabledChildren += mType+","
									self.addToStatesUpdateDict(dev1, "channelNumber", chn)
								self.addToStatesUpdateDict(dev1, "title", title)
								self.addToStatesUpdateDict(dev1, "homematicType", homematicType)
								self.addToStatesUpdateDict(dev1, "childOf", dev.id)

								if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate, :{};  address:{}-child, indigoType-child".format( dev1.name, address) )
						if anyChange: 
							self.addToStatesUpdateDict(dev, "childInfo",  json.dumps(childInfo))
							self.addToStatesUpdateDict(dev, "enabledChildren",  enabledChildren.strip(","))
							for mType in childInfo:
								chId , chn, childDevType  =  childInfo[mType]
								if childDevType not in k_mapHomematicToIndigoDevTypeStateChannelProps: continue
								if "states" not in k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]: continue
								homematicStateNames = k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]["states"]

								if chn not in  self.homematicAllDevices[address]["childInfo"]:
									self.homematicAllDevices[address]["childInfo"][chn] = {}
								for homematicStateName in homematicStateNames:
									if homematicStateName not in k_dontUseStatesForOverAllList:
										self.homematicAllDevices[address]["childInfo"][chn][homematicStateName] = chId
					

				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					if self.pluginState == "stop": return  
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.newDevice = False
		self.executeUpdateStatesList()					
		self.sleep(1)

		if  not self.firstReadAll:
			for address in self.homematicAllDevices:
				devId =  self.homematicAllDevices[address]["indigoId"]

				if  self.homematicAllDevices[address]["indigoStatus"] not in ["active"]: continue
				
				if devId not in indigo.devices: continue

				dev = indigo.devices[devId]
				states = dev.states
				#self.indiLOG.log(20,"dev.name: {}, chid{}".format(dev.name,  states.get("childInfo","") ))
				if not "childInfo" in states: continue
				try:	childInfo = json.loads(states["childInfo"]) 
				except: continue
				for mType in childInfo:
					#self.indiLOG.log(20,"dev.name: {}, mType?{}".format(dev.name, mType))
					chId , chn, childDevType  =  childInfo[mType]
					if childDevType not in k_mapHomematicToIndigoDevTypeStateChannelProps: continue
					if "states" not in k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]: continue
					homematicStateNames = k_mapHomematicToIndigoDevTypeStateChannelProps[childDevType]["states"]
					if chn not in  self.homematicAllDevices[address]["childInfo"]:
						self.homematicAllDevices[address]["childInfo"][chn] = {}
					for homematicStateName in homematicStateNames:
						#self.indiLOG.log(20,"address:{}, homematicStateName:{}, mType{}, chId:{} , chn:{}, childDevType:{}, self.homematicAllDevices[address][..chn]:{} ".format(address, homematicStateName, mType, chId , chn, childDevType, self.homematicAllDevices[address]["childInfo"][chn] ))
						if homematicStateName not in k_dontUseStatesForOverAllList:
							self.homematicAllDevices[address]["childInfo"][chn][homematicStateName] = chId


		for address in self.homematicAllDevices:
			if deviceFound != {} and address not in deviceFound:
				if address.find("address") == -1 and address.find("INT00") == -1 and self.homematicAllDevices[address]["type"] not in ["ROOM","STRING","FLOAT","BOOL","ALARM",""]:
					#self.indiLOG.log(20,"doallDevices  it looks as if HomeMatic#:{}, devId:{}, type:{} was deleted on Homematic, disabling in indigo".format(address, self.homematicAllDevices[address]["indigoId"] , self.homematicAllDevices[address]["type"] ))
					self.homematicAllDevices[address]["homemtaticStatus"] = "deleted"
					if self.homematicAllDevices[address]["indigoStatus"] == "active":
						try: 
							dev = indigo.devices[self.homematicAllDevices[address]["indigoId"]]
							indigo.device.enable(dev, value=False)
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		if self.decideMyLog("Time"):
			self.indiLOG.log(20,"doallDevices  elapsed time: {:.1f} secs".format(time.time()-startTime))

		self.firstReadAll = True


		return

	

	####-----------------	 ---------
	def createEverythingFromCompleteUpdate(self):
		try:
			
			if self.allDataFromHomematic == {} or self.allDataFromHomematic == "": return 

			doRooms = True
			doProgram = True
			doVendor = True
			doSysvar = True
			doVariablesToDevices = True
			doDevices = True


			##self.indiLOG.log(20,self.listOfprograms)
			self.makeListOfallPrograms(doProgram)
			self.makeListOfallVendors(doVendor)
			self.doallRooms(doRooms)
			self.doallSysVar(doSysvar)
			self.doallVarToDev(doVariablesToDevices)
			self.doallDevices(doDevices)

			self.oneCycleComplete = True
			self.executeUpdateStatesList()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)





	####-----------------	 ---------
	def getDeviceData(self):

		try:
			getHomematicClass = "" 
			getValuesLast = 0
			# make sure theat get all data is finished
			time.sleep(2) 
			for iii in range(20):
				if self.firstReadAll: break
				self.sleep(1)

			self.devCounter = 0
			self.threads["getDeviceData"]["status"] = "running"

			while self.threads["getDeviceData"]["status"]  == "running":
					self.sleep(0.3)
					if (time.time() - getValuesLast > self.getValuesEvery) or (time.time() - self.getDataNow > 0 ) : 
						#if self.decideMyLog("Special"): self.indiLOG.log(20,"getting getDataNow :{}, getDataNow :{}".format(time.time() - getValuesLast > self.getValuesEvery,  time.time() - self.getDataNow ))

						if self.testPing(self.ipNumber) != 0:
							self.indiLOG.log(30,"getDeviceData ping to {} not sucessfull".format(self.ipNumber))
							self.sleep(5)
							getValuesLast  = time.time()			
							continue
	
						if  getHomematicClass == "" or "getDeviceData" in self.restartHomematicClass:
							#self.indiLOG.log(20,f" .. (re)starting   class  for getDeviceData   {self.restartHomematicClass:}" )
							self.sleep(0.9)
							getHomematicClass = getHomematicData(self.ipNumber, self.portNumber, kTimeout = self.requestTimeout, calling="getDeviceData" )
							try: 	del self.restartHomematicClass["getDeviceData"] 
							except: pass
	
						# resset fast get after exp of time only before contiue to check  
						if time.time() - self.getDataNow > 0: self.getDataNow = time.time() + 9999999999
						getValuesLast  = time.time()			
						NumberOfhttpcalls, allValues = getHomematicClass.getDeviceValues(self.allDataFromHomematic)
						if self.pluginPrefs.get("writeInfoToFile", False):
							self.writeJson( allValues, fName=self.indigoPreferencesPluginDir + "allValues.json", sort = True, doFormat=True, singleLines=True )
						if allValues != "" and allValues != {}:
							#if self.decideMyLog("Special"): self.indiLOG.log(20,"received data")
							self.upDateDeviceData(allValues, NumberOfhttpcalls)

			time.sleep(0.1)
			if self.threads["getDeviceData"]["status"] == "running": self.indiLOG.log(30,f" .. getDeviceData ended, please restart plugin  end of while state: {self.threads['getDeviceData']['status']:}")
			self.threads["getDeviceData"]["status"] = "stop" 
			return 

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			#self.indiLOG.log(30,"getDeviceData forced or error exiting getDeviceData, due to stop ")
		time.sleep(0.1)
		if self.threads["getDeviceData"]["status"] == "running": self.indiLOG.log(30,f" .. getDeviceData ended, please restart plugin  exit at error;  state: {self.threads['getDeviceData']['status']:}")
		self.threads["getDeviceData"]["status"] = "stop" 
		return 

	####-----------------	 ---------
	def getCompleteupdate(self):

		getHomematicClassALLData = ""
		self.getcompleteUpdateLast  = 0
		self.threads["getCompleteupdate"]["status"] = "running"
		numberOfhttpCalls = 0
		while self.threads["getCompleteupdate"]["status"]  == "running":
			try:
				self.sleep(0.3)
				try:
					if time.time() - self.getcompleteUpdateLast < self.getCompleteUpdateEvery: continue 
					if  getHomematicClassALLData == "" or "getCompleteupdate" in self.restartHomematicClass:
						self.sleep(0.1)
						getHomematicClassALLData = getHomematicData(self.ipNumber, self.portNumber, kTimeout =self.requestTimeout, calling="getCompleteupdate" )
						#self.indiLOG.log(20,f" .. (re)starting   class  for getCompleteupdate  {self.restartHomematicClass:}" )
						self.firstReadAll = False
						try: 	del self.restartHomematicClass["getCompleteupdate"]
						except: pass

					if self.testPing(self.ipNumber) != 0:
						self.indiLOG.log(30,"getAllVendor ping to {} not sucessfull".format(self.ipNumber))
						self.sleep(5)
						self.getcompleteUpdateLast  = time.time()
						continue

					#self.indiLOG.log(20,f"getCompleteupdate .. time for complete update " )


					self.getcompleteUpdateLast  = time.time()

					objects = {
						"allDevice":		[True,0,0], 
						"allRoom":			[True,0,0], 
						"allFunction":		[True,0,0], 
						"allSysvar":		[True,0,0], 
						"allProgram":		[True,0,0], 
						"allVendor":		[True,0,0]
					}
					out = ""
					t0= time.time()
					ncallsThisTime = numberOfhttpCalls
					for xx in objects:
						if self.threads["getCompleteupdate"]["status"] != "running": return 
						if objects[xx][0]:
							#self.indiLOG.log(20,"testing  {:}".format(xx) )
							dt = time.time()
							if self.threads["getCompleteupdate"]["status"] != "running": break
							numberOfhttpCalls, self.allDataFromHomematic[xx] = getHomematicClassALLData.getInfo(xx)
							if self.threads["getCompleteupdate"]["status"] != "running": break
							objects[xx][1] = time.time() - dt
					
							ll = 0
							for yy in self.allDataFromHomematic[xx]:
								#self.indiLOG.log(20,"testing  {:}, yy:{}".format("address" in yy, str(allInfo[xx][yy])[0:30]) )
								if yy == "address": 
									ll = len(self.allDataFromHomematic[xx][yy])
									break
								else:
									ll = 0.5

							objects[xx][2] = ll
							out += "{}:{:.2f}[secs] #{:} items;  ".format(xx, objects[xx][1], objects[xx][2])

					if self.pluginPrefs.get("writeInfoToFile", False):
						self.writeJson(self.allDataFromHomematic, fName=self.indigoPreferencesPluginDir + "allData.json")

					if self.decideMyLog("Digest"): self.indiLOG.log(20,"written new allInfo file  {:}, # of http calls:{:}, Tot # http Calls: {:}, total time:{:.1f}[secs]".format(out, numberOfhttpCalls - ncallsThisTime, numberOfhttpCalls, time.time()- t0) )
					self.createEverythingFromCompleteUpdate()

				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					self.getHomematicClass  = ""

			except	Exception as e:
				#self.indiLOG.log(40,"", exc_info=True)
				#self.indiLOG.log(30,"getCompleteupdate forced or error exiting getCompleteupdate, due to stop ")
				pass
		if self.threads["getCompleteupdate"]["status"] == "running": self.indiLOG.log(30,f" .. getCompleteupdate ended, please restart plugin")
		self.threads["getCompleteupdate"]["status"] = "stop" 
		return 


	###########################	   MAIN LOOP  ## END ######################
	###########################	   MAIN LOOP  ## END ######################
	###########################	   MAIN LOOP  ## END ######################
	###########################	   MAIN LOOP  ## END ######################

	####-----------------	 ---------
	def checkOnDelayedActions(self):
		try:
			if self.delayedAction == {}: return 
			newD = {}
			for devId in copy.deepcopy(self.delayedAction):
				newD[devId] = []
				for nn in range(len(self.delayedAction[devId])):
					actionItems = self.delayedAction[devId][nn]
					if actionItems[0] == "updateState" and time.time() - actionItems[1] > 0:
						try:
							if len(actionItems) == 5:
								self.addToStatesUpdateDict(indigo.devices[devId], actionItems[2], actionItems[3], uiValue=actionItems[4] )
							else:
								self.addToStatesUpdateDict(indigo.devices[devId], actionItems[2], actionItems[3] )
						except: 
							continue
					else:
						newD[devId].append(actionItems)
				if newD[devId] == {}: del newD[devId] 
			self.delayedAction = newD

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	####-----------------	 ---------
	def processPendingCommands(self):
		try:
			if self.pendingCommand == {}: return 

			if self.pendingCommand.get("restartHomematicClass", False): 
				self.restartHomematicClass = {"getDeviceData":True, "getCompleteupdate":True}
				self.indiLOG.log(20,"processPendingCommands: restarting connect ")
				del  self.pendingCommand["restartHomematicClass"] 

			if self.pendingCommand.get("getFolderId", False): 
				self.getFolderId()
				del  self.pendingCommand["getFolderId"]

			if self.pendingCommand.get("setDebugFromPrefs", False): 
				self.setDebugFromPrefs(self.pluginPrefs)
				del  self.pendingCommand["setDebugFromPrefs"]

			if self.pendingCommand.get("createHometicHostDev", False): 
				del self.pendingCommand["createHometicHostDev"]
				found = False
				for dev in indigo.devices.iter(self.pluginId):
					if dev.deviceTypeId == "Homematic-Host":
						found = True
						self.hostDevId = dev.id
						break

				if not found:
					newProps = k_mapHomematicToIndigoDevTypeStateChannelProps["Homematic-Host"]["props"]
					newProps["ipNumber"] = self.pluginPrefs.get("ipNumber","") 
					newProps["portNumber"] = self.pluginPrefs.get("portNumber","") 
					self.newDevice	= True							
					dev = indigo.device.create(
						protocol		= indigo.kProtocol.Plugin,
						address			= self.pluginPrefs.get("ipNumber","")+":"+self.pluginPrefs.get("portNumber","") ,
						name			= "homematic host",
						description		= "",
						pluginId		= self.pluginId,
						deviceTypeId	= "Homematic-Host",
						folder			= self.folderNameDevicesID,
						props			= newProps
						)
					self.newDevice	= False							
					self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
					self.hostDevId = dev.id



		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.newDevice = False
		return 


	####-----------------	 ---------
	def isBool2(self, v, doInverse, vInverse):

		if doInverse:
			if vInverse in [1,True,"1","true","True","T","t"]: return True
			return False
		else:
			if v in [1,True,"1","true","True","T","t"]: return True
			return False

	########################################
	########################################
	####-----------------  logging ---------
	########################################
	########################################

	####-----------------	 ---------
	def writeErrorToLog( self, address, text, logLevel = 20):
		if address not in self.homematicAllDevices: return 
		if time.time() - self.homematicAllDevices[address]["lastErrorMsg"] > self.writeToLogAfter:
			self.indiLOG.log(logLevel, text)
		self.homematicAllDevices[address]["lastErrorMsg"] = time.time()
		return 

	####-----------------	 ---------
	def decideMyLog(self, msgLevel, MAC=""):
		try:
			if MAC != "" and MAC in self.MACloglist:				return True
			if msgLevel	 == "All" or "All" in self.debugAreas:		return True
			if msgLevel	 == ""  and "All" not in self.debugAreas:	return False
			if msgLevel in self.debugAreas:							return True

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False
#
###-----------------  valiable formatter for differnt log levels ---------
# call with: 
# formatter = LevelFormatter(fmt='<default log format>', level_fmts={logging.INFO: '<format string for info>'})
# handler.setFormatter(formatter)
class LevelFormatter(logging.Formatter):
	def __init__(self, fmt=None, datefmt=None, level_fmts={}, level_date={}):
		self._level_formatters = {}
		self._level_date_format = {}
		for level, format in level_fmts.items():
			# Could optionally support level names too
			self._level_formatters[level] = logging.Formatter(fmt=format, datefmt=level_date[level])
		# self._fmt will be the default format
		super(LevelFormatter, self).__init__(fmt=fmt, datefmt=datefmt)
		return

	####-----------------	 ---------
	def format(self, record):
		if record.levelno in self._level_formatters:
			return self._level_formatters[record.levelno].format(record)

		return super(LevelFormatter, self).format(record)



########################################
########################################
####-----------------  get homematic data class ---------
########################################
########################################

class getHomematicData():
	def __init__(self, ip, port, kTimeout=10, calling=""):
		self.ip = ip
		self.port = port
		self.kTimeout = kTimeout
		self.requestSession	 = requests.Session()
		self.LastHTTPerror = 0
		self.delayHttpfterError = 5
		self.suppressErrorsForSecs = 20 # secs
		self.LastErrorLog  = 0
		indigo.activePlugin.indiLOG.log(20,f"getHomematicData starting class ip:{ip:}, port:{port:},  called from:{calling:20s}, @ {datetime.datetime.now()}")
		self.connectCounter = 0
		self.doGetIndividualValuesDevices = False
		return 

	####-----------------	 ---------

	####-----------------	 ---------
	def getInfo(self, area):
		try:
			if indigo.activePlugin.pluginState == "stop": return ""
			if   area == "allDevice": 		return self.connectCounter, self.getAllDevice() 
			elif area == "allRoom": 		return self.connectCounter, self.getAllRoom() 
			elif area == "allFunction": 	return self.connectCounter, self.getAllFunction() 
			elif area == "allProgram": 		return self.connectCounter, self.getAllProgram() 
			elif area == "allVendor": 		return self.connectCounter, self.getAllVendor() 
			elif area == "allSysvar": 		return self.connectCounter, self.getAllSysvar() 
			
		except	Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
		return {area:"empty"}

	####-----------------	 ---------
	def doConnect(self, page, getorput="get", data="", logText=""):
		self.connectCounter += 1
		try:
			if indigo.activePlugin.decideMyLog("Connect"):  indigo.activePlugin.indiLOG.log(20,"doConnect: {}  {}  page:{}< data:{}...<".format(logText, getorput, page, str(data)[0:70]))
			if time.time() - self.LastHTTPerror < self.delayHttpfterError:
				time.sleep(self.delayHttpfterError - (time.time() - self.LastHTTPerror))
			if getorput =="get":
				r = self.requestSession.get(page, timeout=self.kTimeout)
			else:
				r = self.requestSession.put(page, data=data, timeout=self.kTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
			self.LastHTTPerror = 0
			return  r
		except:
			if time.time()- self.LastErrorLog > self.suppressErrorsForSecs: 
				indigo.activePlugin.indiLOG.log(30,"connect to hometic did not work for {}  page={}".format(getorput, page))
				self.LastErrorLog = time.time()
			self.LastHTTPerror = time.time()
		return ""

	####-----------------	 ---------
	def getDeviceValues(self, allData):
		try:
			tStart = time.time()
			if allData == "" or allData == {}: 						return self.connectCounter, {}
			if "allDevice" not in allData: 							return self.connectCounter, {}
			if "allValueLinks" not in allData["allDevice"]: 		return self.connectCounter, {}
			if "allSysvar" not in allData: 							return self.connectCounter, {}
			if "allValueLinks" not in allData["allSysvar"]:			return self.connectCounter, {}

			allValues = {}
			baseHtml = "http://{}:{}".format(self.ip , self.port)
			theList = allData["allDevice"]["allValueLinks"] + allData["allSysvar"]["allValueLinks"]
			#indigo.activePlugin.indiLOG.log(10,"getDeviceValues  the list:{} ...{}".format(str(theList)[0:40],str(theList)[-40:] ))
			linkHtml = "http://{}:{}/{}".format(self.ip , self.port, "~exgdata")
			dataJson = json.dumps({"readPaths":theList })

			r = self.doConnect(linkHtml, getorput="put", data=dataJson, logText="getDeviceValues  ")
			if r == "": return self.connectCounter, allValues

			valesReturnedJson = r.content.decode('ISO-8859-1')
			valesReturnedDict = json.loads(valesReturnedJson)

			for nn in range(len(theList)):
				link  = theList[nn]
				if "pv" not in valesReturnedDict["readResults"][nn]: continue
				if "v"	not in valesReturnedDict["readResults"][nn]["pv"]: continue

				allValues[link] = valesReturnedDict["readResults"][nn]["pv"]
			if indigo.activePlugin.decideMyLog("Time"):  indigo.activePlugin.indiLOG.log(20,"getDeviceValues time used ={:.3f}[secs]".format( time.time()- tStart))
			return self.connectCounter, allValues

		except	Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
		return self.connectCounter, {"allValues":"empty"}

	####-----------------	 ---------
	def getAllDevice(self):
		try:
			tStart = time.time()
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllDevice ping to {} not sucessfull".format(self.ip))
				return {}

			theDict = {"address":{}, "values": {}, "allValueLinks":[]}
			page = "device"
			pageQ = "~query?~path=device"
			baseHtml = "http://{}:{}/".format(self.ip , self.port)
			devices0Html = baseHtml+pageQ+"/*"
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice base Accessing URL: {}".format(devices0Html))

			r = self.doConnect(devices0Html,logText="getAllDevice base ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}
			

			content = r.content.decode('ISO-8859-1')
			devices = json.loads(content)
			for dev in devices:
				if indigo.activePlugin.pluginState == "stop": return theDict 
				theDict["address"][dev["address"]] = dev

			devices1Html = baseHtml + pageQ+"/*/*"
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice devices Accessing URL: {}".format(devices1Html))
	
			r = self.doConnect(devices1Html, logText="getAllDevice devices ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllDevice {}".format(content[0:100]))

			devices = json.loads(content)
			for dev in 	devices:
				if indigo.activePlugin.threads["getCompleteupdate"]["status"] != "running": return 
				if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10," getAllDevice dev {}".format(dev))
				if "parent" not in dev: continue # skip master  
				address = dev["parent"]
				if dev["parent"] not in theDict["address"]: 
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllDevice  aaddress not in detailed devs {}".format(dev["parent"] ))
					continue 

				if "channels" not in theDict["address"][address]:
					theDict["address"][address]["channels"] = {}

				channelNumber = str(dev["index"])
				theDict["address"][address]["channels"][channelNumber] = dev

				# now the details for the channel
				if "~links" not in dev: continue
				for prop in dev["~links"]:
					if indigo.activePlugin.pluginState == "stop": return theDict 
					if "href" not in prop: continue
					hrefProp = prop["href"]
					if hrefProp == "..": continue
					if hrefProp == "$MASTER": continue

					if hrefProp.find("room/") >-1: 
						theDict["address"][address]["channels"][channelNumber]["room"] = hrefProp.split("room/")[1]
						continue

					if hrefProp.find("function/") >-1: 
						theDict["address"][address]["channels"][channelNumber]["function"] = hrefProp.split("function/")[1]
						continue

					# get values
					link = "/device/{}/{}/{}".format(address,channelNumber,hrefProp)
					theDict["allValueLinks"].append(link)

					if self.doGetIndividualValuesDevices:
						if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice allValueLinks Accessing URL: {}".format(link))
						r = self.doConnect(baseHtml+link, logText="getAllDevice valueLink ")
						if r == "": return {}
						propDict= json.loads(r.content)
						if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllDevice valueLink  dict: {}".format(propDict))

					if "values" not in theDict["address"][address]["channels"][channelNumber]:
						theDict["address"][address]["channels"][channelNumber]["values"] = {}
					theDict["address"][address]["channels"][channelNumber]["values"][hrefProp] = {"link":link,"value":""}
					theDict["values"][link] = {}


			linkHtml = "http://{}:{}/{}".format(self.ip , self.port, "~exgdata")
			dataJson = json.dumps({"readPaths":theDict["allValueLinks"] })
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllDevice Accessing URL: {}, dataJ{}".format(linkHtml, dataJson))

			r = self.doConnect(linkHtml, getorput="put", data=dataJson, logText="getAllDevice data ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			valesReturnedJson = r.content.decode('ISO-8859-1')
			valesReturnedDict = json.loads(valesReturnedJson)
			
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllDevice theDict:\n{}".format(json.dumps(theDict, sort_keys=True, indent=2)))

			for nn in range(len(theDict["allValueLinks"])):
				if indigo.activePlugin.pluginState == "stop": return theDict 
				link  = theDict["allValueLinks"][nn]
				try:	dummy, device, address, channelNumber, hrefProp  = link.split("/")
				except: continue
				theDict["address"][address]["channels"][channelNumber]["values"][hrefProp]["value"] = valesReturnedDict["readResults"][nn]
				theDict["values"][link] = valesReturnedDict["readResults"][nn]

		except	Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		if indigo.activePlugin.decideMyLog("Time"):  indigo.activePlugin.indiLOG.log(20,"getAllDevice time used ={:.3f}[secs], #of httpCalls: {}".format( time.time()- tStart, self.connectCounter))
		return theDict


	####-----------------	 ---------
	def getAllRoom(self):
		try:
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllRoom ping to {} not sucessfull".format(self.ip))
				return {}
			theDict = {"address":{}}
			page = "room"
			baseHtml = "http://{}:{}/{}".format(self.ip , self.port,  page)

			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom Accessing URL: {}".format(baseHtml))

			r = self.doConnect(baseHtml, logText="getAllRoom  base")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllRoom all {}:{}".format(page, content))
			objects = json.loads(content)

			if "~links" in objects: 
				objectsLink = objects["~links"]
				theDict["links"] = objects["~links"]

				for room in objectsLink:
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllRoom  {},".format(room))
					if room.get("rel","")  !="room": continue
					if "href" not in room: continue

					address = room["href"]
					if address == "..": continue
					roomDevicesHref = "{}/{}".format(baseHtml, address)
					theDict["address"][address] = {"title":room["title"],"devices":[],"link":roomDevicesHref}
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom room Accessing URL: {},".format(roomDevicesHref))

					r = self.doConnect(roomDevicesHref, logText="getAllRoom data ")
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					roomDevicesDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllRoom dict: {}".format(roomDevicesDict))
					if "~links" not in roomDevicesDict: continue

					for detail in roomDevicesDict["~links"]:
						if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllRoom  detail: {}".format(detail))
						if "href" not in detail: continue
						if detail.get("rel","") != "channel": continue
						if detail["href"] == "..": continue 
						theDict["address"][address]["devices"].append({"link":detail["href"],"title":detail["title"]})

		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		return theDict

	####-----------------	 ---------
	def getAllFunction(self):
		try:
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllFunction ping to {} not sucessfull".format(self.ip))
				return {}
			theDict = {"address":{}}
			page = "function"
			baseHtml = "http://{}:{}/{}".format(self.ip , self.port,  page)

			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllFunction Accessing URL: {}".format(baseHtml))

			r = self.doConnect(baseHtml, logText="getAllFunction base ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllFunction all {}:{}".format(page, content))
			objects = json.loads(content)

			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllFunction {} {},".format(page, item))
					if item.get("rel","") != page: continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue

					roomDevicesHref = "{}/{}".format(baseHtml, address)
					theDict["address"][address] = {"title":item["title"],"devices":[],"link":roomDevicesHref}
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllFunction  Accessing URL: {},".format(roomDevicesHref))

					r = self.doConnect(roomDevicesHref, logText="getAllFunction data ")
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					roomDevicesDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10," getAllFunction dict: {}".format(roomDevicesDict))
					if "~links" not in roomDevicesDict: continue

					for detail in roomDevicesDict["~links"]:
						if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllFunction detail: {}".format(detail))
						if "href" not in detail: continue
						if detail.get("rel","") != "channel": continue
						if detail["href"] == "..": continue 
						theDict["address"][address]["devices"].append({"link":detail["href"],"title":detail["title"]})

		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		return theDict



	####-----------------	 ---------
	def getAllSysvar(self):
		try:
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllSysvar ping to {} not sucessfull".format(self.ip))
				return {}
			theDict = {"address":{},"allValueLinks":[]} 
			page = "sysvar"
			baseHtml = "http://{}:{}/{}".format(self.ip , self.port,  page)

			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar Accessing URL: {}".format(baseHtml))
			r = self.doConnect(baseHtml, logText="getAllSysvar base ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar all {}:{}".format(page, content))
			objects = json.loads(content)


			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar {} {},".format(page,item))
					if item.get("rel","")  != page: continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue
					theDict["address"][address] = {}

					itemsHref = "{}/{}".format(baseHtml, address)
					theDict["address"][address]["link"] = itemsHref
					theDict["allValueLinks"].append("/sysvar/"+itemsHref.split("/sysvar/")[1])
					
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} Accessing URL: {},".format(page, itemsHref))

					r = self.doConnect(itemsHref, logText="getAllSysvar data ")
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					itemsDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} dict: {}".format(page, itemsDict))
					for xx in itemsDict:
						if xx =="~links" : continue
						if xx =="identifier" : continue
						theDict["address"][address][xx] = itemsDict[xx]
					if "~links" not in itemsDict: continue

					valueHref = "{}/{}/~pv".format(baseHtml, address)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} Accessing URL: {},".format(page, valueHref))

					r = self.doConnect(valueHref)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					valueDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} dict: {}".format(page, valueDict))
					theDict["address"][address]["value"] = valueDict

		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		return theDict



	####-----------------	 ---------
	def getAllProgram(self):
		try:
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllProgram ping to {} not sucessfull".format(self.ip))
				return {}

			theDict = {"address":{}}
			page = "program"
			baseHtml = "http://{}:{}/{}".format(self.ip , self.port,  page)

			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram Accessing URL: {}".format(baseHtml))

			r = self.doConnect(baseHtml, logText="getAllProgram base ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllProgram all {}:{}".format(page, content))
			objects = json.loads(content)


			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.pluginState == "stop": return theDict 
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} {},".format(page,item))
					if item.get("rel","")  != page: continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue
					theDict["address"][address] ={}


					itemsHref = "{}/{}".format(baseHtml, address)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} Accessing URL: {},".format(page, itemsHref))

					r = self.doConnect(itemsHref, logText="getAllProgram data ")
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					itemsDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} dict: {}".format(page, itemsDict))
					for xx in itemsDict:
						if xx == "~links": continue
						if xx == "identifier": continue
						theDict["address"][address][xx] = itemsDict[xx]

					if "~links" not in itemsDict: continue
					valueHref = "{}/{}/~pv".format(baseHtml, address)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} Accessing URL: {},".format(page, valueHref))

					r = self.doConnect(valueHref)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					valueDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} dict: {}".format(page, valueDict))
					theDict["address"][address]["value"] = valueDict
					theDict["address"][address]["link"] = valueHref

		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		return theDict




	####-----------------	 ---------
	def getAllVendor(self):
		try:
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllVendor ping to {} not sucessfull".format(self.ip))
				return {}
			theDict = {"address":{}}
			page = "~vendor"
			baseHtml = "http://{}:{}/{}".format(self.ip , self.port,  page)
				

			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor Accessing URL: {}".format(baseHtml))

			r = self.doConnect(baseHtml, logText="getAllVendor base ")
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllVendor all {}:{}".format(page, content))
			objects = json.loads(content)

			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} {},".format(page,item))
					if item.get("rel","")  != "item": continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue

					itemsHref = "{}/{}".format(baseHtml, address)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} 1 Accessing URL: {},".format(page, itemsHref))
					try:

						r = self.doConnect(itemsHref, logText="getAllVendor data ")
						if r == "": return {}
						if indigo.activePlugin.pluginState == "stop": return {}

					except Exception as e:
						if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
						continue

					itemsDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10,"getAllVendor {} dict: {}".format(page, itemsDict))
					theDict["address"][address] = {
							"title":itemsDict.get("title","")}

					if "~links" not in itemsDict: continue
					for valueLinks in itemsDict["~links"]:
						if indigo.activePlugin.pluginState == "stop": return theDict 
						if "href" not in valueLinks: continue
						href1 = valueLinks["href"]
						if href1 == "..": continue
						if href1 == "~pv": 
							valueHref = "{}/{}".format(itemsHref, href1)
							if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} 2 Accessing URL: {},".format(page, valueHref))

							r = self.doConnect(valueHref, logText="getAllVendor data1 ")
							if r == "": return {}
							if indigo.activePlugin.pluginState == "stop": return {}

							valueDict = json.loads(r.content)
							if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} dict: {}".format(page, valueDict))
							theDict["address"][address]["value"] = valueDict
							theDict["address"][address]["link"] = valueHref

						else:
							theDict["address"][address][href1] = {}
							itemsHref2 = "{}/{}".format(itemsHref, href1)
							if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} 3 Accessing URL: {},".format(page, itemsHref2))

							r = self.doConnect(itemsHref2, logText="getAllVendor data2 ")
							if r == "": return {}

							itemsDict2 = json.loads(r.content)
							if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} dict: {}".format(page, itemsDict2))
							if "~links" not in itemsDict2: continue
							theDict["address"][address][href1] = {}
							for valueLinks2 in itemsDict2["~links"]:
								if indigo.activePlugin.pluginState == "stop": return theDict 
								if "href" not in valueLinks2: continue
								href3 = valueLinks2["href"]
								if href3 == "~pv": 
									itemsHref3 = "{}/{}".format(itemsHref2, href3)
									if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} 4 Accessing URL: {},".format(page, itemsHref3))

									r = self.doConnect(itemsHref3, logText="getAllVendor data3 ")
									if r == "": return {}

									itemsDict3 = json.loads(r.content)
									if indigo.activePlugin.decideMyLog("GetDataReturn"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} dict: {}".format(page, itemsDict3))
									theDict["address"][address][href1]["value"] = itemsDict3
									theDict["address"][address][href1]["link"] = itemsHref3


		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		return theDict


