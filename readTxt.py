"""
Read text files using numpy genfromtxt.

Da Pan, 02112016
"""

import numpy as np


def read(filename, hlines, delimiter='\t'):
    """Read text files and return headlines and data

    :param filename: str

    :param hlines: number of headlines

    :param delimiter: str

    :param fTarget: if set, data will be save to fTarget

    :return hstr: list of str

    :return narray: 1d or 2d data
    """

    # Open file to read headlines
    f = open(filename)
    hstr = []

    for i in range(hlines):
        hstr.append(f.readline())

    f.close()

    # Use numpy genfromtxt to read data
    data = np.genfromtxt(filename, delimiter=delimiter, skip_header=hlines)

    return hstr, data


def main():
    hstr, data = read(r'D:\Biochar_NH3_data\NH3_3.lvm', 22)


if __name__ == '__main__':
    main()
