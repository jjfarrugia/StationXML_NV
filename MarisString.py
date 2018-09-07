# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 08:41:59 2018

@author: jfarrugia
"""

from obspy import read_inventory

class MarisString():
    def __init__(self):
        self.inv = read_inventory('NV_MarisString_September2018.dataless')
        self.locations = ['W1', 'W2', 'W3']
        self.channels = ['HNE', 'HNN', 'HNZ']
        
    def write_xmls(self):
        for l in self.locations:
            for c in self.channels:
                self.inv.select(location=l, channel=c).write('NV.KEMF.{}.{}_200.xml'.format(l, c), format='stationxml')
