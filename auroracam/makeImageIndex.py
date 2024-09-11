import glob
import os
import sys
import shutil


def createLatestIndex(here):
    mp4list = glob.glob(os.path.join(here, '*.mp4'))
    jpglist = glob.glob(os.path.join(here, '*.jpg'))
    jpglist.sort()
    

    with open(os.path.join(here, 'latestindex.js'), 'w') as jsfile:
        jsfile.write('$(function() {\n')

        jsfile.write('var outer_div = document.getElementById("vid-list");\n')
        jsfile.write('var h3 = document.createElement("h3");\n')
        jsfile.write('h3.innerText = "Timelapse";\n')
        jsfile.write('outer_div.appendChild(h3);\n')
        for fil in mp4list:
            fil = os.path.basename(fil)
            jsfile.write('var a = document.createElement("a");\n')
            jsfile.write('var img = document.createElement("img");\n')
            jsfile.write(f'img.src="{os.path.basename(jpglist[-1])}";\n')
            jsfile.write('img.style.width="10%";\n')
            jsfile.write('a.appendChild(img);\n')
            jsfile.write(f'a.href="{fil}";\n')
            jsfile.write('outer_div.appendChild(a);\n\n')

        jsfile.write('var outer_div = document.getElementById("cam-list");\n')
        jsfile.write('var h3 = document.createElement("h3");\n')
        jsfile.write('h3.innerText = "Images";\n')
        jsfile.write('outer_div.appendChild(h3);\n')
        for fil in jpglist:
            fil = os.path.basename(fil)
            jsfile.write('var a = document.createElement("a");\n')
            jsfile.write('var img = document.createElement("img");\n')
            jsfile.write(f'img.src="{fil}";\n')
            jsfile.write('img.style.width="10%";\n')
            jsfile.write('a.appendChild(img);\n')
            jsfile.write(f'a.href="{fil}";\n')
            jsfile.write('outer_div.appendChild(a);\n\n')
        jsfile.write('})')

    dstidx = os.path.join(here, 'index.html')
    if not os.path.isfile(dstidx):
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        srcidx = os.path.join(srcdir, 'imgindex.html.template')
        shutil.copy(srcidx, dstidx)
    return


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python createLatestIndex.py /path/to/image/folder')
    else:
        createLatestIndex(sys.argv[1])
