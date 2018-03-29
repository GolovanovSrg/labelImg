#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import codecs


JSON_EXT = '.json'
ENCODE_METHOD = 'utf-8'


class NeuromationWriter:
    def __init__(self, foldername, filename):
        self.foldername = foldername
        self.filename = filename
        self.boxlist = []
        self.verified = False

    def addBndBox(self, xmin, ymin, xmax, ymax, name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax, 'name': name, 'difficult': difficult}
        self.boxlist.append(bndbox)

    def save(self, label_to_id, targetFile=None):
        boxes = {}
        for box in self.boxlist:
            box_id = label_to_id[box['name']]

            if box_id not in boxes:
                boxes[box_id] = []

            box_info = {'boundingBox': {'X': box['xmin'],
                                        'Y': box['ymin'],
                                        'Width': box['xmax'] - box['xmin'],
                                        'Height': box['ymax'] - box['ymin']}}

            boxes[box_id].append(box_info)

        boxes = [{'id': id, 'data': data} for id, data in boxes.items()]

        output_path = self.filename + JSON_EXT if targetFile is None else targetFile
        with codecs.open(output_path, 'w', encoding=ENCODE_METHOD) as output:
            json.dump(boxes, output)


class NeuromationReader:
    def __init__(self, filepath, image, label_to_id, id_to_label):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.verified = True

        img_size = [image.height(), image.width(), 1 if image.isGrayscale() else 3]

        with codecs.open(filepath, 'r', encoding=ENCODE_METHOD) as input:
            data = json.load(input)

        for item in data:
            if 'class' in item:
                id = item['class']
                if id not in id_to_label:
                    label_to_id[id] = id
                    id_to_label[id] = id

                label = id_to_label[id]
                x_min = int(item['boxes']['x_min'] * img_size[1])
                y_min = int(item['boxes']['y_min'] * img_size[0])
                x_max = int(item['boxes']['x_max'] * img_size[1])
                y_max = int(item['boxes']['y_max'] * img_size[0])

                self.addShape(label, x_min, y_min, x_max, y_max, False)

            elif 'id' in item:
                id = item['id']
                if id not in id_to_label:
                    label_to_id[id] = id
                    id_to_label[id] = id

                label = id_to_label[id]

                for box in item['data']:
                    x_min = box['boundingBox']['X']
                    y_min = box['boundingBox']['Y']
                    x_max = x_min + box['boundingBox']['Width']
                    y_max = y_min + box['boundingBox']['Height']

                    self.addShape(label, x_min, y_min, x_max, y_max, False)

            else:
                assert False, "Wrong format"

    def getShapes(self):
        return self.shapes

    def addShape(self, label, xmin, ymin, xmax, ymax, difficult):
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, points, None, None, difficult))
