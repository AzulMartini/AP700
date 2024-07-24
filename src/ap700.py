#!/usr/bin/env python3
from re import S
import pymodbus
from pymodbus.client.sync import ModbusSerialClient
import struct
import time
import rospy
from std_msgs.msg import Float32

# Configuración del puerto serie
SERIAL_PORT = '/dev/ttyUSB4'  # puerto COM en Windows
BAUDRATE = 19200
PARITY = 'E'  # 'N' para ninguna paridad, 'E' para paridad par, 'O' para paridad impar

datos_dec=[]

def leer_datos_modbus():
	rospy.init_node('ap700', anonymous=True)
	SERIAL_PORT = rospy.getparam('~serial_port')

	# Crear topicos para cada dato 

	pub_presion_bar = rospy.Publisher('/geneseas/ap700/pb', Float32, queue_size=1000)	# Presión barométrica 
	pub_temperatura = rospy.Publisher('/geneseas/ap700/temp', Float32, queue_size=1000)	# Temperatura del agua
	pub_ph = rospy.Publisher('/geneseas/ap700/ph', Float32, queue_size=1000)					# PH del agua
	pub_orp = rospy.Publisher('/geneseas/ap700/por', Float32, queue_size=1000)					# ORP ( Potencial de oxido reducción )
	pub_turbidez = rospy.Publisher('/geneseas/ap700/turbidez', Float32, queue_size=1000)		# Turbidez en NTU
	pub_cond_elec_H = rospy.Publisher('/geneseas/ap700/ce_H', Float32, queue_size=1000)			# Conductividad electrica parte alta (HIGH)
	pub_cond_elec_L = rospy.Publisher('/geneseas/ap700/ce_L', Float32, queue_size=1000)			# Conductividad electrica parte baja (LOW)
	pub_cond_elec_20_H = rospy.Publisher('/geneseas/ap700/ce_20_H', Float32, queue_size=1000)	# Conductividad electrica corregida a 20 grados parte alto (HIGH)
	pub_cond_elec_20_L = rospy.Publisher('/geneseas/ap700/ce_20_L',Float32, queue_size=1000)	# Conductividad electrica corregida a 20 grados parte baja (LOW)
	pub_cond_elec_25_H = rospy.Publisher('/geneseas/ap700/ce_25_H',Float32, queue_size=1000)	# Conductividad electrica corregida a 25 grados parte alto (HIGH)
	pub_cond_elec_25_L = rospy.Publisher('/geneseas/ap700/ce_25_L',Float32, queue_size=1000)	# Conductividad electrica corregida a 25 grados parte baja (LOW)
	pub_res_elec_H = rospy.Publisher('/geneseas/ap700/re_H',Float32, queue_size=1000)	# Resistividad electrica parte alto (HIGH)
	pub_res_elec_L = rospy.Publisher('/geneseas/ap700/re_L',Float32, queue_size=1000)	# Resisitividad electrica parte baja (LOW)
	pub_salinidad = rospy.Publisher('/geneseas/ap700/salinidad', Float32, queue_size=1000)		# Salinidad en PSU
	pub_sol_dis_H = rospy.Publisher('/geneseas/ap700/solidos_dis_H',Float32, queue_size=1000)	# Solidos disueltos totales parte alto (HIGH)
	pub_sol_dis_L = rospy.Publisher('/geneseas/ap700/solidos_dis_L',Float32, queue_size=1000)	# Solidos disueltos totales parte baja (LOW)
	pub_gravedad = rospy.Publisher('/geneseas/ap700/ge', Float32, queue_size=1000)		# Gravedad
	pub_ox_dis = rospy.Publisher('/geneseas/ap700/od', Float32, queue_size=1000)	# Oxigeno disuelto 
	pub_ox_dis_p = rospy.Publisher('/geneseas/ap700/odp', Float32, queue_size=1000)	# Oxigeno disuelto porcentaje de aire 
	pub_profundidad = rospy.Publisher('/geneseas/ap700/ps', Float32, queue_size=1000)	# Profundidad de la sonda 

	rate = rospy.Rate(1) # 10hz 
     
	client = ModbusSerialClient(
        method='rtu', 
        port=SERIAL_PORT, 
        baudrate=BAUDRATE,
        parity=PARITY  # Especificar la paridad aquí
    )

	if not client.connect():
		print("Error: No se pudo conectar al dispositivo Modbus RTU")
		return
    
	while not rospy.is_shutdown():
        # Leer 16 registros de entrada, donde se almacenan los datos simulados
		resultado = client.read_input_registers(0, 20, unit=1)
		if not resultado.isError():
            # Decodificar los datos como valores de punto flotante
			datos = [x for x in resultado.registers]
            # Decodificar los datos como valores de punto flotante
			datos_dec = [x for x in datos]
			datos_dec[1] /= 100 # Temperatura 
			datos_dec[2] /= 100 # pH 
			datos_dec[3] /= 10 # Potencial oxidacion/reduccion 
			datos_dec[12] /= 100 # Salinidad 
			datos_dec[15] /= 10 # Gravedad especifica del agua de mar 
			datos_dec[16] /= 100 # Oxigeno disuelto en mg/L 
			datos_dec[17] /= 10 # Oxigeno disuelto, % de saturacion de aire 

			pub_presion_bar.publish(Float32(datos_dec[0]))
			pub_temperatura.publish(Float32(datos_dec[1]))
			pub_ph.publish(Float32(datos_dec[2]))
			pub_orp.publish(Float32(datos_dec[3]))
			pub_turbidez.publish(Float32(datos_dec[4]))
			pub_cond_elec_H.publish(Float32(datos_dec[5]))
			pub_cond_elec_L.publish(Float32(datos_dec[6]))
			pub_cond_elec_20_H.publish(Float32(datos_dec[7]))
			pub_cond_elec_20_L.publish(Float32(datos_dec[8]))
			pub_cond_elec_25_H.publish(Float32(datos_dec[9]))
			pub_cond_elec_25_L.publish(Float32(datos_dec[10]))
			pub_res_elec_H.publish(Float32(datos_dec[11]))
			pub_res_elec_L.publish(Float32(datos_dec[12]))
			pub_salinidad.publish(Float32(datos_dec[13]))
			pub_sol_dis_H.publish(Float32(datos_dec[14]))
			pub_sol_dis_L.publish(Float32(datos_dec[15]))
			pub_gravedad.publish(Float32(datos_dec[16]))
			pub_ox_dis.publish(Float32(datos_dec[17]))
			pub_ox_dis_p.publish(Float32(datos_dec[18]))
			pub_profundidad.publish(Float32(datos_dec[19]))
		
			#print("Datos leidos", datos_dec) # Mensajes para debug

		else:
			print("Error al leer datos Modbus RTU:", resultado)

		rate.sleep() 

	client.close()

if __name__ == "__main__":
    try:
        leer_datos_modbus()
    except rospy.ROSInterruptException:
        pass

