#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 08:02:20 2024

@author: shunokano
"""

from pyccurion.reader import read_map
import matplotlib.pyplot as plt

path = "/home/rigal/Documents/Research/SPIN/Experiment/2D/Transfer/Marzia/260315WS2@Agholes/Accurion/maps/Sample_aged2_x20_AOI38_20260519-151923.ds.dat"
mapdata = read_map(path)

# print(mapdata)

# mapdata.tofile("tests/out")
