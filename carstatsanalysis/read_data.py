#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import pandas as pd
import numpy as np

def parse_long_string(inpstr):
    if type(inpstr) != str:
        print inpstr
        return
    DIRECTIONS = 'NEWS'
    DIRECTIONS = {'N': +1, 'S': -1, 'E': +1, 'W': -1}
    inpstr = re.sub('[\xc2\xb0\'"]','',inpstr)
    ent = inpstr.split()
    degree = int(ent[0])
    minutes = int(ent[1])
    seconds = int(ent[2])
    direction = ent[3]
    if direction not in DIRECTIONS:
        print 'bad direction'
        exit(0)
    lval = (degree + minutes/60. + seconds/3600.)
    return lval

def read_data():
    car_columns = ['lapno', 'laplength', 'laptime', 'laptime2', 'speed', 'lataccel', 
                'longaccel', 'temperature', 'steering_angle', 'rpm', 'engine_temp', 
                'gear', 'height', 'longitude', 'latitude', 'lat_string', 'long_string']

    #print help(pd.read_csv)
    df = pd.read_csv('data.csv', sep=';', header=None, names=car_columns)

    #print df.shape
    #print df.columns
    #print df.head()
    df['longitude'] = df['long_string'].apply(parse_long_string)
    df['latitude'] = df['lat_string'].apply(parse_long_string)
    
    print df.describe()
    
    #print df.head()
    minlon, maxlon = df['longitude'].min(), df['longitude'].max()
    minlat, maxlat = df['latitude'].min(), df['latitude'].max()
    
    with open('MAP_TEMPLATE.html', 'r') as inphtml:
        with open('index.html', 'w') as outhtml:
            for line in inphtml:
                if 'SPORTTITLEDATE' in line:
                    outhtml.write(line.replace('SPORTTITLEDATE', 'CarData'))
                elif 'CENTRALLAT' in line or 'CENTRALLON' in line:
                    outhtml.write(line.replace('CENTRALLAT', '%s' % ((maxlat+minlat)/2.)).replace('CENTRALLON', '%s' % ((maxlon+minlon)/2.)))
                elif 'ZOOMVALUE' in line:
                    outhtml.write(line.replace('ZOOMVALUE', '14'))
                elif 'INSERTMAPSEGMENTSHERE' in line:
                    for idx in range(df.shape[0]):
                        if pd.isnull(df['latitude'].iloc[idx]) or pd.isnull(df['longitude'].iloc[idx]):
                            continue
                        outhtml.write('new google.maps.LatLng(%f,%f),\n' % (df['latitude'].iloc[idx], df['longitude'].iloc[idx]))
                else:
                    outhtml.write(line)
    
if __name__ == '__main__':
    read_data()