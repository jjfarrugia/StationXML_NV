# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 08:41:59 2018

@author: jfarrugia
"""

from obspy import read_inventory, read, Stream
import sys
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

class MarisString():
    def __init__(self):
        self.maris_inv = read_inventory(r'\\ONC-FILESERVER\redirect4\jfarrugia\Documents\GitHub\StationXML_NV\NV_MarisString_September2018.dataless')
        self.locations = ['W1', 'W2', 'W3']
        self.channels = ['HNE', 'HNN', 'HNZ']
        
    def write_xmls(self):
        for l in self.locations:
            for c in self.channels:
                self.maris_inv.select(location=l, channel=c).write('NV.KEMF.{}.{}_200.xml'.format(l, c), format='stationxml')
                
    def load_slarchive_mseed(self, starttime=None, endtime=None, station='KEMF', sr=200.0):
        """
        Accesses the Google Drive folder "slarchive\data2" for MSEED files from the Maris String.
        
        Instrument correction and some basic filtering is applied.
        """
        root = tk.Tk()
        root.withdraw()
        
        self.hne_mseed_paths = filedialog.askopenfilenames(initialdir=r'G:\Team Drives\ONC_Seismic_Data\slarchive\data2\2018\NV\KEMF\HNE.D', 
                                                        title='Choose HNE files')
        self.hnn_mseed_paths = filedialog.askopenfilenames(initialdir=r'G:\Team Drives\ONC_Seismic_Data\slarchive\data2\2018\NV\KEMF\HNN.D', 
                                                        title='Choose HNN files')
        self.hnz_mseed_paths = filedialog.askopenfilenames(initialdir=r'G:\Team Drives\ONC_Seismic_Data\slarchive\data2\2018\NV\KEMF\HNZ.D', 
                                                        title='Choose HNZ files')
        
        self.st = Stream()
        for file in self.hne_mseed_paths:
            try:
                for tr in read(file, format='mseed'):
                    self.st.append(tr)
                    
            except:
                print("Unexpected error on HNE load:", sys.exc_info())
                continue     
        for file in self.hnn_mseed_paths:
            try:
                for tr in read(file, format='mseed'):
                    self.st.append(tr)
                    
            except:
                print("Unexpected error on HNN load:", sys.exc_info())
                continue     
        for file in self.hnz_mseed_paths:
            try:
                for tr in read(file, format='mseed'):
                    self.st.append(tr)
                    
            except:
                print("Unexpected error on HNZ load:", sys.exc_info())
                continue                    
        
        for tr in self.st:
            if tr.stats.sampling_rate != sr:            
                tr.stats.sampling_rate = sr
        self.onc_inv = read_inventory(r'\\ONC-FILESERVER\redirect4\jfarrugia\Documents\GitHub\ONC_StationXML\NV_StationXML.xml')
        self.st.remove_response(self.onc_inv, output='acc', pre_filt=(0.01, 0.1, 50, 100))
        return self.st
            
        

        
