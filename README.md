# Covert-Channel
Installation
1. On Ubuntu 18.04, apt install Python 3.6 and python-pip3
2. Use pip3 to install flask, opencv, bitstring, and numpy
3. Ensure the global variables in CovertClient.py identify the CovertServer IP address and the paths for the data file to hide, the image to hide it in, and the path to write the new image containing the hidden data to.
4. Ensure the global variables in CovertServer.py identify the path to write the exfiltrated image and extracted data to.
5. Run CovertServer.py on own box.
  1. export FLASK_APP=CovertServer.py
  2. run flask --host=0.0.0.0
6. Run CovertClient.py on victim box to exfiltrate data to CovertServer.

1. A numbered list
    1. A nested numbered lis
    2. Which is numbered
2. Which is numbered
