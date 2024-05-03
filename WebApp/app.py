import re, os, io
import logging
import streamlit as st
import pymysql

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
    st.write("Connect with me on LinkedIn [link](%s)" % "https://www.linkedin.com/in/hugh-evans-435134153/")
    st.write("Upload an image to convert it into ASCII art")

    uploaded_file = st.file_uploader("Upload an image")
    name = st.text_input('Name',disabled=False)
    email = st.text_input('Email',disabled=False)
    agree = st.checkbox("I'd like email updates about the ASCII booth project")
    submit = st.form_submit_button('Convert image')

def write_to_db():
    # Write survey response to DB
    timeout = 10
    connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host="ascii-booth-app-db-ascii-booth.k.aivencloud.com",
    password= st.secrets["MYSQL_PASSWORD"],
    read_timeout=timeout,
    port=16534,
    user= st.secrets["MYSQL_USER"],
    write_timeout=timeout,
    )

    try:
        cursor = connection.cursor()
        cursor.execute("REPLACE INTO responses (name, email) VALUES ('{0}', '{1}')".format(name,email))
    finally:
        connection.commit()
        connection.close()

def validate_email_syntax(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


if submit:
    if uploaded_file is None:
        st.write("Please upload an image first")
    elif uploaded_file.type not in ["image/jpeg","image/jpg","image/png"]:
        st.write("Only PNG and JPG file formats are supported")
    elif validate_email_syntax(email) != True:
        st.write("Please enter your email")
    elif uploaded_file is not None:
        image = Image.open(io.BytesIO(uploaded_file.read()))
        asciiImage = asciiConverter.image_to_ascii(image)
        outputImage=asciiConverter.ascii_to_image(asciiImage)
        st.image(outputImage.resize((1000,1000)))
        
        if agree:
            write_to_db()
        