# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from osgeo import gdal
import numpy as np
class DTED_session:
    
    def __init__(self,dted_path,lwrlat,lwrlon,uprlat,uprlon):
        
        self.lwrlat = float(lwrlat)
        self.uprlat = float(uprlat)
        self.lwrlon = float(lwrlon)
        self.uprlon = float(uprlon)        
        self.dted_path = dted_path
        self.data_dict = {}
        lats = np.arange(int(np.floor(lwrlat)),int(np.floor(uprlat)),1)
        lons = np.arange(int(np.floor(lwrlon)),int(np.floor(uprlon)),1)
        
        for lat in lats: 
            for lon in lons: 
                self.data_finder(lat,lon,passive=True)
    

    
    def data_finder(self, lat, lon, passive = False):
        from pathlib import Path
        
        def attach(self,lat_name,lon_name,file_path):
            # has longitude been included yet
            if lon_name in self.data_dict.keys():
                # has latitude been included yet
                if lat_name in self.data_dict[lon_name].keys():
                    # data is already in dictionary; return it if not passive                    
                    if not passive:
                        return self.data_dict[lon_name][lat_name]
                # if the latitude has not been included; then include it
                elif lat_name not in self.data_dict[lon_name]:
                    self.data_dict[lon_name][lat_name] = gdal.Open(file_path)
                    # if not passive; then return the data
                    if not passive:
                        return self.data_dict[lon_name][lat_name]
            # if the longitude has not been included; then include it
            elif lon_name not in self.data_dict.keys():
                self.data_dict[lon_name] = {lat_name:gdal.Open(file_path)}
 
        #    MIL-PRF-89020B, pg 9 indicates that the directory and file names indicate
        #    the South-West corner of a DTED0 cell.
        if lon > 180. or lon < -180.:
            raise ValueError('Longitude outside bounds of convention' + str(lon)) 
        
        if lat <= -91. or lat > 90.:
            raise ValueError('Latitude outside bounds of convention: '+str(lat))
             
        if lon < .0 and lon >= -180.:
            lon_prefix = 'w'
            print(lon)
            lon_str = str(int(np.floor(lon))).split('-')[1]
    
        elif lon > -1.0 and lon < 180.:
            lon_prefix = 'e'
            lon_str = str(int(np.floor(lon)))
           
        if len(lon_str) == 2:
            lon_str = '0'+lon_str
        if len(lon_str) == 1:
            lon_str = '00' + lon_str
        
        lon_name = lon_prefix+lon_str
        
        if lat >= 0 :
            lat_prefix = 'n'
            lat_str = str(int(np.floor(lat)))
        elif lat < 0.:
            lat_prefix = 's'
            lat_str = str(int(np.floor(lat))).split('-')[1]
        
        if len(lat_str) == 1:
            lat_str = '0' + lat_str
        
        lat_name = lat_prefix + lat_str        
        
        file_path = self.dted_path+lon_name+'/'+lat_name+'.dt0'
        # check to see if the required dted file exists
        if Path(file_path).exists():
            return attach(self,lat_name,lon_name,file_path)
            if not passive:
                return self.data_dict[lon_name][lat_name]
            
        # if dted file doesn't exist; create a None entry
        if not Path(file_path).exists():
            # directory exists but no dted file
            if lon_name in self.data_dict.keys():
                self.data_dict[lon_name][lat_name] = None
            # directory does not exist    
            if lon_name not in self.data_dict.keys():
                self.data_dict[lon_name] = {lat_name:None}
            # return data if not passive
            if not passive:
                return self.data_dict[lon_name][lat_name]

                
    def get_height(self, lat, lon):
        if lat >= self.lwrlat and lat <= self.uprlat:
            if lon >= self.lwrlon and lon <= self.uprlon:
                data = self.data_finder(lat,lon)
                if data is None:
                    return None
                else:
                    gt = data.GetGeoTransform()
                    rb = data.GetRasterBand(1)
                    px = int(np.divide((lon - gt[0]),gt[1])) #x pixel
                    py = int(np.divide((lat - gt[3]),gt[5])) #y pixel
                    return rb.ReadAsArray(px,py,1,1)
    


#session = DTED_session('/home/user/data/dted/',-40,140,-30,150)
#import time
#import matplotlib.pyplot as plt
#tick = time.process_time()
#session.get_height(-37.1530586,146.4436926)
#tock = time.process_time()
#print('time taken [s] to read single point: '+str(tock-tick))
#x = np.arange(0.1,10.0,0.01)
#y = []
#for delta in x:
#    y.append(session.get_height(-40 + delta, 140 + delta))
#plt.plot(x,y)
#plt.show()