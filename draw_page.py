from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import inspect, re
from datetime import datetime as dt

class id_emulator:
    def __init__(self, imgname=""):
        return imgname
    def show():
        return 0

class fonthelper:
    hFont = None
    name = ""
    path = None
    size = 0
    glyphs = None
    def __init__(self, path, size):
        self.hFont = ImageFont.truetype(path, size)
        self.path = path
        self.size = size
    def idname(self):
        return "id("+self.name+")"

class imghelper:
    hImg = None
    name = ""
    path= None
    def __init__(self, img, path):
        self.hImg = img
        self.path = path
    def idname(self):
        return "id("+self.name+")"

class it_emulator:
    x = 0
    y = 0
    primimage = None
    draw = None
    displaydef = """
display:
  - platform: lilygo_t5_47_display
    id: mydisplay
    rotation: 270
    update_interval: never
    clear: false
    full_update_every: 20
    power_off_delay_enabled: false
    lambda: |-"""
    fontlist = []   # Font list, will be used to generate esphome font list
    imglist = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.primimage = Image.new("1", (x,y), 1) # Create image in binary format
        self.draw = ImageDraw.Draw(self.primimage)

    def addfont(self, path, size, glyphs=None):
        font = fonthelper(path, size)
        font.glyphs = glyphs
        font.name = "fontid" + str(len(self.fontlist)) #Assign font id based on current count
        self.fontlist.append(font)
        return font

    def generatefontlist(self):
        buffer = "font:\n"
        for font in self.fontlist:
            buffer += "  - file: '" + font.path + "'\n"
            buffer += "    id: " + font.name + "\n"
            buffer += "    size: " + str(font.size) + "\n"
            if (font.glyphs != None):
                buffer += "    glyphs: " + font.glyphs + "\n"
        return buffer

    def addimage(self, imgpath, newsize):
        newimg = self.imgconvert("raw"+imgpath, newsize, imgpath)
        img = imghelper(newimg, imgpath)
        img.name = "imgid" + str(len(self.imglist)) #Assign img id based on current count
        self.imglist.append(img)
        return img

    def generateimagelist(self):
        if len(self.imglist) == 0:
            return ""
        buffer = "image:\n"
        for img in self.imglist:
            buffer += " - file: '"+ img.path + "'\n"
            buffer += "   id: "+ img.name +"\n"
            buffer += "   type: BINARY\n"
        return buffer

    def printImageDef(self):
        print(self.imgdef)

    def imgconvert(self, imgpath, size, newname):
        img1 = Image.open(imgpath).convert("RGBA") # Load image
        img2 = Image.new("RGBA", img1.size, "WHITE") # Create a white rgba background
        img2.paste(img1, (0, 0), img1) #Paste loaded image to white bg 
        img2.thumbnail(size)
        img2.save(newname)
        return img2

    def convert_text_align(self, textalign):
        if  textalign == "TextAlign::TOP_RIGHT":
            return "rt"
        elif  textalign == "TextAlign::TOP_CENTER":
            return "ma"
        elif  textalign == "TextAlign::BOTTOM_LEFT":
            return "ld"
        elif  textalign == "TextAlign::BASELINE_LEFT":
            return "ls"
        elif  textalign == "TextAlign::BOTTOM_RIGHT":
            return "rd"
        else:
            return "la"

    def image(self, x, y, img: imghelper):
        self.primimage.paste(img.hImg, [x,y])   # Pase to file
        self.displaydef += "\n       it.image(" + str(x) + ", " + str(y) + ", "+ img.idname() +" );"
    
    def strftime(self, x,y, pfont: fonthelper, textalign, mystring, timearg):
        tanchor=self.convert_text_align(textalign)
        now = dt.now()
        self.draw.text((x,y), now.strftime(mystring), anchor=tanchor, font=pfont.hFont, fill="black")
        self.displaydef += "\n       it.strftime(" + str(x) + ", " + str(y) + ", " + pfont.idname() + ", " + textalign +", \"" + mystring + "\", " + timearg + ");"

    def printf(self, x,y, pfont: fonthelper, textalign, mystring, args="", represent=None):
        if args != "":
            args = ", " + args
        tanchor=self.convert_text_align(textalign)
        if represent == None:
            self.draw.text((x,y), mystring, anchor=tanchor, font=pfont.hFont, fill="black")
        else:
            self.draw.text((x,y), represent, anchor=tanchor, font=pfont.hFont, fill="black")
        self.displaydef += "\n       it.printf(" + str(x) + ", " + str(y) + ", " + pfont.idname() + ", " + textalign +", \"" + mystring + "\"" +  args + ");"
        #self.displaydef += "\n"
    
def topbottomblock(x,y, p1, p2):
    it.printf(x, y+30, ibm40 ,"TextAlign::TOP_CENTER", "%.1f", p1, "1099.9")
    it.printf(x, y, ibm30 ,"TextAlign::TOP_CENTER", p2)

def weatherblock(x,y):
    it.printf(x, y, mdi160 ,"TextAlign::TOP_LEFT", "%s", "id(fc_weather).state.c_str()", "󰙾")
    it.printf(x+480, y+210, sansprobold100 ,"TextAlign::BOTTOM_RIGHT", "%.1f", "id(kaczkitemp).state", "-12.9") #°C
    it.printf(x+475, y+80, ibm40 ,"TextAlign::TOP_LEFT", "°C") #°C
    topbottomblock(x+290, y, "id(outside_humid).state", "%%")
    topbottomblock(x+460, y, "id(outside_pressure).state", "hPa")
    
def IconTempHumid(x, y, icon, temp, humid):
    it.printf(x, y+15, smallicons ,"TextAlign::TOP_LEFT", icon)
    it.printf(x+70, y+8, miniicons ,"TextAlign::TOP_LEFT", "\U000F050F")
    it.printf(x+110, y, ibm40 ,"TextAlign::TOP_LEFT", "%.1f°C", temp, represent="-19.9°")
    it.printf(x+110, y+42, ibm40 ,"TextAlign::TOP_LEFT", "%.0fhPa", humid, represent="1001")

it = it_emulator(540, 960)

#Font glyphs
weatherglyphs = """
      - "\U000F0594" # clear-night
      - "\U000F0590" # cloudy
      - "\U000F0595" # partlycloudy
      - "\U000F0591" # fog      
      - "\U000F0592" # hail
      - "\U000F0593" # lightning
      - "\U000F067E" # lightning-rainy
      - "\U000F0596" # pouring
      - "\U000F0597" # rainy
      - "\U000F0F36" # snowy
      - "\U000F067F" # snowy-rainy
      - "\U000F0599" # sunny
      - "\U000F059D" # windy
      - "\U000F059E" # windy-variant
      - "\U000F0F38" # exceptional"""
statusglyphs = """
      - "\U000F11B4" # mdi-water-boiler-off 󱆴
      - "\U000F0F92" # mdi-water-boiler 󰾒"""
smalliconsglyphs = """
      - "\U000F01E5" # mdi-duck 󰇥"""
miniiconsglypgs = """
      - "\U000F050F" #mdi-thermometer"""

# Add fonts
sansprobold100  = it.addfont("fonts/SourceSansPro-Bold.ttf", 130, '\"0123456789:.\"')
sansprobold40   = it.addfont("fonts/SourceSansPro-Bold.ttf", 40, '\"0123456789:.\"')
ibm40           = it.addfont("fonts/IBMPlexMono-Bold.ttf", 40)
ibm30           = it.addfont("fonts/IBMPlexMono-Bold.ttf", 30)
mdi160          = it.addfont("fonts/materialdesignicons-webfont.ttf", 200, weatherglyphs)
statusicons     = it.addfont("fonts/materialdesignicons-webfont.ttf", 110, statusglyphs)
smallicons      = it.addfont("fonts/materialdesignicons-webfont.ttf", 80, smalliconsglyphs)
miniicons       = it.addfont("fonts/materialdesignicons-webfont.ttf", 40, miniiconsglypgs)



#Time & Date
it.strftime(3, -30, sansprobold100, "TextAlign::TOP_LEFT", "%H:%M", "id(homeassistant_time).now()")
it.strftime(440, -5, sansprobold40, "TextAlign::TOP_CENTER", "%d.%m.%Y", "id(homeassistant_time).now()")

weatherblock(5,100)
IconTempHumid(5, 400, "\U000F01E5", "id(kaczkitemp).state", "id(kaczkihumi).state")
#Water Heater Status
it.printf(5, 950, statusicons,"TextAlign::BASELINE_LEFT", "%s", "id(waterheater1).state.c_str()", "󱆴")


#Output to yaml, and demo image
it.primimage.save("demo.png")
f = open("display.yaml", "w")
f.write(it.generatefontlist())
f.write(it.generateimagelist())
f.write(it.displaydef)
f.close()
