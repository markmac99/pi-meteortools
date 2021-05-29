#
# annotate an image with station info and meteor count
#

from PIL import Image, ImageFont, ImageDraw 
import sys
import datetime


def annotateImage(img_path, title, metcount):
    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), title, font=fnt, fill=(255))
    metmsg = 'meteors: {:04d}'.format(metcount)
    image_editable.text((width-7*fntheight-15,height-fntheight-15), metmsg, font=fnt, fill=(255))
    my_image.save(img_path)


if __name__ == '__main__':
    now = datetime.datetime.now()
    statid = sys.argv[2]
    title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))
    annotateImage(sys.argv[1], title, int(sys.argv[3]))
