#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# uniFi Plugin
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


"""
_supportedDeviceTypesFromHomematicToIndigo = {
	"HMIP-WRC": 		"HMIP-WRC",			
	"HMIP-WRC1": 		"HMIP-WRC",			
	"HMIP-WRC2": 		"HMIP-WRC",			
	"HMIP-STHO": 		"HMIP-STHO",			
	"HMIP-FALMOT-C12": 	"HMIP-FALMOT-C12",			
	"HMIP-WTH-1": 		"HMIP-WTH",			
	"HMIP-WTH-B-2": 	"HMIP-WTH",			
	"HMIP-WTH-2": 		"HMIP-WTH",		
	"HMIP-SWDM": 		"HMIP-SWDM",			
	"HMIP-SWDM-1": 		"HMIP-SWDM",			
	"HMIP-SWDM-2": 		"HMIP-SWDM",			
	"HMIP-ETRV-B-2":	"HMIP-ETRV",			
	"HMIP-ETRV-2":	 	"HMIP-ETRV",			
	"HMIP-ETRV-1": 		"HMIP-ETRV",			
	"HMIP-PS-2":	 	"HMIP-PS",			
	"HMIP-PS-1":	 	"HMIP-PS",			
	"HMIP-PSM-1": 		"HMIP-PSM",			
	"HMIP-PSM-2": 		"HMIP-PSM",			
	"HMIP-RCV-50": 		"HMIP-RCV-50"			
}
"""

_supportedDeviceTypesFromHomematicToIndigo = {
	"HMIP-WRC": 		"HMIP-WRC",			
	"HMIP-STHO": 		"HMIP-STHO",			
	"HMIP-FALMOT-C12": 	"HMIP-FAL-C12",			
	"HMIP-FAL230-C10": 	"HMIP-FAL-C10",			
	"HMIP-FAL230-C6": 	"HMIP-FAL-C6",			
	"HMIP-FAL24-C10": 	"HMIP-FAL-C10",			
	"HMIP-FAL24-C6": 	"HMIP-FAL-C6",			
	"HMIP-WTH": 		"HMIP-WTH",			
	"HMIP-SWDM": 		"HMIP-SWDM",			
	"HMIP-ETRV":		"HMIP-ETRV",			
	"HMIP-PS-2":		"HMIP-PS",			
	"HMIP-PS-1":		"HMIP-PS",			
	"HMIP-PSM": 		"HMIP-PSM",
	"HMIP-PDT": 		"HMIP-PDT",
	"HMIP-SMI":			"HMIP-SMI",			
	"HMIP-RC8":			"HMIP-RC8",			
	"HMIP-RCV-50": 		"HMIP-RCV-50"	,		
	"HMIP-SYSVAR": 		"HMIP-SYSVAR"			
}

_supportedDeviceTypesFromIndigotoHomematic = {
	"HMIP-WRC": 		["HMIP-WRC","HMIP-WRC1","HMIP-WRC2"], 				
	"HMIP-STHO": 		["HMIP-STHO"],			
	"HMIP-FAL-C12": 	["HMIP-FALMOT-C12"]	,
	"HmIP-FAL-C10": 	["HmIP-FAL230-C10","HmIP-FAL24-C10"]	,
	"HmIP-FAL-C6": 		["HmIP-FAL230-C6","HmIP-FAL24-C6"]	,
	"HMIP-WTH":			["HMIP-WTH-1", "HMIP-WTH-B-2", "HMIP-WTH-2"],
	"HMIP-SWDM":		["HMIP-SWDM-1", "HMIP-SWDM-2", "HMIP-SWDM"],
	"HMIP-ETRV":	 	["HMIP-ETRV-2","HMIP-ETRV-1"],			
	"HMIP-PSM":	 		["HMIP-PSM-2","HMIP-PSM-1"],			
	"HMIP-PS":	 		["HMIP-PS-2","HMIP-PS-1"],	
	"HMIP-PDT":			["HMIP-PDT"],		
	"HMIP-RC8":	 		["HMIP-RC8"],			
	"HMIP-SMI":	 		["HMIP-SMI"],			
	"HMIP-RCV-50":		["HMIP-RCV-50"] ,					
	"HMIP-SYSVAR":		["HMIP-SYSVAR"] 					
}

_isBatteryDevice = [
	"HMIP-WRC",		
	"HMIP-STHO",			
	"HMIP-WTH",
	"HMIP-SWDM",
	"HMIP-SMI",
	"HMIP-RC8",
	"HMIP-ETRV"
]

_isVoltageDevice = [
	"HMIP-WRC",		
	"HMIP-STHO",			
	"HMIP-WTH",
	"HMIP-SWDM",
	"HMIP-ETRV",			
	"HMIP-RC8",		
	"HMIP-SMI",	
	"HMIP-PDT",
	"HMIP-FAL-C12",		
	"HMIP-FAL-C10",		
	"HMIP-FAL-C6",		
	"HMIP-RCV-50"					
]


_isNotRealDevice =[
	"HMIP-RCV-50",
	"HMIP-ROOM",
	"HMIP-SYSVAR"
]




_statesToCopyFromHomematic = {
		"HMIP-SMI":{
				"CURRENT_ILLUMINATION":"integer",
				"CURRENT_ILLUMINATION_STATUS":"integer",
				"ILLUMINATION":"real",
				"ILLUMINATION_STATUS":"integer",
				"MOTION": "booltruefalse",
				"MOTION_DETECTION_ACTIVE": "booltruefalse"
			},
		"HMIP-PS":{
				"ACTUAL_TEMPERATURE":"real",
				"ACTUAL_TEMPERATURE_STATUS":"integer",
				"ERROR_CODE": " integer",
				"ERROR_OVERHEAT": "booltruefalse",
				"ERROR_OVERLOAD": "booltruefalse",
				"ERROR_POWER_FAILURE": "booltruefalse",
#				"PRESS_LONG": " booltruefalsev",
#				"PRESS_LONG_RELEASE": "booltruefalse",
#				"PRESS_LONG_START": "booltruefalse",
#				"PRESS_SHORT": "booltruefalsev",
#				"PROCESS": "integer",
#				"SECTION": " integer",
#				"SECTION_STATUS": "string",
#				"COMBINED_PARAMETER": "string",
#				"WEEK_PROGRAM_CHANNEL_LOCKS": "integer",
#				"WEEK_PROGRAM_TARGET_CHANNEL_LOCK": "integer",
#				"WEEK_PROGRAM_TARGET_CHANNEL_LOCKS": "integer",
				"STATE": "booltruefalse"
			},
		"HMIP-PSM":{
				"ACTUAL_TEMPERATURE":"real",
				"ACTUAL_TEMPERATURE_STATUS":"integer",
				"ERROR_CODE": " integer",
				"ERROR_OVERHEAT": "booltruefalse",
				"ERROR_OVERLOAD": "booltruefalse",
				"ERROR_POWER_FAILURE": "booltruefalse",
#				"PRESS_LONG": " booltruefalsev",
#				"PRESS_LONG_RELEASE": "booltruefalse",
#				"PRESS_LONG_START": "booltruefalse",
#				"PRESS_SHORT": "booltruefalsev",
#				"PROCESS": "integer",
#				"SECTION": " integer",
#				"SECTION_STATUS": "string",
#				"COMBINED_PARAMETER": "string",
#				"WEEK_PROGRAM_CHANNEL_LOCKS": "integer",
#				"WEEK_PROGRAM_TARGET_CHANNEL_LOCK": "integer",
#				"WEEK_PROGRAM_TARGET_CHANNEL_LOCKS": "integer",
				"STATE": "booltruefalse",
				"CURRENT": "integer",
				"CURRENT_STATUS": "integer",
				"ENERGY_COUNTER": "integer",
				"ENERGY_COUNTER_OVERFLOW": "booltruefalse",
				"FREQUENCY": "real",
				"FREQUENCY_STATUS": "integer",
				"POWER": "integer",
				"POWER_STATUS": " integer",
				"VOLTAGE": "real",
				"VOLTAGE_STATUS": "integer",
			},
		"HMIP-PDT":{
				"ACTUAL_TEMPERATURE":"real",
				"ACTUAL_TEMPERATURE_STATUS":"integer",
				"ERROR_CODE": " integer",
				"ERROR_OVERHEAT": "booltruefalse",
				"ERROR_OVERLOAD": "booltruefalse",
				"ERROR_POWER_FAILURE": "booltruefalse",
#				"PRESS_LONG": " booltruefalsev",
#				"PRESS_LONG_RELEASE": "booltruefalse",
#				"PRESS_LONG_START": "booltruefalse",
#				"PRESS_SHORT": "booltruefalsev",
#				"PROCESS": "integer",
#				"SECTION": " integer",
#				"SECTION_STATUS": "string",
#				"COMBINED_PARAMETER": "string",
#				"WEEK_PROGRAM_CHANNEL_LOCKS": "integer",
#				"WEEK_PROGRAM_TARGET_CHANNEL_LOCK": "integer",
#				"WEEK_PROGRAM_TARGET_CHANNEL_LOCKS": "integer",
				"LEVEL": "integer",
				"LEVEL_Status": "integer"
			},

		"HMIP-WTH":{
				"ACTUAL_TEMPERATURE":"real",
				"ACTUAL_TEMPERATURE_STATUS":"integer",
				"FROST_PROTECTION":"booltruefalse",
				"HEATING_COOLING":"integer",
				"HUMIDITY":"real",
				"HUMIDITY_STATUS":"integer",
				"PARTY_MODE":"booltruefalse",
				"QUICK_VETO_TIME":"real",
				"SET_POINT_MODE":"integer",
				"SET_POINT_TEMPERATURE":"real",
				"SWITCH_POINT_OCCURED":"booltruefalse",
				"WINDOW_STATE":"string",
				"BOOST_MODE":"booltruefalse",
				"BOOST_TIME":"integer"
			},
		"HMIP-WRC":{
			"buttonPressed":"string",
			"buttonPressedTime":"string",
			"buttonPressedType":"string",
			"buttonPressedPrevious":"string",
			"buttonPressedTimePrevious":"string",
			"buttonPressedTypePrevious":"string",
			},
		"HMIP-RC8":{
			"buttonPressed":"string",
			"buttonPressedTime":"string",
			"buttonPressedType":"string",
			"buttonPressedPrevious":"string",
			"buttonPressedTimePrevious":"string",
			"buttonPressedTypePrevious":"string",
			},
		"HMIP-ETRV":{
				"ACTUAL_TEMPERATURE":"real",
				"ACTUAL_TEMPERATURE_STATUS":"integer",
				"FROST_PROTECTION":"booltruefalse",
				"PARTY_MODE":"booltruefalse",
				"QUICK_VETO_TIME":"real",
				"SET_POINT_MODE":"integer",
				"SET_POINT_TEMPERATURE":"real",
				"SWITCH_POINT_OCCURED":"booltruefalse",
				"LEVEL":"integer",
				"LEVEL_STATUS":"string",
				"VALVE_STATE":"string",
				"WINDOW_STATE":"string",
				"childId":"integer",
				"BOOST_MODE":"booltruefalse",
				"BOOST_TIME":"integer"
			},
		"HMIP-ETRV-child":{
				"LEVEL":"integer"
			},
		"HMIP-STHO":{
				"ACTUAL_TEMPERATURE":"real",
				"ACTUAL_TEMPERATURE_STATUS":"integer",
				"HUMIDITY":"real",
				"HUMIDITY_STATUS":"integer",
				"TEMPERATURE_OUT_OF_RANGE":"booltruefalse",
				"ERROR_CODE":"booltruefalse"
			},
		"HMIP-ROOM":{
				"roomListNames":"string",
				"NumberOfDevices":"integer",
				"roomListIDs":"string"
			},
		"HMIP-SWDM":{
				"STATE":"integer"
			},
		"HMIP-FAL-C12":{
				"DATE_TIME_UNKNOWN":"booltruefalse",
				"DUTY_CYCLE":"booltruefalse",
				"HEATING_COOLING":"integer",
				"HUMIDITY_ALARM":"booltruefalse",
				"TEMPERATURE_LIMITER":"booltruefalse"
			},
		"HMIP-FAL-C10":{
				"DATE_TIME_UNKNOWN":"booltruefalse",
				"DUTY_CYCLE":"booltruefalse",
				"HEATING_COOLING":"integer",
				"HUMIDITY_ALARM":"booltruefalse",
				"TEMPERATURE_LIMITER":"booltruefalse"
			},
		"HMIP-FAL-C6":{
				"DATE_TIME_UNKNOWN":"booltruefalse",
				"DUTY_CYCLE":"booltruefalse",
				"HEATING_COOLING":"integer",
				"HUMIDITY_ALARM":"booltruefalse",
				"TEMPERATURE_LIMITER":"booltruefalse"
		},
		"HMIP-SYSVAR":{
				"description":"string",
				"sensorValue":"number",
				"value":"string"
			},

}

_temperatureReal = ["temperatureInput1", "setpointHeat","ACTUAL_TEMPERATURE", "PARTY_SET_POINT_TEMPERATURE", "CONTROL_DIFFERENTIAL_TEMPERATURE", "SET_POINT_TEMPERATURE"]

_humdidityReal  = ["HUMIDITY"]


_usedWichStateForRead = {
		"HMIP-PDT":{
				"LEVEL":"2",
		},
		"HMIP-PS":{
				"LEVEL":"2",
		},
		"HMIP-PSM":{
				"LEVEL":"2"
		}
}



_stateValuesToText ={
		"SECTION_STATUS": [			#return state value =
			"ok",  					# 0
			"error" 				# 1
		],
		"LEVEL_STATUS": [
			"ok",					# 0
			"error"					# 1
		],
		"VALVE_STATE": [
			"STATE_NOT_AVAILABLE",  # 0
			"RUN_TO_START",			# 1
			"WAIT_FOR_ADAPTION",
			"ADAPTION_IN_PROGRESS",
			"ADAPTION_DONE",
			"TOO_TIGHT",
			"ADJUSTMENT_TOO_BIG",
			"ADJUSTMENT_TOO_SMALL"	# 7
		],
		"WINDOW_STATE": [
			"closed",				# 0
			"open"					# 1
		],

}

_multiChannelStatesDict = {
			"HMIP-FAL-C12":{
				"channels":"1,2,3,4,5,6,7,8,9,10,11,12",
				"states":{
#					"EMERGENCY_OPERATION":"booltruefalse",
#					"EXTERNAL_CLOCK":"booltruefalse",
#					"FROST_PROTECTION":"booltruefalse",
#					"HUMIDITY_LIMITER":"booltruefalse",
#					"DEW_POINT_ALARM":"booltruefalse",
					"LEVEL":"integer", # valve level
					"LEVEL_STATUS":"string",
					"VALVE_STATE":"string"
				}
			},
			"HMIP-FAL-C10":{
				"channels":"1,2,3,4,5,6,7,8,9,10",
				"states":{
					"LEVEL":"integer", # valve level
					"LEVEL_STATUS":"string",
					"VALVE_STATE":"string"
				}
			},
			"HMIP-FAL-C6":{
				"channels":"1,2,3,4,5,6",
				"states":{
					"LEVEL":"integer", # valve level
					"LEVEL_STATUS":"string",
					"VALVE_STATE":"string"
				}
			},
			"HMIP-PS":{
				"channels":"3,4,5",
				"states":{
#					"COMBINED_PARAMETER": "string",
					"ON_TIME": "integer",
					"PROCESS": "integer",
					"SECTION": "integer",
					"SECTION_STATUS": "string",
					"STATE": "booltruefalse"
				}
			},
			"HMIP-PSM":{
				"channels":"3,4,5",
				"states":{
#					"COMBINED_PARAMETER": "string",
					"ON_TIME": "integer",
					"PROCESS": "integer",
					"SECTION": "integer",
					"SECTION_STATUS": "string",
					"STATE": "booltruefalse"
				}
			}
}




for devTypeId in _multiChannelStatesDict:
	for state in _multiChannelStatesDict[devTypeId]["states"]:
		for ii in _multiChannelStatesDict[devTypeId]["channels"].split(","):
			_statesToCopyFromHomematic[devTypeId][state+"-"+ii] =  _multiChannelStatesDict[devTypeId]["states"][state]


_statesToCreateisBatteryDevice = {
				"LOW_BAT":"booltruefalse",
}

_statesToCreateisVoltageDevice = {
				"OPERATING_VOLTAGE":"real",
				"OPERATING_VOLTAGE_STATUS":"integer"
}

_statesToCreateisRealDevice = {
				"CONFIG_PENDING":"booltruefalse",
				"RSSI_DEVICE":"integer",
				"RSSI_PEER":"integer", 
				"UNREACH":"booltruefalse",
				"roomId":"integer",
				"roomName":"string",
				"firmware":"string",
				"availableFirmware":"string"
}

_wrongReadStates = {
				"CONTROL_DIFFERENTIAL_TEMPERATURE":"real",
				"DURATION_UNIT":"integer",
				"DURATION_VALUE":"integer",
				"INSTALL_TEST":"booltruefalse",
				"UPDATE_PENDING":"booltruefalse",
				"CONTROL_DIFFERENTIAL_TEMPERATURE":"real",
				"PARTY_SET_POINT_TEMPERATURE":"real",
				"PARTY_TIME_END":"real",
				"PARTY_TIME_START":"real",
				"DURATION_UNIT":"integer",
				"DURATION_VALUE":"integer",

}


_statesToCreateCommon = {
				"address":"string",
				"created":"string",
				"title":"string",
				"homematicType":"string",
				"lastSensorChange":"string"
}



_defaultProps = {
		"HMIP-WTH":{
			"displayS":"temperatureInput1",
			"SupportsHvacFanMode": False,
			"SupportsHvacOperationMode": False,
			"SupportsCoolSetpoint": False,
			"ShowCoolHeatEquipmentStateUI": False,
			"NumHumidityInputs": 0,
			"NumTemperatureInputs": 1,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		},
		"HMIP-WRC":{
			"displayS":"buttonPressed",
			"SupportsSensorValue":False,
			"SupportsOnState": True
		},
		"HMIP-RC8":{
			"displayS":"buttonPressed",
			"SupportsSensorValue":False,
			"SupportsOnState": True
		},
		"HMIP-SMI":{
			"displayS":"MOTION",
			"SupportsSensorValue":False,
			"SupportsOnState": True
		},
		"HMIP-STHO":{
			"displayS":"ACTUAL_TEMPERATURE",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-PDT":{
			"displayS":"brightnessLevel",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-FAL-C12":{
			"displayS":"LEVEL-1",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-FAL-C10":{
			"displayS":"LEVEL-1",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-FAL-C6":{
			"displayS":"LEVEL-1",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-SWDM":{
			"displayS":"STATE",
			"SupportsSensorValue":False,
			"SupportsOnState": True
		},
		"HMIP-RCV-50":{
			"displayS":"State",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-ETRV":{
			"displayS":"temperatureInput1",
			"SupportsHvacFanMode": False,
			"SupportsHvacOperationMode": False,
			"SupportsCoolSetpoint": False,
			"ShowCoolHeatEquipmentStateUI": False,
			"NumHumidityInputs": 0,
			"NumTemperatureInputs": 1,
			"childId": 0,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-ETRV-child":{
			"displayS":"brightnessLevel",
			"SupportsSensorValue":True,
		},
		"HMIP-PSM":{
			"displayS":"STATE",
			"SupportsSensorValue":False,
			"SupportsOnState": True
		},
		"HMIP-PS":{
			"displayS":"STATE",
			"SupportsSensorValue":False,
			"SupportsOnState": True
		},
		"HMIP-ROOM":{
			"displayS":"NumberOfDevices",
			"SupportsSensorValue":True,
			"SupportsOnState": False
		},
		"HMIP-SYSVAR":{
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
}

_actionParams = {
		"HMIP-WTH":{
			"states":{
				"SET_POINT_TEMPERATURE":"SET_POINT_TEMPERATURE",
				"BOOST_MODE":"BOOST_MODE"
			},
			"channels":{
				"SET_POINT_TEMPERATUREe":["1"],
				"BOOST_MODE":["1"]
			}
		},
		"HMIP-WRC":{
		},
		"HMIP-STHO":{
		},
		"HMIP-SWDM":{
			"states":{
				"OnOff":"OnOff",
			},
			"channels":{
				"OnOff":["1"]
			}
		},
		"HMIP-FAL-C12":{
			"states":{
				"OnOff":"OnOff",
			},
			"channels":{
				"OnOff":["1"]
			}
		},
		"HMIP-FAL-C10":{
			"states":{
				"OnOff":"OnOff",
			},
			"channels":{
				"OnOff":["1"]
			}
		},
		"HMIP-FAL-C6":{
			"states":{
				"OnOff":"OnOff",
			},
			"channels":{
				"OnOff":["1"]
			}
		},
		"HMIP-RCV-50":{
		},
		"HMIP-ETRV":{
			"states":{
				"SET_POINT_TEMPERATURE":"SET_POINT_TEMPERATURE",
				"BOOST_MODE":"BOOST_MODE",
				"Dimm":"LEVEL"
			},
			"channels":{
				"SET_POINT_TEMPERATURE":["1"],
				"BOOST_MODE":["1"],
				"Dimm":["1"]
			}
		},
		"HMIP-ETRV-child":{
			"states":{
				"Dimm":"LEVEL"
			},
			"channels":{
				"Dimm":["1"]
			},
			"mult":{
				"Dimm":0.01
			}
		},
		"HMIP-PDT":{
			"states":{
				"Dimm":"LEVEL"
			},
			"channels":{
				"Dimm":["3","4","5"]
			},
			"mult":{
				"Dimm":0.01
			}
		},
		"HMIP-PSM":{
			"states":{
				"OnOff":"STATE",
			},
			"channels":{
				"OnOff":["3","4","5"]
			}
		},
		"HMIP-PS":{
			"states":{
				"OnOff":"STATE",
			},
			"channels":{
				"OnOff":["3","4","5"]
			}
		},
		"HMIP-ROOM":{
		}
}

_allCopyStates = [
	"ACTUAL_TEMPERATURE",
	"SET_POINT_TEMPERATURE",
	"LEVEL"
]

_copyStates = {
		"HMIP-WTH":{
			"ACTUAL_TEMPERATURE":"temperatureInput1",
			"SET_POINT_TEMPERATURE":"setpointHeat"
		},
		"HMIP-WRC":{
		},
		"HMIP-STHO":{
		},
		"HMIP-FAL-C12":{
		},
		"HMIP-FAL-C10":{
		},
		"HMIP-FAL-C6":{
		},
		"HMIP-SWDM":{
		},
		"HMIP-RCV-50":{
		},
		"HMIP-ETRV":{
			"ACTUAL_TEMPERATURE":"temperatureInput1",
			"SET_POINT_TEMPERATURE":"setpointHeat"
		},
		"HMIP-ETRV-child":{
			"LEVEL":"brightnessLevel"
		},
		"HMIP-PDT":{
			"LEVEL":"brightnessLevel"
		},
		"HMIP-ROOM":{
		}
}




_stateThatTriggersLastSensorChange = {
	"HMIP-ETRV":"temperatureInput1",
	"HMIP-ETRV-child": "LEVEL",
	"HMIP-PSM": "STATE",
	"HMIP-PS": "STATE",
	"HMIP-SWDM": "STATE",
	"HMIP-WTH": "temperatureInput1"
}


_devTypeHasChildren = {
	"HMIP-ETRV":{ 
		"devType":"HMIP-ETRV-child",
		"state":"LEVEL"
	}
}

readOnlyStates = [
		"SET_POINT_MODE",						#0: auto mode,  1= manual mode, reads write of CONTROL_MODE
		"CONTROL_DIFFERENTIAL_TEMPERATURE",
		"DURATION_VALUE"
]
writeOnlyStates = [
		"CONTROL_MODE"							#0 = auto,  1= mmanu  , on off through set_target_temperature
]

_pressTypes = {"":"none", "sp":"Short Press","lp":"Long Press","ls":"Long Press Start","lx":"Long Press Stop",}



"""
can be written and read
/1/BOOST_MODE  true / false
/1/LEVEL/   0-1.01
/1/SET_POINT_TEMPERATURE/   5-30 
/1/ACTIVE_PROFILE   1,2,3 ..  0-->8
/1/WINDOW_STATE  0/1

"""
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


		return


	###########################		util functions	## START ########################


	####----------------- @ startup set global parameters, create directories etc ---------
	def initSelfVariables(self):
		try:
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
			self.varExcludeSQLList								= []
			self.lastRecuestRenewal								= 0
			self.failedLoginCount								= 0
			self.failedLoginCountMax							= 5
			self.requestSession									= ""
			self.loopWait										= 5
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

			self.allDataFromHomematic = self.readJson(fName=self.indigoPreferencesPluginDir + "allData.json")


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

			if int(ret) ==0:  return 0
			self.sleep(0.1)
			ret = subprocess.call("/sbin/ping  -c 1 -W 400 -o " + ipN, shell=True)
			if self.decideMyLog("Connect"): self.indiLOG.log(10,"/sbin/ping  -c 1 -W 400 -o {} ret-code: ".format(ipN, ret) )

			#indigo.server.log(  ipN+"-2  {}".format(ret) +"  {}".format(time.time() - ss)  )

			if int(ret) ==0:  return 0
			return 1
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"ping error", exc_info=True)

		#indigo.server.log(  ipN+"-3  {}".format(ret) +"  {}".format(time.time() - ss)  )
		return 1



####-------------------------------------------------------------------------####
	def writeJson(self, data, fName="", sort = True, doFormat=True, singleLines= False ):
		try:

			if self.decideMyLog("Logic"): self.indiLOG.log(10,"writeJson: fname:{}, sort:{}, doFormat:{}, singleLines:{}, data:{} ".format(fName, sort, doFormat, singleLines, str(data)[0:100]) )
	
			if doFormat:
				if singleLines:
					out = ""
					for xx in data:
						out += "\n{}:{}".format(xx, data[xx])
				else:
					out = json.dumps(data, sort_keys=sort, indent=2)
			else:
				out = json.dumps(data, sort_keys=sort)

			if fName !="":
				f = self.openEncoding(fName,"w")
				f.write(out)
				f.close()
			return out

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
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
			out += "\nrequestTimeout".ljust(40)							+	"{}".format(self.requestTimeout)
			out += "\nloopWait".ljust(40)								+	"{}".format(self.loopWait)

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



	####-----------------	 ---------
	def setSqlLoggerIgnoreStatesAndVariables(self):
		try:
			if self.indigoVersion <  7.4:                             return 
			if self.indigoVersion == 7.4 and self.indigoRelease == 0: return 
			if not self.pluginPrefs.get("enableSqlLogging",False): 
				for v in self.varExcludeSQLList:
					try:
						if v not in indigo.variables: continue
						var = indigo.variables[v]
						sp = var.sharedProps
						if "sqlLoggerIgnoreChanges" not in sp  or sp["sqlLoggerIgnoreChanges"] != "true":
							continue
						outONV += var.name+"; "
						sp["sqlLoggerIgnoreChanges"] = ""
						var.replaceSharedPropsOnServer(sp)
					except: pass
				return 


			outOffV = ""
			for v in self.varExcludeSQLList:
				if v in indigo.variables:
					var = indigo.variables[v]
					sp = var.sharedProps
					#self.indiLOG.log(30,"setting /testing off: Var: {} sharedProps:{}".format(var.name, sp) )
					if "sqlLoggerIgnoreChanges" in sp and sp["sqlLoggerIgnoreChanges"] == "true": 
						continue
					#self.indiLOG.log(30,"====set to off ")
					outOffV += var.name+"; "
					sp["sqlLoggerIgnoreChanges"] = "true"
					var.replaceSharedPropsOnServer(sp)

			if len(outOffV) > 0: 
				self.indiLOG.log(10," \n")
				self.indiLOG.log(10,"switching off SQL logging for variables\n :{}".format(outOffV) )
				self.indiLOG.log(10,"switching off SQL logging for variables END\n")
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return 


	###########################		util functions	## END  ########################


	###########################		ACTIONS START  ########################


	# Main thermostat action bottleneck called by Indigo Server.
	def actionControlThermostat(self, action, dev):

		try:
			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay dev:{}, action:{}".format(dev.name, action))
			if action.thermostatAction == indigo.kThermostatAction.SetHeatSetpoint: 
				value = action.actionValue
			elif action.thermostatAction == indigo.kThermostatAction.DecreaseHeatSetpoint: 
				value = dev.states["setpointHeat"] - action.actionValue
			elif action.thermostatAction == indigo.kThermostatAction.IncreaseHeatSetpoint: 
				value = dev.states["setpointHeat"] + action.actionValue

			if not self.isValidIP(self.ipNumber): return 

			thisRequestSession	 = requests.Session()
			address = dev.states["address"]

			props = dev.pluginProps
			dj = json.dumps({"v": value })

			if dev.deviceTypeId not in _actionParams: return
			acp = _actionParams[dev.deviceTypeId]

			if "states" not in acp: return
			state =		acp["states"].get("SET_POINT_TEMPERATURE","SET_POINT_TEMPERATURE")
			for ch  in	acp["channels"].get("SET_POINT_TEMPERATURE","1"):

				html = "http://{}:{}/device/{}/{}/{}/~pv".format(self.ipNumber , self.portNumber, address,ch, state )

				if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay html:{}, dd:{}".format(html, dj))
				r = thisRequestSession.put(html, data=dj, timeout=self.requestTimeout, headers={'Connection':'close',"Content-Type": "application/json"})

				if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay ret:{}".format(r))

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####-----------------	 ---------
	def actionControlDimmerRelay(self, action, dev):
		try:
			#self.indiLOG.log(10,"sent \"{}\"  deviceAction:{}".format(dev0.name, action.deviceAction) )


			if not self.isValidIP(self.ipNumber): return 

			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay dev:{}, action:{}".format(dev.name, action))


			thisRequestSession	 = requests.Session()
			address = dev.states["address"].split("-")[0]
			channel = []

			if dev.deviceTypeId not in _actionParams: return
			acp = _actionParams[dev.deviceTypeId]

			if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay acp:{}".format(acp))

			if "states" not in acp: return

			if action.deviceAction == indigo.kDeviceAction.TurnOn:
				if "mult" in acp:
					dj = json.dumps({"v":100* acp["mult"]["Dimm"]})
					state =		acp["states"].get("Dimm","")
					for ch in acp["channels"].get("Dimm","1"):
						channel.append(ch)	
				else:
					dj = json.dumps({"v":True })
					state =		acp["states"].get("OnOff","")
					for ch in acp["channels"].get("OnOff","1"):
						channel.append(ch)	

			elif action.deviceAction == indigo.kDeviceAction.TurnOff:
				if "mult" in acp:
					dj = json.dumps({"v":0.})
					state =		acp["states"].get("Dimm","")
					for ch in acp["channels"].get("Dimm","1"):
						channel.append(ch)	
				else:
					dj = json.dumps({"v":False })
					state =		acp["states"].get("OnOff","")
					for ch in acp["channels"].get("Dimm","1"):
						channel.append(ch)	

			elif action.deviceAction == indigo.kDeviceAction.SetBrightness:
				if "mult" in acp:
					dj = json.dumps({"v":action.actionValue * acp["mult"]["Dimm"]})
				else:
					dj = json.dumps({"v":action.actionValue})

				state =		acp["states"].get("Dimm","")
				for ch in acp["channels"].get("Dimm","1"):
						channel.append(ch)	

			for ch in channel:	
				html = "http://{}:{}/device/{}/{}/{}/~pv".format(self.ipNumber , self.portNumber, address,ch, state )

				if self.decideMyLog("Actions"): self.indiLOG.log(20,"actionControlDimmerRelay html:{}, dj:{}<<".format(html, dj))
				r = thisRequestSession.put(html, data=dj, timeout=self.requestTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
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
			for prop in _defaultProps.get(dev.deviceTypeId,{}):
				if prop != "" and  props.get(prop,"") == "":
					props[prop] = _defaultProps[dev.deviceTypeId][prop]
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
	def didDeviceCommPropertyChange(self, origDev, newDev):
		#if origDev.pluginProps['xxx'] != newDev.pluginProps['address']:
		#	 return True
		return False


####-------------------------------------------------------------------------####
	def getDeviceConfigUiValues(self, pluginProps, typeId, devId):
		try:
			theDictList =  super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)
			return theDictList
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)


	####-----------------	 ---------
	def validateDeviceConfigUi(self, valuesDict=None, typeId="", devId=0):
		try:
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"Validate Device dict:, devId:{}  vdict:{}".format(devId,valuesDict) )
			self.devNeedsUpdate[int(devId)] = True


			if typeId == "HomematicHost":
				if devId != 0:
					self.hostDevId = devId
					dev = indigo.devices[devId]
					props = dev.pluginProps	
					if 	props["ipNumber"] != valuesDict["ipNumber"]:
						self.pendingCommand["restartHomematicClass"] = True

					if 	props["portNumber"] != valuesDict["portNumber"]:
						self.pendingCommand["restartHomematicClass"] = True

					if len(dev.states["created"]) < 10:
						self.addToStatesUpdateDict(dev.id, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))

					valuesDict["address"] = valuesDict["ipNumber"]+":"+valuesDict["portNumber"]

				self.pluginPrefs["ipNumber"] = valuesDict["ipNumber"]
				self.pluginPrefs["portNumber"] = valuesDict["portNumber"]



			return (True, valuesDict)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		errorDict = valuesDict
		return (False, valuesDict, errorDict)

	###########################		update States start  ########################
	####-----------------	 ---------
	def addToStatesUpdateDict(self, devid, key, value, uiValue=""):
		try:
			devId = "{}".format(devid)
			#if self.decideMyLog("Special") and (key == "status" or key == "displayStatus"): self.indiLOG.log(10,"addToStatesUpdateDict (1) devId {} key:{}; value:{}".format(devid, key, value ) )
			### no down during startup .. 100 secs

			localCopy = copy.deepcopy(self.devStateChangeList)
			if devId not in localCopy:
				localCopy[devId] = {}

			if key in localCopy[devId]:
				if value != localCopy[devId][key]:
					localCopy[devId][key] = {}

			if uiValue =="": uiValue = "{}".format(value)
			localCopy[devId][key] = [value,uiValue]
			self.devStateChangeList = copy.deepcopy(localCopy)
			#if self.decideMyLog("Special") and (key == "status" or key == "displayStatus"): self.indiLOG.log(10,"addToStatesUpdateDict (2) devId {} key:{}; value:{}".format(devid, key, value ) )


		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def executeUpdateStatesList(self):
		devId = ""
		key = ""
		local = ""
		try:
			if len(self.devStateChangeList) == 0: return
			local = copy.deepcopy(self.devStateChangeList)
			self.devStateChangeList = {}
			trigList = []
			for devId in  local:
				onlyIfChanged = []
				try: int(devId)
				except: continue
				if len( local[devId]) > 0:
					try: 	dev = indigo.devices[int(devId)]
					except: continue
					#if  dev.deviceTypeId == "HMIP-ROOM": self.indiLOG.log(10,"executeUpdateStatesList :{},".format(dev.name))

					for key in local[devId]:
						#if  dev.deviceTypeId == "HMIP-ROOM": self.indiLOG.log(10,"executeUpdateStatesList :{}, key:{}".format(dev.name,key))
						if key not in dev.states: continue
						value = local[devId][key][0]
						uiValue = local[devId][key][1]
						# excude from update old=new or if  new =="" and old =0.
						nv = "{}".format(value).strip()
						ov = "{}".format(dev.states[key]).strip()
						ov0 = ov.replace(".0","") 
						#if self.decideMyLog("Special")	 and   dev.deviceTypeId == "HMIP-ETRV": self.indiLOG.log(10,"executeUpdateStatesList :{},key:{}, nv:{}, ov:{}, ov0:{}".format(dev.name, key, value, nv, ov, ov0))

						if (
							not ( ( nv == ov) or (nv == "" and ov0 == "0") or (nv == "0" and ov0 == "0") ) or
							( uiValue !="" and uiValue != dev.states.get(state+"_ui","") )
							):
							if uiValue != "":
								onlyIfChanged.append({"key":key,"value":value,"uiValue":uiValue})
							else:
								onlyIfChanged.append({"key":key,"value":value})
							if key == "sensorValue":
								onlyIfChanged.append({"key":"lastSensorChange","value":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

					if onlyIfChanged != []:
						pass
						#if self.decideMyLog("UpdateStates"):	self.indiLOG.log(10,"update device:{:30}  {} == {} states:{}".format(dev.name, "{}".format(value), "{}".format(dev.states[key]), onlyIfChanged))

						try:
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




	####-----------------	 ---------
	def doGetDevStateType(self,  deviceTypeId, statesToCreate,devId):
	
		for state in statesToCreate:
			stateType = statesToCreate[state]

			state2 = ""
			if deviceTypeId in _copyStates :
				state2 = _copyStates[deviceTypeId].get(state, "")
			

			for xx in [state, state2]:
				if xx != "":
					if   stateType == "real":			self.newStateList.append(self.getDeviceStateDictForRealType(xx, xx, xx))
					elif stateType == "integer":		self.newStateList.append(self.getDeviceStateDictForIntegerType(xx, xx, xx))
					elif stateType == "number":			self.newStateList.append(self.getDeviceStateDictForNumberType(xx, xx, xx))
					elif stateType == "string":			self.newStateList.append(self.getDeviceStateDictForStringType(xx, xx, xx))
					elif stateType == "booltruefalse":	self.newStateList.append(self.getDeviceStateDictForBoolTrueFalseType(xx, xx, xx))
					elif stateType == "boolonezero":	self.newStateList.append(self.getDeviceStateDictForBoolTrueFalseType(xx, xx, xx))
					elif stateType == "Boolonoff":		self.newStateList.append(self.getDeviceStateDictForBoolTrueFalseType(xx, xx, xx))
					elif stateType == "boolyesno":		self.newStateList.append(self.getDeviceStateDictForBoolTrueFalseType(xx, xx, xx))
					elif stateType == "enum":			self.newStateList.append(self.getDeviceStateDictForEnumType(xx, xx, xx))
					elif stateType == "separator":		self.newStateList.append(self.getDeviceStateDictForSeparatorType(xx, xx, xx))
			
		return 

	####-----------------	 ---------
	def getDeviceStateList(self, dev):

		try:
	
			self.newStateList  = super(Plugin, self).getDeviceStateList(dev)

			deviceTypeId = dev.deviceTypeId
			if deviceTypeId != "HomematicHost":

				if  deviceTypeId not in _isNotRealDevice:
						self.doGetDevStateType(deviceTypeId, _statesToCreateisRealDevice, dev.id)

				if  deviceTypeId in _isBatteryDevice:
						self.doGetDevStateType(deviceTypeId, _statesToCreateisBatteryDevice, dev.id)

				if  deviceTypeId in _isVoltageDevice:
						self.doGetDevStateType(deviceTypeId, _statesToCreateisVoltageDevice, dev.id)

				if True:
					self.doGetDevStateType(deviceTypeId, _statesToCreateCommon, dev.id)
					self.doGetDevStateType(deviceTypeId, _statesToCopyFromHomematic[deviceTypeId], dev.id)

			#self.indiLOG.log(20,"dev:{}, self.newStateList:{}".format(dev.name, self.newStateList))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return self.newStateList 





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

		
		
		return True

####-----------------   main loop          ---------
	def runConcurrentThread(self):

		if not self.fixBeforeRunConcurrentThread():
			self.indiLOG.log(40,"..error in startup")
			self.sleep(10)
			return

		self.setSqlLoggerIgnoreStatesAndVariables()

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


		try:
			while True:
				self.countLoop += 1
				ret = self.doTheLoop()

				if ret != "ok":
					self.indiLOG.log(20,"LOOP   return break: >>{}<<".format(ret) )

				sl = max(1., self.loopWait / 10. )
				sli = int(self.loopWait / sl)
				for ii in range(sli):
					if self.quitNOW != "": 
						break
					self.sleep(sl)

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

			self.executeUpdateStatesList()

			if self.lastMinuteCheck != datetime.datetime.now().minute:
				self.lastMinuteCheck = datetime.datetime.now().minute

			if self.quitNOW != "": return "break"

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return "ok"


	###########################	   after the loop  ############################
	####-----------------	 ---------
	def postLoop(self):

		self.pluginState   = "stop"
		indigo.server.savePluginPrefs()	

		if self.quitNOW == "config changed":
			pass
		if self.quitNOW == "": self.quitNOW = " restart / stop requested "


		return 


	####-----------------	 ---------
	def periodCheck(self):
		try:

			if	self.countLoop < 2:						return
			if time.time() - self.pluginStartTime < 5: return
			changed = False
			self.processPendingCommands()
			self.checkOnDelayedActions()
			if  self.numberOfVariables >= 0:
				self.addToStatesUpdateDict(self.hostDevId, "lastSucessfullRead", datetime.datetime.fromtimestamp(self.lastSucessfullHostContact).strftime(_defaultDateStampFormat))
				self.addToStatesUpdateDict(self.hostDevId, "numberOfVariables", self.numberOfVariables)
				self.addToStatesUpdateDict(self.hostDevId, "numberOfDevices", self.numberOfDevices)
				self.addToStatesUpdateDict(self.hostDevId, "numberOfRooms", self.numberOfRooms)

			if time.time() - self.lastSucessfullHostContact  > 200:
				if self.hostDevId > 0:
					self.addToStatesUpdateDict(self.hostDevId, "onOffState", False)

			self.lastSecCheck = time.time()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return	changed





	####-----------------	 ---------
	def upDateDeviceData(self,allValues):

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
		
		for link in allValues:
			try:
				lStart = time.time()
				ll = link.split()
				address, channelNumber, state, homematicType = "","","value", ""
				if time.time() - self.lastSucessfullHostContact  > 10:
					if self.hostDevId != 0:
						self.addToStatesUpdateDict(self.hostDevId, "onOffState", True)
						self.lastSucessfullHostContact = time.time()


				if link.find("/sysvar/") > -1: 
					try:	
						address   = link.split("/")[-1]
						homematicType =  "sysvar"
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

				elif link.find("/device/") > -1: 
					try:	
						dummy, dd, address, channelNumber, state  = link.split("/") 
						homematicType =  "device"
					except: continue

				if address in self.homematicIdtoIndigoId:


					v = allValues[link].get("v","")
					ts = allValues[link].get("ts",0)/1000.
					s = allValues[link].get("s","")
					try:	dt = datetime.datetime.fromtimestamp(ts).strftime(_defaultDateStampFormat)
					except: dt = ""

					
					if True:  # test if same value as last time, if yes skip
						devIdNew = self.homematicIdtoIndigoId[address]
						if devIdNew < 1: continue

						if devIdNew not in self.lastDevStates:
							 self.lastDevStates[devIdNew] = {}
						if state not in self.lastDevStates[devIdNew]:
							self.lastDevStates[devIdNew][state] = v
						else:
							if self.lastDevStates[devIdNew][state] == v: 
								continue
							else:
								self.lastDevStates[devIdNew][state] = v 

					if True:  # check if right channel for state, eg LEVEL is in several channel sometimes  ie HIMP-PDT has LEVEL in 4 channels ch 2 is the right one 
						newdevTypeId = self.addressToDevType.get(address,"xxx")
						if 	newdevTypeId in _usedWichStateForRead:
							if state in  _usedWichStateForRead[newdevTypeId]:
								if _usedWichStateForRead[newdevTypeId][state] != channelNumber:
									continue


					if devIdCurrent == devIdNew:
						dev = devCurrent
					else:
						try:
							dev = indigo.devices[self.homematicIdtoIndigoId[address]]
							if dev.id not in self.lastDevStates: 	self.lastDevStates[devId] = {}
							devCurrent = dev
							devIdCurrent = dev.id
							props = dev.pluginProps
							devTypeId = dev.deviceTypeId
						except: continue



					if devTypeId in _multiChannelStatesDict:
						if state in _multiChannelStatesDict[devTypeId]["states"]:
							if channelNumber in _multiChannelStatesDict[devTypeId]["channels"].split(","):
								state = state+"-"+channelNumber


					state2 = ""
					if devTypeId in _copyStates:
						state2 = _copyStates[devTypeId].get(state, state)


					if state in dev.states:
						vui = ""
						if  homematicType ==  "device":

							if self.decideMyLog("UpdateStates") :	 self.indiLOG.log(10," upDateDeviceData in 2 new  prop:{}, state2:{}, state:{} v:{} onst:{}, sens:{}".format( props.get("displayS","") , state2, state,  v , props["SupportsOnState"], props["SupportsSensorValue"]))

							checkStateTotext = _stateValuesToText.get(state.split("-")[0], "")
							if checkStateTotext != "":
								#self.indiLOG.log(20,"getDeviceData, dev:{}, key:{}, value:{}, checkStateTotext:{}".format(dev.name, state, v , checkStateTotext ) )
								if v == 0:
									v = "{}".format( checkStateTotext[ max(0, min(len(checkStateTotext)-1, v)) ])
								else:
									v = "{}- msg#{}".format( checkStateTotext[ max(0, min(len(checkStateTotext)-1, v)) ], v)

							elif state in _temperatureReal:
								if self.pluginPrefs.get("tempUnit","C") == "F":
									v = v *9./32. + 32.
								v = round(float(v),1)
								vui = "{:.1f}ºC".format(v)

							elif state in _humdidityReal:
								v = int(float(v))
								vui = "{:}[%]".format(v)

							elif state.find("LEVEL-") == 0 or state == "LEVEL" and v != "":
								try: 
									v = float(v)*100
									v = int(v)
									vui = "{:}[%]".format(v)
								except: pass

						elif  homematicType ==  "room":
							pass


						elif  homematicType ==  "sysvar":
							vui = "{:}".format(v)
							try: 
								vF = float(v)
							except:
								if type(v) is type(True):
									if v: v = 1
									else: v = 0
								else:
									 vF = 0
							v = str(v)

							self.addToStatesUpdateDict(dev.id, "value", v, uiValue=vui)
							self.addToStatesUpdateDict(dev.id, "sensorValue", vF, uiValue=vui)
							if v.find("dev:") == 0:
								xx = v.split(":")
								
								if len(xx) >= 1 and xx[0].lower() == "dev":
								
									if len(xx) >= 2 :	buttondevAddress = xx[1]
									else:				buttondevAddress = "0"
									if len(xx) >= 3 :	thebutton = xx[2]
									else:				thebutton = "0"
									if len(xx) >= 4 :	pressType = xx[3].lower()
									else:				pressType = ""
									pressType = _pressTypes.get(pressType,"none")
									try:
										devButtonId = self.homematicIdtoIndigoId.get(buttondevAddress,0)
										if devButtonId > 0:
											if devButtonId == devButtonIdCurrent:
												devButton = devButtonCurrent
											else:
												devButton = indigo.devices[devButtonId]
												devButtonCurrent = devButton
												devButtonIdCurrent = devButtonId

											#self.indiLOG.log(20,"getDeviceData, dev:{}, key:{}, value:{}, setting dev:{}, set button to on:{}".format(devButton.name, state, v, devButton.name, thebutton ) )
											dt = datetime.datetime.now().strftime(_defaultDateStampFormat)
											if (
													devButton.states.get("buttonPressed","") != thebutton or
													devButton.states.get("buttonPressedType","") != pressType 
												):
												if thebutton == "0":
													self.addToStatesUpdateDict(devButton.id, "buttonPressedPrevious", devButton.states.get("buttonPressed"))
													self.addToStatesUpdateDict(devButton.id, "buttonPressedTimePrevious", devButton.states.get("buttonPressedTime"))
													self.addToStatesUpdateDict(devButton.id, "buttonPressedTypePrevious", devButton.states.get("buttonPressedType"))
												else:
													self.addToStatesUpdateDict(devButton.id, "lastSensorChange", dt)
							
												self.addToStatesUpdateDict(devButton.id, "buttonPressed", thebutton)
												self.addToStatesUpdateDict(devButton.id, "buttonPressedTime", dt)
												self.addToStatesUpdateDict(devButton.id, "buttonPressedType", pressType)
												self.addToStatesUpdateDict(devButton.id, "onOffState", thebutton != "0")
										else:
											self.indiLOG.log(20,"getDeviceData,  key:{}, value:{}, setting dev (address:{}) did not work ".format( state, v, buttondevAddress, thebutton ) )
								
									except	Exception as e:
										if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
										self.indiLOG.log(20,"getDeviceData,  key:{}, value:{}, setting dev (address:{}) did not work ".format( state, v, buttondevAddress, thebutton ) )
						
							continue
							#if dev.id == 1910111105: self.indiLOG.log(20,"getDeviceData, dev:{}, key:{}, value:{}, ts:{}, s:{}".format(dev.name, state, v, ts, s ) )


						if state2 != "":
							self.addToStatesUpdateDict(dev.id, state2, v, uiValue=vui)
						self.addToStatesUpdateDict(dev.id, state, v, uiValue=vui)

						if props.get("displayS","") in[state, state2]:

							if props["SupportsOnState"]:
								if v in [1,True,"1","true","True"]: TF = True
								else: TF = False
								if "onOffState" in dev.states and dev.states["onOffState"] != TF:
									self.addToStatesUpdateDict(dev.id, "onOffState", TF)
								if devTypeId in _stateThatTriggersLastSensorChange:
									if (
										state in _stateThatTriggersLastSensorChange[devTypeId] and 
											(
									 			 (state in dev.states and dev.states[state] != TF) or 
												("onOffState" in dev.states and dev.states["onOffState"] != TF)
											)
									   ) :
										self.addToStatesUpdateDict(dev.id, "lastSensorChange", datetime.datetime.now().strftime(_defaultDateStampFormat))

									if state2 != state  and state2 in _stateThatTriggersLastSensorChange[devTypeId] and state2 in dev.states and dev.states[state2] != TF:
										self.addToStatesUpdateDict(dev.id, "lastSensorChange", datetime.datetime.now().strftime(_defaultDateStampFormat))

							if props["SupportsSensorValue"]:
								if "sensorValue" in dev.states and  dev.states["sensorValue"] != v:
									self.addToStatesUpdateDict(dev.id, "sensorValue", v, uiValue=vui)
									self.addToStatesUpdateDict(dev.id, "lastSensorChange", datetime.datetime.now().strftime(_defaultDateStampFormat))

								if devTypeId in _stateThatTriggersLastSensorChange:
									if state in _stateThatTriggersLastSensorChange[devTypeId] and dev.states["sensorValue"] != v:
										self.addToStatesUpdateDict(dev.id, "lastSensorChange", datetime.datetime.now().strftime(_defaultDateStampFormat))

									if  state2 != state  and state2 in _stateThatTriggersLastSensorChange[devTypeId] and dev.states[state2] != v:
										self.addToStatesUpdateDict(dev.id, "lastSensorChange", datetime.datetime.now().strftime(_defaultDateStampFormat))

					if devTypeId in _devTypeHasChildren:
						indigoIdforChildnew = int( dev.states.get("childId",0))
						#if indigoIdforChildnew == 1139401366 or self.decideMyLog("UpdateStates") :	 self.indiLOG.log(10," getDeviceData state:{}, ".format( state))
						if indigoIdforChildnew > 0:
							#if indigoIdforChildnew == 1139401366  or self.decideMyLog("UpdateStates") :	 self.indiLOG.log(10," getDeviceData  indigoIdforChild:{}".format(indigoIdforChildnew))
							if indigoIdforChild != indigoIdforChildnew:
								devChild = indigo.devices[indigoIdforChildnew]
								devTypeChild = _devTypeHasChildren[devTypeId]["devType"]

							if  state == _devTypeHasChildren[devTypeId]["state"] and  state in _copyStates[devTypeChild]:
								self.addToStatesUpdateDict(indigoIdforChildnew, _copyStates[devTypeChild][state], v, uiValue=vui)

							if state in devChild.states:  
								self.addToStatesUpdateDict(indigoIdforChildnew, state, v, uiValue=vui)

								if devTypeChild in _stateThatTriggersLastSensorChange:
									if state == _stateThatTriggersLastSensorChange[devTypeChild] and devChild.states[state] != v:
										self.addToStatesUpdateDict(indigoIdforChildnew, "lastSensorChange", datetime.datetime.now().strftime(_defaultDateStampFormat))

							indigoIdforChild = indigoIdforChildnew
						
				if self.decideMyLog("Time"): dtimes.append(time.time() - lStart)

				
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		if self.decideMyLog("Time"):  tMain = time.time() - tStart

		self.executeUpdateStatesList()
		if self.decideMyLog("Time"):  
			tAve = 0
			for x in dtimes:
				tAve += x
			tAve = tAve / max(1,len(dtimes))
			self.indiLOG.log(20,"upDateDeviceData, elapsed times - tot:{:.2f}, tMain:{:.2f}   per state ave:{:.4f},  N-States:{:}  ".format(time.time() - tStart, tMain, tAve, len(dtimes)  ) )
		return 





	####-----------------	 ---------
	def createDevicesFromCompleteUpdate(self):
		try:
			if self.pluginPrefs.get("ignoreNewDevices", False): return
			doDevices = True
			doRooms = True
			doSysvar = True
			doProgram = True
			doVendor = True



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
				self.roomMembers = {}
				self.numberOfRooms = 0
				homematicType = "ROOM"
				for address in self.allDataFromHomematic["allRoom"]["address"]:
					try:
						thisDev = self.allDataFromHomematic["allRoom"]["address"][address]
						if time.time() - self.lastSucessfullHostContact  > 10:
							self.addToStatesUpdateDict(self.hostDevId, "onOffState", True)
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
						if indigoType in _defaultProps:
							newprops = _defaultProps[indigoType]
						nDevices = 0
						roomListIDs = ""
						roomListNames = ""
						for devD in thisDev["devices"]:
							link = devD.get("link", "")
							if link == " ": continue
							if link[-2:] != "/0": continue
							homematicAddress = link.split("/")[2]
							roomListIDs += homematicAddress+";"
								
							nDevices += 1
							tt = devD.get("title", "")
							if tt.rfind(":") == len(tt) -2:
								tt = tt[:-2]
							roomListNames += tt+";"
							try:
								self.roomMembers[homematicAddress] = [int(address),tt]
							except: pass

						if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate,  devFound:{};  address:{}, ndevs:{}, room list:{} == {}".format( devFound, address, nDevices, roomListNames, roomListIDs) )
						roomListNames = roomListNames.strip(";")
						roomListIDs = roomListIDs.strip(";")
						newprops["roomListIDs"] = roomListIDs
						newprops["roomListNames"] = roomListNames
						if not devFound:
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
							self.addToStatesUpdateDict(dev.id, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
							self.addToStatesUpdateDict(dev.id, "address", address)

						self.homematicIdtoIndigoId[address]	= dev.id
						self.addressToDevType[address]= dev.deviceTypeId

						self.addressToDevType[address]= dev.deviceTypeId
						props = dev.pluginProps
						uiValue = uiValue="{} devices".format(nDevices)
						self.addToStatesUpdateDict(dev.id, "title", title)
						self.addToStatesUpdateDict(dev.id, "roomListIDs", roomListIDs)
						self.addToStatesUpdateDict(dev.id, "homematicType", homematicType)
						self.addToStatesUpdateDict(dev.id, "roomListNames", roomListNames)
						self.addToStatesUpdateDict(dev.id, "NumberOfDevices", nDevices)
						if props.get("displayS","") == "NumberOfDevices":
							if props["SupportsSensorValue"]:
								self.addToStatesUpdateDict(dev.id, "sensorValue", nDevices, uiValue=uiValue)
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
						homematicType = thisDev.get("type","")
						homematicTypeUpper = homematicType.upper().split()[0]
						firmware = thisDev.get("firmware","")
						availableFirmware = thisDev.get("availableFirmware","")

						pp = False
						if False and address == "000B1D89A11CD6": pp = True


						indigoType = ""
						for xx in _supportedDeviceTypesFromHomematicToIndigo:
							if homematicTypeUpper.find(xx) == 0:
								indigoType = _supportedDeviceTypesFromHomematicToIndigo[xx] 
								break

						if indigoType == "": continue

						if pp: self.indiLOG.log(20,"createDevicesFromCompleteUpdate, pass 2, ------------".format(address) )

						if  indigoType not in _statesToCopyFromHomematic: continue 

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
						#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, theType:{}, devFound:{};  address:{}".format(theType, devFound, address) )

						name = title +"-"+	address		
						#self.indiLOG.log(20,"createDevicesFromCompleteUpdate, pass 4, title:{}".format(title) )
	
						if not devFound:
							try: 
								dev = indigo.devices[name]
								devFound = True
							except: pass

						newprops = {}
						if indigoType in _defaultProps:
							newprops = _defaultProps[indigoType]


						if not devFound:
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
							self.addToStatesUpdateDict(dev.id, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
							self.addToStatesUpdateDict(dev.id, "address", address)
						if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate, :{};  address:{}, deviceTypeId:{}".format( dev.name, address, dev.deviceTypeId) )
						self.homematicIdtoIndigoId[address]	= dev.id
						self.addressToDevType[address]= dev.deviceTypeId


						if address in self.roomMembers:
							if self.roomMembers[address][0] !="":
								self.addToStatesUpdateDict(dev.id, "roomId", self.roomMembers[address][0])
							if self.roomMembers[address][1] !="":
								self.addToStatesUpdateDict(dev.id, "roomName", self.roomMembers[address][1])
						self.addToStatesUpdateDict(dev.id, "title", title)
						self.addToStatesUpdateDict(dev.id, "firmware", firmware)
						self.addToStatesUpdateDict(dev.id, "availableFirmware", availableFirmware)
						self.addToStatesUpdateDict(dev.id, "homematicType", homematicType)


						# creqte child if designed
						if indigoType in _devTypeHasChildren:
							if  not devFound or (  dev.states["childId"] not in indigo.devices):
								dev1 = indigo.device.create(
									protocol		= indigo.kProtocol.Plugin,
									address			= address,
									name			= name+"- child of {}".format(dev.id),
									description		= "",
									pluginId		= self.pluginId,
									deviceTypeId	= _devTypeHasChildren[indigoType]["devType"],
									folder			= self.folderNameDevicesID,
									props			= _defaultProps[_devTypeHasChildren[indigoType]["devType"]]
									)
								self.addToStatesUpdateDict(dev1.id, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
								self.addToStatesUpdateDict(dev1.id, "address", address+"-child")
								self.addToStatesUpdateDict(dev.id, "childId", dev1.id)
							else:
								dev1 = indigo.devices[self.homematicIdtoIndigoId[address+"-child"]]
							self.homematicIdtoIndigoId[address+"-child"]	= dev1.id

							self.addToStatesUpdateDict(dev1.id, "title", title)
							self.addToStatesUpdateDict(dev1.id, "homematicType", homematicType)
							self.addToStatesUpdateDict(dev1.id, "firmware", firmware)
							self.addToStatesUpdateDict(dev1.id, "availableFirmware", availableFirmware)

							if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate, :{};  address:{}-child, deviceTypeId:{}".format( dev1.name, address, _devTypeHasChildren[indigoType]["devType"]) )

							if address in self.roomMembers:
								if self.roomMembers[address][0] !="":
									self.addToStatesUpdateDict(dev1.id, "roomId", self.roomMembers[address][0])
								if self.roomMembers[address][1] !="":
									self.addToStatesUpdateDict(dev1.id, "roomName", self.roomMembers[address][1])
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

						



			if doSysvar and "address" in self.allDataFromHomematic["allSysvar"]:  
				for address in self.allDataFromHomematic["allSysvar"]["address"]:
					self.numberOfVariables = 0
					try:
						thisDev = self.allDataFromHomematic["allSysvar"]["address"][address]
						self.numberOfVariables +=1

						indigoType = "HMIP-SYSVAR" 
						devFound = False
						for dev in indigo.devices.iter(self.pluginId):
							if dev.deviceTypeId != indigoType: continue
							if dev.states["address"] == address: 
								devFound = True
								break

						title = thisDev.get("title","")
						name = "Sysvar-"+title +"-"+ address		
	
						if not devFound:
							try: 
								dev = indigo.devices[name]
								devFound = True
							except: pass
						newprops = {}
						if indigoType in _defaultProps:
							newprops = _defaultProps[indigoType]

						if self.decideMyLog("Digest"): self.indiLOG.log(10,"createDevicesFromCompleteUpdate,  devFound:{};  address:{}, desc:{}, htype:{}, thisdev:\n{}".format( devFound, address, thisDev.get("description"), thisDev.get("type",""), thisDev ))
						if not devFound:
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
						self.homematicIdtoIndigoId[address]	= dev.id
						self.addressToDevType[address]= dev.deviceTypeId
						if len(dev.states["created"]) < 5:
							self.addToStatesUpdateDict(dev.id, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
						if len(dev.states["address"]) < 5:
							self.addToStatesUpdateDict(dev.id, "address", address)
						self.addToStatesUpdateDict(dev.id, "title", title)
						self.addToStatesUpdateDict(dev.id, "description", thisDev.get("description",""))
						self.addToStatesUpdateDict(dev.id, "homematicType", thisDev.get("type",""))
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



				
			self.executeUpdateStatesList()
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)





	####-----------------	 ---------
	def getDeviceData(self):

		try:
			getHomematicClass = "" 
			getValuesLast = 0
			self.indiLOG.log(20," .. (re)starting   thread for getDeviceData  " )
			self.threads["getDeviceData"]["status"] = "running"
			while self.threads["getDeviceData"]["status"]  == "running":
				self.sleep(0.3)
				if self.testPing(self.ipNumber) != 0:
					self.indiLOG.log(30,"getDeviceData ping to {} not sucessfull".format(self.ipNumber))
					self.sleep(5)
					getValuesLast  = time.time()			
					continue

				if  getHomematicClass == "" or "getDeviceData" in self.restartHomematicClass:
					try: del self.restartHomematicClass["getDeviceData"]
					except: pass
					getHomematicClass = getHomematicData(self.ipNumber, self.portNumber, kTimeout =self.requestTimeout )
				if time.time() - getValuesLast < self.getValuesEvery:  continue 
	
				getValuesLast  = time.time()			
				allValues = getHomematicClass.getDeviceValues(self.allDataFromHomematic)
				if self.pluginPrefs.get("writeInfoToFile", False):
					self.writeJson( allValues, fName=self.indigoPreferencesPluginDir + "allValues.json", sort = True, doFormat=True, singleLines=True )

				self.upDateDeviceData(allValues)
				
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	####-----------------	 ---------
	def getCompleteupdate(self):

		getHomematicClassALLData = ""
		self.getcompleteUpdateLast  = 0
		self.indiLOG.log(20," .. (re)starting   thread for getCompleteupdate  " )
		self.threads["getCompleteupdate"]["status"] = "running"
		while self.threads["getCompleteupdate"]["status"]  == "running":
			try:
				self.sleep(0.3)
				
				try:
					if time.time() - self.getcompleteUpdateLast < self.getCompleteUpdateEvery: continue 
					if  getHomematicClassALLData == "" or "getCompleteupdate" in self.restartHomematicClass:
						try: del self.restartHomematicClass["getCompleteupdate"]
						except: pass

					if self.testPing(self.ipNumber) != 0:
						self.indiLOG.log(30,"getAllVendor ping to {} not sucessfull".format(self.ipNumber))
						self.sleep(5)
						self.getcompleteUpdateLast  = time.time()
						continue


					getHomematicClassALLData = getHomematicData(self.ipNumber, self.portNumber, kTimeout =self.requestTimeout )

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
							self.allDataFromHomematic[xx] = getHomematicClassALLData.getInfo(xx)
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
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



	###########################	   MAIN LOOP  ## END ######################
	###########################	   MAIN LOOP  ## END ######################
	###########################	   MAIN LOOP  ## END ######################
	###########################	   MAIN LOOP  ## END ######################

	####-----------------	 ---------
	def checkOnDelayedActions(self):
		try:
			if self.delayedAction == {}: return 
			for devId in self.delayedAction:
				for actionDict in self.delayedAction[devId]:
					if actionDict["action"] == "updateState":
						self.addToStatesUpdateDict(devId,actionDict["state"], actionDict["value"] )
			self.delayedAction = {}
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	####-----------------	 ---------
	def processPendingCommands(self):
		try:
			if self.pendingCommand == {}: return 

			if self.pendingCommand.get("restartHomematicClass", False): 
				self.restartHomematicClass = {"getDeviceData":True,"getCompleteupdate":True}
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
					newProps["SupportsOnState"] = True
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
					self.addToStatesUpdateDict(dev.id, "created", datetime.datetime.now().strftime(_defaultDateStampFormat))
					self.addToStatesUpdateDict(dev.id, "lastRead", "")
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
	def __init__(self, ip, port, kTimeout=10):
		self.ip = ip
		self.port = port
		self.kTimeout = kTimeout
		self.requestSession	 = requests.Session()

		return 

	####-----------------	 ---------
	def getInfo(self, area):
		try:
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
			if getorput =="get":
				r = self.requestSession.get(page, timeout=self.kTimeout)
			else:
				r = self.requestSession.put(page, data=data, timeout=self.kTimeout, headers={'Connection':'close',"Content-Type": "application/json"})
			return r
		except:
			indigo.activePlugin.indiLOG.log(30,"connect to hometic did not work for {}  page={}".format(getorput, page))
		return ""

	####-----------------	 ---------
	def getDeviceValues(self, allData):
		try:
			tStart = time.time()
			if allData == "": return 
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
			if r == "": return theDict

			content = r.content.decode('ISO-8859-1')
			devices = json.loads(content)
			for dev in devices:
				if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice {}:{}".format(page, dev))
				theDict["address"][dev["address"]] = dev

			devices1Html = baseHtml + pageQ+"/*/*"
			if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllDevice Accessing URL: {}".format(devices1Html))
	
			r = self.doConnect(devices1Html)
			if r == "": return theDict

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
					if r == "": return theDict

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
			if r == "": return theDict

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

					valueDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllSysvar  {} dict: {}".format(page, valueDict))
					theDict["address"][address]["value"] = valueDict

		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
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

					valueDict = json.loads(r.content)
					if indigo.activePlugin.decideMyLog("GetData"): indigo.activePlugin.indiLOG.log(10,"getAllProgram {} dict: {}".format(page, valueDict))
					theDict["address"][address]["value"] = valueDict
					theDict["address"][address]["link"] = valueHref

		except Exception as e:
			if "{}".format(e).find("None") == -1: indigo.activePlugin.indiLOG.log(40,"", exc_info=True)
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
		return theDict


