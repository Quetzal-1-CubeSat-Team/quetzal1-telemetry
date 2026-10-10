# ----------------------------------------------------------------------
# Titulo: Telemetry_Filter.py
# Autor: Aldo Aguilar Nadalini
# Fecha: 27 de julio de 2020
# Descripcion: Programa para filtrar telemetria de Quetzal-1 descargada
#              desde SatNOGS. Este programa elimina beacons localizados
#              en lugar incorrecto, asi como beacons mal decodificados.
# Modificado: 2026-10-10 por Dan Alvarez
# Cambios:     - Se elimina calculo de orbita (TLE, Modulo_Propagator) y
#                columnas ECEF/ECI/LLA/velocidades, puesto que no se
#				 cuenta con los TLE actualmente.
#              - QtCore.QDateTime reemplazado por datetime (misma lógica).
#              - Salida en CSV en lugar de Excel (.xls).
#              - Directorios de entrada/salida como argumentos (--input,
#                --output) y opción --all para procesar las 30 semanas.
#              - El filtro de paquetes repetidos solo se aplica con
# 				 --filter. Sin eso, se escriben todos los paquetes que
# 				 vienen en los archivo HEX.
#              - Columna frame_index (numero de frame dentro del HEX).
#              - Se elimina opcion --framelength (HEX files solo
#                contienen beacons de 137 bytes).
# ----------------------------------------------------------------------

# Librerias ------------------------------------------------------------

# Local libraries
from datetime import datetime, timedelta
import argparse
import csv
import os
import sys

# Own libraries
import Modulo_HEX as mh

# ----------------------------- FUNCIONES ------------------------------

def parse_args():
	"""
	Funcion para recibir parametros de funcionamiento de programa
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('--week', '-i', help='No. of week to analyze', type=int, default=0)
	parser.add_argument('--all', '-a', help='Process all 30 weeks', action='store_true')
	parser.add_argument('--input', help='Input HEX file (default: ../raw/beacons_week_N.hex)', default=None)
	parser.add_argument('--output', '-o', help='Output CSV file (default: ./output/beacons_week_N[_filtered].csv)', default=None)
	parser.add_argument('--filter', '-f', help='Apply original chronological filter', action='store_true')
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
	launch_date = datetime(2020,4,28,15,20,18)						    # Fecha y hora de lanzamiento 15:20:18 - 28/04/2020 UTC
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
	date_time = date_time + timedelta(days=days_to_add)
	date_time = date_time + timedelta(seconds=secs_to_add)

	# Corrector de timestamps para eliminar error de RTC de
	# satelite y obtener real-time UTC
	if (skew_corrector):
		dS = int((date_time - launch_date).total_seconds())			    # Determinar cantidad de segundos desde lanzamiento y UTC timestamp
		real_seconds = round(dS * skew_coeff,0)             			# Realizar correccion de segundos para eliminar adelanto de Nanomind 3200
		date_time = launch_date + timedelta(seconds=real_seconds)	    # Generar fecha corregida

	utc_date = date_time.strftime("%H:%M:%S - %d/%m/%Y")
	return date_time, utc_date

def procesar_semana(week_no, file_hex, file_out, filtrar):
	"""
	Funcion para decodificar (y opcionalmente filtrar) los beacons de
	un HEX file y escribirlos en un archivo CSV

	Parametros
	----------
	week_no : int
		No. de semana a analizar
	file_hex : str
		Ruta de HEX file de entrada
	file_out : str
		Ruta de archivo CSV de salida
	filtrar : bool
		Bandera para aplicar filtro de orden cronologico
	"""

	# -------------------- DECODIFICADOR DE TELEMETRIA ---------------------

	# Decodificar telemetria demodulada y almacenada en archivo HEX
	hex_list = mh.HEX_select(file_hex)
	beacon_amount = len(hex_list)/beacon_length

	# --------------------------- GENERADO DE CSV ---------------------------

	# Inicializar archivo CSV para guardar datos ---------------------------
	print("Executing beacon decoding" + (" and filtering" if filtrar else "") + " (week " + str(week_no) + ").....")
	out_dir = os.path.dirname(file_out)
	if (out_dir != ''):
		os.makedirs(out_dir, exist_ok=True)
	fp = open(file_out, 'w', newline='')
	sheet = csv.writer(fp)
	headers = ['frame_index','UTC_Timestamp',\
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

	# Ejecutar escritura de headers en CSV
	sheet.writerow(headers)

	# Ejecucion continua para lectura de todo beacon en el HEX file
	i = 0
	nrow = 0
	beacon_index = 0
	last_date = datetime(2000,1,1,0,0,0)
	max_date = datetime(2030,1,1,0,0,0)
	while (i < int(beacon_amount)):

		# Decodificar beacons
		_, beacon_data, _ = mh.beacon_decode(hex_list, beacon_index, nrow, False)

		# Calcular UTC Timestamp
		date, timestamp = calcular_UTC(beacon_data[0], beacon_data[1],
									   beacon_data[2], beacon_data[3],
									   beacon_data[4], beacon_data[5],
									   skew_coeff=skew_coeff)

		# Eliminar beacons en mal orden cronologico o mal decodificados
		# (solo si se selecciono --filter)
		if (not filtrar or (date > last_date and date < max_date)):
			sheet.writerow([i, timestamp] + list(beacon_data))			# Escribir linea de cada beacon en CSV
			last_date = date
			nrow += 1

		# Movimiento de lectura de beacon a travez de HEX
		beacon_index = beacon_index + beacon_length
		i += 1

	# Guardar archivo
	fp.close()
	print("Beacon decoding completed: " + str(nrow) + " of " + str(int(beacon_amount)) + " frames written to " + file_out)
	return nrow

# ***************************** EJECUCION ******************************

# Extraer parametros de command line -----------------------------------
args = parse_args()
week_no = args.week

# Configuracion de variables globales
skew_coeff = 0.999939265156109											# Ultima calibracion 2020-10-06 02:00:00 UTC (Desfase de 60.735us)
beacon_length = 137														# Bytes por beacon en HEX files (sin headers AX.25/CSP)

# Proteccion de programa
if (week_no == 0 and not args.all):
	print("No week was selected. Exiting program...")
	sys.exit(0)

# Inicializado de archivos
script_dir = os.path.dirname(os.path.abspath(__file__))
weeks = list(range(1, 31)) if args.all else [week_no]
if (len(weeks) > 1 and (args.input is not None or args.output is not None)):
	print("--input/--output can only be used with a single week. Exiting program...")
	sys.exit(0)

total_rows = 0
for week_no in weeks:
	file_hex = args.input
	if (file_hex is None):
		file_hex = os.path.join(script_dir, '..', 'raw', 'beacons_week_' + str(week_no) + '.hex')
	file_out = args.output
	if (file_out is None):
		suffix = '_filtered' if args.filter else ''
		file_out = os.path.join(script_dir, 'output', 'beacons_week_' + str(week_no) + suffix + '.csv')
	total_rows += procesar_semana(week_no, file_hex, file_out, args.filter)

print("Telemetry processing completed! Total rows: " + str(total_rows))

# ----------------------------------------------------------------------
