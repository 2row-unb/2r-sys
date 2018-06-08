"""
Kernel module is responsible to handle IMUs and Strain Gage
"""

import gabby
import logging
import RPi.GPIO as GPIO
import time
import math

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


class Kernel(gabby.Gabby):
    def transform(self, message):
        logging.debug(
            f"Received message, data: {message.payload.decode('utf-8')}")
        imu_data = [float(x) for x in
                    message.payload.decode('utf-8').split(';')]

        buttons_info = self.get_buttons()
        weight_info = self.get_weight()
        time_info = self.get_time()

        data = [*imu_data, time_info, *buttons_info, weight_info]
        return [gabby.Message(data, self.output_topics)]

    def get_time(self):
        tx= time.time()

        ty  = time.time() - tx

        return ty


    def get_buttons(self):

        #Verifica quantas vezes o botao foi acionado
        #contador = 0
	button _incr = 0
	button_decr = 0
	button_reset = 0

        #Define o pino do botao como entrada
        GPIO.setup(18, GPIO.IN)
        GPIO.setup(11, GPIO.IN)
        GPIO.setup(16, GPIO.IN)

	time.sleep(0.3)
    	if GPIO.input(18) == True:
		contador += 1
		button_incr = contador

        if GPIO.input(11) == True:
		contador += 1
		button_decr = contador

        if GPIO.input(17) == True:

		button_reset = 1
		contador += 1
		if (contador == 2):
			button_reset = 0


        return [button_incr, button_decr, button_reset]


    def get_weight(self):
	#Definindo os pinos da celula de carga 1:
	DAT =15
	CLK=16
	#Definindo os pinos da celula de carga 2:
	DAT2 = 13
	CLK2 = 8
	#Contadores das celulas 1 e 2, respectivamente:
	num=0
	num2=0
	#Definindo pinos como saida:
	gpio.setup(CLK, gpio.OUT)
	gpio.setup(CLK2,gpio.OUT)
	#Funcao da leitura da celula de carga 2:
	def weight2():
  		i=0
  		num2=0
  		gpio.setup(DAT2, gpio.OUT)
  		gpio.output(DAT2,1)
  		gpio.output(CLK2,0)
  		gpio.setup(DAT2, gpio.IN)

  		while gpio.input(DAT2) == 1:
      			i=0
  		for i in range(24):
        		gpio.output(CLK2,1)
        		num2 = num2<<1

        		gpio.output(CLK2,0)
        		if gpio.input(DAT2) == 0:
            			num2 = num2 + 1
  		gpio.output(CLK2,1)

  		num2 = num2^0x800000
  		gpio.output(CLK2,0)
  		wei2 = 0
  		wei2 = ((num2)/1406)

  		PESO2=(((wei2-5943)/15))
  		print PESO2,"kg"
  		time.sleep(0.5)

        #Funcao da leitura da celula de carga 1:
	def weight():
  		i=0
  		num=0
  		gpio.setup(DAT, gpio.OUT)
  		gpio.output(DAT,1)
  		gpio.output(CLK,0)
  		gpio.setup(DAT, gpio.IN)

  		while gpio.input(DAT) == 1:
      			i=0
  		for i in range(24):
        		gpio.output(CLK,1)
        		num = num<<1

        		gpio.output(CLK,0)

        	if gpio.input(DAT) == 0:
            		num=num+1
			gpio.output(CLK,1)

  			num=num^0x800000

  		gpio.output(CLK,0)
  		wei = 0
  		wei = ((num)/1406)


  		PESO=(((wei-5943)/15))
  		print PESO,"kg"
  		time.sleep(0.5)

	#Verificar local certo de colocar essa conta
	P_medio = 0
	P_medio = PESO2 + PESO
	F = 0
	angle = 45
	F = P_medio*9.81*0.7071
	#calculo da energia
	#verificar t como variável global
	Pot_final = o
	Pot_final = E/t

        return Pot_final


    def get_carga()

	#Verifica quantas vezes o botao foi acionado
        contador = 0
	#Define os pinos dos reles como saida - Modulo 1
        GPIO.setup(37, GPIO.OUT)
        GPIO.setup(35, GPIO.OUT)
        GPIO.setup(33, GPIO.OUT)
        GPIO.setup(31, GPIO.OUT)
        #Define os pinos dos reles como saida - Modulo 2
        GPIO.setup(40, GPIO.OUT)
        GPIO.setup(38, GPIO.OUT)
        GPIO.setup(36, GPIO.OUT)
        GPIO.setup(32, GPIO.OUT)

	#Inicio-todos os reles desligados - Modulo 1
        GPIO.output(37,1)
        GPIO.output(35,1)
        GPIO.output(33,1)
        GPIO.output(31,1)
        #Inicio- todos os reles desligados - Modulo 2
        GPIO.output(40,1)
        GPIO.output(38,1)
        GPIO.output(36,1)
        GPIO.output(32,1)

	#Colocar aqui parte do código que indica botão Plus_click
	        if contador == 1:
           		GPIO.output(37, 0)
	       		GPIO.output(32, 0)
        	 if contador == 2:
	       		GPIO.output(37, 1)
	       		GPIO.output(32, 1)
           		GPIO.output(35, 0)
           		GPIO.output(36, 0)
        	 if contador == 3:
	       		GPIO.output(35, 1)
           		GPIO.output(36, 1)
           		GPIO.output(33, 0)
           		GPIO.output(38, 0)
        	  if contador == 4:
	       		GPIO.output( 33, 1)
           		GPIO.output( 38, 1)
           		GPIO.output( 31, 0)
           		GPIO.output( 40, 0)
       		  if contador > 4:
           		GPIO.output(31, 1)
	   		GPIO.output(40, 1)
	   		print('Por favor, escolha uma carga de 1 a 4')
           		contador = 0

	#Colocar aqui a parte do código para Minimus_click:
		if contador == 0:
	        	print('Nao tem carga no equipamento')
              	if contador == 1:
                	GPIO.output(37, 1)
                	GPIO.output(32, 1)
	        	contador = 0
            	if contador == 2:
                	GPIO.output(35, 1)
	        	GPIO.output(36, 1)
	        	GPIO.output(37, 0)
                	GPIO.output(32, 0)
	        	contador = 1
            	if contador == 3:
                	GPIO.output(33, 1)
                	GPIO.output(38, 1)
	        	GPIO.output(35, 0)
                	GPIO.output(36, 0)
	        	contador = 2
             	if contador == 4:
                	GPIO.output(31, 1)
	        	GPIO.output(40, 1)
	        	GPIO.output(33, 0)
                	GPIO.output(38, 0)
	        	contador = 3

      return 0




   	return xxx
