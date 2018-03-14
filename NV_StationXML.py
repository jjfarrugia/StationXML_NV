# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 12:45:56 2018

@author: jfarrugia
"""

# Here are the packages we need
import obspy
from obspy.core.inventory import Inventory, Network, Station, Channel, Site
from obspy.clients.nrl import NRL
from ruamel import yaml
from datetime import datetime
from obspy.core.inventory.util import ExternalReference
import os
from ast import literal_eval

############################## SA_ULN Respone #################################
from obspy import read_inventory
# Load instrument response manually; not available through the IRIS NRL
SA_ULN_RESP = read_inventory(r'RESP.XX.NS401..BNZ.203_60V.0_5G.txt', format='RESP')[0][0][0].response

#Import the meta data bank to Python dictionary
with open(r'_calibrations.yaml', 'r') as file:
    stream = file.read()
    file.close()
calibrations = yaml.safe_load(stream)
with open(r'_metadata.yaml', 'r') as file:
    stream = file.read()
    file.close()
bank = yaml.safe_load(stream)

# Initialize the empty-Inventory with bare-minimum required variables
inv = Inventory(
    networks=[], # We'll add networks later.
    source='Joseph Farrugia, Ocean Networks Canada', # The source should be the id whoever create the file.
    created = obspy.UTCDateTime(datetime.today())
    )
# By default this accesses the NRL online
nrl = NRL()

# Loop to construct the filled-Inventory
Networks = bank['Networks']
for network in bank['Networks'].keys():
    # Write network to the Inventory
    _net_end_date = Networks[network]["To"]
    if _net_end_date == "None":
        _net_end_date = literal_eval(_net_end_date)
    else:
        _net_end_date = obspy.UTCDateTime(_net_end_date)
        
    _network = Network(
            code = network,
            start_date = obspy.UTCDateTime(Networks[network]["From"]),
            end_date = _net_end_date,
            description = Networks[network]["_description"]
            )
    inv.networks.append(_network)
    
    Stations = bank['Networks'][network]['Stations']
    for station in Stations.keys():
        print('---\n' + station + '\n')
        
        try:
            # Write the station to the Inventory
            _end_date = Stations[station]["To"]
            if _end_date == "None":
                _end_date = literal_eval(_end_date)
            else:
                _end_date = obspy.UTCDateTime(_end_date)
            
            _station = Station(
                    code = station,
                    latitude = Stations[station]["_latitude"],
                    longitude = Stations[station]["_longitude"], 
                    elevation = Stations[station]["_elevation"], 
                    start_date = obspy.UTCDateTime(Stations[station]["From"]),
                    creation_date = obspy.UTCDateTime(Stations[station]["From"]),
                    end_date = _end_date,
                    site = Site(name=Stations[station]["_site"]),
                    geology = Stations[station]["_geology"],
#                    equipments = obspy.core.inventory.Equipment(description = Stations[station]["_equipments"],
                    description = Stations[station]["_description"]
                    )
            _network.stations.append(_station)
            
        except TypeError: 
            print('That metadata has not been assigned yet.')
        
        try:
            Epochs = bank['Networks'][network]['Stations'][station]['Epoch']
            for epoch in Epochs.keys():
                try:
                    Channels = bank['Networks'][network]['Stations'][station]['Epoch'][epoch]['Channels']
                    for channel in Channels.keys():
                        _channel_code = channel.split('-')[0]
                        #currently we need to manually load in the instruemnt response for Silicon Audio ULN Accelerometer
                        if Channels[channel]["_sensor_type"] == "SA_ULN":
                            _dl_resp = nrl.get_datalogger_response(
                                    datalogger_keys = Channels[channel]['_datalogger_keys']
                                    )
                            _sensor_resp = SA_ULN_RESP
                            _dl_resp.response_stages.pop(0)
                            _dl_resp.response_stages.insert(0, _sensor_resp.response_stages[0])
                            _response = _dl_resp
                            if Channels[channel]["_equipment_serial"][0].endswith("40Vpg"):
                                 _response.response_stages[4].stage_gain = _response.response_stages[4].stage_gain * float(2/3)
                        
                        #all other responses can be reached at the IRIS NRL
                        else:
                            _response = nrl.get_response(
                                sensor_keys = Channels[channel]['_sensor_keys'],
                                datalogger_keys = Channels[channel]['_datalogger_keys']
                                )
                        
                        #apply sensor calibrations from manufacturer sheets
                        _sc = calibrations['Calibrations'][Channels[channel]["_equipment_serial"][0]]
                        if (_sc['EW'] and _sc['NS'] and _sc['UD']) != "already_calibrated":
                        
                            if _channel_code.endswith('E') or _channel_code.endswith('2'):
                                _sensor_calibs = _sc['EW']
                            elif _channel_code.endswith('N') or _channel_code.endswith('1'):
                                _sensor_calibs = _sc['NS']
                            elif _channel_code.endswith('Z'):
                                _sensor_calibs = _sc['UD']
                        
                            _response.response_stages[0].stage_gain = _sensor_calibs
                        
                        #apply digitizer/datalogger calibrations from manufacturer sheets
                        _dc = calibrations['Calibrations'][Channels[channel]["_equipment_serial"][1]][Channels[channel]["_sensor_type"]]
                        if (_dc['EW'] and _dc['NS'] and _dc['UD']) != "already_calibrated":
                        
                            if _channel_code.endswith('E') or _channel_code.endswith('2'):
                                _datalogger_calibs = 1/_dc['EW']
                            elif _channel_code.endswith('N') or _channel_code.endswith('1'):
                                _datalogger_calibs = 1/_dc['NS']
                            elif _channel_code.endswith('Z'):
                                _datalogger_calibs = 1/_dc['UD']
                                
                            _response.response_stages[2].stage_gain = _datalogger_calibs
                            
                        _response.recalculate_overall_sensitivity()
                        
                        # Construct the channel; these are the channel attributes that need to be specified, or left empty "" if not known.
                        
                        try:
                            #take lat, lon, elev from Channels if it's defined (same station, different Location)
                            lat = Channels[channel]["_latitude"]
                            lon = Channels[channel]["_longitude"]
                            elev = Channels[channel]["_elevation"]
                        except:
                            #take from Stations if not defined under Channels
                            lat = Stations[station]["_latitude"]
                            lon = Stations[station]["_longitude"]
                            elev = Stations[station]["_elevation"]
                        
                        _channel_end_date = epoch.split("_")[1]
                        if _channel_end_date == "None":
                            _channel_end_date = literal_eval(_channel_end_date)
                        else:
                            _channel_end_date = obspy.UTCDateTime(_channel_end_date)
                            
                        _channel = Channel(
                                code = _channel_code,
                                location_code = Channels[channel]['_location_code'],
                                latitude = lat,
                                longitude = lon,
                                elevation = elev,
                                depth = Channels[channel]["_depth"],
                                start_date = obspy.UTCDateTime(epoch.split("_")[0]),
                                end_date = _channel_end_date,
                                azimuth = Channels[channel]["_azimuth"],
                                dip = Channels[channel]["_dip"],
                                types = Channels[channel]["_types"],
                                sample_rate = Channels[channel]["_sample_rate"],
                                equipment = obspy.core.inventory.Equipment(description = Channels[channel]["_equipment_description"], serial_number = Channels[channel]["_equipment_serial"]),
                                sensor = obspy.core.inventory.Equipment(description = Channels[channel]["_sensor_description"], serial_number = Channels[channel]["_equipment_serial"]),
                                response = _response,
                                external_references = [ExternalReference(Channels[channel]["_dataSearchURL"], 'Data Search URL.'),
                                                       ExternalReference(Channels[channel]["_deviceURL"], 'Device URL.')]
                                )
                        _station.channels.append(_channel)
                        
                        print("Channel {}.{} appended successfully to Inventory.".format(_channel_code, Channels[channel]['_location_code']))
                except:
                    print("Check that metadata assignments are correct for station: {}".format(station))
        except:
            print("No epochs assigned to station: {}".format(station))
            
print("\n\n###\nInventory: \n", inv)
     
# Write the Inventory to StationXML
print("""\n\nWriting StationXML file to "{}".""".format(os.getcwd()))
inv.write("NV_ONC.xml", format="stationxml", validate=True)

from obspy.io.stationxml.core import validate_stationxml
print("\n\nStationXML is valid? {}.".format(validate_stationxml('NV_ONC.xml')[0]))
if validate_stationxml('NV_ONC.xml')[1] == ():
    print("\t - No errors were found.")
else:
    print("Errors found: {}".format(validate_stationxml('NV_ONC.xml')[1]))