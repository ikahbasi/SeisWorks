import pickle
import pandas as pd
from obspy import UTCDateTime as utc
import numpy as np
import os
from seisbench.util.annotations import ClassifyOutput

def make_dataframe_from_results(lst_results_file):
    '''
    Create: 1402-05-07
    Update: 1402-06-25
    '''
    dictionary = {}
    for attribute in ['eventid', 'phasetype', 'reference_catalog',
                      'dl_phases', 'stream', 'otime', 'model_name']:
        dictionary[attribute] = []
    for ii, r_file in enumerate(lst_results_file):
        model_name = r_file.split('output_')[-1].split('_')[0]
        # print(ii, f'{(ii+1)/N*100:.2f}%', r_file)
        with open(r_file, 'rb') as fileObj:
            results = pickle.load(fileObj)
        # print(results)
        ###
        for result in results:
            # print(result)
            for attribute in ['eventid', 'phasetype', 'reference_catalog',
                              'dl_phases', 'stream', 'otime']:
                try:
                    dictionary[attribute] += [eval(f'result.{attribute}')]
                except KeyError as error:
                    print(result, error)
                    dictionary[attribute] = [eval(f'result.{attribute}')]
            dictionary['model_name'] += [model_name]
    df = pd.DataFrame(dictionary)
    return df


def get_metadata_from_name(path):
    path = path.split('_')
    for el in path:
        if 'M-' in el[:2]:
            model_name = el.split('-')[-1]
        elif 'ID-' in el[:3]:
            eventid = el.split('-')[-1]
    Dictionary = {'model_name': model_name, 'eventid': eventid}
    return Dictionary

def get_metadata_from_dir(path):
    '''
    Create: 1402-07-03
    '''
    dir_name = os.path.dirname(path)
    folder_name = os.path.basename(dir_name)
    folder_name = folder_name.split('_')
    for el in folder_name:
        if el.startswith('DPDN-'):
            DPDN = el.replace('DPDN-', '')
        elif el.startswith('filt-'):
            freqmin, freqmax = el.replace('filt-', '').split('-')
    Dictionary = {'DPDN': eval(DPDN), 'freqmin': eval(freqmin), 'freqmax': eval(freqmax)}
    return Dictionary
    
    
def picks_grouper(picks):
    '''
    Create: 1402-07-03
    '''
    group = {}
    for pick in picks:
        trid = pick.trace_id
        phasetype = pick.phase
        ID = f'{trid}_{phasetype}'
        if ID not in group:
            group[ID] = []
        group[ID].append(pick)
    return group
            
  
import progressbar
def make_dataframe_from_results_2(lst_results_file):
    '''
    Create: 1402-06-26
    Update: 1402-07-03
    '''
    bar = progressbar.ProgressBar(
        maxval=len(lst_results_file),
        widgets=[progressbar.Bar('#', '[', ']'), ' ', progressbar.Percentage()]
        )
    bar.start()
    #
    dictionary = {}
    for attribute in ['eventid', 'model_name', 'dl_phases', 'DPDN', 'freqmin', 'freqmax']:
        dictionary[attribute] = []
    len_total = len(lst_results_file)
    for ii, r_file in enumerate(lst_results_file):
        bar.update(ii)
        metadata = get_metadata_from_name(path=r_file)
        metadata_dir = get_metadata_from_dir(path=r_file)
        with open(r_file, 'rb') as fileObj:
            picks = pickle.load(fileObj)
        # print(results)
        ###
        picks_groups = picks_grouper(picks)
        for pick in picks_groups.values():
            # print(result)
            dictionary['dl_phases'] += [pick]
            for key, val in metadata.items():
                dictionary[key] += [val]
            for key, val in metadata_dir.items():
                dictionary[key] += [val]
    df = pd.DataFrame(dictionary)
    return df

def r_otime(path):
    '''
    Create: 1402-05-08
    '''
    inp = open(path, 'r')
    for line in inp:
        if 'Date & Time (UTC)' in line:
            break
    inp.close()
    line = line.strip().split()
    date = line[-2]
    time = line[-1]
    otime = utc(f'{date}T{time}')
    return otime

def eventid2catalog(Details_lst_filenames, catalog):
    '''
    Create: 1402-05-08
    '''
    eventid2otime = {}
    for f in Details_lst_filenames:
        otime = r_otime(f)
        name = os.path.basename(f)
        eventid = name.split('-')[-1].split('.')[0]
        eventid2otime[eventid] = otime

    eventid2obspy_event = {}
    for eventid, otime_sit in eventid2otime.items():
        # print(eventid)
        eventid2obspy_event[eventid] = []
        for ev in catalog:
            origin = ev.preferred_origin()
            otime_cat = origin.time
            residual = abs(otime_cat-otime_sit)
            if residual < 2:
                eventid2obspy_event[eventid].append(ev)

        if len(eventid2obspy_event[eventid]) == 0:
            eventid2obspy_event.pop(eventid)
        elif len(eventid2obspy_event[eventid]) == 1:
            eventid2obspy_event[eventid] = eventid2obspy_event[eventid][0]
        elif len(eventid2obspy_event[eventid]) > 1:
            nphases = np.array([len(ev.picks) for ev in eventid2obspy_event[eventid]])
            argmax = nphases.argmax()
            eventid2obspy_event[eventid] = eventid2obspy_event[eventid][argmax]
    return eventid2obspy_event

from obspy.geodetics.base import gps2dist_azimuth
def dist_epicenter2station(event, inventory, stationname):
    coord_station = inventory.get_coordinates(f'BI.{stationname}..SHZ')
    origin = event.preferred_origin()
    dist_m, az12, az21 = gps2dist_azimuth(lat1=origin.latitude,
                                          lon1=origin.longitude,
                                          lat2=coord_station['latitude'],
                                          lon2=coord_station['longitude'])
    dist_km = dist_m / 1000
    return dist_km


def get_iiees_stream_path(path):
    for root, dirs, files in os.walk(path):
        if files:
            f = files[0]
            out_path = f'{root}/{f}'
            break
    return out_path


def select_PickOfevent(ev, station, phase):
    '''
    Create: 1402-06-30
    '''
    found = False
    for pick in ev.picks:
        if (pick.waveform_id.station_code==station) and (pick.phase_hint.upper().startswith(phase)):
            target = pick
            found = True
            break
    if not found:
        target = False
    return target

def select_ArrivalOfPick(pick, ev):
    '''
    Create: 1402-06-30
    '''
    origin = ev.preferred_origin()
    find_arrival = False
    for arrival in origin.arrivals:
        if pick.resource_id == arrival.pick_id:
            find_arrival = True
            break
    if not find_arrival:
        find_arrival = False
    return arrival
