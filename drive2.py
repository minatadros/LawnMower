import RPi.GPIO as GPIO
import bluetooth
import string
import subprocess
import os
import time
import multiprocessing
import numpy as np
import argparse
import cv2
##import Adafruit_MCP3008 
##import Adafruit_GPIO.SPI as SPI

GPIO.setmode(GPIO.BCM)
#MCP3008 connections
CLK = 11 #GPIO11 lowest 25%
MISO = 9 #GPIO9 medium 50%
MOSI = 10 #GPIO10 75%
GPIO.setup(CLK, GPIO.IN)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(MOSI, GPIO.IN)
##CS = 8 #GPIO 8
##mcp = Adafruit_MCP3008.MCP3008(clk=CLK,cs=CS,miso=MISO,mosi=MOSI)
##
battryLevel1 = 0
batteryLevel2 = 0
batterylevel3 = 0 


#frequency = 16.5e3 # about 5kHz frequency
frequency = 1e3
speed = 0
angle = 0
notify = 0
# pins for the motor on the right
MotorR_DIRpin = 6 # pin 31  # GPIO6
MotorR_PWMpin = 13 # pin 33  # GPIO13
systemONpin = 27 #pin 13 # GPIO27
MotorL_DIRpin = 23 #pin 16 # GPIO23
MotorL_PWMpin = 18 #pin 12 # GPIO18

#parameters for the motor on the left

# sonar parameters
trigCenter = 21 #pin 40 # center trigger #GPIO 21
echoCenter = 20 #pin 38 # center echo
trigForwardLeft = 19 #pin 35 # Left Forward trigger
echoForwardLeft = 26 # pin 37 # Left Forward echo
trigForwardRight = 2 #pin 3  # Right Forward trigger
echoForwardRight = 3 #pin 5 # Right Forward echo

trigReverseLeft = 12 #pin 32 # reverse left trigger
echoReverseLeft = 16 #pin 36 # reverse left echo
trigReverseRight = 14 #pin 8 # reverse right trigger
echoReverseRight = 15 #pin 10 #reverse right echo
# SONAR setups
GPIO.setup(trigCenter,GPIO.OUT)  # center sonar trigger setup
GPIO.setup(echoCenter,GPIO.IN) # center sonar Echo setup
GPIO.setup(trigForwardLeft,GPIO.OUT)  # Forward Left sonar trigger setup
GPIO.setup(echoForwardLeft,GPIO.IN) # Forward Left sonar Echo setup
GPIO.setup(trigForwardRight,GPIO.OUT)  # Forward Right sonar trigger setup
GPIO.setup(echoForwardRight,GPIO.IN) # Forward Right sonar Echo setup
GPIO.setup(trigReverseRight,GPIO.OUT)  # Reverse Right sonar trigger setup
GPIO.setup(echoReverseRight,GPIO.IN) # Reverse Right sonar Echo setup
GPIO.setup(trigReverseLeft,GPIO.OUT)  # Reverse Left sonar trigger setup
GPIO.setup(echoReverseLeft,GPIO.IN) # Reverse Left sonar Echo setup

# sonar initialization
GPIO.output(trigCenter,0) # center sonar output off
GPIO.output(trigForwardLeft,0) # ForwardLeft sonar output off
GPIO.output(trigForwardRight,0) # ForwardRight sonar output off
# sonar timings 
Centerpulse_start = 0
Centerpulse_end = 0
ForwardLeftpulse_start = 0
ForwardLeftpulse_end = 0
ForwardRightpulse_start = 0
ForwardRightpulse_end = 0

reverseLeftpulse_start = 0
reverseLeftpulse_end = 0
reverseRightpulse_start = 0
reverseRightpulse_end = 0
#motorFlags
forwardFlag = 1
reverseFlag = 1
# sonar flags
sonarForwardRightFlag = 0
sonarForwardLeftFlag = 0
sonarCenterFlag = 0

sonarReverseLeftFlag = 0
sonarReverseRightFlag = 0

# camera Flag
camFlag = 0
#*****************************************************
#relay pin setup
GPIO.setup(systemONpin, GPIO.OUT) 
#setup for motor on the right
GPIO.setup(MotorR_DIRpin, GPIO.OUT) # set GPIO31 to output mode
#GPIO.output(MotorR_DIRpin,0)  # initialize the GPIO31 output to low
GPIO.setup(MotorR_PWMpin, GPIO.OUT) # set GPIO33 to output mode
PWMright = GPIO.PWM(MotorR_PWMpin,frequency) # define PWMrigth to use the PWM method for the right motor
PWMright.start(0) # initialize duty cycle for the motor on the right to 0%

#setup for the motor on the left
GPIO.setup(MotorL_DIRpin, GPIO.OUT) # set GPIO23  to output mode
GPIO.output(MotorL_DIRpin,0)  # initialize the GPIO23 output to low
GPIO.setup(MotorL_PWMpin, GPIO.OUT) # set GPIO23  to output mode
GPIO.output(MotorR_DIRpin,0)
GPIO.output(MotorL_DIRpin,0)
GPIO.output(MotorR_PWMpin,0)
GPIO.output(MotorL_PWMpin,0)
GPIO.output(systemONpin,0)
PWMleft = GPIO.PWM(MotorL_PWMpin,frequency) # define PWMleft to use the PWM method for the left motor
PWMleft.start(0)  # initialize duty cycle for the motor on the left to 0%
#*******************************************************************************************************************************
def BatteryLevelIndicator():
    global batteryLevel1
    global batteryLevel2
    global batteryLevel3
    while(GPIO.input(MOSI) == 0):
        #print("running in highest battery level")
        time.sleep(120)
    client_socket.send("2")
    time.sleep(0.2)
    while(GPIO.input(MISO) == 0):
        #print("running in Medium battery level")
        time.sleep(120)
    client_socket.send("3")
    time.sleep(0.2)
    while(GPIO.input(CLK) == 0):
        #print("running in lowest battery level")
        time.sleep(120)
    client_socket.send("4")
    time.sleep(0.2)
    
        

#**********************************************************************************************************************************
def cameraDetect():
    global a1_min 
    global a1_max 
    global a2_min 
    global a2_max
    global a3_min 
    global a3_max
    global row
    global column
    global cnt
    global average1
    global average2
    global average3
    global camFlag
    while True:
        cmd = "raspistill -o cam.jpg -t 500"
        subprocess.call(cmd,shell=True)
        image = cv2.imread('cam.jpg',1)
        row = image.shape[0]
        column = image.shape[1]
        lowRow = int(row/4)
        lowColumn = int(column/4)
        highRow = row-int(row/4)
        highColumn = column-int(column/4)
        
        
        
        last = image.shape[2]
        a = np.array(image[0:row,0:column,0:last])
        a1 = a[lowRow:highRow,lowColumn:highColumn,0:1]
        average1 = np.mean(a1)
        print("average1 = ")
        print(average1)
        a2 = a[lowRow:highRow,lowColumn:highColumn,1:2]
        average2 = np.mean(a2)
        print("average2 = ")
        print(average2)
        a3 = a[lowRow:highRow,lowColumn:highColumn,2:last]
        average3 = np.mean(a3)
        print("average3 = ")
        print(average3)
        if(average1>2 and average3>2):
            try:
                camFlag = 1
                client_socket.send("M")
                time.sleep(0.2)
                            
            except:
                print("disconnected")
        else:
            camFlag=0
            client_socket.send("P")
            time.sleep(0.2)
##            client_socket.send("F")
##            time.sleep(0.2)

#****************************************************************************************************************************
def sonarObstacle():
    global ForwardLeftpulse_start
    global ForwardLeftpulse_end
    global ForwardRightpulse_start
    global ForwardRightpulse_end
    global sonarForwardLeftFlag
    global sonarForwardRightFlag
    global Centerpulse_start   
    global Centerpulse_end 
    global sonarCenterFlag
    global sonarReverseLeftFlag
    global sonarReverseRightFLag
    global camFlag
    
    
    while True:
        #Forward sonar
#Forward Right
        if(forwardFlag == 1):
            print("hello sonar")
            GPIO.output(trigForwardRight,1)
            time.sleep(0.00001)
            GPIO.output(trigForwardRight,0)
            while GPIO.input(echoForwardRight)==0:
                ForwardRightpulse_start = time.time()
            while GPIO.input(echoForwardRight)==1:
                ForwardRightpulse_end = time.time()
            ForwardRightpulse_duration = ForwardRightpulse_end - ForwardRightpulse_start
            ForwardRightdistance = ForwardRightpulse_duration * 17150
            ForwardRightdistance = round(ForwardRightdistance,2)
            print("Forward Right distance is: ")
            print(ForwardRightdistance)
            
            if(ForwardRightdistance <= 30):
                try:
                    sonarForwardRightFlag = 1
                    client_socket.send("R")
                    time.sleep(0.2)
                        
                except:
                    print("disconnected")
            else:
                sonarForwardRightFlag = 0

            
##      # forward Left      
            GPIO.output(trigForwardLeft,1)
            time.sleep(0.00001)
            GPIO.output(trigForwardLeft,0)
            while GPIO.input(echoForwardLeft)==0:
                ForwardLeftpulse_start = time.time()
            while GPIO.input(echoForwardLeft)==1:
                ForwardLeftpulse_end = time.time()
            ForwardLeftpulse_duration = ForwardLeftpulse_end - ForwardLeftpulse_start
            ForwardLeftdistance = ForwardLeftpulse_duration * 17150
            ForwardLeftdistance = round(ForwardLeftdistance,2)
            print("Forward Left distance is: ")
            print(ForwardLeftdistance)
            
            if(ForwardLeftdistance <= 30):
                try:
                    sonarForwardLeftFlag = 1
                    client_socket.send("L")
                    time.sleep(0.2)
                        
                except:
                    print("disconnected")
            else:
                sonarForwardLeftFlag = 0
##      # Center      
            GPIO.output(trigCenter,1)
            time.sleep(0.00001)
            GPIO.output(trigCenter,0)
            while GPIO.input(echoCenter)==0:
                Centerpulse_start = time.time()
            while GPIO.input(echoCenter)==1:
                Centerpulse_end = time.time()
            Centerpulse_duration = Centerpulse_end - Centerpulse_start
            Centerdistance = Centerpulse_duration * 17150
            Centerdistance = round(Centerdistance,2)
            print("Center distance is: ")
            print(Centerdistance)
            
            if(Centerdistance <= 30):
                try:
                    sonarCenterFlag = 1
                    client_socket.send("C")
                    time.sleep(0.2)
                        
                except:
                    print("disconnected")
            else:
                sonarCenterFlag = 0

##            if(sonarForwardRightFlag==0 and sonarCenterFlag==0):
##                client_socket.send("F")
##                time.sleep(0.2)
##        # back sonar
        if(reverseFlag == 1):
            print("here in reverse")
          # reverse right  
            GPIO.output(trigReverseRight,1)
            time.sleep(0.00001)
            GPIO.output(trigReverseRight,0)
            while GPIO.input(echoReverseRight)==0:
                ReverseRightpulse_start = time.time()
            while GPIO.input(echoReverseRight)==1:
                ReverseRightpulse_end = time.time()
            ReverseRightpulse_duration = ReverseRightpulse_end - ReverseRightpulse_start
            ReverseRightdistance = ReverseRightpulse_duration * 17150
            ReverseRightdistance = round(ReverseRightdistance,2)
            print("reverse Right distance is: ")
            print(ReverseRightdistance)
            
            if(ReverseRightdistance <= 30):
                try:
                    sonarReverseRightFlag = 1
                    client_socket.send("V")
                    time.sleep(0.2)
                        
                except:
                    print("disconnected")
            else:
                sonarReverseRightFlag = 0

            
      # reverse Left      
            GPIO.output(trigReverseLeft,1)
            time.sleep(0.00001)
            GPIO.output(trigReverseLeft,0)
            while GPIO.input(echoReverseLeft)==0:
                ReverseLeftpulse_start = time.time()
            while GPIO.input(echoReverseLeft)==1:
                ReverseLeftpulse_end = time.time()
            ReverseLeftpulse_duration = ReverseLeftpulse_end - ReverseLeftpulse_start
            ReverseLeftdistance = ReverseLeftpulse_duration * 17150
            ReverseLeftdistance = round(ReverseLeftdistance,2)
            print("reverse Left distance is: ")
            print(ReverseLeftdistance)
            
            if(ReverseLeftdistance <= 30):
                try:
                    sonarReverseLeftFlag = 1
                    client_socket.send("T")
                    time.sleep(0.2)
                        
                except:
                    print("disconnected")
            else:
                sonarReverseLeftFlag = 0
        if(sonarReverseRightFlag ==0 and sonarReverseLeftFlag==0 and sonarForwardLeftFlag ==0 and sonarForwardRightFlag==0 and sonarCenterFlag==0):
            client_socket.send("F")
            time.sleep(0.2)
                
            

            

#*********************************************************************
# turn Forward right
def turnForward_Right(a,s):
    global forwardFlag
    global reverseFlag
    global sonarForwardRightFlag
    global camFlag
    forwardFlag = 1
    reverseFlag = 0
    if(sonarForwardRightFlag==0 and camFlag==0):
        if(s==100):
            PWMleft.ChangeDutyCycle(0)
            GPIO.output(MotorL_PWMpin,1)
        else:
            PWMleft.ChangeDutyCycle(s)
        temp = (s*a)/90
        PWMright.ChangeDutyCycle(temp)
        GPIO.output(MotorR_DIRpin,1)  # set the GPIO31 output to high
        GPIO.output(MotorL_DIRpin,1)  # initialize the GPIO23 output to high
    
#******************************************************

# turn Forward left
def turnForward_Left(a,s):
    global forwardFlag
    global reverseFlag
    global sonarForwardLeftFlag
    global camFlag
    forwardFlag = 1
    reverseFlag = 0
    if(sonarForwardLeftFlag==0 and camFlag==0):
        if(s==100):
            PWMright.ChangeDutyCycle(0)
            GPIO.output(MotorR_PWMpin,1)
        else:
            PWMright.ChangeDutyCycle(s)
        a = 180-a
        temp = (s*a)/90
        PWMleft.ChangeDutyCycle(temp)
        GPIO.output(MotorR_DIRpin,1)  # set the GPIO31 output to high
        GPIO.output(MotorL_DIRpin,1)  # initialize the GPIO23 output to high
        
#******************************************************************
# move forward
def moveForward(s):
    global forwardFlag
    global reverseFlag
    global sonarCenterFlag
    global camFlag
    reverseFlag = 0
    forwardFlag = 1
    if(sonarCenterFlag==0 and camFlag==0):
        if(s==100):
            PWMright.ChangeDutyCycle(0)   #
            PWMleft.ChangeDutyCycle(0)
            GPIO.output(MotorR_PWMpin,1)
            GPIO.output(MotorL_PWMpin,1)
        else:
            PWMright.ChangeDutyCycle(s)   #
            PWMleft.ChangeDutyCycle(s)
        GPIO.output(MotorR_DIRpin,1)  # set the GPIO31 output to high
        GPIO.output(MotorL_DIRpin,1)  # initialize the GPIO23 output to high
        
    
#**********************************************************
# reverse movement
def moveReverse(s):
    global forwardFlag
    global reverseFlag
    global sonarReverseLeftFlag
    global sonarReverseRightFlag
    forwardFlag = 0
    reverseFlag = 1
    if(sonarReverseLeftFlag==0 and sonarReverseRightFlag==0):
        if(s==100):
            PWMright.ChangeDutyCycle(0)
            PWMleft.ChangeDutyCycle(0)
            GPIO.output(MotorL_PWMpin,1)
            GPIO.output(MotorR_PWMpin,1)
        else:
            PWMright.ChangeDutyCycle(s)
            PWMleft.ChangeDutyCycle(s)
        GPIO.output(MotorR_DIRpin,0)  # set the GPIO31 output to low
        GPIO.output(MotorL_DIRpin,0)  # initialize the GPIO23 output to low
        
#**************************************************
def turnReverse_Left(a,s):
    global forwardFlag
    global reverseFlag
    global sonarReverseLeftFlag
    forwardFlag = 0
    reverseFlag = 1
    if(sonarReverseLeftFlag==0):
        if(s==100):
            PWMright.ChangeDutyCycle(0)
            GPIO.output(MotorR_PWMpin,1)
            
        else:
            PWMright.ChangeDutyCycle(s)
        a = a-180
        temp = (s*a)/90
        PWMleft.ChangeDutyCycle(temp)
        GPIO.output(MotorR_DIRpin,0)  # set the GPIO31 output to high
        GPIO.output(MotorL_DIRpin,0)  # initialize the GPIO23 output to high
    
#*****************************************************
def turnReverse_Right(a,s):
    global forwardFlag
    global reverseFlag
    global sonarReverseRightFlag
    forwardFlag = 0
    reverseFlag = 1
    if(sonarReverseRightFlag==0):
        if(s==100):
            PWMleft.ChangeDutyCycle(0)
            GPIO.output(MotorL_PWMpin,1)
        else:
            PWMleft.ChangeDutyCycle(s)
        a = 360 - a
        temp = (s*a)/90
        PWMright.ChangeDutyCycle(temp)
        GPIO.output(MotorR_DIRpin,0)  # set the GPIO31 output to high
        GPIO.output(MotorL_DIRpin,0)  # initialize the GPIO23 output to high
        
#***********************************************************
def moveLeft(s):
    global forwardFlag
    global reverseFlag
    global sonarForwardLeftFlag
    global sonarReverseLeftFlag
    global camFlag
    forwardFlag = 1
    reverseFlag = 0
    if(sonarForwardLeftFlag==0 and sonarReverseLeftFlag==0 and camFlag==0):
        if(s==100):
            PWMright.ChangeDutyCycle(0)

            GPIO.output(MotorR_PWMpin,1)
            
        else:
            PWMright.ChangeDutyCycle(s)
        PWMleft.ChangeDutyCycle(0)
        GPIO.output(MotorL_DIRpin,0)  # initialize the GPIO23 output to high
        GPIO.output(MotorR_DIRpin,1)  # set the GPIO31 output to high
        
    
#***********************************************
def moveRight(s):
    global forwardFlag
    global reverseFlag
    global sonarReverseRightFlag
    global sonarForwardRightFLag
    global camFlag
    forwardFlag = 1
    reverseFlag = 0
    if(sonarReverseRightFlag==0 and sonarForwardRightFlag==0 and camFlag==0):
        
        if(s==100):
            PWMleft.ChangeDutyCycle(0)
            GPIO.output(MotorL_PWMpin,1)
            
        else:
            PWMleft.ChangeDutyCycle(s)
        PWMright.ChangeDutyCycle(0)
        GPIO.output(MotorR_DIRpin,0)  # set the GPIO31 output to high
        GPIO.output(MotorL_DIRpin,1)  # initialize the GPIO23 output to high
    
#****************************************************************
def stop():
    global forwardFlag
    global reverseFlag
    forwardFlag = 1
    reverseFlag = 0
    PWMleft.ChangeDutyCycle(0)
    PWMright.ChangeDutyCycle(0)
    

# stop output signal when user presses enter key
def stopOutputSignal(str):
    input(str)
    PWMleft.stop()
    PWMright.stop()
    GPIO.cleanup()
#***********************************************************
def seperate_angle_speed(s):
    flag = 0
    print(str1)
    for i in range(0,len(s)):
        if(s[i] != "Z" and flag == 0):
            str1 = str1 + s[i]
        elif(s[i] == "Z"):
            flag = 1
        elif(s[i]!="Y" and flag==1):
            str2 = str2 + s[i]
#******************************************************************
def setAngle(s):
    angle = int(s)
    print("angle =  " + repr(angle))
#************************************************************************
def setSpeed(s):
    speed = int(s)
    print("speed = " + repr(speed))
#*****************************************************************
    

#subprocess.call(['sudo','hciconfig','hci0','reset'])
subprocess.call(['sudo','hciconfig','hci0','piscan'])
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM) # create a server socket with RFCOMM protocol
port = 1
server_socket.bind(("",port)) # assign aan address and port number to socket
server_socket.listen(1) # listen to accept 1 connection request at a time
client_socket,address = server_socket.accept() # get access to the  client socket for transferring/recieving data
cont = 0
flag3 = 0
p1 = multiprocessing.Process(target=sonarObstacle)
p1.start()
p2 = multiprocessing.Process(target=cameraDetect)
p2.start()
p3 = multiprocessing.Process(target=BatteryLevelIndicator())
p3.start()
#*********************************************************************************************
while True:
    try:
        #BatteryLevelIndicator()
        #time.sleep(1)
        data = client_socket.recv(10)
        #time.sleep(1)
        str = data
        print(str)
        flag2 = 1
        for i in range(0,len(str)):
            if(str[i] == "o" or str[i]=="f"):
                print("interrupt command recieved!!!")
                flag2 = 0
        if(flag2==0):
            if(str[i]=="o"):
                print("open command recieved!!!")
                GPIO.output(systemONpin,1)
                
            elif(str[i]=="f"):
                GPIO.output(systemONpin,0)
                print("system closed by user!!!")
                
                

        elif(flag2==1):
            str1 = ""
            str2 = ""
            newdata = str.split(" ")
            if(len(newdata)>1):
                str1 = newdata[0]
                str2 = newdata[1]
                print("str1 = " + repr(str1) + "str2 = " + repr(str2))
                if(str1 == ""):
                    angle = 0
                else:
                    angle = int(str1)
                if(str2 == ""):
                    speed = 0
                else:
                    speed = int(str2)
            else:
                stop()
            if(speed >= 0 and speed <= 100):
                if( angle >= 75 and angle <= 105):
                    moveForward(speed)
                    print("\nMove Forward\n")
                elif(angle <= 195 and angle >= 165):
                    moveLeft(speed)
                    print("\nMove left\n")
                elif(angle <= 285 and angle >= 255):
                    moveReverse(speed)
                    print("\nmove reverse\n")
                elif(angle <= 15  or angle>= 345):
                    moveRight(speed)
                    print("\nmove right\n")
                elif(angle > 15 and angle < 75):
                    turnForward_Right(angle,speed)
                    print("\nturn forward right\n")
                elif(angle > 105 and angle < 165 ):
                    turnForward_Left(angle,speed)
                    print("\nturn forward left\n")
                elif(angle > 195 and angle < 255):
                    turnReverse_Left(angle,speed)
                    print("\nturn reverse left\n")
                elif(angle > 285 and angle < 345):
                    turnReverse_Right(angle,speed)
                    print("\nturn reverse right\n")
                else:
                    stop()
            else:
                stop()
    except:
        stop()
        print("disconnected!!!!")
        client_socket.close()
        server_socket.close()
        time.sleep(1)
        #os.system('sudo reboot')


        







 


