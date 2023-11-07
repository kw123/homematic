#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# homematic Plugin
# Developed by Karl Wachs
# karlwachs@me.com

import datetime
import json

import subprocess
import fcntl
import os 
import sys
import pwd
import time
import platform
import struct
import codecs

import queue as queue
from queue import PriorityQueue

import socket
import getNumber as GT
import threading
import logging
import copy
import requests
from checkIndigoPluginName import checkIndigoPluginName 

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

from params import *



# left to be done:
#  for motion detection set action to reset afte 10secs 
# 
#  what to do with no update states ..
#
#
#


_dataVersion = 1.0
_defaultName ="Homematic"
## Static parameters, not changed in pgm


from params import *


_defaultDateStampFormat = "%Y-%m-%d %H:%M:%S"

######### set new  pluginconfig defaults
# this needs to be updated for each new property added to pluginProps. 
# indigo ignores the defaults of new properties after first load of the plugin 
kDefaultPluginPrefs = {
	"MSG":										"please enter values",
	"generalON":								False,
	"debugOn":									False,
	"expertOn":									False,
	"userId":									"",
	"password":									"",
	"portNumber":								"2121",
	"ipNumber":									"192.168.1.x",
	"ignoreNewDevices":							False,
	"folderNameDevices":						_defaultName,
	"folderNameVariables":						_defaultName,
	"delayOffForButtons":						"5",
	"tempUnit":									"C",
	"loopWait":									10,
	"getCompleteUpdateEvery":					60,
	"getValuesEvery":							3,
	"writeInfoToFile":							False,
	"requestTimeout":							10,
	"debugLogic":								False,
	"debugConnect":								False,
	"debugGetData":								False,
	"debugActions":								False,
	"debugUpdateStates":						False,
	"debugSpecial":								False,
	"debugAll":									False,
	"showLoginTest":							True
}

_debugAreas = ["Logic","Connect","GetData","Digest","Actions","UpdateStates","Time","Special","All"]
for xx in _debugAreas:
	kDefaultPluginPrefs["debug"+xx] = False


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
		self.sleep(0)
		return
		
####

	####-----------------			  ---------
	def __del__(self):
		indigo.PluginBase.__del__(self)

	###########################		INIT	## START ########################

	####----------------- @ startup set global parameters, create directories etc ---------
	def startup(self):
		if not checkIndigoPluginName(self, indigo): 
			exit() 

		try:
			self.initSelfVariables()

			self.currentVersion			 						= self.readJson(self.indigoPreferencesPluginDir+"dataVersion",defReturn={}).get("currentVersion",{})

			self.setDebugFromPrefs(self.pluginPrefs)

			self.getFolderId()

			self.pluginStartTime 								= time.time()


		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			exit(0)

		self.sleep(0)
		return


	###########################		util functions	## START ########################


	####----------------- @ startup set global parameters, create directories etc ---------
	def initSelfVariables(self):
		try:
			self.variablesToDevicesLast							= {}
			self.variablesToDevices 							= {}
			self.checkOnThreads 								= time.time()
			self.autosaveChangedValues							= 0
			self.dayReset 										= -1
			self.averagesCounts									= {}
			self.nextFullStateCheck 							= 0 # do a full one at start
			self.nextFullStateCheckAfter						= 61.345 # secs
			self.oneCycleComplete								= False
			self.addressToDevType								= {} # save execution time, only check those tha have chnaged w/o reading the states
			self.lastDevStates									= {} # save execution time, only check those tha have chnaged w/o reading the states
			self.hostDevId										= 0
			self.homematicIdtoIndigoId							= {}
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
			self.loopWait										= 2
			self.getcompleteUpdateLast							= 0
			self.getCompleteUpdateEvery 						= float(self.pluginPrefs.get("getCompleteUpdateEvery", "90"))
			self.getValuesEvery 								= float(self.pluginPrefs.get("getValuesEvery", "10"))
			self.getValuesLast									= 0
			self.requestTimeout									= float(self.pluginPrefs.get("requestTimeout", "10"))
			self.portNumber										= self.pluginPrefs.get("portNumber", "")
			self.ipNumber										= self.pluginPrefs.get("ipNumber", "")
			self.restartHomematicClass							= {}
			self.folderNameVariablesID 							= 0
			self.folderNameDevicesID							= 0
			self.roomMembers									= {}
			self.allDataFromHomematic							= self.readJson(fName=self.indigoPreferencesPluginDir + "allData.json")


		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			exit(0)


		return


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
			if self.decideMyLog("Connect"): self.indiLOG.log(10," sbin/ping  -c 1 -W 40 -o {} return-code: {}".format(ipN, ret) )

			#indigo.server.log(  ipN+"-1  {}".format(ret) +"  {}".format(time.time() - ss)  )

			if int(ret) == 0:  return 0
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

			try:
				self.folderNameVariablesID = indigo.variables.folders.getId(self.pluginPrefs.get("folderNameVariables", _defaultName))
			except:
				pass
			if self.folderNameVariablesID == 0:
				try:
					ff = indigo.variables.folder.create(self.pluginPrefs.get("folderNameVariables", _defaultName))
					self.folderNameVariablesID = ff.id
				except:
					self.folderNameVariablesID = 0
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
			out = "\n"
			out += "\n "
			out += "\n{}   =============plugin config Parameters========".format(_defaultName)

			out += "\ndebugAreas".ljust(40)								+	"{}".format(self.debugAreas)
			out += "\nlogFile".ljust(40)								+	self.PluginLogFile
			out += "\nipNumber".ljust(40)								+	self.ipNumber
			out += "\nport#".ljust(40)									+	self.portNumber
			out += "\nread values every".ljust(40)						+	"{}".format(self.getValuesEvery)
			out += "\nread complete info every".ljust(40)				+	"{}".format(self.getCompleteUpdateEvery)
			out += "\nloopWait".ljust(40)								+	"{}".format(self.loopWait)
			out += "\nrequestTimeout".ljust(40)							+	"{}".format(self.requestTimeout)

			out += "\n{}    =============plugin config Parameters========  END\n".format(_defaultName)

			out += self.listOfprograms
			out += self.listOfEvents

			out += "\n    Homematic address -> indigo id, name  =================="
			out += "\nHomematicAddr         Title                                        IndigoId devType         Indigo name "
			addList =[]
			for ad in self.homematicIdtoIndigoId:
				addList.append(ad)
			for address in sorted(addList):
				indigoId = self.homematicIdtoIndigoId[address]
				dev = indigo.devices[indigoId]
				try:	
						iname = dev.name
						devTypeId = dev.deviceTypeId
						title = dev.states.get("title"," not title")
				except: 
						iname = "no indigo name"
						devTypeId = "no devtype"
						title = "no title"
				out += "\n{:21} {:40} {:12} {:15} {:}".format(address, title, indigoId, devTypeId, iname)
			out += "\n "

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
	####-------------action filters  -----------
	def filterDevices(self, filter="", valuesDict={}, typeId=""):

		try:
			ret = []
			devType = k_actionTypes.get(filter,"")
			if devType == "": 
				self.indiLOG.log(20,"filterDevices: no proper filter given.. filter:{}, devType:{}".format(filter, devType))
				return ret

			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId in devType: 
					ret.append([dev.id, dev.name])

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return ret


	#  ---------- thermostat action  boost
	def boostThermostatAction(self, action, typeId):
		return self.boostThermostat(action.props, typeId)

	def boostThermostat(self, action, typeId=""):

		try:
			
			if self.decideMyLog("Actions"): self.indiLOG.log(20,"boostThermostat action:{}".format(str(action).replace("\n",", ")))

			if not self.isValidIP(self.ipNumber): return 

			dev = indigo.devices[int(action["deviceId"])]

			address = dev.states["address"]

			acp = k_actionParams.get(dev.deviceTypeId, {})

			props = dev.pluginProps
			dj = json.dumps({"v": action.get("OnOff","on") == "on" })

			if dev.deviceTypeId not in k_actionParams: return
			acp = k_actionParams[dev.deviceTypeId]

			if "states" not in acp: return
			state = acp["states"].get("BOOST_MODE","BOOST_MODE")
			channels = acp["channels"].get("BOOST_MODE","1")
			self.doSendAction( channels, address, state, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	# Main thermostat action set target temp called by Indigo Server.
	def boostThermostatAction(self, action, typeId):
		return self.boostThermostat(action.props, typeId)

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

			if dev.deviceTypeId not in k_actionParams: return
			acp = k_actionParams.get(dev.deviceTypeId, {})

			if "states" not in acp: return
			state =	acp["states"].get("SET_POINT_TEMPERATURE","SET_POINT_TEMPERATURE")
			channels = acp["channels"].get("SET_POINT_TEMPERATURE",["1"])

			self.doSendAction( channels, address, state, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####- door lock/unlock 
	def doorLockUnLockAction(self, action, typeId):
		return self.doorLockUnLock(action.props, typeId)

	def doorLockUnLock(self, action, typeId):
		try:


			if self.decideMyLog("Actions"): self.indiLOG.log(20,"doorLockUnLock dev:{}, action:{}".format(dev.name, str(action).replace("\n",", ")))

			if not self.isValidIP(self.ipNumber): 
				self.indiLOG.log(30,"doorLockUnLock {}  device:{}, bad IP number:{} ".format(dev.name, action,self.ipNumber) )
				return 


			address = dev.states["address"].split("-")[0]
			channels = []

			if dev.deviceTypeId not in k_actionParams: 
				self.indiLOG.log(30,"doorLockUnLock {}  device:{}, bad deviceTypeId:{} ".format(dev.name, action, dev.deviceTypeId) )
				return

			acp = k_actionParams.get(dev.deviceTypeId, {})

			if self.decideMyLog("Actions"): self.indiLOG.log(20,"doorLockUnLock acp:{}".format(acp))

			if "states" not in acp: 
				self.indiLOG.log(30,"doorLockUnLock {}  device:{}, sates not in acp:{} ".format(dev.name, action, acp) )
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
	def actionControlDimmerRelay(self, action, dev):
		try:


			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay dev:{}, action:{}".format(dev.name, str(action).replace("\n",", ")))

			if not self.isValidIP(self.ipNumber): 
				self.indiLOG.log(30,"actionControlDimmerRelay {}  device:{}, bad IP number:{} ".format(dev.name, action, self.ipNumber) )
				return 


			address = dev.states["address"].split("-")[0]
			channels = []

			if dev.deviceTypeId not in k_actionParams: 
				self.indiLOG.log(30,"actionControlDimmerRelay {}  device:{}, bad deviceTypeId:{} ".format(dev.name, action, dev.deviceTypeId) )
				return

			acp = k_actionParams.get(dev.deviceTypeId, {})

			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay acp:{}".format(acp))

			if "states" not in acp: 
				self.indiLOG.log(30,"actionControlDimmerRelay {}  device:{}, sates not in acp:{} ".format(dev.name, action, acp) )
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

			elif action.deviceAction == indigo.kDeviceAction.SetBrightness:
				if action.actionValue == 0:	
					dj = json.dumps({"v":0 })
					state =		acp["states"].get("Dimm","")
					for ch in acp["channels"].get("Dimm","1"):
						channels.append(ch) # turn off all channels
				else:
					if "mult" in acp:
						dj = json.dumps({"v": round(action.actionValue*acp["mult"]["Dimm"] ,2)})
					else:
						dj = json.dumps({"v":action.actionValue})
					for ch in acp["channels"].get("Dimm",["1"]):
						channels.append(ch)	# dimm only one channel
						break
			else:
				self.indiLOG.log(30,"actionControlDimmerRelay  {}  action not suppported  {}".format(dev.name, action))


				state =	acp["states"].get("Dimm","")

			self.doSendAction( channels, address, state, dj )

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,f"{dev.name:}, {action:}", exc_info=True)

		return 


	####- exec send 
	def doSendAction(self, channels, address, state, dj ):
		try:
			thisRequestSession = requests.Session()
			for ch in channels:	
				html = "http://{}:{}/device/{}/{}/{}/~pv".format(self.ipNumber ,self.portNumber, address, ch, state )
				r = "error"
				if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay html:{}, dj:{}<<".format(html, dj))

				try:
					r = thisRequestSession.put(html, data=dj, timeout=self.requestTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
				except Exception as e:
					self.indiLOG.log(30,"actionControlDimmerRelay  bad return for html:{}, dj:{} ==> {}, err:{}".format(html, dj, r, e))

				if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay ret:{}".format(r))
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return 


	###########################		ACTIONS END  ########################





	###########################		DEVICE	#################################
	def deviceStartComm(self, dev):
		if self.decideMyLog("Logic"): self.indiLOG.log(10,"starting device:  {}  {} ".format(dev.name, dev.id))


		if "address" in dev.states:
			address = dev.states["address"]
			self.homematicIdtoIndigoId[address]	= dev.id
			self.addressToDevType[address] = dev.deviceTypeId

		if	self.pluginState == "init":
			dev.stateListOrDisplayStateIdChanged()
			props = dev.pluginProps
			updateProp = True
			for prop in k_defaultProps.get(dev.deviceTypeId,{}):
				if prop != "" and  props.get(prop,"") == "":
					props[prop] = k_defaultProps[dev.deviceTypeId][prop]
					updateProp = True
					if self.decideMyLog("Logic"): self.indiLOG.log(10,"starting device:{}  uodating prop from  {}  to {} ".format(dev.name, props[prop], defaultProps[devTdev.deviceTypeIdypeId][prop]))
			if updateProp:
				dev.replacePluginPropsOnServer(props)

		elif self.pluginState == "run":
			self.devNeedsUpdate[dev.id] = True

		return

	####-----------------	 ---------
	def deviceStopComm(self, dev):
		if	self.pluginState != "stop":
			self.devNeedsUpdate[dev.id] = True
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"stopping device:  {}  {}".format(dev.name, dev.id) )

	####-----------------	 ---------
	def deviceDeleted(self, dev):  ### indigo calls this
		if "address" in dev.states:
			address = dev.states["address"]
			if address in self.homematicIdtoIndigoId:
				del self.homematicIdtoIndigoId[address]
			if address in self.homematicIdtoIndigoId:
				del self.addressToDevType[address] 
		if dev.deviceTypeId == "HomematicHost":
			self.hostDevId = 0
		return 


	####-----------------	 ---------
	def didDeviceCommPropertyChange(self, origDev, newDev):
		#if origDev.pluginProps['xxx'] != newDev.pluginProps['address']:
		#	 return True
		return False


####-------------------------------------------------------------------------####
	def getDeviceConfigUiValues(self, pluginProps, typeId, devId):
		try:
			theDictList =  super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)

			if typeId == "HomematicHost":
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


			if typeId == "HomematicHost":
				if not self.isValidIP(valuesDict["ipNumber"]):
					errorDict["ipNumber"] = "bad ip number"
					return (False, valuesDict, errorDict)

				if devId != 0:
					self.hostDevId = devId
					dev = indigo.devices[devId]
					props = dev.pluginProps	
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
			f = open(self.indigoPreferencesPluginDir + "changedValues.json", "w")
			f.write(json.dumps(self.changedValues))
			f.close()
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
							for ttx in k_GlobalConst_fillMinMaxStates:
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


			if dev.states.get("address","")  == "xx001860C98C9E3E":
				self.indiLOG.log(20,"addToStatesUpdateDict (2) dev:{:35s}, key:{}; value:{}".format(dev.name, key, value) )

			localCopy = copy.deepcopy(self.devStateChangeList)
			if dev.id not in localCopy:
				localCopy[dev.id] = {}

			if key in k_forceIntegerStates:
				try: 	value = int(value)
				except:	value = 0

			localCopy[dev.id][key] = [value, uiValue]

			doprint = False

			if key in k_sensorsThatHaveMinMaxReal:
				self.fillMinMaxSensors( dev, key, value, 1, localCopy[dev.id])
				self.updateChangedValuesInLastXXMinutes(dev, value, key, localCopy[dev.id],  decimalPlaces=1)
				doprint = True
			if key in k_sensorsThatHaveMinMaxInteger:
				self.fillMinMaxSensors( dev, key, value, 0, localCopy[dev.id])
				self.updateChangedValuesInLastXXMinutes(dev, value, key, localCopy[dev.id], decimalPlaces=0)
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
			lastSensorChangeFound = False
			for devId in  local:
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
						#if self.decideMyLog("Special")	 and   dev.deviceTypeId == "HMIP-ETRV": self.indiLOG.log(10,"executeUpdateStatesList :{},key:{}, nv:{}, ov:{}, ov0:{}".format(dev.name, key, value, nv, ov, ov0))

						if   key.find("RSSI") == 0 			and abs(dev.states[key] - value) < 3: continue
						elif key == "humidityInput1"		and abs(dev.states[key] - value) < 3: continue
						elif key == "HUMIDITY" 				and abs(dev.states[key] - value) < 3: continue
						elif key == "ILLUMINATION" 			and abs(dev.states[key] - value) < 3: continue
						elif key == "ACTUAL_TEMPERATURE" 	and abs(dev.states[key] - value) < 1: continue
						elif key == "temperatureInput1" 	and abs(dev.states[key] - value) < 1: continue

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

						if "lastSensorChange" in dev.states and not lastSensorChangeFound and (key == "sensorValue" or key == "onOffState" or state == k_stateThatTriggersLastSensorChange.get(dev.deviceTypeId,"")):
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

			if len(trigList) >0:
				for devName	 in trigList:
					indigo.variable.updateValue(_defaultName+"_With_Status_Change",devName)
				#self.triggerEvent("someStatusHasChanged")
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
			self.getCompleteUpdateEvery =					float(valuesDict.get("getCompleteUpdateEvery", "90"))
			self.getValuesEvery =							float(valuesDict.get("getValuesEvery", "10"))
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
				if dev.deviceTypeId == "HomematicHost":
					found = True
					if dev.deviceTypeId == "HomematicHost":
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
		if dev != "":
			devTypId = dev.deviceTypeId
			if devTypId == "HMIP-FALMOT":
				props = dev.pluginProps
				nch = int(props.get("numberOfPhysicalChannels",99))
				checkStates =  k_statesThatAreMultiChannelStates[devTypId]["states"]

		for state in statesToCreate:
			stateType = statesToCreate[state]

			if checkStates != []:
				#self.indiLOG.log(20,"dev:{}, state:{}, checkStates:{}".format(dev.name, state, checkStates))

				if state.split("-")[0] in checkStates:
					stN = int(state.split("-")[1])
					#self.indiLOG.log(20,"dev:{}, state:{}, channelActive-{} ?:{}".format(dev.name, state, stN, props.get("channelActive-{}".format(stN), False)))
					if stN > nch: 
						continue  # dont create state that do not exist
					if not props.get("channelActive-{}".format(stN), False):
						continue # if not active skip

			for xx in [state]:
				if xx != "":
					if   stateType == "real":			self.newStateList.append(self.getDeviceStateDictForRealType(xx, xx, xx))
					elif stateType == "integer":		self.newStateList.append(self.getDeviceStateDictForIntegerType(xx, xx, xx))
					elif stateType == "number":			self.newStateList.append(self.getDeviceStateDictForNumberType(xx, xx, xx))
					elif stateType == "real":			self.newStateList.append(self.getDeviceStateDictForRealType(xx, xx, xx))
					elif stateType == "string":			self.newStateList.append(self.getDeviceStateDictForStringType(xx, xx, xx))
					elif stateType == "booltruefalse":	self.newStateList.append(self.getDeviceStateDictForBoolTrueFalseType(xx, xx, xx))
					elif stateType == "boolonezero":	self.newStateList.append(self.getDeviceStateDictForBoolOneZeroType(xx, xx, xx))
					elif stateType == "Boolonoff":		self.newStateList.append(self.getDeviceStateDictForBoolOnOffType(xx, xx, xx))
					elif stateType == "boolyesno":		self.newStateList.append(self.getDeviceStateDictForBoolYesNoType(xx, xx, xx))
					elif stateType == "enum":			self.newStateList.append(self.getDeviceStateDictForEnumType(xx, xx, xx))
					elif stateType == "separator":		self.newStateList.append(self.getDeviceStateDictForSeparatorType(xx, xx, xx))
					if state in k_sensorsThatHaveMinMaxReal:
						for yy in k_stateMeasures:
							self.newStateList.append(self.getDeviceStateDictForRealType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
						for yy in k_stateMeasuresCount:
							self.newStateList.append(self.getDeviceStateDictForIntegerType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
					if state in k_sensorsThatHaveMinMaxInteger: 
						for yy in k_stateMeasures:
							self.newStateList.append(self.getDeviceStateDictForIntegerType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))
						for yy in k_stateMeasuresCount:
							self.newStateList.append(self.getDeviceStateDictForIntegerType(xx+"_"+yy, xx+"_"+yy, xx+"_"+yy))

		return 

	####-----------------	 ---------
	def getDeviceStateList(self, dev):

		try:
	
			self.newStateList  = super(Plugin, self).getDeviceStateList(dev)

			deviceTypeId = dev.deviceTypeId
			if deviceTypeId != "HomematicHost":

				if  deviceTypeId not in k_isNotRealDevice:
						self.doGetDevStateType(deviceTypeId, k_statesToCreateisRealDevice)

				if  deviceTypeId in k_isBatteryDevice:
						self.doGetDevStateType(deviceTypeId, k_statesToCreateisBatteryDevice)

				if  deviceTypeId in k_isVoltageDevice:
						self.doGetDevStateType(deviceTypeId, k_statesToCreateisVoltageDevice)

				if True:
					self.doGetDevStateType(deviceTypeId, k_allDevicesHaveTheseStates)
					self.doGetDevStateType(deviceTypeId, k_createStates[deviceTypeId], dev=dev)

			#self.indiLOG.log(20,"dev:{}, self.newStateList:{}".format(dev.name, self.newStateList))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return self.newStateList 

	####-----------------	 ---------
	def getDeviceDisplayStateId(self, dev):
			displayStateId  = super(Plugin, self).getDeviceDisplayStateId(dev)
			newd = ""
			deviceTypeId = dev.deviceTypeId

			if deviceTypeId in k_defaultProps:
				newd =  k_defaultProps[deviceTypeId].get("displayStateId","")
				if newd != "": return newd

			return displayStateId


	"""
######## set defaults for action and menu screens
	#/////////////////////////////////////////////////////////////////////////////////////
	# Actions Configuration
	#/////////////////////////////////////////////////////////////////////////////////////
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the actions for the plugin; you normally don't need to
	# override this as the base class returns the actions from the Actions.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getActionsDict(self):
		return super(Plugin, self).getActionsDict()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine obtains the callback method to execute when the action executes; it
	# normally just returns the action callback specified in the Actions.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getActionCallbackMethod(self, typeId):
		return super(Plugin, self).getActionCallbackMethod(typeId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the configuration XML for the given action; normally this is
	# pulled from the Actions.xml file definition and you need not override it
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getActionConfigUiXml(self, typeId, devId):
		return super(Plugin, self).getActionConfigUiXml(typeId, devId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the UI values for the action configuration screen prior to it
	# being shown to the user
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------	 ---------
	def getActionConfigUiValues(self, pluginProps, typeId, devId):
		return super(Plugin, self).getActionConfigUiValues(pluginProps, typeId, devId)


	#/////////////////////////////////////////////////////////////////////////////////////
	# Menu Item Configuration
	#/////////////////////////////////////////////////////////////////////////////////////
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the menu items for the plugin; you normally don't need to
	# override this as the base class returns the menu items from the MenuItems.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getMenuItemsList(self):
		return super(Plugin, self).getMenuItemsList()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the configuration XML for the given menu item; normally this is
	# pulled from the MenuItems.xml file definition and you need not override it
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getMenuActionConfigUiXml(self, menuId):
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
	"""


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
			if dev.deviceTypeId == "HomematicHost":
				self.hostDevId = dev.id
				break


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

			if time.time() - self.lastSecCheck  > 41:
				if self.hostDevId > 0:
					if  self.numberOfVariables >= 0:
						dev = indigo.devices[self.hostDevId]
						self.addToStatesUpdateDict(dev, "numberOfVariables", self.numberOfVariables)
						self.addToStatesUpdateDict(dev, "numberOfDevices", self.numberOfDevices)
						self.addToStatesUpdateDict(dev, "numberOfRooms", self.numberOfRooms)

					if time.time() - self.lastSucessfullHostContact  > 100:
							self.addToStatesUpdateDict(indigo.devices[self.hostDevId], "sensorValue", 0, uiValue="Offline")

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


				self.lastSecCheck = time.time()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return	changed





	####-----------------	 ---------
	def upDateDeviceData(self, allValues):

			#self.indiLOG.log(10,"all Values:{}".format(json.dumps(allValues, sort_keys=True, indent=2)))
		indigoIdforChild = 0
		## this for saving execution time. there are several states for each device, we dont need to reload the device multile times
		devChild = ""
		devTypeChild = ""
		devCurrent = ""
		devIdCurrent = -1
		devButtonCurrent = ""
		devButtonIdCurrent = -1
		tStart = time.time()
		dtimes = []
		
		self.devCounter +=1
		lastKeydev = 0
		dtNow = datetime.datetime.now().strftime(_defaultDateStampFormat)
		if allValues == {} or allValues == "": return 
		if allValues is None: return 

		for link in allValues:
			if link == "": continue
			try:
				lStart = time.time()
				ll = link.split()
				
				address, channelNumber, homematicStateName, homematicType = "","","value", ""
				if time.time() - self.lastSucessfullHostContact  > 10:
					if self.hostDevId != 0:
						self.addToStatesUpdateDict(indigo.devices[self.hostDevId], "sensorValue", 1, uiValue="Online")
						self.lastSucessfullHostContact = time.time()


				if link.find("/sysvar/") > -1: 
					try:	
						address   = link.split("/")[-1]
						homematicType =  "sysvar"
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

				elif link.find("/device/") > -1: 
					try:	
						dummy, dd, address, channelNumber, homematicStateName  = link.split("/") 
						homematicType =  "device"
					except: continue

				if address in self.homematicIdtoIndigoId:
					# get data:

					chState = channelNumber+"-"+homematicStateName
					stateCh = homematicStateName+"-"+channelNumber
					state = homematicStateName

					vHomatic = allValues[link].get("v","")
					v = vHomatic
					vui = ""
					tso = allValues[link].get("ts",0)
					ts = tso/1000.
					s = allValues[link].get("s",100)
					try:	dt = datetime.datetime.fromtimestamp(ts).strftime(_defaultDateStampFormat)
					except: dt = ""


					# now check how to use this 

					if True:  # check if right channel for state, eg LEVEL is in several channel sometimes  ie HIMP-PDT has LEVEL in 4 channels ch 2 is the right one 
						newdevTypeId = self.addressToDevType.get(address,"xxx")
						if 	newdevTypeId in k_useWichChannelForStateFromHomematicToIndigo:
							if homematicStateName in  k_useWichChannelForStateFromHomematicToIndigo[newdevTypeId]:
								if k_useWichChannelForStateFromHomematicToIndigo[newdevTypeId][homematicStateName] != channelNumber:
									continue


					if newdevTypeId in k_deviceTypesWithButtonPress and (homematicStateName in k_buttonPressStates ):
						if not vHomatic: continue
						if s > 0: continue
						#if address == "0002DF29B03B08" and homematicStateName.find("SHORT") >-1: self.indiLOG.log(20," upDateDeviceData address:{},  homematicStateName:{}, v:{}, t:{}".format(address,  chState, v,tso))
						#v = ts # button press always has true after first press, never goes to false, the info is the time stamp
						state = "buttonAction"
						v = tso

					#if address == "002EA0C98EEE0B" and channelNumber =="0": self.indiLOG.log(20," upDateDeviceData address:{},  newdevTypeId:{}, T?:{}, T?:{}".format(address,  newdevTypeId, newdevTypeId in k_deviceTypesWithKeyPad, homematicStateName in k_keyPressStates ))
					if newdevTypeId in k_deviceTypesWithKeyPad and (homematicStateName in k_keyPressStates  or homematicStateName[:19] in k_keyPressStates):
						if s > 0: continue
						#self.indiLOG.log(20," upDateDeviceData address:{},  homematicStateName:{}, v:{}, t:{}".format(address,  chState, v, tso))
						#v = ts # button press always has true after first press, never goes to false, the info is the time stamp
						state = "kepPadAction"
						key = v
						v = tso


					
					devIdNew = self.homematicIdtoIndigoId[address]
					if devIdNew < 1: continue

					 # test if same value as last time, if yes skip, but do a fulll one every 100 secs anyway
					if time.time() > self.nextFullStateCheck: # dont do this check if last full is xx secs ago
						#self.indiLOG.log(10," upDateDeviceData do a full check ".format( ))
						pass

					else:
						if devIdNew not in self.lastDevStates:
							 self.lastDevStates[devIdNew] = {}
						if chState not in self.lastDevStates[devIdNew]:
							self.lastDevStates[devIdNew][chState] = [v, tso]
						else:
							if self.lastDevStates[devIdNew][chState][0] == v and self.lastDevStates[devIdNew][chState][1] == tso: 
								continue
							else:
								self.lastDevStates[devIdNew][chState] = [v, tso] 

					# data accepted, now load it into indigo states
					if devIdCurrent == devIdNew:
						dev = devCurrent
					else:
						try:
							dev = indigo.devices[self.homematicIdtoIndigoId[address]]
							if dev.id not in self.lastDevStates: 	self.lastDevStates[dev.id] = {}
							devCurrent = dev
							devIdCurrent = dev.id
							devTypeId = dev.deviceTypeId
							lastKeyDev = 0
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							del self.homematicIdtoIndigoId[address]
							continue

					if not dev.enabled: continue
					props = dev.pluginProps

					if newdevTypeId in k_deviceTypesWithButtonPress and state == "buttonAction": #homematicStateName in k_buttonPressStates:
						# anything valid here?
						if channelNumber != "0" and tso != 0 and vHomatic and s == 0: 

								# get last values:
								lastValuesText = dev.states.get("lastValuesText","")
								try: 	lastInfo = json.loads(lastValuesText)
								except: lastInfo = {}

								#if address == "0002DF29B03B08": self.indiLOG.log(20," upDateDeviceData chState:{:20s}, lastButtonInfo:{},   t:{}".format(chState,  lastButtonInfo.get(chState, -1) ,   tso))


								if lastInfo.get(chState, -1) != tso:
									self.addToStatesUpdateDict(dev, "buttonPressedPrevious", dev.states.get("buttonPressed"))
									self.addToStatesUpdateDict(dev, "buttonPressedTimePrevious", dev.states.get("buttonPressedTime"))
									self.addToStatesUpdateDict(dev, "buttonPressedTypePrevious", dev.states.get("buttonPressedType"))
									self.addToStatesUpdateDict(dev, "buttonPressed", channelNumber)
									self.addToStatesUpdateDict(dev, "buttonPressedTime", dt)
									self.addToStatesUpdateDict(dev, "buttonPressedType", homematicStateName)
									self.addToStatesUpdateDict(dev, "onOffState", True)
									if dev.id not in self.delayedAction:
										self.delayedAction[dev.id] = []
									self.delayedAction[dev.id].append(["updateState", time.time() + float(self.pluginPrefs.get("delayOffForButtons",5)), "onOffState",False] )
									lastInfo[chState] = tso
									self.addToStatesUpdateDict(dev, "lastValuesText", json.dumps(lastInfo))
								continue


					if newdevTypeId in k_deviceTypesWithKeyPad and state == "kepPadAction": #homematicStateName in k_buttonPressStates:
						# anything valid here?
								# get last values:
						if lastKeyDev == 0:
							lastValuesText = dev.states.get("lastValuesText","")
							try: 	lastInfo = json.loads(lastValuesText)
							except: lastInfo = {}
							if dev.id not in self.delayedAction:
								self.delayedAction[dev.id] = []
							USER_AUTHORIZATION = dev.states["USER_AUTHORIZATION"].split(",")
						lastKeyDev = dev.id

						if channelNumber == "0": 
							if homematicStateName.find("USER_AUTHORIZATION_") == 0:
								NumberOfUsersMax = int(props.get("NumberOfUsersMax",8))
								if  len(USER_AUTHORIZATION) != NumberOfUsersMax:
									USER_AUTHORIZATION =  ["0" for i in range(NumberOfUsersMax)]
								nn = min(10,max(1,int(homematicStateName.split("_")[2])))-1

								if vHomatic != (USER_AUTHORIZATION[nn] == "1"):
									if vHomatic: USER_AUTHORIZATION[nn] = "1"
									else:		USER_AUTHORIZATION[nn] = "0"
									self.addToStatesUpdateDict(dev, "USER_AUTHORIZATION", ",".join(USER_AUTHORIZATION))

						if channelNumber == "0" and homematicStateName == "CODE_ID" and tso != 0 and vHomatic and s == 0: 
								if lastInfo.get(chState, -1) != tso:
									if int(key) > 8: 
										key = "bad code entered"
										self.addToStatesUpdateDict(dev, "userPrevious", dev.states.get("user"))
										self.addToStatesUpdateDict(dev, "userTimePrevious", dev.states.get("userTime"))
										self.addToStatesUpdateDict(dev, "user", key)
										self.addToStatesUpdateDict(dev, "userTime", dt)
									else:
										self.addToStatesUpdateDict(dev, "userPrevious", dev.states.get("user"))
										self.addToStatesUpdateDict(dev, "userTimePrevious", dev.states.get("userTime"))
										self.addToStatesUpdateDict(dev, "user", key)
										self.addToStatesUpdateDict(dev, "userTime", dt)
										self.addToStatesUpdateDict(dev, "onOffState", True)
										if dev.id not in self.delayedAction:
											self.delayedAction[dev.id] = []
										self.delayedAction[dev.id].append(["updateState", time.time() + float(self.pluginPrefs.get("delayOffForButtons",5)), "onOffState",False] )
									lastInfo[chState] = tso
									self.addToStatesUpdateDict(dev, "lastValuesText", json.dumps(lastInfo))
								continue





					if newdevTypeId == "HMIP-SPDR" and state.find("PASSAGE_COUNTER_VALUE") == 0:
						if channelNumber in ["2","3"]:
							if   channelNumber == "2": state = state+"-left"
							elif channelNumber == "3": state = state+"-right"



					if devTypeId in k_statesThatAreMultiChannelStates:
						if homematicStateName in k_statesThatAreMultiChannelStates[devTypeId]["states"]:
							if channelNumber in k_statesThatAreMultiChannelStates[devTypeId]["channels"].split(","):
								state = homematicStateName+"-"+channelNumber





					stateCopy = ""
					state3 = ""
					if devTypeId in k_duplicateStatesFromHomematicToIndigo:
						stateCopy = k_duplicateStatesFromHomematicToIndigo[devTypeId].get(homematicStateName, "")
					v2 = v
					v3 = v


					if state in dev.states:

						vui = ""
						if  homematicType ==  "sysvar":
							if   devTypeId == "HMIP-SYSYVAR-FLOAT": 	self.addToStatesUpdateDict(dev, "sensorValue", round(v,1), f"{v:.1f}")
							elif devTypeId == "HMIP-SYSYVAR-STRING": 	self.addToStatesUpdateDict(dev, "value", v)
							elif devTypeId == "HMIP-SYSYVAR-BOOL": 		self.addToStatesUpdateDict(dev, "onOffState", v)
							elif devTypeId == "HMIP-SYSYVAR-ALARM": 	self.addToStatesUpdateDict(dev, "onOffState", v)
							continue


						if  homematicType ==  "device":

							if props.get("invertState","no") == "yes":
								try: 	
									if type(v) == type(1):
										v = - v + 1
									elif type(v) == type(True):
										if v: v = False
										else:  v = True
								except:	pass


							if  homematicType ==  "room":
								continue


							## do status for states 
							if homematicStateName in dev.states and homematicStateName in k_stateValueNumbersToTextInIndigo:
								stautusReplacementList = k_stateValueNumbersToTextInIndigo[homematicStateName]
								#self.indiLOG.log(20,"getDeviceData, dev:{}, key:{}, value:{}, stautusReplacementList:{}".format(dev.name, homematicStateName, v , stautusReplacementList ) )
								self.addToStatesUpdateDict(dev, homematicStateName, "{}".format( stautusReplacementList[ max(0, min(len(stautusReplacementList)-1, v)) ]))
								continue


							if devTypeId in ["HMIP-DLD"] and state == "LOCK_STATE":
								self.addToStatesUpdateDict(dev, "lastSensorChange", dt)
								self.addToStatesUpdateDict(dev, "onOffState", v > 1, uiValue=v2 )
								continue


							if homematicStateName == "RAINING":
									if dt != "":
										if v: 
											if dev.states["RAIN_START"] != dt: 	self.addToStatesUpdateDict(dev, "RAIN_START", dt)
										else:
											if dev.states["RAIN_END"] != dt:	self.addToStatesUpdateDict(dev, "RAIN_END", dt)

							if devTypeId == "HMIP-SPDR":
								#self.indiLOG.log(20,"getDeviceData, dev:{}, key:{}, value:{}, ts:{}, s:{}".format(dev.name, state, v, ts, s ) )

								if channelNumber in ["2","3"]:

									#elif  state.find("PASSAGE_COUNTER_OVERFLOW") == 0:
									#	self.addToStatesUpdateDict(dev, state, v)

									if state.find("PASSAGE_COUNTER_VALUE") == 0:
										self.addToStatesUpdateDict(dev, state, v) 
										if v != dev.states[state]:		
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

									continue





							if state in k_statesThatAreTemperatures:
								try: 	v = float(v)
								except: v = 0.
								if self.pluginPrefs.get("tempUnit","C") == "F":
									v = round(v *9./32. + 32.,1)
								vui = "{:.1f}ºC".format(v)


							elif state in k_statesThatAreHumidity:
								try: 	v = float(v)
								except: v = 0.
								v = int(v)
								vui = "{:}[%]".format(v)

							elif state in k_statesThatAreWind:
								try: 	v = float(v)
								except: v = 0.
								v = round(v,1)
								vui = "{:}[km/h]".format(v)

							elif state in k_statesThatAreWindDir:
								try: 	v = float(v)
								except: v = 0.
								v = int(v)
								vui = "{:}º".format(v)

							elif state in k_statesThatAreIlumination:
								try: 	v = float(v)
								except: v = 0.
								v = int(v)
								vui = "{:}[Lux]".format(v)


							elif state.find("LEVEL-") == 0 or state == "LEVEL" and v != "":
								try: 	v = float(v)
								except: v = 0.
								try: 
									v = float(v)*100
									v = int(v)
									vui = "{:}[%]".format(v)
								except: pass


						if stateCopy != "":
							self.addToStatesUpdateDict(dev, stateCopy, v, uiValue=vui)
						self.addToStatesUpdateDict(dev, state, v, uiValue=vui)

						if props.get("displayS","--") in [state, stateCopy]:

							if "onOffState" in dev.states and props.get("SupportsOnState",False):
								if v in [1,True,"1","true","True"]: TF = True
								else: TF = False
								if dev.states["onOffState"] != TF:
									self.addToStatesUpdateDict(dev, "onOffState", TF, uiValue=vui)
									if "lastEvent" in dev.states:
										if TF:
											self.addToStatesUpdateDict(dev, "lastEventOn", dtNow)
										else:
											self.addToStatesUpdateDict(dev, "lastEventOff", dtNow)
 

							if "sensorValue" in dev.states and props.get("SupportsSensorValue",False):
								if dev.states["sensorValue"] != v:
									self.addToStatesUpdateDict(dev, "sensorValue", v, uiValue=vui)

					if devTypeId in k_devTypeHasChildren:
						indigoIdforChildnew = int( dev.states.get("childId",0))
						#if indigoIdforChildnew == 1139401366 or self.decideMyLog("UpdateStates") :	 self.indiLOG.log(10," getDeviceData state:{}, ".format( state))
						if indigoIdforChildnew > 0:
							#if indigoIdforChildnew == 1139401366  or self.decideMyLog("UpdateStates") :	 self.indiLOG.log(10," getDeviceData  indigoIdforChild:{}".format(indigoIdforChildnew))
							if indigoIdforChild != indigoIdforChildnew:
								devChild = indigo.devices[indigoIdforChildnew]
								devTypeChild = k_devTypeHasChildren[devTypeId]["devType"]

							if  state == k_devTypeHasChildren[devTypeId]["state"] and  state in k_duplicateStatesFromHomematicToIndigo[devTypeChild]:
								self.addToStatesUpdateDict(devChild, k_duplicateStatesFromHomematicToIndigo[devTypeChild][state], v, uiValue=vui)

							if state in devChild.states:  
								self.addToStatesUpdateDict(devChild, state, v, uiValue=vui)

							indigoIdforChild = indigoIdforChildnew
						
				if self.decideMyLog("Time"): dtimes.append(time.time() - lStart)

				
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		if self.decideMyLog("Time"):  tMain = time.time() - tStart

		if time.time() > self.nextFullStateCheck:  
			self.nextFullStateCheck  = time.time() + self.nextFullStateCheckAfter

		self.executeUpdateStatesList()
		if self.decideMyLog("Time"):  
			tAve = 0
			for x in dtimes:
				tAve += x
			tAve = tAve / max(1,len(dtimes))
			self.indiLOG.log(20,"upDateDeviceData, counter:{} elapsed times - tot:{:.3f}, tMain:{:.3f}   per state ave:{:.5f},  N-States:{:}  ".format(self.devCounter, time.time() - tStart, tMain, tAve, len(dtimes)  ) )
		return 




	####-----------------	 ---------

	def updateRain(self, dev, state, value, tinsecs):
		try:
			return 


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return





	####-----------------	 ---------
	def createDevicesFromCompleteUpdate(self):
		try:
			doDevices = True
			doRooms = True
			doSysvar = True
			doProgram = True
			doVendor = True

			if self.allDataFromHomematic == {} or self.allDataFromHomematic == "": return 

			if doProgram and "address" in self.allDataFromHomematic["allProgram"]: 
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
				##self.indiLOG.log(20,self.listOfprograms)


			if doVendor and "address" in self.allDataFromHomematic["allVendor"]: 
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

			if doRooms and "address" in self.allDataFromHomematic["allRoom"]: 
				#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, rooms :{}; :{} .. all:{}".format( doRooms, "address" in self.allDataFromHomematic["allRoom"], str(self.allDataFromHomematic["allRoom"]["address"])[0:100]) )
 
				self.numberOfRooms = 0
				homematicType = "ROOM"
				self.roomMembers = {}
				for address in self.allDataFromHomematic["allRoom"]["address"]:
					try:
						thisDev = self.allDataFromHomematic["allRoom"]["address"][address]
						if self.hostDevId  > 0 and time.time() - self.lastSucessfullHostContact  > 20:
							self.addToStatesUpdateDict(indigo.devices[self.hostDevId], "sensorValue", 1, uiValue="Online")
							self.lastSucessfullHostContact = time.time()

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
						if indigoType in k_defaultProps:
							newprops = k_defaultProps[indigoType]
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
							self.lastDevStates[dev.id] = {}
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
							self.addToStatesUpdateDict(dev, "address", address)
						if not dev.enabled: continue

						self.homematicIdtoIndigoId[address]	= dev.id
						self.addressToDevType[address]= dev.deviceTypeId

						self.addressToDevType[address]= dev.deviceTypeId
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


			if doDevices and  "address" in self.allDataFromHomematic["allDevice"]:  
				self.numberOfDevices = 0
				for address in self.allDataFromHomematic["allDevice"]["address"]:
					try:
						thisDev = self.allDataFromHomematic["allDevice"]["address"][address]

						if "type" not in thisDev: continue

						if thisDev["type"].upper().find("HMIP-") == -1: continue
						self.numberOfDevices += 1

						title = thisDev.get("title","")
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

						if indigoType == "": continue

						if  indigoType not in k_createStates: continue 

						devFound = False
						if address in self.homematicIdtoIndigoId:
							try:
								dev = indigo.devices[self.homematicIdtoIndigoId[address]]
								devFound = True
							except: pass

						if not devFound:
							for dev in indigo.devices.iter(self.pluginId):
								if dev.deviceTypeId != indigoType: continue
								if "address" not in dev.states:
									#self.indiLOG.log(20,"createDevicesFromCompleteUpdate,dev:{} theType:{}, devFound:{};  address:{}".format(dev.name, theType, devFound, address) )
									continue
								if dev.states["address"] == address: 
									devFound = True
									break
						name = title +"-"+	address		
						#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, pass 4, title:{}".format(title) )
	
						if not devFound:
							try: 
								dev = indigo.devices[name]
								devFound = True
							except: pass

						if not devFound:
							newprops = {}
							if indigoType in k_defaultProps:
								newprops = k_defaultProps[indigoType]
							if "numberOfPhysicalChannels" in newprops:
								Nch = homematicTypeUpper.split("-C")[1]
								newprops["numberOfPhysicalChannels"] = Nch
							if k_indigoDeviceTypeIdToId[indigoType] == "thermostat":
								newprops["heatIsOn"] = True
							
							if self.pluginPrefs.get("ignoreNewDevices", False): continue
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
							self.lastDevStates[dev.id] = {}
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
							self.addToStatesUpdateDict(dev, "address", address)
							if k_indigoDeviceTypeIdToId.get(dev.deviceTypeId,"")  == "thermostat" and dev.hvacMode == indigo.kHvacMode.Off:
								indigo.thermostat.setHvacMode(dev, indigo.kHvacMode.Heat)
						if not dev.enabled: continue
						self.homematicIdtoIndigoId[address]	= dev.id
						self.addressToDevType[address]= dev.deviceTypeId

						self.addToStatesUpdateDict(dev, "roomId", str(sorted(self.roomMembers.get(address,""))).strip("[").strip("]").replace("'",'') )
						self.addToStatesUpdateDict(dev, "title", title)
						self.addToStatesUpdateDict(dev, "firmware", firmware)
						self.addToStatesUpdateDict(dev, "availableFirmware", availableFirmware)
						self.addToStatesUpdateDict(dev, "homematicType", homematicType)


						# create child if designed
						if indigoType in k_devTypeHasChildren:
							if  not devFound or (  dev.states["childId"] not in indigo.devices):
								dev1 = indigo.device.create(
									protocol		= indigo.kProtocol.Plugin,
									address			= address,
									name			= name+"- child of {}".format(dev.id),
									description		= "",
									pluginId		= self.pluginId,
									deviceTypeId	= k_devTypeHasChildren[indigoType]["devType"],
									folder			= self.folderNameDevicesID,
									props			= k_defaultProps[k_devTypeHasChildren[indigoType]["devType"]]
									)
								self.addToStatesUpdateDict(dev1, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
								self.addToStatesUpdateDict(dev1, "address", address+"-child")
								self.addToStatesUpdateDict(dev, "childId", dev1.id)
							else:
								dev1 = indigo.devices[self.homematicIdtoIndigoId[address+"-child"]]
							self.homematicIdtoIndigoId[address+"-child"]	= dev1.id

							self.addToStatesUpdateDict(dev1, "title", title)
							self.addToStatesUpdateDict(dev1, "homematicType", homematicType)
							self.addToStatesUpdateDict(dev1, "firmware", firmware)
							self.addToStatesUpdateDict(dev1, "availableFirmware", availableFirmware)

							if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate, :{};  address:{}-child, deviceTypeId:{}".format( dev1.name, address, k_devTypeHasChildren[indigoType]["devType"]) )

							self.addToStatesUpdateDict(dev1, "roomId",  str(sorted(self.roomMembers.get(address,""))).strip("[").strip("]").replace("'",''))
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

						


			if doSysvar and "address" in self.allDataFromHomematic["allSysvar"]:  
				self.numberOfVariables = 0
				#self.indiLOG.log(20,"createDevicesFromCompleteUpdate,  variablesToDevices:{}".format( json.dumps(self.variablesToDevices,sort_keys=True, indent=2) ))
				for address in self.allDataFromHomematic["allSysvar"]["address"]:
					try:
						thisDev = self.allDataFromHomematic["allSysvar"]["address"][address]
						self.numberOfVariables +=1

						
						vType = thisDev.get("type","string")
						indigoType = "HMIP-SYSVAR-"+vType
						title = thisDev.get("title","")
						if title.find("OldVal") >= 0: continue
						if title.find("sv") == 0:
							useThis = title.strip("sv").strip("HmiIP").split("_")
							if len(useThis) == 3: 	linkedDevAddress = useThis[2].split(":")
							else:					linkedDevAddress = []
							linkAdr = useThis[1]
							stateType = useThis[0].split("Counter")[0]
							if stateType in k_mapTheseVariablesToDevices:
								if linkAdr not in self.variablesToDevices:
									#self.indiLOG.log(20,"createDevicesFromCompleteUpdate,  title:{:45};  adding linkAdr:{}".format( title, linkAdr))
									self.variablesToDevices[linkAdr] = {"devAddress":"","type":{}}
								if stateType not in self.variablesToDevices[linkAdr]["type"]:
									self.variablesToDevices[linkAdr]["type"][stateType] = {"values":{"CounterToday":-999, "CounterYesterday": -999, "Counter":-999}, "channel":""}
								valueState = useThis[0].split(stateType)[1]
								self.variablesToDevices[linkAdr]["type"][stateType] ["values"][valueState] 	= thisDev["value"].get("v",0)

								if linkAdr in self.variablesToDevices and linkedDevAddress != []:		
									if self.variablesToDevices[linkAdr]["devAddress"] == "":			
										self.variablesToDevices[linkAdr]["devAddress"] 					= linkedDevAddress[0]
									self.variablesToDevices[linkAdr]["type"][stateType] ["channel"] 	= linkedDevAddress[1]
							continue

							#if linkAdr == "6568": self.indiLOG.log(20,"createDevicesFromCompleteUpdate,  title:{:45};  linkAdr:{}, stateType:{}; variablesToDevices:{}".format( title, linkAdr, stateType, self.variablesToDevices[linkAdr]))

						name = "Sysvar-"+title +"-"+ address		
						value = thisDev["value"].get("v",0)

						devFound = False
						try:
							dev = indigo.devices[self.homematicIdtoIndigoId[address]]
							devFound = True
						except: pass

						if not devFound:
							for dev in indigo.devices.iter(self.pluginId):
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
						if indigoType in k_defaultProps:
							newprops = k_defaultProps[indigoType]

						if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate,  devFound:{};  address:{}, desc:{}, htype:{}, thisdev:\n{}".format( devFound, address, thisDev.get("description"), thisDev.get("type",""), thisDev ))
						if not devFound:
							if self.pluginPrefs.get("ignoreNewDevices", False): continue
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
							self.lastDevStates[dev.id] = {}
						if not dev.enabled: continue
						self.homematicIdtoIndigoId[address]	= dev.id
						self.addressToDevType[address]= dev.deviceTypeId
						if len(dev.states["created"]) < 5:
							self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
						if len(dev.states["address"]) < 5:
							self.addToStatesUpdateDict(dev, "address", address)
						self.addToStatesUpdateDict(dev, "title", title)
						self.addToStatesUpdateDict(dev, "description", thisDev.get("description",""))
						self.addToStatesUpdateDict(dev, "homematicType", thisDev.get("type",""))
						if vType == "FLOAT":
							self.addToStatesUpdateDict(dev, "sensorValue", round(value,1), f"{value:.1f}")
						elif vType == "BOOL":
							self.addToStatesUpdateDict(dev, "onOffState", value)
						elif vType == "ALARM":
							self.addToStatesUpdateDict(dev, "onOffState", value)
						elif vType == "STRING":
							self.addToStatesUpdateDict(dev, "value", value)

					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


			# self.indiLOG.log(20,"createDevicesFromCompleteUpdate,  variablesToDevices:{}".format( json.dumps(self.variablesToDevices,sort_keys=True, indent=2) ))
			# fill dev states with contents of variables gathered above 
			devLoaded = {}
			for linkAdr in self.variablesToDevices:
				changed = 0
				devInfo = self.variablesToDevices[linkAdr]
				if linkAdr  not in self.variablesToDevicesLast: changed += 1
				address = devInfo["devAddress"]
				if address in self.homematicIdtoIndigoId:
					if not changed and address not in self.variablesToDevicesLast[linkAdr]["devAddress"]: changed +=2
					#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, address:{} == {}, linkAdr:{}, newDev:{}".format(devInfo["devAddress"] , dev.name, linkAdr, devInfo))
					for stateType in devInfo["type"]:
						if stateType in k_mapTheseVariablesToDevices:
							if not changed and stateType not in self.variablesToDevicesLast[linkAdr]["type"]: changed +=4
							
							for key2 in devInfo["type"][stateType]["values"]:
								#self.indiLOG.log(20,"createDevicesFromCompleteUpdate,stateType:{}, key2:{}, value:{}, map..{}, tf:{}".format(stateType, key2, devInfo["type"][stateType]["values"][key2], k_mapTheseVariablesToDevices[stateType], key2 in k_mapTheseVariablesToDevices[stateType]))

								if devInfo["type"][stateType]["values"][key2] == -999: continue
								if not changed and key2 not in self.variablesToDevicesLast[linkAdr]["type"][stateType]["values"]: changed +=8
								if key2 in k_mapTheseVariablesToDevices[stateType]:
										key = k_mapTheseVariablesToDevices[stateType][key2][0]
										norm = k_mapTheseVariablesToDevices[stateType][key2][1]
										form = k_mapTheseVariablesToDevices[stateType][key2][2]
										value0 = devInfo["type"][stateType]["values"][key2]
										if not changed and value0 != self.variablesToDevicesLast[linkAdr]["type"][stateType]["values"][key2]: 
											changed +=16
											#self.indiLOG.log(20,"createDevicesFromCompleteUpdate address:{}, key:{}, value0:{}, oldV:{}, form:{}, changed:{}".format(address, key, value0, self.variablesToDevicesLast[linkAdr]["type"][stateType]["values"][key2], form, changed))
										
										#self.indiLOG.log(20,"createDevicesFromCompleteUpdate address:{}, key:{}, value0:{} changed:{}".format(address, key, value0, changed))
										value = round(value0/norm,1) 

										if changed:
											if devInfo["devAddress"]  not in devLoaded:
												dev = indigo.devices[self.homematicIdtoIndigoId[address]]	
												devLoaded[address] = True
											if key in dev.states:
												#self.indiLOG.log(20,"createDevicesFromCompleteUpdate address:{}, key:{}, value:{}, form:{}".format(address, key, value, form))
												self.addToStatesUpdateDict(dev, key, value, f"form")
								
			self.variablesToDevicesLast = copy.deepcopy(self.variablesToDevices)
			self.oneCycleComplete = True
			self.executeUpdateStatesList()
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)





	####-----------------	 ---------
	def getDeviceData(self):

		try:
			getHomematicClass = "" 
			getValuesLast = 0
			time.sleep(3)
			self.devCounter = 0
			self.threads["getDeviceData"]["status"] = "running"

			while self.threads["getDeviceData"]["status"]  == "running":
					self.sleep(0.3)
					if time.time() - getValuesLast < self.getValuesEvery:  continue 
					if self.testPing(self.ipNumber) != 0:
						self.indiLOG.log(30,"getDeviceData ping to {} not sucessfull".format(self.ipNumber))
						self.sleep(5)
						getValuesLast  = time.time()			
						continue

					if  getHomematicClass == "" or "getDeviceData" in self.restartHomematicClass:
						#self.indiLOG.log(20,f" .. (re)starting   class  for getDeviceData   {self.restartHomematicClass:}" )
						self.sleep(0.9)
						getHomematicClass = getHomematicData(self.ipNumber, self.portNumber, kTimeout =self.requestTimeout, calling="getDeviceData" )
						try: 	del self.restartHomematicClass["getDeviceData"] 
						except: pass

	
					getValuesLast  = time.time()			
					allValues = getHomematicClass.getDeviceValues(self.allDataFromHomematic)
					if self.pluginPrefs.get("writeInfoToFile", False):
						self.writeJson( allValues, fName=self.indigoPreferencesPluginDir + "allValues.json", sort = True, doFormat=True, singleLines=True )
					if allValues != "" and allValues !={}:
						self.upDateDeviceData(allValues)

			time.sleep(0.1)
			if self.threads["getDeviceData"]["status"] == "running": self.indiLOG.log(30,f" .. getDeviceData ended, please restart plugin  end of while state: {self.threads['getDeviceData']['status']:}")
			self.threads["getDeviceData"]["status"] = "stop" 
			return 

		except	Exception as e:
			#self.indiLOG.log(40,"", exc_info=True)
			#self.indiLOG.log(30,"getDeviceData forced or error exiting getDeviceData, due to stop ")
			pass
		time.sleep(0.1)
		if self.threads["getDeviceData"]["status"] == "running": self.indiLOG.log(30,f" .. getDeviceData ended, please restart plugin  exit at error;  state: {self.threads['getDeviceData']['status']:}")
		self.threads["getDeviceData"]["status"] = "stop" 
		return 

	####-----------------	 ---------
	def getCompleteupdate(self):

		getHomematicClassALLData = ""
		self.getcompleteUpdateLast  = 0
		self.threads["getCompleteupdate"]["status"] = "running"
		while self.threads["getCompleteupdate"]["status"]  == "running":
			try:
				self.sleep(0.3)
				try:
					if time.time() - self.getcompleteUpdateLast < self.getCompleteUpdateEvery: continue 
					if  getHomematicClassALLData == "" or "getCompleteupdate" in self.restartHomematicClass:
						self.sleep(0.1)
						getHomematicClassALLData = getHomematicData(self.ipNumber, self.portNumber, kTimeout =self.requestTimeout, calling="getCompleteupdate" )
						#self.indiLOG.log(20,f" .. (re)starting   class  for getCompleteupdate  {self.restartHomematicClass:}" )
						try: 	del self.restartHomematicClass["getCompleteupdate"]
						except: pass

					if self.testPing(self.ipNumber) != 0:
						self.indiLOG.log(30,"getAllVendor ping to {} not sucessfull".format(self.ipNumber))
						self.sleep(5)
						self.getcompleteUpdateLast  = time.time()
						continue

					self.getcompleteUpdateLast  = time.time()

					objects = {
						"allDevice":	[True,0,0], 
						"allRoom":		[True,0,0], 
						"allFunction":	[True,0,0], 
						"allSysvar":	[True,0,0], 
						"allProgram":	[True,0,0], 
						"allVendor":	[True,0,0]
					}
					out = ""
					for xx in objects:
						if objects[xx][0]:
							#self.indiLOG.log(20,"testing  {:}".format(xx) )
							dt = time.time()
							if self.threads["getCompleteupdate"]["status"] != "running": break
							self.allDataFromHomematic[xx] = getHomematicClassALLData.getInfo(xx)
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
							out += "{}:{:.3f}, addresses:{:};  ".format(xx, objects[xx][1], objects[xx][2])

					if self.pluginPrefs.get("writeInfoToFile", False):
						self.writeJson(self.allDataFromHomematic, fName=self.indigoPreferencesPluginDir + "allData.json")

					if self.decideMyLog("Digest"): self.indiLOG.log(10,"written new allInfo file  elapsed times used  {:}".format(out) )
					self.createDevicesFromCompleteUpdate()

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
						if len(actionItems) == 5:
							self.addToStatesUpdateDict(indigo.devices[devId], actionItems[2], actionItems[3] , uiValue=actionItems[4] )
						else:
							self.addToStatesUpdateDict(indigo.devices[devId], actionItems[2], actionItems[3] )
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
					if dev.deviceTypeId == "HomematicHost":
						found = True
						self.hostDevId = dev.id
						break

				if not found:
					newProps = {}
					newProps["SupportsSensorValue"] = True
					newProps["SupportsOnState"] = False
					newProps["SupportsStatusRequest"] = False
					newProps["ipNumber"] = self.pluginPrefs.get("ipNumber","") 
					newProps["portNumber"] = self.pluginPrefs.get("portNumber","") 
					dev = indigo.device.create(
						protocol		= indigo.kProtocol.Plugin,
						address			= self.pluginPrefs.get("ipNumber","")+":"+self.pluginPrefs.get("portNumber","") ,
						name			= "homematic host",
						description		= "",
						pluginId		= self.pluginId,
						deviceTypeId	= "HomematicHost",
						folder			= self.folderNameDevicesID,
						props			= newProps
						)
					self.addToStatesUpdateDict(dev, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
					self.hostDevId = dev.id



		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


########################################
########################################
####-----------------  logging ---------
########################################
########################################


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
####-----------------  valiable formatter for differnt log levels ---------
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
		self.delayHttp = 0
		self.delayAmount = 5
		indigo.activePlugin.indiLOG.log(20,f"getHomematicData starting class ip:{ip:}, port:{port:},  called from:{calling:}")

		return 

	####-----------------	 ---------

	####-----------------	 ---------
	def getInfo(self, area):
		try:
			if indigo.activePlugin.pluginState == "stop": return ""
			if   area == "allDevice": 		return self.getAllDevice() 
			elif area == "allRoom": 		return self.getAllRoom() 
			elif area == "allFunction": 	return self.getAllFunction() 
			elif area == "allProgram": 		return self.getAllProgram() 
			elif area == "allVendor": 		return self.getAllVendor() 
			elif area == "allSysvar": 		return self.getAllSysvar() 
			
		except	Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
		return {area:"empty"}

	####-----------------	 ---------
	def doConnect(self, page, getorput="get", data=""):
		try:
			if indigo.activePlugin.decideMyLog("Connect"):  indigo.activePlugin.indiLOG.log(10,"doConnect: page:{},  {}".format(page,getorput))
			if time.time() - self.delayHttp < self.delayAmount:
				time.sleep(self.delayAmount)
			if getorput =="get":
				r = self.requestSession.get(page, timeout=self.kTimeout)
			else:
				r = self.requestSession.put(page, data=data, timeout=self.kTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
			self.delayHttp = 0
			return r
		except:
			indigo.activePlugin.indiLOG.log(30,"connect to hometic did not work for {}  page={}".format(getorput, page))
			self.delayHttp = time.time()
		return ""

	####-----------------	 ---------
	def getDeviceValues(self, allData):
		try:
			tStart = time.time()
			if allData == "" or allData == {}: return 
			if "allDevice" not in allData: return 
			if "allValueLinks" not in allData["allDevice"]: return 

			allValues = {}
			baseHtml = "http://{}:{}".format(self.ip , self.port)
			theList = allData["allDevice"]["allValueLinks"] + allData["allSysvar"]["allValueLinks"]
			#indigo.activePlugin.indiLOG.log(10,"getDeviceValues  the list:{} ...{}".format(str(theList)[0:40],str(theList)[-40:] ))
			linkHtml = "http://{}:{}/{}".format(self.ip , self.port, "~exgdata")
			dataJson = json.dumps({"readPaths":theList })

			r = self.doConnect(linkHtml, getorput="put", data=dataJson)
			if r == "": return allValues

			valesReturnedJson = r.content.decode('ISO-8859-1')
			#indigo.activePlugin.indiLOG.log(10,"getDeviceValues  tvalesReturnedJson:{} ...{}".format(valesReturnedJson[0:100],valesReturnedJson[-100:] ))
			valesReturnedDict = json.loads(valesReturnedJson)
			#if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getDeviceValues {}".format(valesReturnedJson[0:100]))

			for nn in range(len(theList)):
				link  = theList[nn]
				if "pv" not in valesReturnedDict["readResults"][nn]: continue
				if "v"	not in valesReturnedDict["readResults"][nn]["pv"]: continue

				allValues[link] = valesReturnedDict["readResults"][nn]["pv"]
			if indigo.activePlugin.decideMyLog("GetData"):  indigo.activePlugin.indiLOG.log(10,"getDeviceValues time used ={:.3f}[secs]".format( time.time()- tStart))
			return allValues

		except	Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
		return {"allValues":"empty"}

	####-----------------	 ---------
	def getAllDevice(self):
		try:
			if indigo.activePlugin.testPing(self.ip) != 0:
				if indigo.activePlugin.decideMyLog("Connect"): indigo.activePlugin.indiLOG.log(20,"getAllDevice ping to {} not sucessfull".format(self.ip))
				return {}

			theDict = {"address":{}, "values": {}, "allValueLinks":[]}
			page = "device"
			pageQ = "~query?~path=device"
			baseHtml = "http://{}:{}/".format(self.ip , self.port)
			devices0Html = baseHtml+pageQ+"/*"
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice Accessing URL: {}".format(devices0Html))

			r = self.doConnect(devices0Html)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}
			

			content = r.content.decode('ISO-8859-1')
			devices = json.loads(content)
			for dev in devices:
				if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice {}:{}".format(page, dev))
				theDict["address"][dev["address"]] = dev

			devices1Html = baseHtml + pageQ+"/*/*"
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice Accessing URL: {}".format(devices1Html))
	
			r = self.doConnect(devices1Html)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice {}".format(content[0:100]))

			devices = json.loads(content)
			for dev in 	devices:
				if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllDevice dev {}".format(dev))
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
					theDict["allValueLinks"] .append(link)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice prop Accessing URL: {}".format(link))

					r = self.doConnect(baseHtml+link)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					propDict= json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice   prop dict: {}".format(propDict))

					if "values" not in theDict["address"][address]["channels"][channelNumber]:
						theDict["address"][address]["channels"][channelNumber]["values"] = {}
					theDict["address"][address]["channels"][channelNumber]["values"][hrefProp] = {"link":link,"value":""}
					theDict["values"][link] = {}


			linkHtml = "http://{}:{}/{}".format(self.ip , self.port, "~exgdata")
			dataJson = json.dumps({"readPaths":theDict["allValueLinks"] })
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice Accessing URL: {}, dataJ{}".format(linkHtml, dataJson))

			r = self.doConnect(linkHtml, getorput="put", data=dataJson)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			valesReturnedJson = r.content.decode('ISO-8859-1')
			valesReturnedDict = json.loads(valesReturnedJson)
			
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice theDict:\n{}".format(json.dumps(theDict, sort_keys=True, indent=2)))

			for nn in range(len(theDict["allValueLinks"])):
				link  = theDict["allValueLinks"][nn]
				try:	dummy, device, address, channelNumber, hrefProp  = link.split("/")
				except: continue
				theDict["address"][address]["channels"][channelNumber]["values"][hrefProp]["value"] = valesReturnedDict["readResults"][nn]
				theDict["values"][link] = valesReturnedDict["readResults"][nn]

		except	Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
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

			r = self.doConnect(baseHtml)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom all {}:{}".format(page, content))
			objects = json.loads(content)

			if "~links" in objects: 
				objectsLink = objects["~links"]
				theDict["links"] = objects["~links"]

				for room in objectsLink:
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom  {},".format(room))
					if room.get("rel","")  !="room": continue
					if "href" not in room: continue

					address = room["href"]
					if address == "..": continue
					roomDevicesHref = "{}/{}".format(baseHtml, address)
					theDict["address"][address] = {"title":room["title"],"devices":[],"link":roomDevicesHref}
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom room Accessing URL: {},".format(roomDevicesHref))

					r = self.doConnect(roomDevicesHref)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					roomDevicesDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom dict: {}".format(roomDevicesDict))
					if "~links" not in roomDevicesDict: continue

					for detail in roomDevicesDict["~links"]:
						if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllRoom  detail: {}".format(detail))
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

			r = self.doConnect(baseHtml)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllFunction all {}:{}".format(page, content))
			objects = json.loads(content)

			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllFunction {} {},".format(page, item))
					if item.get("rel","") != page: continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue

					roomDevicesHref = "{}/{}".format(baseHtml, address)
					theDict["address"][address] = {"title":item["title"],"devices":[],"link":roomDevicesHref}
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllFunction  Accessing URL: {},".format(roomDevicesHref))

					r = self.doConnect(roomDevicesHref)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					roomDevicesDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllFunction dict: {}".format(roomDevicesDict))
					if "~links" not in roomDevicesDict: continue

					for detail in roomDevicesDict["~links"]:
						if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllFunction detail: {}".format(detail))
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
			r = self.doConnect(baseHtml)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar all {}:{}".format(page, content))
			objects = json.loads(content)


			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar {} {},".format(page,item))
					if item.get("rel","")  != page: continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue
					theDict["address"][address] = {}

					itemsHref = "{}/{}".format(baseHtml, address)
					theDict["address"][address]["link"] = itemsHref
					theDict["allValueLinks"].append("/sysvar/"+itemsHref.split("/sysvar/")[1])
					
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} Accessing URL: {},".format(page, itemsHref))

					r = self.doConnect(itemsHref)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					itemsDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} dict: {}".format(page, itemsDict))
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
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} dict: {}".format(page, valueDict))
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

			r = self.doConnect(baseHtml)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram all {}:{}".format(page, content))
			objects = json.loads(content)


			if "~links" in objects: 
				objectsLink = objects["~links"]

				for item in objectsLink:
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} {},".format(page,item))
					if item.get("rel","")  != page: continue
					if "href" not in item: continue

					address = item["href"]
					if address == "..": continue
					theDict["address"][address] ={}


					itemsHref = "{}/{}".format(baseHtml, address)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} Accessing URL: {},".format(page, itemsHref))

					r = self.doConnect(itemsHref)
					if r == "": return {}
					if indigo.activePlugin.pluginState == "stop": return {}

					itemsDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} dict: {}".format(page, itemsDict))
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
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} dict: {}".format(page, valueDict))
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

			r = self.doConnect(baseHtml)
			if r == "": return {}
			if indigo.activePlugin.pluginState == "stop": return {}

			content = r.content.decode('ISO-8859-1')
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor all {}:{}".format(page, content))
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
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} 1 Accessing URL: {},".format(page, itemsHref))
					try:

						r = self.doConnect(itemsHref)
						if r == "": return {}
						if indigo.activePlugin.pluginState == "stop": return {}

					except Exception as e:
						if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
						continue

					itemsDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor {} dict: {}".format(page, itemsDict))
					theDict["address"][address] = {
							"title":itemsDict.get("title","")}

					if "~links" not in itemsDict: continue
					for valueLinks in itemsDict["~links"]:
						if "href" not in valueLinks: continue
						href1 = valueLinks["href"]
						if href1 == "..": continue
						if href1 == "~pv": 
							valueHref = "{}/{}".format(itemsHref, href1)
							if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} 2 Accessing URL: {},".format(page, valueHref))

							r = self.doConnect(valueHref)
							if r == "": return {}
							if indigo.activePlugin.pluginState == "stop": return {}

							valueDict = json.loads(r.content)
							if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} dict: {}".format(page, str(valueDict)[:100]))
							theDict["address"][address]["value"] = valueDict
							theDict["address"][address]["link"] = valueHref

						else:
							theDict["address"][address][href1] = {}
							itemsHref2 = "{}/{}".format(itemsHref, href1)
							if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} 3 Accessing URL: {},".format(page, itemsHref2))

							r = self.doConnect(itemsHref2)
							if r == "": return {}

							itemsDict2 = json.loads(r.content)
							if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} dict: {}".format(page, itemsDict2))
							if "~links" not in itemsDict2: continue
							theDict["address"][address][href1] = {}
							for valueLinks2 in itemsDict2["~links"]:
								if "href" not in valueLinks2: continue
								href3 = valueLinks2["href"]
								if href3 == "~pv": 
									itemsHref3 = "{}/{}".format(itemsHref2, href3)
									if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllVendor  {} 4 Accessing URL: {},".format(page, itemsHref3))

									r = self.doConnect(itemsHref3)
									if r == "": return {}

									itemsDict3 = json.loads(r.content)
									if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10," getAllVendor {} dict: {}".format(page, itemsDict3))
									theDict["address"][address][href1]["value"] = itemsDict3
									theDict["address"][address][href1]["link"] = itemsHref3


		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
			return {}
		return theDict


