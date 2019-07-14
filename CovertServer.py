#!/usr/bin/python3
"""@package CovertServer covert server to collect exfiltrated data
"""

import sys
import cv2
from bitstring import BitArray, BitStream
import numpy as np
import json

default_path_to_image = "hidden.png"
default_path_to_data = "extracted.txt"


from flask import Flask, request
app = Flask(__name__)
@app.route('/', methods=['POST'])
def result():
    f = request.files['file']
    try:
        fd = open("hidden2.png", "wb")
        fd.write(f.read())
        fd.close()
    except:
        print("Failed to write image to disk.")
    extract_data(default_path_to_image, default_path_to_data)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}



def print_usage():
    """!@brief Print usage information if user 
        provides help arguments or provides too many arguments
    """
    print("This script hides a file's data inside an image.")
    print("Two options to run script:")
    print("    python3 covert.py")
    print("    ./covert.py")
    print("The script hides data from secret.txt in the hello.jpg image by default")
    print("    Both default files must reside in same directory as covert.py")
    print("The first argument defines a custom image")
    print("    ./covert.py image.jpg")
    print("The second argument defines a custom data file")
    print("    ./covert.py image.jpg data.txt")
    print("A custom image name must be provided whenever a custom data file name is provided")


def check_args():
    """!@brief Parse command line arguments.
    Print usage information and exit if user inputs help arguments or inputs too many arguments.
    Declare path_to_image and path_to_data variables based on provided arguments.
    """
    # Print usage information if user input -h or --help as an argument
    if ("-h" or"--help") in sys.argv:
        print_usage()
        sys.exit()

    # User provides no custom names, use default image and data file paths
    if len(sys.argv) == 1:
        return default_path_to_image, default_path_to_data

    # User only provides custom image name
    elif len(sys.argv) == 2:
        return sys.argv[1], default_path_to_data
    
    # User provides custom image and data file name
    elif len(sys.argv) == 3:
        return sys.argv[1], sys.argv[2]
    
    # Print usage information if user provides too many arguments
    elif len(sys.argv) > 3:
        print(" - Too many arguments provided. See usage information below. -")
        print()
        print_usage()
        sys.exit()


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
