# homematic
indigo plugin to link with homematic on raspberry pi (raspberrymatic)

this plugin does the following:
1. copy states  from homematic host to indigo devices/ states
2. indigo through actions can set states and values on the homematic host

prerequisities / steps
1. create micro sd with raspberry matic (homematic on raspberry) image
2. start rpi
3. install add on "ccuJack" - that is used to communicat with the rpi through http
4. strongly recommended to install addon  "HM-tools" for unix tools
5. create devices on rpi, hermostates, sensors etc
6. install homematic plugin on indigo server
7. in config set ip number and port number (normally 2121)
8. all devices system variables and rooms should be created automatically on the indigo server

supported devices
device type			description
-	HMIP-WRC			  2 button remote
-	HMIP-RC8			  2 button remote
-	HMIP-STHO			  internal / external Temp / humidity sensor
-	HMIP-FALMOT-C12			12 channel underfloor heating 
-	HMIP-FAL230-C10			10 230V
-	HMIP-FAL230-C6			6  230V
-	HMIP-FAL24-C10			10 24V
-	HMIP-FAL24-C6			6  24V
-	HMIP-WTH		  	wall thermostat 
-	HMIP-SWDM		  	magnet on / off sensor
-	HMIP-ETRV		  	radiator attached thermostat
-	HMIP-PS			  	powerplug switch
-	HMIP-PSM		  	powerplug switch w energy measurement



