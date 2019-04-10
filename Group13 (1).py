# Importing necessary modules and packages
import picamera
import RPi.GPIO as GPIO
import smtplib
import os
from time import sleep
from datetime import datetime

# Modules for sending mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email username and password
receiver = 'groupmassey13@gmail.com'
password = '******'
sender = 'groupmassey13@gmail.com'

# Board setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Directory where we are saving the images
DIR = './Database/'

# Setup of sensor, using GPIO4
pir_sensor = 4
GPIO.setup(pir_sensor, GPIO.IN, GPIO.PUD_DOWN)

# Variable to keep track of the motion sensor value
current_state = 0

# Function to send the email
def send_mail():
    print("Sending Email") # debug to show email sending
    # Create the directory if it doesn't exists
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    # Save image to file
    image = os.path.join(DIR, IMAGE_TIMESTAMP + '.jpg')
    
    # Capture the face and clean resources used
    with picamera.PiCamera() as camera:
        camera.rotation = 270
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        pic = camera.capture(image)
        print ("Picture taken at ", set_timestamp()) # debug to show picture taken
        
    # Sending mail
    print ("Email setup started at ", set_timestamp()) # debug to show email starting
    msg = MIMEMultipart()
    msg['To'] = receiver
    msg['Subject'] = 'Movement Detected on the Property!'
    msg['From'] = sender
    body = 'Picture has been taken and is attached below.'
    
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(image, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    print ("Message encoded at ", set_timestamp()) # debug to show encoded time
    part.add_header('Content-Disposition', 'attachment; filename= %s' % image)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print ("Connecting to server at ", set_timestamp()) # debug to show server connection
    server.login(receiver, password)
    print ("Server login ", set_timestamp())
    text = msg.as_string()
    server.sendmail(receiver, sender, text)
    print ("Email sent at ", set_timestamp()) # debug to see when send_mail executed
    server.quit()
    print ("Server connection closed at ", set_timestamp()) # debug to see connection closed
    
# Function for setting up the Timestamp
def set_timestamp():
    currentTime = datetime.now()
    # Returning timestamp when executed
    return currentTime.strftime("%Y.%m.%d-%H:%M:%S")

while True:
    # Read in the value from the sensor into variable
    current_state = GPIO.input(pir_sensor)
    # When output from motion sensor is HIGH
    if current_state == 1: 
        print ("Intruder Detected!")    # debug when motion is triggered
        IMAGE_TIMESTAMP = set_timestamp()  # Adding timestamp to filename
        send_mail()
        sleep(2)
    # When output from motion sensor is LOW
    elif current_state == 0:  
        print ("No Intruders.")  # debug when no motion
        sleep(2)
