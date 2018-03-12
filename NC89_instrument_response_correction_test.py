# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:10:29 2018

@author: jfarrugia
"""

#%% Get some raw data from IRIS to pass through our new stationXML file
from obspy import read_inventory
inv = read_inventory('NV_ONC.xml', format="XML")
plotting_flag = 1

if plotting_flag==1:
    from obspy.clients.iris import Client
    client = Client(timeout = 100)
    from obspy import UTCDateTime
    import pandas as pd
    import matplotlib.pyplot as plt
    
    start_t = UTCDateTime("2018-01-10T03:00:00")
    end_t = start_t + 60*30
    st_e = client.timeseries(
            network = 'NV', 
            station = 'NC89', 
            location = None, 
            channel = 'HHE', 
            starttime = start_t, 
            endtime = end_t,
            filter = ['decimate=5.0']
            )
    st_e_noresponse = st_e.remove_response(inventory=inv, output='ACC')
    st_e_noresponse.write('E_honduras_correct_response.dat', format='TSPAIR')
    
    st_n = client.timeseries(
            network = 'NV', 
            station = 'NC89', 
            location = None, 
            channel = 'HHN', 
            starttime = start_t, 
            endtime = end_t,
            filter = ['decimate=5.0']
            )
    st_n_noresponse = st_n.remove_response(inventory=inv, output='ACC')
    st_n_noresponse.write('N_honduras_correct_response.dat', format='TSPAIR')
    
    st_z = client.timeseries(
            network = 'NV', 
            station = 'NC89', 
            location = None, 
            channel = 'HHZ', 
            starttime = start_t, 
            endtime = end_t,
            filter = ['decimate=5.0']
            )
    st_z_noresponse = st_z.remove_response(inventory=inv, output='ACC')
    st_z_noresponse.write('Z_honduras_correct_response.dat', format='TSPAIR')
    
    df_seis = pd.read_csv('E_honduras_correct_response.dat', 
                         delim_whitespace = True, 
                         names = ['t','ae'], 
                         index_col = ['t'], 
                         skiprows = 1, 
                         skipfooter = 1, 
                         engine = 'python', 
                         infer_datetime_format = True, 
                         parse_dates = True
                         )
    
    df_seis['an'] = pd.read_csv('N_honduras_correct_response.dat', 
                         delim_whitespace = True, 
                         names = ['t','an'], 
                         index_col = ['t'], 
                         skiprows = 1, 
                         skipfooter = 1, 
                         engine = 'python', 
                         infer_datetime_format = True, 
                         parse_dates = True
                         )
    
    df_seis['az'] = pd.read_csv('Z_honduras_correct_response.dat', 
                         delim_whitespace = True, 
                         names = ['t','az'], 
                         index_col = ['t'], 
                         skiprows = 1, 
                         skipfooter = 1, 
                         engine = 'python', 
                         infer_datetime_format = True, 
                         parse_dates = True
                         )
    
    df_apt = pd.read_csv(r'\\synbak.onc.uvic.ca\SciShare\Joe\RBR_APT\data\APT_COMPLETE_CALIBRATED\RBRTILTMETERACCBPR63055_20180110T000000.000Z-CALIBRATED-ALIGNED.acc', 
                         names = ['t_logger','t_log_corr','ax','ay','az','P','P_temp','Z_temp'], 
                         index_col = ['t_log_corr'],
                         engine = 'python', 
                         skiprows = 1, 
                         infer_datetime_format = True, 
                         parse_dates = True
                         )
    
    df_apt_slice = df_apt[df_apt.index < '2018-01-10 03:30:00.000000']
    df_apt_slice = df_apt_slice[df_apt_slice.index > '2018-01-10 03:00:00.000000']
    x2 = df_apt_slice.index.to_pydatetime()
    x1 = df_seis.index.to_pydatetime()
    y1 = (df_seis['ae'] - df_seis['ae'].mean()).values
    y2 = (df_seis['an'] - df_seis['an'].mean()).values
    y3 = (df_seis['az'] - df_seis['az'].mean()).values
    y4 = (df_apt_slice['ax'] - df_apt_slice['ax'].mean()).values
    y5 = (df_apt_slice['ay'] - df_apt_slice['ay'].mean()).values
    y6 = (df_apt_slice['az'] - df_apt_slice['az'].mean()).values
    
    fig = plt.subplots(nrows = 3, ncols = 1)
    ax1 = plt.subplot(311)
    plt.plot(x1, y1, ls ='-', color = 'grey', label = 'NC89, E')
    plt.plot(x2, y4, ls = '--', color = 'black', label = 'APT, E')
    plt.legend(loc = 'upper right')
    ax1.grid(axis = 'both')
    
    ax2 = plt.subplot(312, sharex=ax1, sharey=ax1)
    plt.plot(x1, y2, ls ='-', color = 'grey', label = 'NC89, N')
    plt.plot(x2, y5, ls = '--', color = 'black', label = 'APT, N')
    ax2.set_ylabel('Acceleration [m/s/s]')
    plt.legend(loc = 'upper right')
    ax2.grid(axis = 'both')
    
    ax3 = plt.subplot(313, sharex=ax1, sharey=ax1)
    plt.plot(x1, y3, ls ='-', color = 'grey', label = 'NC89, Z')
    plt.plot(x2, y6, ls = '--', color = 'black', label = 'APT, Z')
    plt.legend(loc = 'upper right')
    ax3.grid(axis = 'both')
    plt.xlabel('Time')