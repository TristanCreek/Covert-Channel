# Covert-Channel
## About
Covert communication channel developed to exfiltrate data via an HTTP POST request that contains a 4K PNG (3840 x 2160 pixels) data payload. The covert client stores secret data to exfiltrate in the two least significant bits of each color component (red, green, and blue) of each pixel in an image. This provides a maximum secret data payload of 5.93 MB per image.

Testing with the client and server on the same box yielded a max throughput of 12.48 MB/s. This requires the user to smartly leverage the available secret data storage within the image because the covert client does NOT split data larger than 5.93 MB into multiple images. The covert client implements a hard limit at 5.93 MB per file and simply fails if the data to exfiltrate exceeds that limit.

We provide data.txt and image.png to test this covert channel. The covert client hides data.txt insides image.png by default given both files exist in the same directory as CovertClient.py when ran. The user can change the file names at the top of CovertClient.py to use custom payload files.

I only guarantee this covert channel for 3840 x 2160 PNG images. Other sizes of lossless image formats should work, but I make no guarantees. For this covert channel to work, you MUST use a lossless format image such as PNG. Lossy image formats like JPG fail to maintain the integrity of the secret data.

## Installation
### Victim Box

1. On Ubuntu 18.04, apt install Python 3.6 and python-pip3
    1. sudo apt install python3.6 python-pip3
2. Use pip3 to install opencv, bitstring, and numpy
    1. sudo pip3 install opencv-python bitstring numpy
3. Ensure the global variables in CovertClient.py identify the CovertServer IP address and the paths for the data file to hide, the image to hide it in, and the path to write the new image containing the hidden data to.


### Personal Box

1. On Ubuntu 18.04, apt install Python 3.6 and python-pip3
    1. sudo apt install python3.6 python-pip3
2. Use pip3 to install flask, opencv, bitstring, and numpy
    1. sudo pip3 install flask opencv-python bitstring numpy
3. Ensure the global variables in CovertServer.py identify the path to write the exfiltrated image and extracted data to.


## Exfiltrate File
1. Run CovertServer.py on personal box.
    1. export FLASK_APP=CovertServer.py
    2. run flask --host=0.0.0.0
2. Run CovertClient.py on victim box to exfiltrate data to CovertServer.
    1. ./CovertServer.py

## Credits
Developed by me, @NickBratsch, and an anonymous man of many great capabilties.
