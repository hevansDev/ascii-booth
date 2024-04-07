import cv2

from time import sleep
from PIL import Image, ImageFont, ImageDraw
from escpos.printer import Usb
from mastodon import Mastodon
from gpiozero import Button
from signal import pause
from configparser import ConfigParser

class ReceiptPrinter(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.printer = Usb(0x0416,0x5011,0,out_ep=0x03,profile="TM-L90")

    def ascii_to_image(self,ascii):
        ## Convert ASCII to jpeg so it can be printed / posted with greater ease
        img = Image.new('L', (1120,1400), 255)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("courier.ttf", 24)
        draw.text((0, 0),ascii,0,font=font)
        return img.resize((self.width,self.height))
    
    def print_receipt(self,img):
        print("Printing image...",end="")
        img.rotate(180).save('out.jpeg')
        self.printer.image("out.jpeg",center=True)
        self.printer.cut()
        print("Printed image")

class AsciiConverter(object):
    ### Convert images to ASCII
    def __init__(self,characters):
        self.characters = characters
    
    def greyscale_to_index(self,num):
        return int(num  / 255 * (len(self.characters)-1))

    def image_to_ascii(self,img):
        print("Converting image to ASCII...",end="")
        greyImage = img.convert('L')
        resizedImage = greyImage.resize((80,70), resample=Image.Resampling.BILINEAR)
        pixels = resizedImage.load()
        ascii = ''
        for y in range(0,resizedImage.height):
            for x in range(0,resizedImage.width):
                pixel = pixels[x,y]
                i = self.greyscale_to_index(pixel)
                ascii+=str(self.characters[i])
            ascii+='\n'
        print("Converted image to ASCII")
        return ascii

class Camera(object):
    ### Capture and format images from Webcam
    def __init__(self,width,height):  # noqa: F811
        self.width = width
        self.height = height
    
    def take_picture(self):
        print("Capturing image...",end='')
        cap = cv2.VideoCapture(0) # /dev/video0
        sleep(2)
        ret, frame = cap.read()
        cap.release()

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        outputImage = img.resize((self.width,self.height))
        print("Image captured")
        return outputImage

class SocialFeed(object):
    def __init__(self):
        #TODO store secrets securely
        config = ConfigParser()
        config.read('auth.ini') 
        self.mastodon = Mastodon(client_id = config.get('mastodon', 'client_id'),
                                 client_secret= config.get('mastodon', 'client_secret'),
                                 access_token = config.get('mastodon', 'access_token'),
                                 api_base_url = 'https://hachyderm.io/')
    
    def post_image(self,img):
        print("Posting image...",end="")
        img.save('out.jpeg')  #TODO post directly from object?
        media = self.mastodon.media_post('out.jpeg')
        #TODO what is the most accesible way of describing these images? 
        media['description'] = 'An ASCII art image of a face'
        self.mastodon.status_post("", media_ids=[media['id']])
        print("Posted image")

def take_ascii_picture():
    print("ASCII Booth working...")
    capturedImage = camera.take_picture()
    asciiImage = asciiConverter.image_to_ascii(capturedImage)
    outputImage=testPrinter.ascii_to_image(asciiImage)
    testPrinter.print_receipt(outputImage)
    socials.post_image(outputImage)
    print("Done")


if __name__ == '__main__':
    printable_width = 576
    printable_height = 576
    camera = Camera(printable_width,printable_height)
    asciiConverter = AsciiConverter('Ñ@#W$9876543210?!abc;:+=-,._ ')
    testPrinter = ReceiptPrinter(printable_width,printable_height)
    socials = SocialFeed()
    button = Button(3)
    button.when_pressed = take_ascii_picture
    print("ASCII Booth Ready!")
    pause()