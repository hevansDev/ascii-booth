import cv2
import socket
import logging

from time import sleep
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from escpos.printer import Usb
from mastodon import Mastodon
from gpiozero import Button
from signal import pause
from configparser import ConfigParser

# TODO add black to precommit

logger = logging.getLogger(__name__)

class ReceiptPrinter(object):
    def __init__(self, printable_width, printable_height):
        self.width = printable_width
        self.height = printable_height
        self.printer = Usb(0x0416,0x5011,0,out_ep=0x03)
    
    def print_receipt(self,img):
        logger.info("Printing image..." )
        img = img.resize((self.width,self.height))
        img.rotate(180).save('out.jpeg')
        self.printer.image("out.jpeg",center=True)
        self.printer.cut()
        logger.info("Printed image")
    
    def print_status_page(self):
        logger.info("Printing status page..." )
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname+".local")
        photoPrinter.printer.text('{} : {}'.format(hostname,IPAddr))
        photoPrinter.printer.cut()
        logger.info("Printed status page")

class AsciiConverter(object):
    ### Convert images to ASCII
    def __init__(self,characters,character_width,character_height):
        self.characters = characters
        self.width = character_width
        self.height = character_height
    
    def greyscale_to_index(self,num):
        return int(num  / 255 * (len(self.characters)-1))

    def image_to_ascii(self,img):
        logger.info("Converting image to ASCII..." )
        greyImage = img.convert('L')
        resizedImage = greyImage.resize((self.width,self.height), resample=Image.Resampling.BILINEAR)
        pixels = resizedImage.load()
        ascii = ''
        for y in range(0,resizedImage.height):
            for x in range(0,resizedImage.width):
                pixel = pixels[x,y]
                i = self.greyscale_to_index(pixel)
                ascii+=str(self.characters[i])
            ascii+='\n'
        logger.info("Converted image to ASCII")
        return ascii
    
    def ascii_to_image(self,ascii):
        ## Convert ASCII to jpeg so it can be printed / posted with greater ease
        img = Image.new('L', (13*self.width,20*self.height), 255) #TODO calculate width and height of image dynaimcally
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("/home/hugh/script/courier.ttf", 24)
        draw.text((0, 0),ascii,0,font=font)
        return img

class Camera(object):
    ### Capture and format images from Webcam
    def take_picture(self):
        logger.info("Capturing image...")
        cap = cv2.VideoCapture(0) # /dev/video0
        sleep(2)
        ret, frame = cap.read()
        cap.release()
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        logger.info("Image captured")
        # Brigthen image
        #enhancer1 = ImageEnhance.Brightness(img)
        #enhancer2 = ImageEnhance.Contrast(img)
        #img = enhancer1.enhance(10)
        #img = enhancer2.enhance(2)
        return img

class SocialFeed(object):
    def __init__(self):
        logger.info("Connecting to Mastodon...")
        try:
            self.config = ConfigParser()
            self.config.read('/home/hugh/script/config.ini') 
            self.mastodon = Mastodon(client_id = self.config.get('mastodon', 'client_id'),
                                    client_secret= self.config.get('mastodon', 'client_secret'),
                                    access_token = self.config.get('mastodon', 'access_token'),
                                    api_base_url = 'https://hachyderm.io/')
        except Exception as e:
            logger.error("Couldn't connect to Mastodon\n",e)
            return
        logger.info("Connected to Mastodon")
    
    def post_image(self,img):
        if self.config.get('mastodon', 'enabled') != 'False':
            logger.info("Posting image...")
            try:
                img = img.resize((1080,1080))
                img.save('out.jpeg')  #TODO post directly from object?
                media = self.mastodon.media_post('out.jpeg')
                #TODO what is the most accesible way of describing these images? 
                media['description'] = 'An ASCII art image of a face'
                self.mastodon.status_post("", media_ids=[media['id']])
                logger.info("Posted image")
            except Exception as e:
                logger.info("Couldn't post image\n",e)
            return
        logger.info("Posting disabled")
        

def take_ascii_picture():
    logger.info("ASCII Booth working...")
    capturedImage = camera.take_picture()
    asciiImage = asciiConverter.image_to_ascii(capturedImage)
    outputImage=asciiConverter.ascii_to_image(asciiImage)
    photoPrinter.print_receipt(outputImage)
    socials.post_image(outputImage)
    logger.info("Done")

if __name__ == '__main__':
    logging.basicConfig(filename='booth.log', force=True)
    camera = Camera()
    asciiConverter = AsciiConverter('Ñ@#W$9876543210?!abc;:+=-,._ ', # Characters to compose ASCII art from, an array of characters sorted from densest to lease dense
                                    character_width=48, #The length of each line in the ASCII art in chars
                                    character_height=48 #The number of lines of chars in the ASCII art
                                    )
    photoPrinter = ReceiptPrinter(printable_width=576,printable_height=576)
    socials = SocialFeed()
    button = Button(3)
    button.when_pressed = take_ascii_picture
    photoPrinter.print_status_page()
    print('ASCII Booth Ready!')
    logger.info("ASCII Booth Ready!")
    pause()