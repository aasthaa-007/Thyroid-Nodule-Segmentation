from xml.etree import ElementTree
from pathlib import Path
from os import listdir
from os.path import splitext
import json
from Thyroid_Main import Thyroid_Main
import csv
from tqdm import tqdm
directory_of_images = "C:/Users/suraj/Desktop/Group_40_preprocessing/Archive"
directory_for_output = Path('./cropped')
directory_of_masks = Path('./mask')

Thyroid_Main.Get_Directory(directory_of_images, directory_for_output, directory_of_masks)

def file_filter_xml_files(f):
    if splitext(f)[1] in ['.xml']:
        return True
    else:
        return False

files = listdir(directory_of_images)
files = list(filter(file_filter_xml_files, files))

f = open('category.csv', 'w', newline='')
csv_writer = csv.writer(f)

with tqdm(total=len(files)) as pbar:
    for file in files:
        tree = ElementTree.parse(directory_of_images +"/"+ file)
        root = tree.getroot()

        numberTag = int(list(root.iter(tag='number'))[0].text)
        tirads = list(root.iter(tag='tirads'))[0].text

        marks = list(root.iter(tag='mark'))
        for mark in marks:
            
            subscript = int(list(mark.iter(tag='image'))[0].text)

            svg_ = list(mark.iter(tag='svg'))[0].text
            svgs = []
            try:
                svgs = json.loads(svg_)  # list
            except:
                continue
            finally:
                nod_num = len(svgs)
                if nod_num != 1:
                    nod_num = 2

                for i, svg in enumerate(svgs):
                    pointsList = svg['points']
                    thy_object = Thyroid_Main(file_name=file,
                                    numberTag=numberTag,
                                    subscript=subscript,
                                    tirads=tirads,
                                    pointsList=pointsList,
                                    nod_num=nod_num,
                                    part=i+1)
                    thy_object.draw_mask()
                    thy_object.resize_nodule()
                    thy_object.fill_mask_with_color()
                    thy_object.erode_dilate()
                    thy_object.removing_border()
                    thy_object.save()
                    # print("thyobject")
                    # print(thy_object)
                    if thy_object.nod_num == 2:
                        item = f'{splitext(thy_object.file_name)[0]}({thy_object.part})'
                    else:
                        item = f'{splitext(thy_object.file_name)[0]}'

                    label = thy_object.tirads
                    bi_label = ''
                    if label in ['5', '6','4a', '4b', '4c']:
                        bi_label = 1
                    elif label in ['1', '2', '3']:
                        bi_label = 0

                    csv_writer.writerow((item, str(thy_object.tirads), bi_label))
        pbar.update(1)
f.close()

