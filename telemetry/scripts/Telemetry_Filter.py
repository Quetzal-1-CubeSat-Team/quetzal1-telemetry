# ----------------------------------------------------------------------
# Titulo: Telemetry_Filter.py
# Autor: Aldo Aguilar Nadalini
# Fecha: 27 de julio de 2020
# Descripcion: Programa para filtrar telemetria de Quetzal-1 descargada
#              desde SatNOGS. Este programa elimina beacons localizados
#              en lugar incorrecto, asi como beacons mal decodificados.
# ----------------------------------------------------------------------

# Librerias ------------------------------------------------------------

# Local libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
import argparse
import time
import sys

# Third-party libraries
import xlwt
from xlwt import Workbook
import xlrd

# Own libraries
from Modulo_Propagator import Orbit_Propagator
import Modulo_HEX as mh

# ----------------------------- FUNCIONES ------------------------------

def parse_args():
	"""
	Funcion para recibir parametros de funcionamiento de programa
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('--week', '-i', help='No. of week to analyze', type=int, default=0)
	parser.add_argument('--framelength', '-l', help='Amount of bytes per frame', type=int, default=137)
	return parser.parse_args()

def calcular_RTC(rtc_hour, rtc_min, rtc_sec, rtc_day, rtc_month, rtc_year):
	"""
	Funcion para volver datos de beacon de RTC a una cadena con el
	formato hh:mm:ss dd/MM/yy

	Parametros
	----------
	rtc_hour : str
		Horas que el satelite lleva funcionando
	rtc_min : str
		Minutos que el satelite lleva funcionando
	rtc_sec : str
		Segundos que el satelite lleva funcionando
	rtc_day : str
		Dias que el satelite lleva funcionando
	rtc_month : str
		Meses que el satelite lleva funcionando
	rtc_year : str
		Anios que el satelite lleva funcionando
	"""

	# Generar cadena de RTC
	rtc_hour = '0' + str(rtc_hour)
	rtc_minute = '0' + str(rtc_min)
	rtc_second = '0' + str(rtc_sec)
	rtc_day = '0' + str(rtc_day)
	rtc_month = '0' + str(rtc_month)
	rtc_year = '0' + str(rtc_year)
	rtc_date = ':'.join([rtc_hour[-2:], rtc_minute[-2:], rtc_second[-2:] + ' - ' + '/'.join([rtc_day[-2:], rtc_month[-2:], rtc_year[-2:]])])
	return rtc_date

def calcular_UTC(rtc_hour, rtc_min, rtc_sec, rtc_day, rtc_month, rtc_year, skew_coeff=1, skew_corrector=True):
	"""
	Funcion para volver datos de beacon de RTC a una cadena con el
	formato hh:mm:ss dd/MM/yy pero convertido a tiempo UTC

	Parametros
	----------
	rtc_hour : str
		Horas que el satelite lleva funcionando
	rtc_min : str
		Minutos que el satelite lleva funcionando
	rtc_sec : str
		Segundos que el satelite lleva funcionando
	rtc_day : str
		Dias que el satelite lleva funcionando
	rtc_month : str
		Meses que el satelite lleva funcionando
	rtc_year : str
		Anios que el satelite lleva funcionando
	skew_coeff : float
		Coeficiente de ajuste de RTC
	skew_corrector : bool}
		Bandera de ajuste de RTC
	"""

	# Generar cadena de RTC
	rtc_date = calcular_RTC(rtc_hour, rtc_min, rtc_sec, rtc_day,
							rtc_month, rtc_year)

	# Inicializar fecha de lanzamiento
	launch_date = QtCore.QDateTime(2020,4,28,15,20,18)				    # Fecha y hora de lanzamiento 15:20:18 - 28/04/2020 UTC
	date_time = launch_date
	month_days = [31,31,29,31,30,31,30,31,31,30,31,30]

	# Extraer datos de RTC time
	years_to_add = int(rtc_date[-2:])
	months_to_add = int(rtc_date[-5:-3])
	sum_months = sum(month_days[:months_to_add])
	days_to_add = int(rtc_date[-8:-6]) + sum_months + (years_to_add * 365)
	hours_to_add = int(rtc_date[:2])
	mins_to_add = int(rtc_date[3:5])
	secs_to_add = int(rtc_date[6:8]) + (mins_to_add * 60) + (hours_to_add * 3600)

	# Agregar tiempo transcurrido en RTC para calcular UTC a partir
	# de hora de lanzamiento
	date_time = date_time.addDays(days_to_add)
	date_time = date_time.addSecs(secs_to_add)

	# Corrector de timestamps para eliminar error de RTC de
	# satelite y obtener real-time UTC
	if (skew_corrector):
		dS = launch_date.secsTo(date_time)							    # Determinar cantidad de segundos desde lanzamiento y UTC timestamp
		real_seconds = round(dS * skew_coeff,0)             			# Realizar correccion de segundos para eliminar adelanto de Nanomind 3200
		date_time = launch_date.addSecs(real_seconds)				    # Generar fecha corregida

	utc_date = date_time.toString("hh:mm:ss - dd/MM/yyyy")
	return date_time, utc_date

# ***************************** EJECUCION ******************************

# Extraer parametros de command line -----------------------------------
week_no = parse_args().week
beacon_length = parse_args().framelength

# Configuracion de variables globales
skew_coeff = 0.999939265156109											# Ultima calibracion 2020-10-06 02:00:00 UTC (Desfase de 60.735us)

# Proteccion de programa
if (week_no == 0):
	print("No week was selected. Exiting program...")
	sys.exit(0)

beacon_lengths = [137, 141, 157, 207]
header_lengths = [0, 4, 20, 70]
if (beacon_length not in beacon_lengths):
	print("Incorrect frame length selected. Exiting program...")
	sys.exit(0)
else:
	idx = beacon_lengths.index(beacon_length)
	beacon_header_length = header_lengths[idx]

# Inicializado de archivos
file_hex = 'C://Users//Aldo//OneDrive - Universidad del Valle de Guatemala//Quetzal-1 Data//Raw Beacons (Weekly)//beacons_week_' + str(week_no) + '.hex'
file_tle = 'C://Users//Aldo//OneDrive - Universidad del Valle de Guatemala//Quetzal-1 Data//TLE Set (Weekly)//tle_week_' + str(week_no) + '.txt'
file_out = 'C://Users//Aldo//OneDrive - Universidad del Valle de Guatemala//Quetzal-1 Data//Parsed Beacons (Weekly)//beacons_week_' + str(week_no) + '.xls'

# -------------------- DECODIFICADOR DE TELEMETRIA ---------------------

# Decodificar telemetria demodulada y almacenada en archivo HEX
hex_list = mh.HEX_select(file_hex)
beacon_amount = len(hex_list)/beacon_length
beacon_counter = beacon_header_length

# ------------------------ PROPAGADOR DE ORBITA ------------------------

# Leer datos de TLE de semana
weekly_tle = ['QUETZAL-1']
with open(file_tle, 'r') as fp:
	for line in fp.readlines():
		weekly_tle.append(line)
		if (len(weekly_tle) == 3):
			break
TLE_LINES = (weekly_tle[1].strip(),weekly_tle[2].strip())

# Inicializacion de propagador de orbita
propagator = Orbit_Propagator(TLE_LINES,skew_coeff)

# ------------------------- GENERADO DE EXCEL --------------------------

# Inicializar archivo de Excel para guardar datos ----------------------
print("Executing beacon decoding and filtering.....")
wb = Workbook()
sheet = wb.add_sheet('Logger')
headers = ['UTC_Timestamp','x_ecef','y_ecef','z_ecef','x_eci','y_eci','z_eci',\
     'longitude','latitude','altitude','vx_eci','vy_eci','vz_eci',\
	 'hora', 'minuto', 'segundo', 'dia', 'mes', 'year', 'ADM_status', 'EPS_status', \
	 'HEATER_status', 'ADCS_status', 'PAYLOAD_status', 'ADM_resetS', \
	 'EPS_resetS', 'ADCS_resetS', 'ADCS_resetH', 'COMMS_resetH', 'CDHS_reset',\
	 'EPS_temperature', 'state_charge', 'battery_voltage', 'average_current',\
	 'remaining_capacity', 'average_power', 'state_health', 'CH1_voltage', \
	 'CH1_current', 'CH2_voltage', 'CH2_current', 'CH3_voltage', 'CH3_current',\
	 'ADCS_current', 'COMMS_current', 'PAYLOAD_current', 'HEATER_current',\
	 'fault_flags', 'communication_flags', 'transmission_flags_EPS',\
	 'gyro_X', 'gyro_Y', 'gyro_Z', 'mag_X', 'mag_Y', 'mag_Z', 'ADC1_CH1', 'ADC1_CH2',\
	 'ADC1_CH3', 'ADC1_CH4', 'ADC1_CH5', 'ADC1_CH6', 'ADC2_CH1', 'ADC2_CH2',\
	 'ADC2_CH3', 'ADC2_CH4', 'ADC2_CH5', 'ADC2_CH6', 'BNO055_temperature',\
	 'ADCS_temperature1', 'transmission_flags_ADCS',\
	 'package_counter', 'camera_mode', 'picture_counter', 'CDHS_CYCLE_TIME',\
	 'CDHS_WDT', 'ADM_SOC_LIMIT', 'ADCS_SOC_LIMIT', 'COMMS_SOC_LIMIT', \
	 'PLD_SOC_LIMIT', 'HEATER_CYCLE_TIME', 'HEATER_EMON_TIME', 'HEATER_EMOFF_TIME', \
	 'ADM_CYCLE_TIME', 'ADM_BURN_TIME', 'ADM_MAX_CYCLES', 'ADM_WAIT_TIME1',\
	 'ADM_WAIT_TIME2', 'ADM_ENABLE', 'COMMS_CYCLE_TIME', 'PLD_CYCLE_TIME',\
	 'PLD_OP_MODE', 'CAM_RESOLUTION', 'CAM_EXPOSURE', 'CAM_SAVE_TIME', 'PLD_ENABLE']

# Ejecutar escritura de headers en Excel
for x in range(0, len(headers)):
	sheet.write(0, x, headers[x])

# Ejecucion continua para lectura de todo beacon en el HEX file
i = 0
nrow = 0
listados_utc = []
beacon_index = beacon_header_length
last_date = QtCore.QDateTime(2000,1,1,0,0,0)
max_date = QtCore.QDateTime(2030,1,1,0,0,0)
while (i < int(beacon_amount)):

	# Decodificar beacons
	_, beacon_data, _ = mh.beacon_decode(hex_list, beacon_index, nrow, False)

	# Calcular UTC Timestamp
	date, timestamp = calcular_UTC(beacon_data[0], beacon_data[1],
								   beacon_data[2], beacon_data[3],
								   beacon_data[4], beacon_data[5],
								   skew_coeff=skew_coeff)

	# Eliminar beacons en mal orden cronologico o mal decodificados
	if (last_date.secsTo(date) > 0 and date.daysTo(max_date) > 0):
		listados_utc.append(timestamp)									# Agregar timestamp a listado a utilizar para propagador de orbita
		sheet.write(nrow + 1, 0, timestamp)                             # Escribir timestamp de beacon en Excel
		for x in range(0, len(headers) - 13):
			sheet.write(nrow + 1, x + 13, beacon_data[x])               # Escribir linea de cada beacon en Excel
		last_date = date
		nrow += 1

	# Movimiento de lectura de beacon a travez de HEX
	beacon_index = beacon_index + beacon_length
	i += 1
print("Beacon decoding and filtering completed.")

# Obtener localizacion y velocidad Earth-centered Earth-fixed (ECEF) de
# satelite durante transmision de cada beacon
print("Calculating satellite ECEF coordinates......")
x_ecef, y_ecef, z_ecef, v_ecef = propagator.obtener_estados_ECEF(listados_utc)
v_ecef = [i for i in zip(*v_ecef)]	                                    # Trasponer matriz de velocidades

# Conversion de coordenadas ECEF a formato Earth-centered Inertial Frame
# (ECI)
print("Calculating satellite ECI coordinates.......")
x_eci, y_eci, z_eci = propagator.conversion_ECEF_ECI(x_ecef, y_ecef, z_ecef, listados_utc)

# Conversion de velocidad ECEF a formato ECI
print("Calculating satellite ECI velocity.......")
vx_eci, vy_eci, vz_eci = propagator.conversion_ECEF_ECI(v_ecef[0], v_ecef[1], v_ecef[2], listados_utc)

# Conversion de coordenadas ECEF a formato Longitude-Latitude-Altitude
# (LLA)
print("Calculating satellite LLA coordinates.......")
longitudes, latitudes, altitudes = propagator.conversion_ECEF_LLA(x_ecef, y_ecef, z_ecef, radians=False)

# Ejecutar escritura de coordenadas ECEF, ECI, LLA en Excel
for j in range(0, len(x_ecef)):
	sheet.write(j + 1, 1, x_ecef[j])
	sheet.write(j + 1, 2, y_ecef[j])
	sheet.write(j + 1, 3, z_ecef[j])
	sheet.write(j + 1, 4, x_eci[j])
	sheet.write(j + 1, 5, y_eci[j])
	sheet.write(j + 1, 6, z_eci[j])
	sheet.write(j + 1, 7, longitudes[j])
	sheet.write(j + 1, 8, latitudes[j])
	sheet.write(j + 1, 9, altitudes[j])
	sheet.write(j + 1, 10, vx_eci[j])
	sheet.write(j + 1, 11, vy_eci[j])
	sheet.write(j + 1, 12, vz_eci[j])

# Guardar archivo
wb.save(file_out)
print("Telemetry processing completed!")

# ----------------------------------------------------------------------
