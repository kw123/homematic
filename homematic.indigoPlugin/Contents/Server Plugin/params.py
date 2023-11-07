#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# homematic Plugin
# Developed by Karl Wachs
# karlwachs@me.com


k_statesThatAreTemperatures = [
	"temperatureInput1", "setpointHeat","ACTUAL_TEMPERATURE", "PARTY_SET_POINT_TEMPERATURE", "CONTROL_DIFFERENTIAL_TEMPERATURE", "SET_POINT_TEMPERATURE"
]

k_statesThatAreHumidity  = [
	"HUMIDITY"
]

k_statesThatAreWind = [
	"WIND_SPEED"
]

k_statesThatAreWindDir = [
	"WIND_DIR",
	"WIND_DIR_RANGE"
]

k_statesThatAreIlumination = [
	"ILLUMINATION"
]


k_statesToCreateisBatteryDevice = {
	"LOW_BAT":"booltruefalse",
}

k_statesToCreateisVoltageDevice = {
	"OPERATING_VOLTAGE":"real",
	"OPERATING_VOLTAGE_STATUS":"string"
}

k_statesToCreateisRealDevice = {
	"CONFIG_PENDING":"booltruefalse",
	"RSSI_DEVICE":"integer",
	"RSSI_PEER":"integer", 
	"UNREACH":"booltruefalse",
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


k_mapTheseVariablesToDevices = {
	"Rain": {
		"Counter":["RAIN_TOTAL", 1., "{value:.1f}{[mm]}"],
		"CounterToday":["RAIN_TODAY", 1., "{value:.1f}{[mm]}"],
		"CounterYesterday":["RAIN_YESTERDAY", 1., "{value:.1f}{[mm]}"],
	},
	"Sunshine":{
		"Counter":["SUNSHINE_DURATION_TOTAL", 1.,  "{value:.0f}{[min]}"],
		"CounterToday":["SUNSHINE_DURATION_TODAY", 1.,  "{value:.0f}{[min]}"],
		"CounterYesterday":["SUNSHINE_DURATION_YESTERDAY", 1., "{value:.0f}{[min]}"],
	},
	"Energy":{
		"Counter":["ENERGY_USED", 1.,  "{value:.1f}{[Wh]}"]
	}
}



k_duplicateStatesFromHomematicToIndigo = {  # all predefined states in indigo devices, just copy
	"HMIP-WTH":{
		"ACTUAL_TEMPERATURE":"temperatureInput1",
		"SET_POINT_TEMPERATURE":"setpointHeat",
		"HUMIDITY":"humidityInput1"
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
	}
}

## factors:
# rain: 19.8/11.8  = factor 1.67 in mm 
# sunshine 2*60 +31 = 151  —> 464  = factor  3 == every 20 secs  in mimutes

k_testIfmemberOfStateMeasures = "ChangeHours01"

k_GlobalConst_fillMinMaxStates = [
	"ACTUAL_TEMPERATURE", "POWER", "CURRENT","HUMIDITY","ILLUMINATION", "WIND_SPEED"
]

# these are added to custom states for eg temerature etc
k_stateMeasures	= [
	"MinToday", "MaxYesterday", "MinYesterday", "MaxToday", "AveToday", "AveYesterday", "ChangeMinutes10", "ChangeMinutes20", "ChangeHours01", "ChangeHours02", "ChangeHours06", "ChangeHours12", "ChangeHours24"
]

# used for counting to calc averages
k_stateMeasuresCount = [
	"MeasurementsToday", "MeasurementsYesterday"
]

#for dev states props
k_sensorsThatHaveMinMaxReal = [
	"ACTUAL_TEMPERATURE", "POWER", "CURRENT"
]

k_sensorsThatHaveMinMaxInteger = [
	"HUMIDITY","ILLUMINATION", "WIND_SPEED"
]

### this mapps the homematic state to dev.deviceTypeId
k_supportedDeviceTypesFromHomematicToIndigo = {
	"HMIP-STHO": 		"HMIP-STHO",			
	"HMIP-FAL": 		"HMIP-FALMOT",			
	"HMIP-WTH": 		"HMIP-WTH",		
	"HMIP-BWTH": 		"HMIP-WTH",		
	"HMIP-SCI": 		"HMIP-SWDM",			
	"HMIP-STV": 		"HMIP-SWD",			
	"HMIP-SWD||": 		"HMIP-SWD",		# || only accept strict HMIP-SWD no additional characters	
	"HMIP-SWSD": 		"HMIP-SWSD",			
	"HMIP-SWDM": 		"HMIP-SWDM",			
	"HMIP-SWDO": 		"HMIP-SWDM",			
	"HMIP-SPDR": 		"HMIP-SPDR",			
	"HMIP-SRD": 		"HMIP-SRD",			
	"HMIP-ETRV":		"HMIP-ETRV",			
	"HMIP-PS-":			"HMIP-PS",			
	"HMIP-PCBS":		"HMIP-PS",
	"HMIP-PSM": 		"HMIP-PSM",
	"HMIP-PDT": 		"HMIP-PDT",
	"HMIP-SWO-PR": 		"HMIP-SWO-PR",
	"HMIP-SMI":			"HMIP-SMI",			
	"HMIP-SMO":			"HMIP-SMI",	
	"HMIP-DLD": 		"HMIP-DLD",			
	"HMIP-WRC": 		"HMIP-BUTTON",			
	"HMIP-FCI6": 		"HMIP-BUTTON",			
	"HMIP-DBB": 		"HMIP-BUTTON",			
	"HMIP-RC":			"HMIP-BUTTON",	
	"HMIP-RC8":			"HMIP-BUTTON",	
	"HMIP-KRC":			"HMIP-BUTTON",			
	"HMIP-WKP": 		"HMIP-WKP",	
	"ROOM": 			"HMIP-ROOM",			
	"HMIP-SYSVAR": 		"HMIP-SYSVAR"			
}


# this maps fro devtypeid to devicetypeid ID
k_indigoDeviceTypeIdToId = {
	"HMIP-ETRV": "thermostat",
	"HMIP-ETRV-child": "dimmer",
	"HMIP-PDT": "dimmer",
	"HMIP-WTH": "thermostat",
	"HMIP-STHO": "sensor",
	"HMIP-SPDR": "sensor",
	"HMIP-SRD": "sensor",
	"HMIP-SWDM": "sensor",
	"HMIP-SWD": "sensor",
	"HMIP-SWO-PR":"sensor",
	"HMIP-SWSD": "sensor",
	"HMIP-BUTTON": "sensor",
	"HMIP-WKP": "sensor",
	"HMIP-FALMOT": "sensor",
	"HMIP-DLD": "sensor",
	"HMIP-PSM": "relay",
	"HMIP-PS": "relay",
	"HMIP-ROOM": "sensor",
	"HMIP-SMI": "sensor",
	"HMIP-SYSVAR": "sensor",
	"HMIP-HomematicHost": "sensor"
}



k_isBatteryDevice = [
	"HMIP-STHO",			
	"HMIP-WTH",
	"HMIP-SWDM",
	"HMIP-SWD",
	"HMIP-SWO-PR"
	"HMIP-SWSD",
	"HMIP-SMI",
	"HMIP-BUTTON",
	"HMIP-WKP",
	"HMIP-SPDR",	
	"HMIP-ETRV"
]


k_isVoltageDevice = [
	"HMIP-STHO",			
	"HMIP-WTH",
	"HMIP-SWDM",
	"HMIP-SWD",
	"HMIP-SWSD",
	"HMIP-SRD",
	"HMIP-SWO-PR"
	"HMIP-ETRV",			
	"HMIP-BUTTON",
	"HMIP-WKP",
	"HMIP-SMI",	
	"HMIP-PDT",
	"HMIP-SPDR",	
	"HMIP-FALMOT",
	"HMIP-PCBS",		
	"HMIP-RCV-50"					
]


k_isNotRealDevice =[
	"HMIP-RCV-50",
	"HMIP-ROOM",
	"HMIP-SYSVAR"
]

k_forceIntegerStates = [
	"LEVEL",
	"LEVEL-1",
	"LEVEL-2",
	"LEVEL-3",
	"LEVEL-4",
	"LEVEL-5",
	"LEVEL-6",
	"LEVEL-7",
	"LEVEL-8",
	"LEVEL-9",
	"LEVEL-10",
	"LEVEL-11",
	"LEVEL-12",
	"LEVEL-13",
	"brightnessLevel"
]

# these will be crated for the indcated devices
k_createStates = {
	"HMIP-SRD":{
			"ACTUAL_TEMPERATURE": "real",
#			"ACTUAL_TEMPERATURE_STATUS": "string",
			"lastEventOn": "string",
			"lastEventOff": "string",
			"ERROR_CODE":"integer",
			"RAINING": "booltruefalse",
			"RAIN_START": "string",
			"RAIN_END": "string",
			"HEATER_STATE": "booltruefalse"
		},
	"HMIP-SWO-PR":{
			"ACTUAL_TEMPERATURE": "real",
#			"ACTUAL_TEMPERATURE_STATUS": "string",
			"HUMIDITY": "integer",
#			"HUMIDITY_STATUS": "string",
			"ILLUMINATION": "integer",
#			"ILLUMINATION_STATUS": "string",
			"RAINING": "booltruefalse",
			"RAIN_START": "string",
			"RAIN_END": "string",
			"RAIN_RATE": "real",
			"RAIN_TODAY": "real",
			"RAIN_YESTERDAY": "real",
			"RAIN_TOTAL": "real",
#			"RAIN_COUNTER_OVERFLOW": "booltruefalse",
#			"RAIN_COUNTER_STATUS": "string",
			"SUNSHINE_DURATION_TODAY": "integer",
			"SUNSHINE_DURATION_YESTERDAY": "integer",
			"SUNSHINE_DURATION_TOTAL": "integer",
#			"SUNSHINEDURATION_OVERFLOW": "booltruefalse",
#			"SUNSHINE_THRESHOLD_OVERRUN": "booltruefalse",
			"WIND_DIR": "integer",
			"WIND_DIR_RANGE": "real",
#			"WIND_DIR_RANGE_STATUS": "string",
#			"WIND_DIR_STATUS": "string",
			"WIND_SPEED": "real",
#			"WIND_SPEED_STATUS": "string"#
#			"WIND_THRESHOLD_OVERRUN": "booltruefalse"
		},
	"HMIP-DLD":{
			"ACTIVITY_STATE": "string",
			"LOCK_STATE": "string",
			"PROCESS": "string",
			"SECTION": "string",
			"SECTION_STATUS": "string",
			"WP_OPTIONS": "string",
		},
	"HMIP-SWD":{
			"ERROR_NON_FLAT_POSITIONING":"booltruefalse",
			"ERROR_CODE":"integer",
			"WATERLEVEL_DETECTED":"booltruefalse",
			"ALARMSTATE":"booltruefalse",
			"MOISTURE_DETECTED": "booltruefalse",
			"lastSensorChange": "string"
		},
	"HMIP-SWDM":{
			"STATE":"integer",
			"SABOTAGE":"booltruefalse",
			"lastSensorChange":"string"
		},
	"HMIP-SWSD":{
			"displayStatus":"string",
			"SMOKE_DETECTOR_ALARM_STATUS":"string",
			"ERROR_DEGRADED_CHAMBER":"booltruefalse",
			"SMOKE_DETECTOR_TEST_RESULT":"string"
		},
	"HMIP-SMI":{
			"CURRENT_ILLUMINATION":"integer",
			"CURRENT_ILLUMINATION_STATUS":"string",
			"ILLUMINATION":"real",
			"ILLUMINATION_STATUS":"string",
			"MOTION": "booltruefalse",
			"MOTION_DETECTION_ACTIVE": "booltruefalse"
		},
	"HMIP-SPDR":{
			"direction": "string",
			"PASSAGE_COUNTER_VALUE-left":"integer",
			"PASSAGE_COUNTER_VALUE-right":"integer",
			"PPREVIUOS_PASSAGE-left":"string",
			"PPREVIUOS_PASSAGE-right":"string",
			"LAST_PASSAGE-right": "string",
			"LAST_PASSAGE-left": "string"
		},
	"HMIP-PS":{
			"ACTUAL_TEMPERATURE":"real",
#			"ACTUAL_TEMPERATURE_STATUS":"string",
			"ERROR_CODE": " integer",
			"ERROR_OVERHEAT": "booltruefalse",
			"ERROR_OVERLOAD": "booltruefalse",
			"ERROR_POWER_FAILURE": "booltruefalse",
			"STATE": "booltruefalse"
		},
	"HMIP-PSM":{
			"ACTUAL_TEMPERATURE":"real",
#			"ACTUAL_TEMPERATURE_STATUS":"string",
			"ERROR_CODE": " integer",
			"ERROR_OVERHEAT": "booltruefalse",
			"ERROR_OVERLOAD": "booltruefalse",
			"ERROR_POWER_FAILURE": "booltruefalse",
			"STATE": "booltruefalse",
			"CURRENT": "real",
			"CURRENT_STATUS": "integer",
			"ENERGY_USED": "real",
			"ENERGY_COUNTER_OVERFLOW": "booltruefalse",
			"FREQUENCY": "real",
			"FREQUENCY_STATUS": "string",
			"POWER": "real",
			"POWER_STATUS": " string",
			"VOLTAGE": "real",
			"VOLTAGE_STATUS": "string",
		},
	"HMIP-PDT":{
			"ACTUAL_TEMPERATURE":"real",
#			"ACTUAL_TEMPERATURE_STATUS":"string",
			"ERROR_CODE": " integer",
			"ERROR_OVERHEAT": "booltruefalse",
			"ERROR_OVERLOAD": "booltruefalse",
			"ERROR_POWER_FAILURE": "booltruefalse",
			"LEVEL": "integer",
			"LEVEL_Status": "integer"
		},
	"HMIP-WTH":{
			"ACTUAL_TEMPERATURE":"real",
#			"ACTUAL_TEMPERATURE_STATUS":"string",
			"FROST_PROTECTION":"booltruefalse",
			"HEATING_COOLING":"string",
			"HUMIDITY":"integer",
#			"HUMIDITY_STATUS":"string",
			"PARTY_MODE":"booltruefalse",
			"QUICK_VETO_TIME":"real",
			"SET_POINT_MODE":"integer",
			"SET_POINT_TEMPERATURE":"real",
			"SWITCH_POINT_OCCURED":"booltruefalse",
			"WINDOW_STATE":"string",
			"BOOST_MODE":"booltruefalse",
			"BOOST_TIME":"integer"
		},
	"HMIP-WKP":{
			"user":"string",
			"userTime":"string",
			"userPrevious":"string",
			"userTimePrevious":"string",
			"CODE_STATE":"string",
			"SABOTAGE_STICKY":"booltruefalse",
			"SABOTAGE":"booltruefalse",
			"BLOCKED_PERMANENTLY":"booltruefalse",
			"BLOCKED_TEMPORARY":"booltruefalse",
			"USER_AUTHORIZATION":"string",
			"lastValuesText":"string"
		},
	"HMIP-BUTTON":{
			"buttonPressed":"string",
			"buttonPressedTime":"string",
			"buttonPressedType":"string",
			"buttonPressedPrevious":"string",
			"buttonPressedTimePrevious":"string",
			"buttonPressedTypePrevious":"string",
			"lastValuesText":"string"
		},
	"HMIP-ETRV":{
			"ACTUAL_TEMPERATURE":"real",
#			"ACTUAL_TEMPERATURE_STATUS":"string",
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
#			"ACTUAL_TEMPERATURE_STATUS":"string",
			"HUMIDITY":"integer",
#			"HUMIDITY_STATUS":"string",
			"TEMPERATURE_OUT_OF_RANGE":"booltruefalse",
			"ERROR_CODE":"booltruefalse"
		},
	"HMIP-ROOM":{
			"roomListNames":"string",
			"NumberOfDevices":"integer",
			"roomListIDs":"string"
		},
	"HMIP-FALMOT":{
			"DATE_TIME_UNKNOWN":"booltruefalse",
			"DUTY_CYCLE":"booltruefalse",
			"HEATING_COOLING":"integer",
			"HUMIDITY_ALARM":"booltruefalse",
			"TEMPERATURE_LIMITER":"booltruefalse"
		},
	"HMIP-SYSVAR-FLOAT":{
			"description":"string",
			"sensorValue":"real",
		},
	"HMIP-SYSVAR-STRING":{
			"description":"string",
			"value":"string"
		},
	"HMIP-SYSVAR-BOOL":{
			"description":"string",
			"onOffState":"booltruefalse",
		},
	"HMIP-SYSVAR-ALARM":{
			"description":"string",
			"onOffState":"booltruefalse"
		},
}



# homematic send states in different channels, which one to select:
k_useWichChannelForStateFromHomematicToIndigo = {
	"HMIP-PDT":{
			"LEVEL":"2",
	},
	"HMIP-PS":{
			"STATE":"2",
	},
	"HMIP-PSM":{
			"STATE":"2"
	}
}
# replace homematic state number values (0,1,2,3,4,5..) with these in indigo
k_stateValueNumbersToTextInIndigo ={
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
	"WIND_DIR_RANGE_STATUS":[ 
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
		"error"					# 1
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
		"automatic",			
		"manual"				
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
		"open"					# 1
	],

}

# these states are send by several channels eg 2/STATUS -- intdigo state: STATUS-1
k_statesThatAreMultiChannelStates = {
	"HMIP-FALMOT":{
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
	}

}


for devTypeId in k_statesThatAreMultiChannelStates:
	for state in k_statesThatAreMultiChannelStates[devTypeId]["states"]:
		for ii in k_statesThatAreMultiChannelStates[devTypeId]["channels"].split(","):
			k_createStates[devTypeId][state+"-"+ii] =  k_statesThatAreMultiChannelStates[devTypeId]["states"][state]


k_deviceTypesWithButtonPress=[
	"HMIP-BUTTON"
]

k_buttonPressStates = [
	"PRESS_SHORT",
	"PRESS_LONG",
	"PRESS_LONG_RELEASE",
	"PRESS_LONG_START"
]

k_deviceTypesWithKeyPad = [
	"HMIP-WKP"
]

k_keyPressStates = [
	"CODE_ID",
	"USER_AUTHORIZATION_"
]

k_stateThatTriggersLastSensorChange = {
	"HMIP-SWO-PR":["ACTUAL_TEMPERATURE","HUMIDITY","ILLUMINATION","RAIN_COUNTER","WIND_DIR","WIND_SPEED"],
	"HMIP-STHO":["ACTUAL_TEMPERATURE","HUMIDITY"],
	"HMIP-WTH": ["temperatureInput1","setpointHeat"],
	"HMIP-ETRV":["temperatureInput1","setpointHeat"],
	"HMIP-ETRV-child": ["LEVEL"],
	"HMIP-DLD": ["LOCK_STATE"],
	"HMIP-PSM": ["STATE"],
	"HMIP-PS": ["STATE"],
	"HMIP-PDT": ["LEVEL"],
	"HMIP-SWDM": ["STATE"],
	"HMIP-SMI": ["MOTION"],
	"HMIP-SWD": ["ALARMSTATE","WATERLEVEL_DETECTED"]
}


k_devTypeHasChildren = {
	"HMIP-ETRV":{ 
		"devType":"HMIP-ETRV-child",
		"state":"LEVEL"
	}
}


k_defaultProps = {
	"HMIP-SRD":{
		"displayS":"RAINING",
		"SupportsStatusRequest":False,
		"SupportsSensorValue": False,
		"SupportsOnState":  True
	},
	"HMIP-SWO-PR":{
		"displayS":"ACTUAL_TEMPERATURE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue": True,
		"SupportsOnState":  False
	},
	"HMIP-SWSD":{
		"displayStateId":"SMOKE_DETECTOR_ALARM_STATUS",
		"SupportsStatusRequest":False,
		"SupportsSensorValue": False,
		"SupportsOnState":  False
	},
	"HMIP-DLD":{
		"displayStateId":"LOCK_STATE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue": False,
		"SupportsOnState":  True
	},
	"HMIP-SMI":{
		"displayS":"MOTION",
		"SupportsStatusRequest":False,
		"SupportsSensorValue": False,
		"SupportsOnState":  True
	},
	"HMIP-WTH":{
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
	},
	"HMIP-ETRV":{
		"SupportsStatusRequest":False,
		"SupportsHvacFanMode": False,
		"SupportsHvacOperationMode": False,
		"SupportsCoolSetpoint": False,
		"SupportsStatusRequest": False,
		"ShowCoolHeatEquipmentStateUI": False,
		"SupportsHeatSetpoint": True,
		"NumHumidityInputs": 0,
		"NumTemperatureInputs": 1,
		"SupportsSensorValue":True,
		"SupportsOnState": True,
		"heatIsOn":True,
		"childId": 0,
	},
	"HMIP-ETRV-child":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":True,
		"SupportsStatusRequest": False
	},
	"HMIP-BUTTON":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-SWD":{
		"displayS":"ALARMSTATE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-STHO":{
		"displayS":"ACTUAL_TEMPERATURE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue":True,
		"SupportsOnState": False
	},
	"HMIP-FALMOT":{
		"SupportsStatusRequest":False,
		"displayS":"LEVEL-1",
		"SupportsSensorValue":True,
		"SupportsOnState": False,
		"numberOfPhysicalChannels": 12,
		"channelActive-1": True,
		"channelActive-2": True,
		"channelActive-3": True,
		"channelActive-4": True,
		"channelActive-5": True,
		"channelActive-6": True,
		"channelActive-7": True,
		"channelActive-8": True,
		"channelActive-9": True,
		"channelActive-10": True,
		"channelActive-11": True,
		"channelActive-12": True
	},
	"HMIP-SWDM":{
		"displayS":"STATE",
		"invertState":"no",
		"SupportsStatusRequest":False,
		"SupportsOnState": True
	},
	"HMIP-RCV-50":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":True,
		"SupportsOnState": False
	},
	"HMIP-SPDR":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-PDT":{
		"displayS":"STATE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue":True,
		"SupportsOnState": False
	},
	"HMIP-PSM":{
		"displayS":"STATE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-BUTTON":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-WKP":{
		"NumberOfUsersMax": 8,
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-PS":{
		"displayS":"STATE",
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-ROOM":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":True,
		"SupportsOnState": False
	},
	"HMIP-SYSVAR-FLOAT":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":True,
		"SupportsOnState": False
	},
	"HMIP-SYSVAR-STRING":{
		"displayStateId":"value",
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": False
	},
	"HMIP-SYSVAR-ALARM":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	},
	"HMIP-SYSVAR-BOOL":{
		"SupportsStatusRequest":False,
		"SupportsSensorValue":False,
		"SupportsOnState": True
	}
}


# used to fileter devcies
k_actionTypes = {
	"thermostats":["HMIP-ETRV","HMIP-WTH"],
	"doorLocks":["HMIP-DLD"]
}


# what command to send to homematic with indigo actions 
k_actionParams = { # devType:{States:Dimm/OnOff/...}, ChannelstoSendTo[..], {Multiply :indigovalue with for homematic
	"HMIP-SWSD":{
		"states":{
			"OnOff":"SMOKE_DETECTOR_COMMAND", # use this key to send command to homematic
			"OnOff":"SMOKE_DETECTOR_EVENT", # use this key to send command to homematic
		},
		"channels":{
			"OnOff":["1"]
		},
		"OnOffValues":{
			"On":"2",
			"Off":"1"
		}
	},
	"HMIP-DLD":{
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
	"HMIP-PDT":{
		"states":{
			"Dimm":"LEVEL" # use this key to send command to homematic
		},
		"channels":{
			"Dimm":["3","4","5"], # send to channels
			"OnOff":["3","4","5"]
		},
		"mult":{  # multiply indigos value with:
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
	"HMIP-SWDM":{
		"states":{
			"OnOff":"OnOff",
		},
		"channels":{
			"OnOff":["1"]
		}
	},
	"HMIP-FALMOT":{
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
			"Dimm":0.01 # same for all channels
		}
	}
}


