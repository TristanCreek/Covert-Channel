# Covert-Channel
Installation
1. On Ubuntu 18.04, apt install Python 3.6 and python-pip3
2. Use pip3 to install flask, opencv, bitstring, and numpy
3. Ensure the global variables in CovertClient.py identify the CovertServer IP address and the paths for the data file to hide, the image to hide it in, and the path to write the new image containing the hidden data to.
4. Ensure the global variables in CovertServer.py identify the path to write the exfiltrated image and extracted data to.
5. Run CovertServer.py on own box.
5.1. export FLASK_APP=CovertServer.py
5.2. run flask --host=0.0.0.0
6. Run CovertClient.py on victim box to exfiltrate data to CovertServer.
