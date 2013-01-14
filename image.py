from flask import Flask, send_file, abort
from PIL import ImageFont, Image, ImageDraw
from StringIO import StringIO
import re


if __name__ == "__main__":
    app = Flask(__name__)

def getFont(size):
    #XXX Change this to match your system
    #TODO try a list of known fonts on both Linux and Windows so this can be left as is
    return ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", size)

@app.route('/img/<sz>')
def gen_image(sz):
    #try-catch to stop whole app from falling over - we don't give a damn about this functionality so that's safe.
    try:
        #Check the format of the sz parameter is valid, i.e. something like this: 12345x12345
        if (re.match('\A\d*x\d*\Z', sz) is None):
            abort(400) #400 is invalid syntax

        #parse the image dimensions
        x=int(sz.split('x')[0])
        y=int(sz.split('x')[1])

        #bounds check for sanity
        if (x >4096 or x <=0 or y > 4096 or y <= 0):
            #stop before they exhaust RAM
            abort(400) #400 is invalid syntax

        #Create a temp stream and colour grey:
        tmp = StringIO()
        img=Image.new("RGBA", (int(x),int(y)),(128,128,128))

        #calculate the max font size we can fit
        fontSize = 0
        while (True):
            fontSize = fontSize + 1
            f=getFont(fontSize)
            #make sure the font fits:
            (fontx, fonty) = f.getsize(sz)
            if (fontx >= x or fonty >= y):
                #back of by 1pt to fit in the border of the image
                f=getFont(fontSize - 1)
                break
            #yeah, gettin a bit stupid, stop and just give them big letters
            if (fontSize >= 100):
                break;

        #calculate the pixel locations to perfectly center the text
        (fontx, fonty) = f.getsize(sz)
        fontx = (x/2)-(fontx/2)
        fonty = (y/2)-(fonty/2)

        #render the text
        draw = ImageDraw.Draw(img) #create draw object using the image as the buffer
        draw.text((fontx,fonty), sz, (255, 255, 255), font=f) #render the text onto the image

        #write to the temp string and rewind to the start for the send_file flask api
        img.save(tmp, format="JPEG", quality=70)
        tmp.seek(0,0)

        #MIME type will tell browser to render the image as JPEG.
        return send_file(tmp, mimetype='image/jpeg')
    except Exception as ex:
        #TODO return some sort of error message to the user, for now just return 500 (internal server error)
        abort(500)

if __name__ == '__main__':
    app.run(debug=True)
