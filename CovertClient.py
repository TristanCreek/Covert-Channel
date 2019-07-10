""""@package CovertClient covert channel to exfiltrate data
"""
import sys
from scapy.all import *


def Store_Base64_To_IPv4(base64_char):
    """!@brief Craft TCP packet with a Base64 character in
        the most significant byte of the sequence value
    @param base64_char Base64 character to store in the sequence value
    @return packet scapy IPv4 packet with Base64 character stored in the sequence value
    """

    # rd - recursion desired, qd=
    recv = sr(IP(dst="127.0.0.1")/TCP(dport=[21,22,23]))
    recv.show()

def main():
    """!@main calls all helper functions
    """
    Store_Base64_To_IPv4("AB")


if __name__ == "__main__":
    main()