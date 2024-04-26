import re
import os
import io
import logging
import streamlit as st

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

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
        img = Image.new('L', (13*self.width,20*self.height), 255) #TODO calculate width and height of image dynamically
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.getcwd()+"/WebApp/static/courier.ttf", 24)
        draw.text((0, 0),ascii,0,font=font)
        return img
    
asciiConverter = AsciiConverter('Ñ@#W$9876543210?!abc;:+=-,._ ', # Characters to compose ASCII art from, an array of characters sorted from densest to lease dense
                                character_width=128, #The length of each line in the ASCII art in chars
                                character_height=128 #The number of lines of chars in the ASCII art
                                )

with st.form("ascii_app"):

   st.write("ASCII Picture App")

   uploaded_file = st.file_uploader("Upload an image")
   email = st.text_input('Email',disabled=False)
   agree = st.checkbox("I'd like to see the full version of this talk")
   submit = st.form_submit_button('Generate image')

   

def validate_email_syntax(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


if submit:
    if validate_email_syntax(email) != True:
        st.write("Please enter your email")
    elif uploaded_file is not None:
        image = Image.open(io.BytesIO(uploaded_file.read()))
        asciiImage = asciiConverter.image_to_ascii(image)
        outputImage=asciiConverter.ascii_to_image(asciiImage)
        st.image(outputImage.resize((1000,1000)))
        with open("contacts.txt", "a") as myfile:
            myfile.write("{},{}\n".format(email,agree))
    else:
        st.write("Please upload an image first")