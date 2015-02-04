#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def parse_long_string(inpstr):
    if type(inpstr) != str:
        print inpstr
        return inpstr
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

    df['longitude'] = df['long_string'].apply(parse_long_string)
    df['latitude'] = df['lat_string'].apply(parse_long_string)
    
    print df.describe()
    
    minlon, maxlon = df['longitude'].min(), df['longitude'].max()
    minlat, maxlat = df['latitude'].min(), df['latitude'].max()
    
    if not os.path.exists('html'):
        os.makedirs('html')
    plot_files = []
    for col in ['laplength', 'speed', 'temperature', 'rpm', 'engine_temp', 'height']:
        plt.clf()
        df[col].hist()
        plt.title('Histogram of %s' % col)
        plt.savefig('html/%s_hist.png' % col)
        plot_files.append('%s_hist.png' % col)
    
    exit(0)
    df = df.drop(['lapno'], axis=1)
    nonzero_lap = df['laplength'] > 0
    df = df[nonzero_lap]
    print df.columns
    pd.scatter_matrix(df, diagonal='hist')
    plt.title('Scatter Matrix')
    plt.savefig('html/scatter_matrix.png')
    plot_files.append('scatter_matrix.png')
    
    with open('MAP_TEMPLATE.html', 'r') as inphtml:
        with open('html/index.html', 'w') as outhtml:
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
                elif 'INSERTOTHERIMAGESHERE' in line:
                    for plot_file in plot_files:
                        outhtml.write('<p>\n<img src="%s">\n</p>' % plot_file)
                else:
                    outhtml.write(line)
    return df
    
if __name__ == '__main__':
    read_data()