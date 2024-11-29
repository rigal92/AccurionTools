#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 08:02:20 2024

@author: shunokano
"""

from pyccurion.nanofilm.ndimage import imread
import matplotlib.pyplot as plt

path = 'tests/Data/MoS2GE04_00_20240828-112719_Delta_0051.png'
mapdata = imread(path)

print(mapdata)

# mapdata.tofile("tests/out")
