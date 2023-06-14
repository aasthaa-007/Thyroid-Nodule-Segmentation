from pathlib import Path
from numpy import ndarray
from skimage.morphology import dilation, erosion
from PIL import ImageDraw,Image
import numpy as np
from os.path import splitext


class Thyroid_Main:
    directory_of_images = None
    directory_for_output = None
    directory_of_masks = None

    def __init__(self,file_name,numberTag,subscript,pointsList,tirads,nod_num,part):
        # identity of every image captured from the xml file
        self.numberTag = numberTag    
        self.nod_num = nod_num  
        self.subscript = subscript  
        self.part = part        
        self.pointsList = pointsList    # points list
        self.pointsList.append(self.pointsList[0])

        self.tirads = tirads    # tirads values

        self.file_name = splitext(file_name)[0] + f'_{self.subscript}' + '.jpg'  # image's name
        self.img = Image.open(Thyroid_Main.directory_of_images +"/"+ self.file_name).convert('L')  # PIL's image

        self.nod = None
        self.mask = None

        self.up = 0
        self.right = 0
        self.down = 0
        self.left = 0

    @classmethod
    def Get_Directory(cls, directory_of_images: Path, directory_for_output: Path, directory_of_masks: Path):
        cls.directory_of_images = directory_of_images
        cls.directory_for_output = directory_for_output
        cls.directory_of_masks = directory_of_masks

    def removing_border(self, bar=10):
        """removing border"""
        mask_value = np.asarray(self.mask)
        nodule = np.asarray(self.nod)
               
        curr_row = np.mean(nodule, axis=1)
        nodule = nodule[curr_row > bar, :]
        mask_value = mask_value[curr_row > bar, :]

        curr_col = np.mean(nodule, axis=0)
        nodule = nodule[:, curr_col > bar]
        mask_value = mask_value[:, curr_col > bar]

        self.nod = Image.fromarray(nodule).resize((300, 300))
        self.mask = Image.fromarray(mask_value).resize((300, 300))
        
        # print(self.nod)
        # print(nodule);
        # print("mask")
        # print(mask_value)
    
    def draw_mask(self):
        self.mask = Image.new(mode='1', size=self.img.size, color=1)

        drawing_mask = ImageDraw.Draw(self.mask)
        for i in range(len(self.pointsList)-1):
            x1 = self.pointsList[i]['x']
            y1 = self.pointsList[i]['y']

            x2 = self.pointsList[i+1]['x']
            y2 = self.pointsList[i+1]['y']

            drawing_mask.line((x1, y1, x2, y2), width=5, fill=0)

    def resize_nodule(self, border=30):
        horizontal_list = [point['x'] for point in self.pointsList]
        vertical_list = [point['y'] for point in self.pointsList]

        self.up = max(0, min(vertical_list) - border)
        self.right = min(self.img.width, max(horizontal_list) + border)
        self.down = min(self.img.height, max(vertical_list) + border)
        self.left = max(0, min(horizontal_list) - border)        

        self.nod = self.img.crop((self.left, self.up, self.right, self.down)).resize((300, 300))
        self.mask = self.mask.crop((self.left, self.up, self.right, self.down)).resize((300, 300))

    def fill_mask_with_color(self):
        image = np.asarray(self.mask)
        img_copy = np.copy(image)
        q_point = [(0, 0)]
        seen_queue = set()
        seen_queue.add((0, 0))
        while len(q_point) > 0:
            x, y = q_point.pop()
            img_copy[x, y] = 0
            # neighbours
            neis = [(x + 1, y),
                    (x - 1, y),
                    (x, y - 1),
                    (x, y + 1)]
            for nei in neis:
                x0 = nei[0]
                y0 = nei[1]
                if (nei not in seen_queue) and x0 >= 0 and y0 >= 0 and x0 < self.mask.width \
                        and y0 < self.mask.height and img_copy[x0, y0] != 0:
                    q_point.append(nei)
                    seen_queue.add(nei)
        self.mask = Image.fromarray(img_copy)

    def erode_dilate(self, e=3, d=5):
        img = np.asarray(self.mask)
        cross = np.array([[0, 1, 0],
                          [1, 1, 1],
                          [0, 1, 0]])
        for i in range(e):
            img = erosion(img, cross)
        for i in range(d):
            img = dilation(img, cross)
        self.mask = Image.fromarray(img)

    def save(self):
        Thyroid_Main.directory_for_output.mkdir(parents=True, exist_ok=True)
        Thyroid_Main.directory_of_masks.mkdir(parents=True, exist_ok=True)

        # img has two nodules
        if self.nod_num == 2:
            file_png = (splitext(self.file_name)[0] + f'({self.part}).png')
            file_gif = (splitext(self.file_name)[0] + f'({self.part}).gif')
            out_path = Thyroid_Main.directory_for_output / file_png
            mask_path = Thyroid_Main.directory_of_masks / file_gif

            self.nod.save(out_path, quality=100)
            self.mask.save(mask_path, quality=100)
        # one nodule in image
        else:
            self.nod.save(Thyroid_Main.directory_for_output / (splitext(self.file_name)[0] + '.png'), quality=100)
            self.mask.save(Thyroid_Main.directory_of_masks / (splitext(self.file_name)[0] + '.gif'), quality=100)


