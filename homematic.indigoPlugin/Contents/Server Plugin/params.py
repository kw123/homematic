#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# homematic Plugin
# Developed by Karl Wachs
# karlwachs@me.com
import copy 
from params_user import *

def mergeDicts(a,b):
	z = copy.copy(a)
	for xx in b:
		z[xx] = b[xx]
	return z

try:
	userdefs = k_userDefs
except:
	userdefs = {}
### this mapps the homematic state to dev.deviceTypeId
k_supportedDeviceTypesFromHomematicToIndigo = {
###	homatic name        indigo dev type               what kind of device type 
	"HMIP-FALMOT":		"HMIP-FALMOT",				# floor heating system valve driver 
	"HMIP-DLD": 		"HMIP-DLD",					# Door-Lock
	"HMIP-DBB": 		"HMIP-BUTTON",				# handheld remote switch 
	"HMIP-DSD": 		"HMIP-BUTTON",				# battery board ring sensor/ switch 
	"HMIP-BRC":			"HMIP-BUTTON",				# behind wall switch 
	"HMIP-RC":			"HMIP-BUTTON",				# any handheld switch 
	"HMIP-RC8":			"HMIP-BUTTON",				# 8 button 
	"HMIP-KRC":			"HMIP-BUTTON",				# 4 button hand device
	"HMIP-DBB":			"HMIP-BUTTON",				# 4 button hand device
	"HMIP-KRCA":		"HMIP-BUTTON",				# 4 button hand device
	"HMIP-FCI": 		"HMIP-BUTTON",				# x channel behind wall switch / button
	"HMIP-STI":			"HMIP-BUTTON",				# capacitor single / double button 
	"HMIP-WRC2": 		"HMIP-BUTTON",				# wall switch 5
	"HMIP-WRCC2": 		"HMIP-BUTTON",				# wall switch 2
	"HMIP-WRC4": 		"HMIP-BUTTON",				# wall switch 4 
	"HMIP-WRC6": 		"HMIP-BUTTON",				# wall switch 6
	"HMIP-WRCR": 		"HMIP-BUTTON",				# wall switch rotate
	"HMIP-WRCD":		"HMIP-WRCD",				# switch w display
	"HMIP-WKP": 		"HMIP-WKP",					# key pad 
	"HMIP-SWO-PR": 		"HMIP-SWO-PR",				# weather sensor temp, hum ,rain, wind, wind direction, sun
	"HMIP-SWO-PL": 		"HMIP-SWO-PR",				# weather sensor temp, hum ,rain, wind,                 sun
	"HMIP-SWO-B": 		"HMIP-SWO-PR",				# weather sensor temp, hum ,rain, wind
	"HMIP-SRD": 		"HMIP-SRD",					# rain sensor
	"HMIP-SL": 			"HMIP-SL",					# Light sensor
	"HMIP-SFD": 		"HMIP-SFD",					# particulate sensor 
	"HMIP-STE2": 		"HMIP-STE2",					# particulate sensor 
	"HMIP-STHO": 		"HMIP-STHO",				# Temp-Humidity Sensor
	"HMIP-SCTH": 		"HMIP-SCTH",				# CO2 Temp Humidity Sensor
	"HMIP-SWSD": 		"HMIP-SWSD",				# smoke alarm
	"HMIP-SCI": 		"HMIP-SWDM",				# contact sensor
	"HMIP-SWDM": 		"HMIP-SWDM",				# Magnet Contact sensor
	"HMIP-SRH": 		"HMIP-SRH",					# window open=2/tilted=1/close=0
	"HMIP-STV": 		"HMIP-SWDM",				# tilt sensor
	"HMIP-SWDO": 		"HMIP-SWDM",				# optical sensor
	"HMIP-SWD||": 		"HMIP-SWD",					# eater sensor,  || only accept strict HMIP-SWD no additional characters
	"HMIP-SPDR": 		"HMIP-SPDR",				# left right pass sensor 
	"HMIP-SAM":			"HMIP-SAM",					# gravity, movement sensor on/off
	"HMIP-SMI":			"HMIP-SMI",					# movement sensor inside
	"HMIP-SMO":			"HMIP-SMI",					# movement sensor outside
	"HMIP-SPI":			"HMIP-SMI",					# movement sensor
	"HMIP-MOD-OC8": 	"HMIP-MOD-OC8",				# 8 channel open collector output switch
	"HMIP-MIO16-PCB": 	"HMIP-MIO16-PCB",			# multi channel i/o 4 analog trigger, digital trigger, 4 open collector, 4 relay output
	"HMIP-MIOB": 		"HMIP-MIOB",				# multi channel i/o 4 for heating system
	"HMIP-MP3P": 		"HMIP-MP3P",				# sound/ light output 
	"HMIP-ASIR": 		"HMIP-ASIR",				# alarm siren
	"HMIP-FROLL": 		"HMIP-ROLL",				# Jalousie(Jealousy) / curtains  up / down  / left right
	"ELV-SH-WSC": 		"ELV-SH-WSC",				# 2 channel servo controller
	"HMIP-PDT": 		"HMIP-PDT",					# dimmer output 
	"HMIP-FDT": 		"HMIP-PDT",					# dimmer output
	"HMIP-BDT":			"HMIP-PDT",					# dimmer outlet
	"HMIP-DRD3":		"HMIP-PDT3",				# 3 dimmer fuse box 
	"HMIP-DRBL":		"HMIP-PDT4",				# 4 dimmer fuse box 
	"HMIP-DRSI1":		"HMIP-PS",					# on/off germnan fuse box relay
	"HMIP-PS||":		"HMIP-PS",					# on/off outlet
	"HMIP-FS":			"HMIP-PS",					# on.off outlet
	"HMIP-PS-":			"HMIP-PS",					# any simple on/off outlet
	"HMIP-PCBS||":		"HMIP-PS",					# on/off board relay
	"HMIP-PCBS-":		"HMIP-PS",					# on/off board relay
	"HMIP-PCBS2":		"HMIP-PS2",					# 2 on/off board relay
	"ELV-SH-SW1-BA":	"HMIP-PS",					# on/off board relay w battery
	"ELV-SH-TACO":		"ELV-SH-TACO",				# Temperature and acceleration sensor 
	"HMIP-WGC":			"HMIP-PS",					# garage door controller 
	"HMIP-DRSI4":		"HMIP-PS4",					# on/off german fuse box 4-relay
	"HMIP-PSM": 		"HMIP-PSM",					# on/off outlet w energy measurements
	"HMIP-FSM": 		"HMIP-PSM",					# on/off outlet w energy measurements
	"HMIP-USBSM": 		"HMIP-PSM",					# on/off outlet w energy measurements USB 
	"HMIP-BSM":			"HMIP-PSM",					# PowerOutlet Switch W Energy measurement
	"HMIP-ETRV":		"HMIP-ETRV",				# eTRV-RadiatorValve
	"HMIP-BWTH": 		"HMIP-WTH",					# wall thermostat
	"HMIP-WTH": 		"HMIP-WTH",					# wall thermostat
	"HMIP-HEATING": 	"HMIP-HEATING",				# heating group of several EVTR and WTH, not a real device 
	"RPI-RF-MOD": 		"Homematic-AP",				# RPI host
	"HMIP-HAP": 		"Homematic-AP",				# ACCESS point
	"ROOM": 			"HMIP-ROOM"				# room, not a real device , shows devices in room
}

#merge with user defined devices
for xx in userdefs:
	k_supportedDeviceTypesFromHomematicToIndigo[xx] = userdefs[xx]

# used to test if memeber of statemeasures
k_testIfmemberOfStateMeasures = "ChangeHours01"


# these are added to custom states for eg temerature etc
k_stateMeasures	= [
	"MinToday","MinTodayAt", "MaxYesterday", "MaxYesterdayAt",  "MinYesterday",  "MinYesterdayAt", "MaxToday", "MaxTodayAt", "AveToday", "AveYesterday", "ChangeMinutes10", "ChangeMinutes20", "ChangeHours01", "ChangeHours02", "ChangeHours06", "ChangeHours12", "ChangeHours24"
] 

# used for counting to calc averages, add to states
k_stateMeasuresCount = [
	"MeasurementsToday", "MeasurementsYesterday"
]

#for dev states props
k_statesThatHaveMinMaxReal = [
	"Temperature", "Power", "Current", "Voltage", "OperatingVoltage", "Illumination", "sensorValue","RainRate_mm_pH"
]

k_statesThatHaveMinMaxInteger = [
	"Humidity", "WindSpeed", "CO2"
]

k_statesWithfillMinMax = k_statesThatHaveMinMaxReal + k_statesThatHaveMinMaxInteger


k_ChildrenHaveTheseStates ={
		"childOf":"integer",
		"channelNumber":"string"
} 


# copy indgo state to something readable ie thermostates 
k_doubleState ={
	"temperatureInput1":"Temperature",
	"humidityInput1": "Humidity"
}

# for check is state should be created, some devices have temp, others not, but are defined here as the same device, test converted to upper case
k_checkIfPresentInValues = ["TEMPERATURE","HUMIDITY","RAIN","ILLUMINATION","WIND"]


k_isBatteryDevice = [
	"HMIP-STHO",			
	"HMIP-WTH",
	"HMIP-SWDM",
	"HMIP-SAM",
	"HMIP-SWD",
	"HMIP-SWO-PR",
	"HMIP-SL",
	"HMIP-STE2",
	"HMIP-SWO-B",
	"HMIP-SW1",
	"HMIP-SWSD",
	"HMIP-DLD",
	"HMIP-SCTH",
	"HMIP-SCTH",
	"HMIP-MP#P",
	"HMIP-SMI",
	"HMIP-BUTTON",
	"HMIP-ASIR",
	"HMIP-SPDR",
	"HMIP-SRH",	
	"ELV-SH-TACO",
	"HMIP-ETRV"
]

# add some states ie operating voltage to these devceis 
k_isVoltageDevice = [
	"ELV-SH-WSC",
	"HMIP-ASIR",
	"HMIP-STHO",	
	"HMIP-SCTH",		
	"HMIP-WTH",
	"HMIP-SWDM",
	"HMIP-SWD",
	"HMIP-SWSD",
	"HMIP-SPDR",
	"HMIP-SRD",
	"HMIP-SWO-PR"
	"HMIP-SL",
	"HMIP-STE2",
	"HMIP-ETRV",			
	"HMIP-BUTTON",
	"HMIP-WKP",
	"HMIP-SMI",	
	"HMIP-MOD-OC8",	
	"HMIP-MIO16-PCB",	
	"HMIP-MIOB",
	"HMIP-MP3P",	
	"HMIP-FALMOT",
	"HMIP-DLD",
	"HMIP-PSM",		
	"HMIP-PS",		
	"HMIP-PS2",		
	"HMIP-PS4",		
	"HMIP-PDT",		
	"HMIP-PDT3",		
	"HMIP-PDT4",
	"HMIP-SRH",	
	"HMIP-ROLL",	
	"ELV-SH-TACO",
	"HMIP-SFD"
]

# these don't have eg low battery, or unreach ...
k_isNotRealDevice =[
	"HMIP-RCV-50",
	"HMIP-ROOM",
	"HMIP-SYSVAR-FLOAT",
	"HMIP-SYSVAR-STRING",
	"HMIP-SYSVAR-BOOL",
	"HMIP-SYSVAR-ALARM",
	"HMIP-SYSVAR",
]


k_deviceTypesWithButtonPress=[
	"HMIP-BUTTON",
]

k_deviceTypesWithOnOff=[
	"HMIP-OnOff",
]


k_buttonPressStates = {
	"STATE":{"refresh":"1"},
	"PRESS_SHORT":{"refresh":"1"},
	"PRESS_LONG":{"refresh":"1"},
	"PRESS_LONG_RELEASE":{"refresh":"1"},
	"PRESS_LONG_START":{"refresh":"1"},
	"OPTICAL_ALARM_ACTIVE":{"refresh":"1"},
	"ACOUSTIC_ALARM_ACTIVE":{"refresh":"1"}
}


k_OnOffStates = {
	"STATE":{"refresh":"1"}
}


k_deviceTypesWithKeyPad = [
	"HMIP-WKP"
]

k_keyPressStates = {
	"CODE_ID":{"refresh":"1"},
	"USER_AUTHORIZATION_01":{"refresh":"1"},
	"USER_AUTHORIZATION_02":{"refresh":"1"},
	"USER_AUTHORIZATION_03":{"refresh":"1"},
	"USER_AUTHORIZATION_04":{"refresh":"1"},
	"USER_AUTHORIZATION_05":{"refresh":"1"},
	"USER_AUTHORIZATION_06":{"refresh":"1"},
	"USER_AUTHORIZATION_07":{"refresh":"1"},
	"USER_AUTHORIZATION_08":{"refresh":"1"}
}


k_systemAP = [
	"Homematic-AP",
	"Homematic-Host"
]


k_statesToCreateisBatteryDevice = {
	"LOW_BAT":"booltruefalse"
}


k_statesToCreateisRealDevice = {
	"CONFIG_PENDING":"booltruefalse",
	"RSSI_DEVICE":"integer",
	"RSSI_PEER":"integer", 
	"online":"booltruefalse",
	"roomId":"string",
	"firmware":"string",
	"availableFirmware":"string"
}

k_allDevicesHaveTheseStates = {
	"address":"string",
	"created":"string",
	"title":"string",
	"homematicType":"string",
	"lastSensorChange":"string"
}

# these sates are alreadu defined in indigo 
k_alreadyDefinedStatesInIndigo = [
	"onOffState",
	"temperatureInput1",
	"brightnessLevel",
	"humidityInput1",
	"setpointHeat",
	"sensorValue"
]

k_statesWithOffsetInProperties = [
	"temperatureInput1",
	"humidityInput1",
	"Temperature",
	"sensorValue",
	"Humidity"
]

k_statesWithPreviousValue = [
	"temperatureInput1",
	"humidityInput1",
	"Temperature",
	"sensorValue",
	"Humidity",
	"WIND_DIR"
]

k_deviceIsRateDevice = [
	"HMIP-Rain"
]

k_deviceWithDayWeekMonth = {
	"HMIP-Rain":{
		"indigoState":	"RainTotal", 
		"rateState":	"RainRate_mm_pH", 
		"onOffState":	"Raining", 
		"reset":		"RainTotal_Reset",
		"devideby":		1,
		"roundBy":		0,
		"roundByRate":	1
	},
	"HMIP-PSM":{
		"indigoState":	"Energy_Wh", 
		"rateState":	"", 
		"onOffState":	"", 
		"reset":		"Energy_Wh_Reset",
		"devideby":		1,
		"roundBy":		0
	},
	"HMIP-Sunshine":{
		"indigoState":	"SunshineMinutes", 
		"rateState":	"", 
		"onOffState":	"", 
		"reset":		"SunshineMinutes_Reset",
		"devideby":		1,
		"roundBy":		0,
		"format":		"{:.0f} Min"
	}
}

# homematic delivers some info in varibales, here we put them into teh corresponding dev/states 
k_mapTheseVariablesToDevices = {
}


k_doNotCreateStateForChildDevices = [
	"online",
	"UNREACH"
]

k_mapMonthNumberToMonthName = {
	"1": "January",
	"2": "Februray",
	"3": "March",
	"4": "April",
	"5": "May",
	"6": "June",
	"7": "July",
	"8": "August",
	"9": "September",
	"10": "October",
	"11": "November",
	"12": "December"
}


k_refreshTimes = [1., 7., 30.]

k_repeatGet = {
	"1":k_refreshTimes[0],
	"2":k_refreshTimes[1],
	"3":k_refreshTimes[2]
}
# common states defs
k_UNREACHP = {			"indigoState": "online",			"dType": "booltruefalse",							"channelNumber": "0",												"inverse":True,		"refresh":"3"}
k_UNREACH = {			"indigoState": "online",			"dType": "booltruefalse",							"channelNumber": "0",				"duplicateState":"onOffState",	"inverse":True,		"refresh":"3"}
k_RelayMap = {			"indigoState": "onOffState",		"dType": "booltruefalse", 							"channelNumber": "2",																	"refresh":"1"}
k_DimmerMap = {			"indigoState": "brightnessLevel",	"dType": "integer",			"format": "{}%",		"channelNumber": "2",	"mult": 100,													"refresh":"1"}
k_Voltage = {			"indigoState": "Voltage",			"dType": "real",			"format": "{:.1f}V",	"channelNumber": "7"				,													"refresh":"3"}
k_Power = {				"indigoState": "Power",				"dType": "real",			"format": "{:.1f}W",	"channelNumber": "7"				,													"refresh":"3"}
k_Current = {			"indigoState": "Current",			"dType": "real",			"format": "{:.2f}A",	"channelNumber": "7"				,													"refresh":"3"}
k_Frequency = {			"indigoState": "Frequency",			"dType": "real",			"format": "{:.1f}Hz",	"channelNumber": "7"				,													"refresh":"3"}
k_Illumination = {		"indigoState": "Illumination",		"dType": "real",			"format": "{:.1f}Lux"										,													"refresh":"1"}
k_Temperature = {		"indigoState": "Temperature",		"dType": "real",			"format": "{:.1f}ºC"										,													"refresh":"3"}
k_Acceleration = {		"indigoState": "Acceleration",		"dType": "real",			"format": "{:.1f}m/s"										,													"refresh":"1"}
k_Humidity = {			"indigoState": "Humidity",			"dType": "integer",			"format": "{}%"												,													"refresh":"3"}


# tehse states do not come directly from hoematic, thy are calculated from otgher states and timing
k_dontUseStatesForOverAllList = [
	"childOf",
	"childInfo",
	"enabledChildren",
	"channelNumber",
	"SunshineThisDay",
	"SunshineYesterday",
	"SunshineMinutes",
	"user",
	"userTime",
	"userPrevious",
	"userTimePrevious",
	"buttonPressed",
	"buttonPressedTime",
	"buttonPressedType",
	"buttonPressedPrevious",
	"buttonPressedTimePrevious",
	"buttonPressedTypePrevious",
	"lastValuesText",
	"value",
	"roomListNames",
	"NumberOfDevices",
	"roomListIDs",
	"description",
	"sensorValue",
	"onOffState",
	"numberOfRooms",
	"numberOfDevices",
	"numberOfVariables"
]


# this is teh main list of sattes, props, xml action for each device type - we use here the indigo dev type, not the homematic def type
# states are the homematic states, if indgo statename is different "indigoState" defines that state name
# for action channel info eg "channels": 'int(dev.states["channelNumber"])+1' is converted with "eval()" to a real number 
# deviceXml describes the xml code in devices.xml.
k_mapHomematicToIndigoDevTypeStateChannelProps = { 

	# general types
	"HMIP-OnOff":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"STATE":{"indigoState": "onOffState", "dType": "booltruefalse", "channelNumber": "-99", "refresh":"1"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI>'+
		'<Field id="inverse"   type="checkbox"  defaultValue="false" > <Label>invert on/off state</Label> </Field>'+
		'<Field id="useForOn"  type="textfield" defaultValue="on" >    <Label>use what string for ON </Label> </Field>'+
		'<Field id="useForOff" type="textfield" defaultValue="off" >   <Label>use what string for OFF </Label> </Field>'+
		'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"inverse":False,
			"useForOn":"on",
			"useForOff":"off",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},


	"HMIP-Relay":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"STATE":mergeDicts(k_RelayMap,{"channelNumber":"-99"})
		},
		"actionParams":{
			"states":{ "OnOff":"STATE"},
			"channels":{"OnOff":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3']}
		},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},

	"HMIP-Dimmer":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"-99"})
		},
		"actionParams":{
			"states":{"Dimm":"LEVEL" },
			"channels":{"Dimm":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3'], 
			"OnOff":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3']
			},
			"mult":{"Dimm":0.01}
		},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Dimmer-C":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"-99"}),
			"COLOR":{"dType":"string","intToState":True,"channelNumber":"6",		"refresh":"3"}
		},
		"actionParams":{
			"states":{"Dimm":"LEVEL" },
			"channels":{"Dimm":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3'], 
						"OnOff":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3']
			},
			"mult":{"Dimm":0.01}
			},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"isSimpleColorDevice":True,
			"SupportsStatusRequest":False,
			"SupportsWhite":True,
			"SupportsRGB":True,
			"SupportsColor":True
		}
	},

	"HMIP-Dimmer-V":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"-99"}),
			"LEVEL_STATUS":{"dType":"string","intToState":True,"channelNumber":"-99",		"refresh":"3"},
			"FROST_PROTECTION":{"dType":"booltruefalse","channelNumber":"-99",				"refresh":"3"},
			"VALVE_STATE":{"dType":"string","intToState":True,"channelNumber":"-99",		"refresh":"3"}
		},
		"actionParams":{
			"states":{"Dimm":"LEVEL" },
			"channels":{"Dimm":['int(dev.states["channelNumber"])'], 
						"OnOff":['int(dev.states["channelNumber"])']
			},
			"mult":{"Dimm":0.01}
			},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Dimmer-R":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"4"}),
			"LEVEL_STATUS":{"dType":"string","intToState":True,"channelNumber":"-99",		"refresh":"3"}
		},
		"actionParams":{
			"states":{"Dimm":"LEVEL" },
			"channels":{"Dimm":['int(dev.states["channelNumber"])'], 
						"OnOff":['int(dev.states["channelNumber"])']
			},
			"mult":{"Dimm":0.01}
			},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},


	"HMIP-LEVEL":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"LEVEL":{"dType":"integer","mult":100,"format":"{}%","channelNumber":"-99",		"refresh":"1"},
			"LEVEL_STATUS":{"dType":"string","intToState":True,"channelNumber":"-99",		"refresh":"3"},
			"FROST_PROTECTION":{"dType":"booltruefalse","channelNumber":"-99",				"refresh":"3"},
			"VALVE_STATE":{"dType":"string","intToState":True,"channelNumber":"-99",		"refresh":"3"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"LEVEL",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Voltage":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"VOLTAGE":{"dType":"real","indigoState":"Voltage","format":"{:.2f}V","channelNumber":"-99",		"refresh":"3"},
			"VOLTAGE_STATUS":{"dType":"string","intToState":True,"channelNumber":"-99",						"refresh":"3"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Voltage",
		"props":{
			"displayS":"Voltage",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False,
		}
	},


	"HMIP-Acceleration":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"ACCELERATION":mergeDicts(k_Acceleration,{"channelNumber":"5"})
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Acceleration",
		"props":{
			"displayS":"Acceleration",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},


	"HMIP-Temperature":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"})
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Temperature",
		"props":{
			"displayS":"Temperature",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Humidity":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"HUMIDITY":mergeDicts(k_Humidity,{"channelNumber":"-99"})
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Humidity",
		"props":{
			"displayS":"Humidity",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Illumination":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"ILLUMINATION":mergeDicts(k_Illumination,{"channelNumber":"-99"})
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Illumination",
		"props":{
			"displayS":"Illumination",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-SL":{
		"states":{
			"ILLUMINATION":mergeDicts(k_Illumination,{"channelNumber":"1"}),
			"CURRENT_ILLUMINATION":mergeDicts(k_Illumination,{"channelNumber":"1"})
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Illumination",
		"props":{
			"displayS":"Illumination",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Rain":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"RAINING":{"dType": "booltruefalse","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["onOffState"],"channelNumber":"1",		"refresh":"2"},
			"RAIN_COUNTER":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"],"channelNumber":"1",			"refresh":"3"},
			"lastEventOff":{"dType": "string"},
			"lastEventOn":{"dType": "string"},
			k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Reset":{"dType": "string"},
			"at0":{"dType": "string","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_At0"},
			"Day-7":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Day-7"},
			"Day-6":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Day-6"},
			"Day-5":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Day-5"},
			"Day-4":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Day-4"},
			"Day-3":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Day-3"},
			"Day-2":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Day-2"},
			"Day-1":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Yesterday"},
			"Day-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Today"},
			"Week-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_ThisWeek"},
			"Week-1":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Week-1"},
			"Week-2":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Week-2"},
			"Week-3":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Week-3"},
			"Week-4":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_Week-4"},
			"Month-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_ThisMonth"},
			"Month-1" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["1"]},
			"Month-2" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["2"]},
			"Month-3" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["3"]},
			"Month-4" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["4"]},
			"Month-5" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["5"]},
			"Month-6" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["6"]},
			"Month-7" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["7"]},
			"Month-8" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["8"]},
			"Month-9" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["9"]},
			"Month-10":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["10"]},
			"Month-11":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["11"]},
			"Month-12":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["12"]},
			"Year":    {"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_ThisYear"},
			"LastYear":  {"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Rain"]["indigoState"]+"_LastYear"},
			"rainrate":{"dType": "real","indigoState":"RainRate_mm_pH"}
		},
		"noIndigoState":k_buttonPressStates,
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"RainTotal",
		"props":{
			"displayS":"Raining",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True,
			"isDeviceWithRate":  True
		}
	},

	"HMIP-Sunshine":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"SunshineMinutes_Reset":{"dType": "string"},
			"SUNSHINEDURATION":{"dType":"integer","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"],"channelNumber":"1",		"refresh":"3"},
			"at0":{"dType": "string","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_At0"},
			"Day-7":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Day-7"},
			"Day-6":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Day-6"},
			"Day-5":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Day-5"},
			"Day-4":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Day-4"},
			"Day-3":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Day-3"},
			"Day-2":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Day-2"},
			"Day-1":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Yesterday"},
			"Day-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Today"},
			"Week-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_ThisWeek"},
			"Week-1":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Week-1"},
			"Week-2":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Week-2"},
			"Week-3":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Week-3"},
			"Week-4":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Week-4"},
			"Month-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_ThisMonth"},
			"Month-1" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["1"]},
			"Month-2" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["2"]},
			"Month-3" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["3"]},
			"Month-4" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["4"]},
			"Month-5" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["5"]},
			"Month-6" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["6"]},
			"Month-7" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["7"]},
			"Month-8" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["8"]},
			"Month-9" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["9"]},
			"Month-10":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["10"]},
			"Month-11":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["11"]},
			"Month-12":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["12"]},
			"Year":    {"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_ThisYear"},
			"LastYear":  {"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_LastYear"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"SunshineToday",
		"props":{
			"displayS":k_deviceWithDayWeekMonth["HMIP-Sunshine"]["indigoState"]+"_Today",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"HMIP-Wind":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"WIND_DIR":{"dType": "integer","channelNumber":"1",															"refresh":"2"},
			"WIND_DIR_RANGE":{"dType": "real","channelNumber":"1",														"refresh":"2"},
			"WIND_SPEED":{"dType": "real","indigoState":"WindSpeed", "channelNumber":"1","format":"{:.1f}[km/h]",		"refresh":"2"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"WindSpeed",
		"props":{
			"displayS":"WindSpeed",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False,
		}
	},

	"HMIP-Direction":{
		"states":{
			"channelNumber":{"dType": "string"},
			"childOf":{"dType": "integer"},
			"ABSOLUTE_ANGLE":{"indigoState":"Angle","dType":"integer","format":"{:d}º","duplicateState":"sensorValue","channelNumber":"-99"},
			"MOTION":{"indigoState":"Horizontal","dType": "booltruefalse","inverse":True,"channelNumber":"-99"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"Angle",
		"props":{
			"displayS":"Angle",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState": False,
		}
	},

	# Multi channel types
	"HMIP-SCTH":{
		"states":{
			"CONCENTRATION":{"indigoState":"CO2","dType": "integer","format":"{:}[ppm]",				"refresh":"2"},
			"enabledChildren":{"dType": "string"},
			"childInfo":{"dType": "string","init":'{"Temperature":[0,"4","HMIP-Temperature"], "Humidity":[0,"4","HMIP-Humidity"], "Relay":[0,"7","HMIP-Relay"], "Dimmer":[0,"11","HMIP-Dimmer"]}'}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-Temperature"  type="checkbox" defaultValue="true" > <Label>create Temperature device </Label></Field>'+
				'<Field id="enable-Humidity"     type="checkbox" defaultValue="true" > <Label>create Humidity device </Label></Field>'+
				'<Field id="enable-Relay"        type="checkbox" defaultValue="true" > <Label>create Relay device </Label></Field>'+
				'<Field id="enable-Dimmer"       type="checkbox" defaultValue="true" > <Label>create Dmmer (light) device </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"CO2",
		"props":{
			"displayS":"CO2",
			"enable-Temperature": True,
			"enable-Humidity": True,
			"enable-Relay": True,
			"enable-Dimmer": True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
	},
	# Multi channel types
	"HMIP-STE2":{
		"states":{
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"indigoState":"Temperature","channelNumber":"3"}),
			"enabledChildren":{"dType": "string"},
			"childInfo":{"dType": "string","init":'{"T1":[0,"1","HMIP-Temperature"],"T2":[0,"2","HMIP-Temperature"]}'}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-T1"  type="checkbox" defaultValue="true" > <Label>create Temperature 1 device </Label></Field>'+
				'<Field id="enable-T2"  type="checkbox" defaultValue="true" > <Label>create Temperature 2 device </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"Temperature",
		"props":{
			"displayS":"Temperature",
			"enable-T1": True,
			"enable-T2": True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
	},


	"HMIP-SFD":{
		"states":{
			"UNREACH":k_UNREACHP,
			"ERROR_COMMUNICATION_PARTICULATE_MATTER_SENSOR":{"dType":"string","intToState":True,"channelNumber":"0",		"refresh":"3"},
			"TYPICAL_PARTICLE_SIZE":{"dType":"real","channelNumber":"1","format":"{:.1f} um",								"refresh":"2"},
			"NUMBER_CONCENTRATION_PM_10":{"dType":"real","channelNumber":"1","format":"{:.1f}/cm3",							"refresh":"2"},
			"NUMBER_CONCENTRATION_PM_2_5":{"dType":"real","channelNumber":"1","format":"{:.1f}/cm3",						"refresh":"2"},
			"NUMBER_CONCENTRATION_PM_1":{"dType":"real","channelNumber":"1","format":"{:.1f}/cm3",							"refresh":"2"},
			"MASS_CONCENTRATION_PM_10":{"dType":"real","channelNumber":"1","format":"{:.1f} ug/m3",							"refresh":"2"},
			"MASS_CONCENTRATION_PM_2_5":{"dType":"real","channelNumber":"1","format":"{:.1f} ug/m3",						"refresh":"2"},
			"MASS_CONCENTRATION_PM_1":{"dType":"real","channelNumber":"1","format":"{:.1f} ug/m3",							"refresh":"2"},
			"MASS_CONCENTRATION_PM_1_24H_AVERAGE":{"dType":"real","channelNumber":"1","format":"{:.1f} ug/m3",				"refresh":"2"},
			"MASS_CONCENTRATION_PM_2_5_24H_AVERAGE":{"dType":"real","channelNumber":"1","format":"{:.1f} ug/m3",			"refresh":"2"},
			"MASS_CONCENTRATION_PM_10_24H_AVERAGE":{"dType":"real","channelNumber":"1","format":"{:.1f} ug/m3",				"refresh":"2"},
			"enabledChildren":{"dType": "string"},
			"childInfo":{"dType": "string","init":'{"Temperature":[0,"1","HMIP-Temperature"],"Humidity":[0,"1","HMIP-Humidity"]}'}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-Temperature"  type="checkbox" defaultValue="true"   >  <Label>Enable Temperature device </Label></Field>'+
				'<Field id="enable-Humidity"     type="checkbox" defaultValue="true"   >  <Label>Enable Humidity device </Label></Field>'+
				'<Field id="displayS"    		 type="menu" defaultValue="MASS_CONCENTRATION_PM_10_24H_AVERAGE"   >'+
				'<List>'+
					'    <Option value="MASS_CONCENTRATION_PM_10_24H_AVERAGE"  >MASS_CONCENTRATION_PM_10_24H_AVERAGE </Option>'+
					'    <Option value="MASS_CONCENTRATION_PM_2_5_24H_AVERAGE" >MASS_CONCENTRATION_PM_2_5_24H_AVERAGE </Option>'+
					'    <Option value="MASS_CONCENTRATION_PM_1_24H_AVERAGE"   >MASS_CONCENTRATION_PM_1_24H_AVERAGE </Option>'+
					'    <Option value="NUMBER_CONCENTRATION_PM_10"            >NUMBER_CONCENTRATION_PM_10 </Option>'+
					'    <Option value="NUMBER_CONCENTRATION_PM_2_5"           >NUMBER_CONCENTRATION_PM_2_5 </Option>'+
					'    <Option value="NUMBER_CONCENTRATION_PM_1"             >NUMBER_CONCENTRATION_PM_1 </Option>'+
					'    <Option value="MASS_CONCENTRATION_PM_10"              >MASS_CONCENTRATION_PM_10 </Option>'+
					'    <Option value="MASS_CONCENTRATION_PM_2_5"             >MASS_CONCENTRATION_PM_2_5 </Option>'+
					'    <Option value="MASS_CONCENTRATION_PM_1"               >MASS_CONCENTRATION_PM_1 </Option>'+
					'    <Option value="TYPICAL_PARTICLE_SIZE"                 >TYPICAL_PARTICLE_SIZE </Option>'+
				'</List>'+
				'<Label>Select state to show in staus column</Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"MASS_CONCENTRATION_PM_10,MASS_CONCENTRATION_PM_2_5,MASS_CONCENTRATION_PM_1",
		"props":{
			"displayS":"MASS_CONCENTRATION_PM_10_24H_AVERAGE",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False,
			"enable-Temperature":  True,
			"enable-Humidity":  True
		}
	},



	"HMIP-SWO-PR":{
		"states":{
			"UNREACH":k_UNREACH,
			"enabledChildren":{"dType": "string"},
			"childInfo":{"dType": "string","init":'{"Temperature":[0,"1","HMIP-Temperature"], "Humidity":[0,"1","HMIP-Humidity"], "Illumination":[0,"1","HMIP-Illumination"],  "Rain":[0,"1","HMIP-Rain"],  "Sunshine":[0,"1","HMIP-Sunshine"],  "Wind":[0,"1","HMIP-Wind"]}'}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-Temperature"  type="checkbox" defaultValue="true"   >  <Label>Enable Temperature device </Label></Field>'+
				'<Field id="enable-Humidity"     type="checkbox" defaultValue="true"   >  <Label>Enable Humidity device </Label></Field>'+
				'<Field id="enable-Illumination" type="checkbox" defaultValue="true"   >  <Label>Enable Illumination device </Label></Field>'+
				'<Field id="enable-Sunshine"     type="checkbox" defaultValue="true"   >  <Label>Enable Sunshine device </Label></Field>'+
				'<Field id="enable-Rain"         type="checkbox" defaultValue="true"   >  <Label>Enable Rain device </Label></Field>'+
				'<Field id="enable-Wind"         type="checkbox" defaultValue="true"   >  <Label>Enable Wind device </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"onOffState",
		"props":{
			"displayS":"online",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True,
			"enable-Temperature":  True,
			"enable-Humidity":  True,
			"enable-Illumination":  True,
			"enable-Rain":  True,
			"enable-Sunshine":  True,
			"enable-Wind":  True
		}
	},

	"HMIP-MOD-OC8":{
		"states":{
			"UNREACH":k_UNREACH,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"0"}),
			"childInfo":{"dType": "string","init":'{"1":[0,"9","HMIP-Relay"], "2":[0,"13","HMIP-Relay"], "3":[0,"17","HMIP-Relay"],  "4":[0,"21","HMIP-Relay"],  "5":[0,"25","HMIP-Relay"],  "6":[0,"29","HMIP-Relay"],  "7":[0,"33","HMIP-Relay"],  "8":[0,"37","HMIP-Relay"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-1" type="checkbox" defaultValue="true"  > <Label>create output device 1 for channel #9 </Label></Field>'+
				'<Field id="enable-2" type="checkbox" defaultValue="false" > <Label>create output device 2 for channel #13 </Label></Field>'+
				'<Field id="enable-3" type="checkbox" defaultValue="false" > <Label>create output device 3 for channel #17 </Label></Field>'+
				'<Field id="enable-4" type="checkbox" defaultValue="false" > <Label>create output device 4 for channel #21 </Label></Field>'+
				'<Field id="enable-5" type="checkbox" defaultValue="false" > <Label>create output device 5 for channel #25 </Label></Field>'+
				'<Field id="enable-6" type="checkbox" defaultValue="false" > <Label>create output device 6 for channel #29 </Label></Field>'+
				'<Field id="enable-7" type="checkbox" defaultValue="false" > <Label>create output device 7 for channel #33 </Label></Field>'+
				'<Field id="enable-8" type="checkbox" defaultValue="false" > <Label>create output device 8 for channel #37  </Label></Field> '
			'</ConfigUI>',
		"props":{
			"displayS":"online",
			"enable-1":True,
			"enable-2":False,
			"enable-3":False,
			"enable-4":False,
			"enable-5":False,
			"enable-6":False,
			"enable-7":False,
			"enable-8":False,
			"SupportsOnState": True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False
		}
	},
	"HMIP-MIOB":{
		"states":{
			"UNREACH":k_UNREACH,
			"childInfo":{
				"dType": "string","init":
					'{"R1":[0,"1","HMIP-Relay"], "R2":[0,"5","HMIP-Relay"],'+
					'"D1":[0,"11","HMIP-Dimmer-R"],'+
					'"B1":[0,"9","HMIP-BUTTON"], "B2":[0,"10","HMIP-BUTTON"] }' 
			},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
			"states":{"Dimm":"LEVEL"}, "channels":{"Dimm":["11"],"OnOff":["11"]}, "mult":{"Dimm":0.01}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-R1"  type="checkbox" defaultValue="true"  > <Label>create output device 1 for channel #1 </Label></Field>'+
				'<Field id="enable-R1"  type="checkbox" defaultValue="true"  > <Label>create output device 1 for channel #1 </Label></Field>'+
				'<Field id="enable-R2"  type="checkbox" defaultValue="false" > <Label>create output device 2 for channel #5 </Label></Field>'+
				'<Field id="enable-D1"  type="checkbox" defaultValue="true"  > <Label>create Dimmer device   for channle 11</Label></Field>'+
				'<Field id="enable-B1"  type="checkbox" defaultValue="false" > <Label>create INPUT  device 1 for channel #9 </Label></Field>'+
				'<Field id="enable-B2"  type="checkbox" defaultValue="false" > <Label>create INPUT  device 2 for channel #10</Label></Field>'+
				'<Field id="show" type="label">'+
				'  <Label>'+
				'   enable child devices as you see fit'+
				'  </Label>'+
				'</Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"online",
			"enable-R1":  True,
			"enable-R2":  False,
			"enable-D1":  False,
			"enable-B1":  False,
			"enable-B2":  False,
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},


	"HMIP-MIO16-PCB":{
		"states":{
			"UNREACH":k_UNREACH,
			"childInfo":{"dType": "string","init":
			'{"R1":[0,"17","HMIP-Relay"], "R2":[0,"21","HMIP-Relay"], "R3":[0,"25","HMIP-Relay"], "R4":[0,"29","HMIP-Relay"], "R5":[0,"33","HMIP-Relay"], "R6":[0,"37","HMIP-Relay"], "R7":[0,"41","HMIP-Relay"], "R8":[0,"45","HMIP-Relay"]'+
			',"V1":[0,"1","HMIP-Voltage"], "V2":[0,"4","HMIP-Voltage"], "V3":[0,"7","HMIP-Voltage"], "V4":[0,"10","HMIP-Voltage"]'+
			',"B99":[0,"-99","HMIP-BUTTON"] }' },
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-R1"  type="checkbox" defaultValue="true"  > <Label>create output device 1 for channel #17 </Label></Field>'+
				'<Field id="enable-R2"  type="checkbox" defaultValue="false" > <Label>create output device 2 for channel #21 </Label></Field>'+
				'<Field id="enable-R3"  type="checkbox" defaultValue="false" > <Label>create output device 3 for channel #25 </Label></Field>'+
				'<Field id="enable-R4"  type="checkbox" defaultValue="false" > <Label>create output device 4 for channel #29 </Label></Field>'+
				'<Field id="enable-R5"  type="checkbox" defaultValue="false" > <Label>create output device 5 for channel #33 </Label></Field>'+
				'<Field id="enable-R6"  type="checkbox" defaultValue="false" > <Label>create output device 6 for channel #37 </Label></Field>'+
				'<Field id="enable-R7"  type="checkbox" defaultValue="false" > <Label>create output device 7 for channel #41 </Label></Field>'+
				'<Field id="enable-R8"  type="checkbox" defaultValue="false" > <Label>create output device 8 for channel #45  </Label></Field>'+
				'<Field id="enable-V1"  type="checkbox" defaultValue="true"  > <Label>create VOLTAGE INPUT device 1 for channel #1 </Label></Field>'+
				'<Field id="enable-V2"  type="checkbox" defaultValue="false" > <Label>create VOLTAGE INPUT device 2 for channel #2 </Label></Field>'+
				'<Field id="enable-V3"  type="checkbox" defaultValue="false" > <Label>create VOLTAGE INPUT device 3 for channel #3</Label></Field>'+
				'<Field id="enable-V4"  type="checkbox" defaultValue="false" > <Label>create VOLTAGE INPUT device 4 for channel #5</Label></Field>'+
				'<Field id="enable-B99" type="checkbox" defaultValue="true"  > <Label>create button for channel 13,14,15,16</Label></Field>'+
				'<Field id="show" type="label">'+
				'  <Label>'+
				'   For the digital input channels see menu / PRINT parameters and help to logfile to setup correctly'+
				'   For the analog inout channel you need to set "ch 0: ...Statusmeldungen =0/0" '+
				'      it still takes 150 seconds to send a new Voltage'+ 
				'      with ch2 and 3 you can set threshold that will trigger a send when threshold is passed'+
				'  </Label>'+
				'</Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"online",
			"enable-R1":  True,
			"enable-R2":  False,
			"enable-R3":  False,
			"enable-R4":  False,
			"enable-R5":  False,
			"enable-R6":  False,
			"enable-R7":  False,
			"enable-R8":  False,
			"enable-V1":  True,
			"enable-V2":  False,
			"enable-V3":  False,
			"enable-V4":  False,
			"enable-B99":  True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},


	"HMIP-WRCD":{
		"states":{
			"UNREACH":k_UNREACH,
			"childInfo":{"dType": "string","init":'{"Button":[0,"-99","HMIP-BUTTON"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":'',
		"triggerLastSensorChange":"UNREACH",
		"props":{
			"displayS":"online",
			"enable-Button":True,
			"SupportsStatusRequest":False,
			"SupportsOnState":  True
		}
	},


	"HMIP-MP3P":{
		"states":{
			"UNREACH":k_UNREACH,
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"1"}),
			"childInfo":{"dType": "string","init":'{"Dimmer-C":[0,"5","HMIP-Dimmer-C"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
			"states":{"Dimm":"LEVEL"}, "channels":{"Dimm":["2","3","4"],"OnOff":["2","3","4"]}, "mult":{"Dimm":0.01}
		},
		"deviceXML":'',
		"triggerLastSensorChange":"LEVEL",
		"props":{
			"SupportsStatusRequest":False,
			"enable-Dimmer-C":True
		}
	},

	"HMIP-DLD":{
		"states":{
			"UNREACH":k_UNREACHP,
			"ACTIVITY_STATE":{"dType":"string","intToState":True,"channelNumber":"1",		"refresh":"1"},
			"LOCK_STATE":{"dType":"string","intToState":True,"channelNumber":"1",			"refresh":"1"},
			"SECTION_STATUS":{"dType":"string","intToState":True,"channelNumber":"1",		"refresh":"3"},
			"WP_OPTIONS":{"dType":"string","intToState":True,"channelNumber":"1",			"refresh":"3"},
			"PROCESS":{"dType":"string","intToState":True,"channelNumber":"1",				"refresh":"3"},
			"SECTION":{"channelNumber": "1","dType": "integer",								"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"actionParams":{
			"states":{
				"OnOff":"LOCK_TARGET_LEVEL" # use this key to send command to homematic
			},
			"channels":{
				"OnOff":["1"]
			},
			"OnOffValues":{
				"On":"1",
				"Off":"2"
			}
		},
		"deviceXML":
				'<ConfigUI>'+ 
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="4.6" > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="3.3" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"LOCK_STATE",
		"props":{
			"operatingVoltage100":"4.6",
			"operatingVoltage0":"3.3",
			"SupportsBatteryLevel":True,
			"displayStateId":"LOCK_STATE",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},

	"HMIP-FALMOT":{
		"states":{
			"UNREACH":k_UNREACHP,
			"DUTY_CYCLE":{"dType": "booltruefalse","channelNumber":"-99",					"refresh":"3"},
			"HEATING_COOLING":{"dType": "integer","channelNumber":"-99",					"refresh":"3"},
			"HUMIDITY_ALARM":{"dType": "booltruefalse","channelNumber":"-99",				"refresh":"3"},
			"TEMPERATURE_LIMITER":{"dType": "booltruefalse","channelNumber":"-99",			"refresh":"3"},
			"childInfo":{"dType": "string","init":'{"1":[0,"1","HMIP-LEVEL"], "2":[0,"2","HMIP-LEVEL"], "3":[0,"3","HMIP-LEVEL"],  "4":[0,"4","HMIP-LEVEL"],  "5":[0,"5","HMIP-LEVEL"],  "6":[0,"6","HMIP-LEVEL"], "7":[0,"7","HMIP-LEVEL"], "8":[0,"8","HMIP-LEVEL"], "9":[0,"9","HMIP-LEVEL"], "10":[0,"10","HMIP-LEVEL"], "11":[0,"11","HMIP-LEVEL"], "12":[0,"12","HMIP-LEVEL"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field	 id="displayS" type="menu" defaultValue="enabledChannels" hidden="yes">'+
					'<List>'+
						'<Option value="enabledChannels"	>enabledChannels</Option>'+
					'</List>'+
				'</Field>'+
				'<Field  id="numberOfPhysicalChannels" type="menu"  defaultValue="12">'+
					'<Label>how many channel are present</Label>'+
					'<List>'+
						'<Option value="4" >4 </Option>'+
						'<Option value="6" >6 </Option>'+
						'<Option value="8" >8 </Option>'+
						'<Option value="10">10 </Option>'+
						'<Option value="12">12 </Option>'+
					'</List>'+
				'</Field>'+
				'<Field id="enable-1"  type="checkbox" defaultValue="true"   visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="4,6,8,10,12" >  <Label>Is Channel 1 Active? </Label></Field>'+
				'<Field id="enable-2"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="4,6,8,10,12" >  <Label>Is Channel 2 Active? </Label></Field>'+
				'<Field id="enable-3"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="4,6,8,10,12" >  <Label>Is Channel 3 Active? </Label></Field>'+
				'<Field id="enable-4"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="4,6,8,10,12" >  <Label>Is Channel 4 Active? </Label></Field>'+
				'<Field id="enable-5"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="6,8,10,12" >  <Label>Is Channel 5 Active? </Label></Field>'+
				'<Field id="enable-6"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="6,8,10,12" >  <Label>Is Channel 6 Active? </Label></Field>'+
				'<Field id="enable-7"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="8,10,12" >  <Label>Is Channel 7 Active? </Label></Field>'+
				'<Field id="enable-8"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="8,10,12" >  <Label>Is Channel 8 Active? </Label></Field>'+
				'<Field id="enable-9"  type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="10,12" >  <Label>Is Channel 9 Active? </Label></Field>'+
				'<Field id="enable-10" type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="10,12" > <Label>Is Channel 10 Active? </Label></Field>'+
				'<Field id="enable-11" type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="12" > <Label>Is Channel 11 Active? </Label></Field>'+
				'<Field id="enable-12" type="checkbox" defaultValue="false"  visibleBindingId="numberOfPhysicalChannels" visibleBindingValue="12" > <Label>Is Channel 12 Active? </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"numberOfPhysicalChannels": 12,
			"displayS":"enabledChildren",
			"enable-1": True,
			"enable-2": False,
			"enable-3": False,
			"enable-4": False,
			"enable-5": False,
			"enable-6": False,
			"enable-7": False,
			"enable-8": False,
			"enable-9": False,
			"enable-10": False,
			"enable-11": False,
			"enable-12": False,
			"isEnabledChannelDevice":True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState": False
		}
	},

	"HMIP-HEATING":{
		"states":{
			"ACTUAL_TEMPERATURE": 		mergeDicts(k_Temperature,{"indigoState":"temperatureInput1","channelNumber":"1"}),
			"SET_POINT_TEMPERATURE":	mergeDicts(k_Temperature,{"indigoState":"setpointHeat","channelNumber":"-99"}),
			"HUMIDITY":					mergeDicts(k_Humidity,{"indigoState":"humidityInput1"}),
			"SWITCH_POINT_OCCURED":{"dType": "booltruefalse","channelNumber":"-99",					"refresh":"3"},
			"FROST_PROTECTION":{"dType": "booltruefalse","channelNumber":"-99",						"refresh":"3"},
			"PARTY_MODE":{"dType": "booltruefalse","channelNumber":"-99",							"refresh":"3"},
			"BOOST_MODE":{"dType": "booltruefalse","channelNumber":"-99",							"refresh":"3"},
			"QUICK_VETO_TIME":{"dType": "real","channelNumber":"-99",								"refresh":"3"},
			"BOOST_TIME":{"dType": "real","channelNumber":"-99",									"refresh":"3"},
			"SET_POINT_MODE":{"dType": "string","channelNumber":"1","intToState":True,				"refresh":"3"},
			"ACTIVE_PROFILE":{"dType": "integer","channelNumber":"1",								"refresh":"3"},
			"VALVE_ADAPTION":{"dType": "booltruefalse","channelNumber":"1",							"refresh":"3"},
			"WINDOW_STATE":{"dType": "integer","channelNumber":"1","intToState":True,				"refresh":"1"},
			"childInfo":{"dType": "string","init":'{"Dimmer-V":[0,"1","HMIP-Dimmer-V"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
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
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"temperatureInput1,setpointHeat",
		"props":{
			"enable-Dimmer-V":True,
			"enable-Humidity":True,
			"SupportsStatusRequest":False,
			"SupportsHvacFanMode": False,
			"SupportsHvacOperationMode": False,
			"SupportsCoolSetpoint": False,
			"ShowCoolHeatEquipmentStateUI": False,
			"SupportsHeatSetpoint": True,
			"NumHumidityInputs": 1,
			"NumTemperatureInputs": 1,
			"SupportsSensorValue":True,
			"SupportsOnState": True,
			"heatIsOn":True
		}
	},
	"HMIP-ETRV":{
		"states":{
			"UNREACH":k_UNREACHP,
			"ACTUAL_TEMPERATURE": 		mergeDicts(k_Temperature,{"indigoState":"temperatureInput1","channelNumber":"1"}),
			"SET_POINT_TEMPERATURE":	mergeDicts(k_Temperature,{"indigoState":"setpointHeat","channelNumber":"-99"}),
			"SET_POINT_MODE":{"dType": "string","channelNumber":"1","intToState":True,"indigoState":"SET_POINT_MODE",		"refresh":"3"},
			"WINDOW_STATE":{"dType": "string","intToState":True,															"refresh":"3"},
			"SWITCH_POINT_OCCURED":{"dType": "booltruefalse",																"refresh":"3"},
			"FROST_PROTECTION":{"dType": "booltruefalse",																	"refresh":"3"},
			"ACTIVE_PROFILE":{"dType": "integer","channelNumber":"1",														"refresh":"3"},
			"PARTY_MODE":{"dType": "booltruefalse",																			"refresh":"3"},
			"BOOST_MODE":{"dType": "booltruefalse",																			"refresh":"3"},
			"QUICK_VETO_TIME":{"dType": "real",																				"refresh":"3"},
			"BOOST_TIME":{"dType": "real",																					"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"},
			"childInfo":{"dType": "string","init":'{"Dimmer-V":[0,"1","HMIP-Dimmer-V"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
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
		"deviceXML":
				'<ConfigUI>'+ 
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="3.0 > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="2.2" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"temperatureInput1,setpointHeat",
		"props":{
			"operatingVoltage100":"3.0",
			"operatingVoltage0":"2.2",
			"SupportsBatteryLevel":True,
			"enable-Dimmer-V":True,
			"SupportsStatusRequest":False,
			"SupportsHvacFanMode": False,
			"SupportsHvacOperationMode": False,
			"SupportsCoolSetpoint": False,
			"ShowCoolHeatEquipmentStateUI": False,
			"SupportsHeatSetpoint": True,
			"NumHumidityInputs": 0,
			"NumTemperatureInputs": 1,
			"SupportsSensorValue":True,
			"SupportsOnState": True,
			"heatIsOn":True
		}
	},


	"HMIP-STHO":{
		"states":{
			"UNREACH":k_UNREACHP,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"1"}),
			"enabledChildren":{"dType": "string"},
			"childInfo":{"dType": "string","init":'{ "Humidity":[0,"1","HMIP-Humidity"]}'}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-Humidity" type="checkbox" defaultValue="true" > <Label>create Humidity device </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"Temperature",
			"enable-Humidity": True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
	},


	"HMIP-SRD":{
		"states":{
			"UNREACH":k_UNREACHP,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"RAINING":{"dType": "booltruefalse",										"refresh":"3"},
			"ERROR_CODE":{"dType": "string","intToState":True,"channelNumber":"-99",	"refresh":"3"},
			"lastEventOn":{"dType": "string"},
			"lastEventOff":{"dType": "string"},
			"HEATER_STATE":{"dType": "booltruefalse",									"refresh":"3"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"RAINING",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},
	"HMIP-PDT":{
		"states":{
			"UNREACH":k_UNREACHP,
			"LEVEL":k_DimmerMap,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"}
		},
		"actionParams":{
			"states":{
				"Dimm":"LEVEL" # use this key to send command to homematic
			},
			"channels":{
				"Dimm":["3","4","5"], # send to channels
				"OnOff":["3","4","5"]
			},
			"mult":{"Dimm":0.01}
		},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"LEVEL",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
	},

	"HMIP-PDT3":{
		"states":{
			"UNREACH":k_UNREACH,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",	"			refresh":2},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"childInfo":{"dType": "string","init":'{"1":[0,"4","HMIP-Dimmer"], "2":[0,"8","HMIP-Dimmer"],"3":[0,"12","HMIP-Dimmer"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-1" type="checkbox" defaultValue="true" >   <Label>Enable 1. dimmer </Label></Field>'+
				'<Field id="enable-2" type="checkbox" defaultValue="false" >  <Label>Enable 2. dimmer </Label></Field>'+
				'<Field id="enable-3" type="checkbox" defaultValue="false" >  <Label>Enable 3. dimmer </Label></Field>'+
			'</ConfigUI>',
		"props":{
			"displayS":"online",
			"enable-1": True,
			"enable-2": False,
			"enable-3": False,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"ELV-SH-TACO":{
		"states":{
			"UNREACH":k_UNREACH,
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",	"refresh":"3"},
			"childInfo":{"dType": "string","init":'{"1":[0,"1","HMIP-Temperature"], "2":[0,"2","HMIP-Direction"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-1" type="checkbox" defaultValue="true" >   <Label>Enable Temperature Sensor</Label></Field>'+
				'<Field id="enable-2" type="checkbox" defaultValue="false" >  <Label>Enable Direction Sensor </Label></Field>'+
			'</ConfigUI>',
		"props":{
			"displayS":"online",
			"enable-1": True,
			"enable-2": True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-PDT4":{
		"states":{
			"UNREACH":k_UNREACH,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"childInfo":{"dType": "string","init":'{"1":[0,"9","HMIP-Dimmer"], "2":[0,"13","HMIP-Dimmer"],"3":[0,"17","HMIP-Dimmer"],"4":[0,"21","HMIP-Dimmer"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-1" type="checkbox" defaultValue="true" >   <Label>Enable 1. dimmer </Label></Field>'+
				'<Field id="enable-2" type="checkbox" defaultValue="false" >  <Label>Enable 2. dimmer </Label></Field>'+
				'<Field id="enable-3" type="checkbox" defaultValue="false" >  <Label>Enable 3. dimmer </Label></Field>'+
				'<Field id="enable-4" type="checkbox" defaultValue="false" >  <Label>Enable 4. dimmer </Label></Field>'+
			'</ConfigUI>',
		"props":{
			"displayS":"online",
			"enable-1": True,
			"enable-2": False,
			"enable-3": False,
			"enable-4": False,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},



	"HMIP-ASIR":{
		"states":{
			"UNREACH":k_UNREACH,
			"SABOTAGE":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"2"},
			"channelNumber":{"dType": "string","init":"3"},
			"childInfo":{"dType": "string","init":'{"BUTTON":[0,  "3","HMIP-BUTTON"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-BUTTON" type="checkbox" defaultValue="true" >   <Label>enable Button device</Label></Field>'+
				'<Field id="show" type="label">'+
				'  <Label>'+
				'   for the alarm action to work you need to (a) create a system variable on homematic'+
				'       (b) add a program with a trigger on change of above variable and under  "sonst" add a script, see menu help '+
				'      then in menu or action you can carte an action that will trigger the optical or acustical output.'+
				'  </Label>'+
			'</ConfigUI>',
		"props":{
			"displayS":"online",
			"enable-BUTTON":True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},



	"ELV-SH-WSC":{
		"states":{
			"UNREACH":k_UNREACHP,
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"3"}),
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"0"}),
			"ERROR_CODE":{"channelNumber": "0","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"channelNumber":{"dType": "string","init":"3"},
			"childInfo":{"dType": "string","init":'{"BUTTON":[0,"-99","HMIP-BUTTON"],"DIMMER":[0,"7","HMIP-Dimmer"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
			"states":{
				"Dimm":"LEVEL" # use this key to send command to homematic
			},
			"channels":{
					"Dimm":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3'], 
					"OnOff":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3']
			},
			"mult":{"Dimm":0.01}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-BUTTON" type="checkbox" defaultValue="true" >   <Label>enable Button device</Label></Field>'+
				'<Field id="enable-DIMMER" type="checkbox" defaultValue="true" >   <Label>enable 2. Servo device</Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"LEVEL",
		"props":{
			"enable-BUTTON":True,
			"enable-DIMMER":True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": True
		}
	},

	"HMIP-ROLL":{
		"states":{
			"UNREACH":k_UNREACHP,
			"LEVEL":mergeDicts(k_DimmerMap,{"channelNumber":"3"}),
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"0"}),
			"ERROR_CODE":{"channelNumber": "0","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"channelNumber":{"dType": "string","init":"3"},
			"childInfo":{"dType": "string","init":'{"BUTTON":[0,"-99","HMIP-BUTTON"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{
			"states":{
				"Dimm":"LEVEL" # use this key to send command to homematic
			},
			"channels":{
					"Dimm":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3'], 
					"OnOff":['int(dev.states["channelNumber"])+1', 'int(dev.states["channelNumber"])+2','int(dev.states["channelNumber"])+3']
			},
			"mult":{"Dimm":0.01}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-BUTTON" type="checkbox" defaultValue="true" >   <Label>enable Button device</Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"LEVEL",
		"props":{
			"enable-BUTTON": True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": True
		}
	},


	"HMIP-SRH":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE": {"channelNumber": "1","dType":"string", "intToState":True,"indigoState":"WINDOW_STATE",	"refresh":"1"},
			"SABOTAGE":{"channelNumber": "0","dType": "booltruefalse",											"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"actionParams":{
		},
		"deviceXML":
				'<ConfigUI>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="1.5" > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="1.1" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"WINDOW_STATE",
		"props":{
			"operatingVoltage100":"1.5",
			"operatingVoltage0":"1.1",
			"SupportsBatteryLevel":True,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": False,
			"displayStateId":"WINDOW_STATE"
		}
	},

	"HMIP-PS":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE": k_RelayMap,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"}
		},
		"actionParams":{
			"states":{
				"OnOff":"STATE",
			},
			"channels":{
				"OnOff":["3","4","5"]
			}
		},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"STATE",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-PS2":{
		"states":{
			"UNREACH":k_UNREACH,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"childInfo":{"dType": "string","init":'{"1":[0,"3","HMIP-Relay"],"2":[0,"7","HMIP-Relay"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-1" type="checkbox" defaultValue="true" >   <Label>Enable 1. relay </Label></Field>'+
				'<Field id="enable-2" type="checkbox" defaultValue="false" >  <Label>Enable 2. relay </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"online",
			"enable-1": True,
			"enable-2": False,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},


	"HMIP-PS4":{
		"states":{
			"UNREACH":k_UNREACH,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0","dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"childInfo":{"dType": "string","init":'{"1":[0,"5","HMIP-Relay"],"2":[0,"9","HMIP-Relay"],"3":[0,"13","HMIP-Relay"],"4":[0,"17","HMIP-Relay"]}'},
			"enabledChildren":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="enable-1" type="checkbox" defaultValue="true" >   <Label>Enable 1. relay </Label></Field>'+
				'<Field id="enable-2" type="checkbox" defaultValue="false" >  <Label>Enable 2. relay </Label></Field>'+
				'<Field id="enable-3" type="checkbox" defaultValue="false" >  <Label>Enable 3. relay </Label></Field>'+
				'<Field id="enable-4" type="checkbox" defaultValue="false" >  <Label>Enable 4. relay </Label></Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"online",
			"enable-1": True,
			"enable-2": False,
			"enable-3": False,
			"enable-4": False,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},


	"HMIP-PSM":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE":k_RelayMap,
			"ACTUAL_TEMPERATURE":mergeDicts(k_Temperature,{"channelNumber":"-99"}),
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",				"refresh":"3"},
			"ERROR_OVERHEAT":{"channelNumber": "0", "dType": "booltruefalse",		"refresh":"3"},
			"ERROR_OVERLOAD":{"channelNumber": "0", "dType": "booltruefalse",		"refresh":"3"},
			"ERROR_POWER_FAILURE":{"channelNumber": "0","dType": "booltruefalse",	"refresh":"3"},
			"FREQUENCY":mergeDicts(k_Frequency,{"channelNumber":"6"}),
			"CURRENT":mergeDicts(k_Current,{"channelNumber":"6"}),
			"POWER":mergeDicts(k_Power,{"channelNumber":"6"}),
			"VOLTAGE":mergeDicts(k_Voltage,{"channelNumber":"6"}),
			"ENERGY_COUNTER":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"],				"refresh":"3"},
			k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Reset":{"dType": "string"},
			"at0":{"dType": "string","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_At0"},
			"Day-7":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Day-7"},
			"Day-6":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Day-6"},
			"Day-5":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Day-5"},
			"Day-4":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Day-4"},
			"Day-3":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Day-3"},
			"Day-2":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Day-2"},
			"Day-1":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Yesterday"},
			"Day-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Today"},
			"Week-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_ThisWeek"},
			"Week-1":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Week-1"},
			"Week-2":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Week-2"},
			"Week-3":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Week-3"},
			"Week-4":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_Week-4"},
			"Month-0":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_ThisMonth"},
			"Month-1" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["1"]},
			"Month-2" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["2"]},
			"Month-3" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["3"]},
			"Month-4" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["4"]},
			"Month-5" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["5"]},
			"Month-6" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["6"]},
			"Month-7" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["7"]},
			"Month-8" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["8"]},
			"Month-9" :{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["9"]},
			"Month-10":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["10"]},
			"Month-11":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["11"]},
			"Month-12":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_"+k_mapMonthNumberToMonthName["12"]},
			"Year":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_ThisYear"},
			"LastYear":{"dType": "real","indigoState":k_deviceWithDayWeekMonth["HMIP-PSM"]["indigoState"]+"_LastYear"}
		},
		"actionParams":{
			"states":{
				"OnOff":"STATE",
			},
			"channels":{
				"OnOff":["3","4","5"]
			}
		},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"STATE",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-WTH":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE":mergeDicts(k_RelayMap,{"channelNumber":"1"}),
			"ACTUAL_TEMPERATURE": 		mergeDicts(k_Temperature,{"indigoState":"temperatureInput1"}),
			"SET_POINT_TEMPERATURE":	mergeDicts(k_Temperature,{"indigoState":"setpointHeat"}),
			"HUMIDITY":					mergeDicts(k_Humidity,{"indigoState":"humidityInput1"}),
			"SET_POINT_MODE":{"dType": "string","intToState":True,						"refresh":"3"},
			"WINDOW_STATE":{"dType": "string","intToState":True,						"refresh":"3"},
			"SWITCH_POINT_OCCURED":{"dType": "booltruefalse",							"refresh":"3"},
			"FROST_PROTECTION":{"dType": "booltruefalse",								"refresh":"3"},
			"PARTY_MODE":{"dType": "booltruefalse",										"refresh":"3"},
			"BOOST_MODE":{"dType": "booltruefalse",										"refresh":"3"},
			"QUICK_VETO_TIME":{"dType": "real",											"refresh":"3"},
			"BOOST_TIME":{"dType": "real",												"refresh":"3"},
			"HEATING_COOLING":{"dType": "string","intToState":True,						"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"actionParams":{
			"states":{
				"SET_POINT_TEMPERATURE":"SET_POINT_TEMPERATURE",
				"BOOST_MODE":"BOOST_MODE"
			},
			"channels":{
				"SET_POINT_TEMPERATURE":["1"],
				"BOOST_MODE":["1"]
			}
		},
		"deviceXML":
				'<ConfigUI>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="3.0 > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="2.2" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"temperatureInput1,setpointHeat",
		"props":{
			"operatingVoltage100":"3.0",
			"operatingVoltage0":"2.2",
			"SupportsBatteryLevel":True,
			"SupportsStatusRequest":False,
			"SupportsHvacFanMode": False,
			"SupportsHvacOperationMode": False,
			"SupportsCoolSetpoint": False,
			"ShowCoolHeatEquipmentStateUI": False,
			"NumHumidityInputs": 1,
			"NumTemperatureInputs": 1,
			"SupportsSensorValue": True,
			"heatIsOn":True,
			"SupportsOnState":  False
		}
	},

	"HMIP-SPI":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE":mergeDicts(k_RelayMap,{"channelNumber":"1"}),
			"ILLUMINATION":k_Illumination,
			"ILLUMINATION_STATUS":{"dType": "string","intToState":True,								"refresh":"3"},
			"CURRENT_ILLUMINATION":mergeDicts(k_Illumination,{"indigoState":"CURRENT_ILLUMINATION"}),
			"CURRENT_ILLUMINATION_STATUS":{"dType": "string","intToState":True,						"refresh":"3"},
			"PRESENCE_DETECTION_STATE":{"dType": "booltruefalse",									"refresh":"3"},
			"PRESENCE_DETECTION_ACTIVE":{"dType": "booltruefalse",									"refresh":"3"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayS":"PRESENCE_DETECTION_STATE",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	},

	"HMIP-SMI":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE":mergeDicts(k_RelayMap,{"channelNumber":"1"}),
			"ILLUMINATION":k_Illumination,
			"ILLUMINATION_STATUS":{"dType": "string","intToState":True,					"refresh":"3"},
			"CURRENT_ILLUMINATION":mergeDicts(k_Illumination,{"indigoState":"CURRENT_ILLUMINATION"}),
			"CURRENT_ILLUMINATION_STATUS":{"dType": "string","intToState":True,			"refresh":"3"},
			"MOTION":{"dType": "booltruefalse",											"refresh":"1"},
			"MOTION_DETECTION_ACTIVE":{"dType": "booltruefalse",						"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
				'<ConfigUI>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="3.0 > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="2.2" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"MOTION",
		"props":{
			"operatingVoltage100":"3.0",
			"operatingVoltage0":"2.2",
			"displayS":"MOTION",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState": True
		}
	},


	"HMIP-SAM":{
		"states":{
			"UNREACH":k_UNREACHP,
			"MOTION":{"dType": "booltruefalse"},
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"MOTION",
		"props":{
			"displayS":"MOTION",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState": True
		}
	},


	"HMIP-SWDM":{
		"states":{
			"UNREACH":k_UNREACHP,
			"STATE":{"dType": "string","intToState":True,"channelNumber":"1",						"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"actionParams":{
			"states":{
				"OnOff":"OnOff",
			},
			"channels":{
				"OnOff":["1"]
			}
		},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="invertState" type="menu"  defaultValue="no" tooltip="pick one">'+
					'<Label>Invert state on to off and vs versa</Label>'+
					'<List>'+
						'<Option value="yes"  >invert state</Option>'+
						'<Option value="no"   >keep as is	</Option>'+
					'</List>'+
				'</Field>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="1.5" > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="1.1" > <Label>set Battery Volt at 0%</Label> </Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"STATE",
		"props":{
			"operatingVoltage100":"1.5",
			"operatingVoltage0":"1.1",
			"SupportsBatteryLevel":True,
			"displayS":"ALARMSTATE",
			"displayS":"STATE",
			"invertState":"no",
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-SWD":{
		"states":{
			"UNREACH":k_UNREACHP,
			"ALARMSTATE":{"dType": "string","intToState":True,"channelNumber":"1",				"refresh":"1"},
			"MOISTURE_DETECTED":{"dType": "booltruefalse","channelNumber":"1",					"refresh":"1"},
			"WATERLEVEL_DETECTED":{"dType": "booltruefalse","channelNumber":"1",				"refresh":"1"},
			"ERROR_NON_FLAT_POSITIONING":{"dType": "booltruefalse","channelNumber":"0",			"refresh":"1"},
			"ERROR_CODE":{"channelNumber": "0","dType": "integer",								"refresh":"3"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":
				'<ConfigUI>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="3.0 > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="2.2" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"ALARMSTATE,WATERLEVEL_DETECTED",
		"props":{
			"operatingVoltage100":"3.0",
			"operatingVoltage0":"2.2",
			"SupportsBatteryLevel":True,
			"displayS":"ALARMSTATE",
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},
	"HMIP-SWSD":{
		"states":{
			"UNREACH":k_UNREACHP,
			"SMOKE_DETECTOR_ALARM_STATUS":{"dType": "string","intToState":True,"channelNumber":"1",	"refresh":"3"},
			"MOISTURE_DETECTED":{"dType": "booltruefalse","channelNumber":"1",						"refresh":"1"},
			"WATERLEVEL_DETECTED":{"dType": "booltruefalse","channelNumber":"1",					"refresh":"1"},
			"ERROR_NON_FLAT_POSITIONING":{"dType": "booltruefalse","channelNumber":"0",				"refresh":"1"},
			"ERROR_CODE":{"channelNumber": "-99","dType": "integer",								"refresh":"3"}
		},
		"actionParams":{
			"states":{
				"OnOff":"SMOKE_DETECTOR_COMMAND", # use this key to send command to homematic
				#"OnOff":"SMOKE_DETECTOR_EVENT", # use this key to send command to homematic  check
			},
			"channels":{
				"OnOff":["1"]
			},
			"OnOffValues":{
				"On":"2",
				"Off":"1"
			}
		},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayStateId":"SMOKE_DETECTOR_ALARM_STATUS",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  False
		}
	},

	"HMIP-SPDR":{
		"states":{
			"UNREACH":k_UNREACHP,
			"displayStatus":{"dType":"string"},
			"pCV-l":{"dType": "integer", "indigoState":"PASSAGE_COUNTER_VALUE-left"},
			"pCV-r":{"dType": "integer", "indigoState":"PASSAGE_COUNTER_VALUE-right"},
			"pT-l":{"dType": "string",   "indigoState":"PREVIOUS_PASSAGE-left"},
			"pT-r":{"dType": "string",   "indigoState":"PREVIOUS_PASSAGE-right"},
			"dir": {"dType": "string",   "indigoState":"direction"},
			"lT-l":{"dType": "string",   "indigoState":"LAST_PASSAGE-left"},
			"lT-r":{"dType": "string",   "indigoState":"LAST_PASSAGE-right"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"noIndigoState":{"PASSAGE_COUNTER_VALUE":{"refresh":"1"}},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="useWhatForDirection" type="menu"  defaultValue="left-right" tooltip="pick one">'+
					'<Label>Use what string for state direction:</Label>'+
					'<List>'+
						'<Option value="left-right"  >left - right</Option>'+
						'<Option value="in-out"  >in - out</Option>'+
						'<Option value="out-in"  >out - in</Option>'+
					'</List>'+
				'</Field>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="3.0 > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="2.2" > <Label>set Battery Volt at 0%</Label> </Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"operatingVoltage100":"3.0",
			"operatingVoltage0":"2.2",
			"SupportsBatteryLevel":True,
			"useWhatForDirection":"left-right",
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-WKP":{
		"states":{
			"UNREACH":k_UNREACHP,
			"lastValuesText":{"dType":"string"},
			"user":{"dType":"string"},
			"userTime":{"dType":"string"},
			"userPrevious":{"dType":"string"},
			"userTimePrevious":{"dType":"string"},
			"ua":{"dType":"string",	"indigoState":"USER_AUTHORIZATION"		},
			"SABOTAGE_STICKY":{"dType": "booltruefalse","channelNumber":"0",		"refresh":"3"},
			"SABOTAGE":{"dType": "booltruefalse","channelNumber":"0",				"refresh":"3"},
			"BLOCKED_TEMPORARY":{"dType": "booltruefalse","channelNumber":"0",		"refresh":"3"},
			"CODE_STATE":{"dType": "string","intToState":True,"channelNumber":"0",	"refresh":"1"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"noIndigoState":k_keyPressStates,
		"actionParams":{},
		"deviceXML":
				'<ConfigUI>'+
				'<Field id="operatingVoltage100" type="textfield"  defaultValue="3.0 > <Label>set Battery Volt at 100%</Label> </Field>'+
				'<Field id="operatingVoltage0" type="textfield"  defaultValue="2.2" > <Label>set Battery Volt at 0%</Label> </Field>'+
				'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"operatingVoltage100":"3.0",
			"operatingVoltage0":"2.2",
			"SupportsBatteryLevel":True,
			"NumberOfUsersMax": 8,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},


	"HMIP-BUTTON":{
		"states":{
			"UNREACH":k_UNREACHP,
			"buttonPressed":{"dType":"string","channelNumber":"-99"},
			"buttonPressedTime":{"dType":"string","channelNumber":"-99"},
			"buttonPressedType":{"dType":"string","channelNumber":"-99"},
			"buttonPressedPrevious":{"dType":"string","channelNumber":"-99"},
			"buttonPressedTimePrevious":{"dType":"string","channelNumber":"-99"},
			"buttonPressedTypePrevious":{"dType":"string","channelNumber":"-99"},
			"lastValuesText":{"dType":"string","channelNumber":"-99"},
			"childInfo":{"dType": "string", "init":'{"1":[0,"1","HMIP-OnOff"], "2":[0,"2","HMIP-OnOff"], "3":[0,"3","HMIP-OnOff"],  "4":[0,"4","HMIP-OnOff"],  "5":[0,"5","HMIP-OnOff"],  "6":[0,"6","HMIP-OnOff"], "7":[0,"7","HMIP-OnOff"], "8":[0,"8","HMIP-OnOff"]}'},
			"enabledChildren":{"dType": "string"},
			"batteryLevel":{"dType": "integer"},
			"lastBatteryReplaced":{"dType": "string"}
		},
		"noIndigoState":k_buttonPressStates,
		"actionParams":{},
		"deviceXML":
		'<ConfigUI>'+
			'<Field id="enableOnOff" type="checkbox" defaultValue="false" >  														 <Label>Enable on option</Label></Field>'+
			'<Field id="enable-1" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 1 as on off channel</Label></Field>'+
			'<Field id="enable-2" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 2 as on off channel</Label></Field>'+
			'<Field id="enable-3" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 3 as on off channel</Label></Field>'+
			'<Field id="enable-4" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 4 as on off channel</Label></Field>'+
			'<Field id="enable-5" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 5 as on off channel</Label></Field>'+
			'<Field id="enable-6" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 6 as on off channel</Label></Field>'+
			'<Field id="enable-7" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 7 as on off channel</Label></Field>'+
			'<Field id="enable-8" type="checkbox" defaultValue="false" visibleBindingId="enableOnOff" visibleBindingValue="true" >  <Label>Enable channel 7 as on off channel</Label></Field>'+
			'<Field id="operatingVoltage100" type="textfield"  defaultValue="1.5" > <Label>set Battery Volt at 100%</Label> </Field>'+
			'<Field id="operatingVoltage0" type="textfield"  defaultValue="1.1" > <Label>set Battery Volt at 0%</Label> </Field>'+
		'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"operatingVoltage100":"1.5",
			"operatingVoltage0":"1.1",
			"SupportsBatteryLevel":True,
			"enableOnOff": False,
			"enable-1": False,
			"enable-2": False,
			"enable-3": False,
			"enable-4": False,
			"enable-5": False,
			"enable-6": False,
			"enable-7": False,
			"enable-8": False,
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-ROOM":{
		"states":{
			"roomListNames":{"dType": "string"},
			"NumberOfDevices":{"dType": "integer"},
			"roomListIDs":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
	},

	"HMIP-SYSVAR-FLOAT":{
		"states":{
			"description":{"dType": "string"},
			"unit":{"dType": "string"},
			"sensorValue":{"dType": "real"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":True,
			"SupportsOnState": False
		}
	},

	"HMIP-SYSVAR-STRING":{
		"states":{
			"description":{"dType": "string"},
			"value":{"dType": "string"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"displayStateId":"value",
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": False
		}
	},

	"HMIP-SYSVAR-BOOL":{
		"states":{
			"description":{"dType": "string"},
			"onOffState":{"dType": "booltruefalse"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"HMIP-SYSVAR-ALARM":{
		"states":{
			"description":{"dType": "string"},
			"onOffState":{"dType": "booltruefalse"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue":False,
			"SupportsOnState": True
		}
	},

	"Homematic-AP":{
		"states":{
			"CARRIER_SENSE_LEVEL":{"dType": "integer","channelNumber":"0","format":"{}%",		"refresh":"3"},
			"DUTY_CYCLE_LEVEL":{"dType": "real","channelNumber":"0","format":"{:.1f}%",			"refresh":"3"}
		},
		"actionParams":{},
		"deviceXML":'<ConfigUI> <Field id="show" type="label"> <Label>Nothing to configure</Label> </Field></ConfigUI>',
		"triggerLastSensorChange":"CARRIER_SENSE_LEVEL,DUTY_CYCLE_LEVEL",
		"props":{
			"displayS":"DUTY_CYCLE_LEVEL",
			"SupportsStatusRequest":False,
			"SupportsSensorValue": True,
			"SupportsOnState":  False
		}
	},

	"Homematic-Host":{
		"states":{
			"buttonPressed":{"dType": "integer"},
			"numberOfRooms":{"dType": "integer"},
			"numberOfDevices":{"dType": "integer"},
			"numberOfVariables":{"dType": "integer"}
		},
		"actionParams":{},
		"deviceXML":
			'<ConfigUI>'+
				'<Field id="SupportsStatusRequest" type="checkbox" defaultValue="False" hidden="true"></Field>'+
				'<Field id="SupportsSensorValue" type="checkbox" defaultValue="False" hidden="true"></Field>'+
				'<Field id="SupportsOnState" type="checkbox" defaultValue="true" hidden="true"></Field>'+
				'<Field id="ipNumber"  type="textfield"  >'+
				'<Label>overwrite ip Number if wanted</Label>'+
				'</Field>'+
				'<Field  id="portNumber"  type="textfield"  >'+
				'<Label>overwrite port Number if wanted</Label>'+
				'</Field>'+
			'</ConfigUI>',
		"triggerLastSensorChange":"",
		"props":{
			"SupportsStatusRequest":False,
			"SupportsSensorValue": False,
			"SupportsOnState":  True
		}
	}
}




# replace homematic state number values (0,1,2,3,4,5..) with these states eg = = "OK, 1 = "ERROR"  etc in indigo
k_stateValueNumbersToTextInIndigo ={
	"ERROR_COMMUNICATION_PARTICULATE_MATTER_SENSOR":[
		"ok", 
		"ERROR"
	],	
	"COLOR": [
		"off",
		"blue", 
		"green", 
		"turquoise",	
		"red", 
		"violet", 
		"yellow", 
		"white"
	],
	"ILLUMINATION_STATUS": [
		"NORMAL",  			# 0
		"UNKNOWN",  			# 1
		"OVERFLOW"  					# 2
	],
	"CODE_STATE":[
		"IDLE",
		"KNOWN_CODE_ID_RECEIVED",
		"UNKNOWN_CODE_ID_RECEIVED"
	],
	"RAIN_COUNTER_STATUS": [
		"NORMAL",  			# 0
		"UNKNOWN"  			# 1
	],
	"WIND_DIR_RANGE_STATUS": [
		"NORMAL",  			# 0
		"UNKNOWN",  			# 1
		"OVERFLOW" 					# 2
	],
	"WIND_DIR_STATUS":[
		"NORMAL",  			# 0
		"UNKNOWN"		# 1
	],
	"WIND_SPEED_STATUS":[
		"NORMAL",  			# 0
		"UNKNOWN",  			# 1
		"OVERFLOW"  					# 2
	],
	"SMOKE_DETECTOR_ALARM_STATUS":[
		"IDLE_OFF",  			# 0
		"PRIMARY_ALARM",  					# 1
		"INTRUSION_ALARM",  				# 2
		"SECONDARY_ALARM" 				# 3
	],
	"SMOKE_DETECTOR_TEST_RESULT":[
		"NONE",  			# 0
		"SMOKE_TEST_OK",  					# 1
		"COMMUNICATION_TEST_SENT",  				# 2
		"COMMUNICATION_TEST_OK" 				# 3
	],
	"ACTIVITY_STATE": [			#return state value =
		"UNKNOWN",  			# 0
		"UP",  					# 1
		"DOWN",  				# 2
		"STABLE" 				# 3
	],
	"LOCK_STATE": [			#return state value =
		"UNKNOWN",  			# 0
		"LOCKED",  					# 1
		"UNLOCKED"  				# 2
	],
#		"LOCK_TARGET_LEVEL": [			#return state value =
#			"LOCKED",  					# 0
#			"UNLOCKED"  				# 1
#			"OPEN"  				# 2
#		],
	"PROCESS": [			#return state value =
		"STABLE",  			# 0
		"NOT_STABLE"  					# 1
	],
	"SECTION_STATUS": [			#return state value =
		"ok",  					# 0
		"error/unknown" 		# 1
	],
	"WP_OPTIONS": [			#return state value =
		"NOP",  					# 0
		"ON", 		# 1
		"OFF" 		# 2
	],
	"ACTUAL_TEMPERATURE_STATUS": [			#return state value =
		"NORMAL",  			# 0
		"UNKNOWN",  			# 1
		"OVERFLOW",					# 2
		"UNDERFLOW" 					# 2
	],
	"HUMIDITY_STATUS": [			#return state value =
		"NORMAL",  			# 0
		"UNKNOWN",  			# 1
		"OVERFLOW",					# 2
		"UNDERFLOW" 					# 2
	],
	"FREQUENCY_STATUS": [			#return state value =
		"ok",  					# 0
		"error" 				# 1
	],
	"ACTUAL_VOLTGAGE_STATUS": [			#return state value =
		"ok",  					# 0
		"error" 				# 1
	],
	"OPERATING_VOLTAGE_STATUS": [			#return state value =
		"ok",  					# 0
		"error" 				# 1
	],
	"LEVEL_STATUS": [
		"ok",					# 0
		"error"					# 1
	],
	"POWER_STATUS": [
		"ok",					# 0
		"error"					# 1
	],
	"VOLTAGE_STATUS": [
		"ok",					# 0
		"error/Overflow"					# 1
		"error/Underflow"					# 1
	],
	"CURRENT_STATUS": [
		"ok",					# 0
		"error"					# 1
	],
	"CURRENT_ILLUMINATION_STATUS": [
		"ok",					# 0
		"error"					# 1
	],
	"SET_POINT_MODE": [
		"Automatic",			
		"Manual",
		"Urlaub"				
	],
	"HEATING_COOLING": [
		"heating",			
		"cooling"				
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
		"tilted",				# 0
		"open"					# 1
	],

}



#here we fill all default items and create the device state type dicts 
# all derived from lists and dicts above

## here some shortcuts
k_indigoDeviceisVariableDevice			= []
k_devTypeHasChildren 					= []
k_devsThatAreChildDevices 				= []
k_deviceTypesParentWithButtonPressChild	= []
k_deviceTypesParentWithOnOffChild		= []
k_indigoDeviceisDoorLockDevice			= []
k_indigoDeviceisThermostatDevice 		= []
k_indigoDeviceisDisplayDevice 			= ["HMIP-WRCD"]
k_logMessageAtCreation 					= {}
k_actionTypes 							= { "thermostat":[], "doorLock":[] ,"SYSVAR-STRING":[] ,"alarm":[],"display":[],"variable":[]}
k_createStates 							= {}

# add states and props if member of a category, saves a lot of lines above 
for devType in k_mapHomematicToIndigoDevTypeStateChannelProps:

	# just to make the next lines shorter
	dd =  k_mapHomematicToIndigoDevTypeStateChannelProps[devType]

	if devType not in k_createStates:
		k_createStates[devType] = {}

	if devType.find("SYSVAR") > -1:
			k_indigoDeviceisVariableDevice.append(devType)
	
	if devType in k_isVoltageDevice:
		if "OPERATING_VOLTAGE" not in dd["states"]:
			dd["states"]["OPERATING_VOLTAGE"] = {"channelNumber": "0","dType": "real","indigoState":"OperatingVoltage"}

	if "childInfo" in dd["states"]:
		if devType not in k_devTypeHasChildren:
			k_devTypeHasChildren.append(devType)

		if "init" in dd["states"]["childInfo"]:
			if dd["states"]["childInfo"]["init"].find("HMIP-BUTTON" ) > 0:
				if devType not in k_deviceTypesParentWithButtonPressChild:
					k_deviceTypesParentWithButtonPressChild.append(devType)

		if "init" in dd["states"]["childInfo"]:
			if dd["states"]["childInfo"]["init"].find("HMIP-OnOff" ) > 0:
				if devType not in k_deviceTypesParentWithOnOffChild:
					k_deviceTypesParentWithOnOffChild.append(devType)

	if "childOf" in dd["states"]:
		if devType not in k_devsThatAreChildDevices:
			k_devsThatAreChildDevices.append(devType)

	if devType in k_isBatteryDevice and "childOf" not in dd["states"]:
		if "LOW_BAT" not in dd["states"]:
			dd["states"]["LOW_BAT"] = {"channelNumber": "0","dType": "booltruefalse","indigoState":"LOW_BAT"}


	if "LOW_BAT" in dd["states"] and "batteryLevel" not in dd["states"] :
			dd["states"]["batteryLevel"] = {"dType": "integer"}
			dd["states"]["lastBatteryReplaced"] = {"dType": "string"}
			dd["props"]["SupportsBatteryLevel"] = True


	if "LOCK_STATE" in dd["states"]:
		if devType not in k_indigoDeviceisDoorLockDevice:
			k_indigoDeviceisDoorLockDevice.append(devType)




	if "SET_POINT_TEMPERATURE" in dd["states"]:
		if devType not in k_indigoDeviceisThermostatDevice:
			k_indigoDeviceisThermostatDevice.append(devType)



	if "enable-" in str(dd["props"]):
		k_logMessageAtCreation[devType] = "in DEVICE EDIT, please select active child devices"




	for homematicStateName in dd["states"]:
		if "indigoState" not in dd["states"][homematicStateName]:
			dd["states"][homematicStateName]["indigoState"] = homematicStateName

		state =  dd["states"][homematicStateName]["indigoState"]


		if state not in k_createStates[devType]:
			k_createStates[devType][state] =  dd["states"][homematicStateName]["dType"]

			if state in k_statesWithfillMinMax:
				dd["props"]["hasMinMaxOption"] = True
				if dd["deviceXML"].find("Nothing to configure") > -1:
					dd["deviceXML"] = "<ConfigUI> </ConfigUI>"
	
				ll = dd["deviceXML"].find("</ConfigUI>")
				temp = dd["deviceXML"][0:ll]

				if "minMaxEnable-"+state not in dd["props"]:
					newString  = temp + '<Field id="minMaxEnable-'+state+ '" type="checkbox"  defaultValue="false" >   <Label>Enable '+state+' min max states</Label></Field></ConfigUI>'
					dd["deviceXML"] = newString
					dd["props"]["minMaxEnable-"+state] = False

			if state in k_statesWithPreviousValue:
				if dd["deviceXML"].find("Nothing to configure") > -1:
					dd["deviceXML"] = "<ConfigUI> </ConfigUI>"
	
				ll = dd["deviceXML"].find("</ConfigUI>")
				temp = dd["deviceXML"][0:ll]

				if "previousValue-"+state not in dd["props"]:
					newString  = temp + '<Field id="previousValue-'+state+ '" type="checkbox"  defaultValue="false" >   <Label>Enable '+state+' previous value</Label></Field></ConfigUI>'
					dd["deviceXML"] = newString
					dd["props"]["previousValue-"+state] = False


		if state in k_doubleState:
			stateD = k_doubleState[state]
			if stateD not in k_createStates[devType]:
				k_createStates[devType][stateD] =  dd["states"][homematicStateName]["dType"]

			if stateD in k_statesWithfillMinMax:
				if dd["deviceXML"].find("Nothing to configure") > -1:
					dd["deviceXML"] = "<ConfigUI> </ConfigUI>"
	
				ll = dd["deviceXML"].find("</ConfigUI>")
				temp = dd["deviceXML"][0:ll]
				newString  = temp + '<Field id="minMaxEnable-'+stateD+ '" type="checkbox"  defaultValue="true" >   <Label>Enable '+stateD+' min max states</Label></Field></ConfigUI>'
				dd["deviceXML"] = newString
				dd["props"]["minMaxEnable-"+state] = False

		if state in k_statesWithOffsetInProperties:
				if dd["deviceXML"].find("Nothing to configure") > -1:
					dd["deviceXML"] = "<ConfigUI> </ConfigUI>"
	
				ll = dd["deviceXML"].find("</ConfigUI>")
				temp = dd["deviceXML"][0:ll]

				if "offset-"+state not in dd["props"]:
					newString  = temp + '<Field id="offset-'+state+ '" type="textfield"  defaultValue="0" >   <Label>offset '+state+'</Label></Field></ConfigUI>'
					dd["deviceXML"] = newString
					dd["props"]["offset-"+state ] = "0"
			


tType = "variable"
for devType in k_indigoDeviceisVariableDevice:
	if devType not in k_actionTypes[tType]:
			k_actionTypes[tType].append(devType)

tType = "display"
for devType in k_indigoDeviceisDisplayDevice:
	if devType not in k_actionTypes[tType]:
			k_actionTypes[tType].append(devType)

tType = "doorLock"
for devType in k_indigoDeviceisDoorLockDevice:
	if devType not in k_actionTypes[tType]:
			k_actionTypes[tType].append(devType)

tType = "thermostat"
for devType in k_indigoDeviceisThermostatDevice:
	if devType not in k_actionTypes[tType]:
		k_actionTypes[tType].append(devType)


k_devTypeIsAlarmDevice = [
	"HMIP-ASIR"
]

tType = "alarm"
for devType in k_devTypeIsAlarmDevice:
		k_actionTypes[tType].append(devType)

k_devTypeIsSTRINGvariable = [
	"HMIP-SYSVAR-STRING"
]

tType = "SYSVAR-STRING"
for devType in k_devTypeIsSTRINGvariable:
		k_actionTypes[tType].append(devType)

