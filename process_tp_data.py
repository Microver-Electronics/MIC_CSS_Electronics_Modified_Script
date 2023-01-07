## Microver 12/20/22   - Css Electronics API script modifying
## Our comment sign is started with 2 hashtags, anothers is original code comments

import warnings
warnings.filterwarnings('ignore')
import canedge_browser, os
from utils import setup_fs, load_dbc_files, ProcessData, MultiFrameDecoder
import can_decoder
import pandas as pd
import numpy as np
import re

def extract_can_id(df):

    unique_list = list()
    for i in df['CAN ID']:
        print((str(hex(i))[-2:]))
        unique_list.append((str(hex(i))[-2:]))

def process_tp_example(devices, dbc_path, tp_type):
    fs = setup_fs(s3=False)
    db_list = load_dbc_files(dbc_paths)
    log_files = canedge_browser.get_log_files(fs, devices)

    proc = ProcessData(fs, db_list)

    for log_file in log_files:
        output_folder = "output" + log_file.replace(".MF4", "")
        if not os.path.exists(output_folder):
            os.makedirs(f"{output_folder}")

        df_raw, device_id = proc.get_raw_data(log_file)

        df_raw.to_csv(f"{output_folder}/tp_raw_data.csv")

        # replace transport protocol sequences with single frames
        tp = MultiFrameDecoder(tp_type)
        df_raw = tp.combine_tp_frames(df_raw)
        df_raw.to_csv(f"{output_folder}/tp_raw_data_combined.csv")

        #extract physical values as normal, but add tp_type
        ## We have to modify extract_phys function because this function is cauising error
        df_phys, df_ascii = proc.extract_phys(df_raw)

        ## Microver 12/26/2022
        ## POST PROCESSING

        db = can_decoder.load_dbc("dbc_files/canExt.dbc")

        signals = db.signals()  ## signal values from dbc file

        modified_df = pd.concat([df_phys, df_ascii]) ## concating ascii value table with the remaining data

        modified_df.reset_index(inplace=True)  ## Reset index to normal index

        modified_df.sort_index(ascending=True, inplace=True)

        modified_df['TimeStamp'] = pd.to_datetime(modified_df.TimeStamp, format='%Y-%m-%d %H:%M:%S')

        modified_df['TimeStamp'] = modified_df.TimeStamp.dt.ceil(freq='s')  ## Freq parameter, it's changeable

        signal_source_list = list()  ## Actual signal source list, filled with every signal source address

        for i in modified_df['CAN ID']:

            signal_source_list.append(str(hex(i))[-2:])

        modified_df['Signal Source'] = signal_source_list

        unique_source_address_list = modified_df['Signal Source'].unique() ## Unique source address list

        signal_source_engine_model_dict = dict()  ## This is the dictionary that help with which source address belongs to which engine model

        engine_model_list = list()

        for source_address in unique_source_address_list:

            signal_source_engine_model_dict[source_address] = (modified_df[modified_df['Signal Source'] == source_address][modified_df['Signal'] == 'EngineModel']['Physical Value'].values[0])

        for i in modified_df['Signal Source'].values:

            engine_model_list.append(signal_source_engine_model_dict.get(i))

        modified_df['Engine Model'] = engine_model_list

        for source_address in unique_source_address_list:

            engine_specific_df = modified_df[modified_df['Signal Source'] == source_address]

            engine_model = signal_source_engine_model_dict.get(source_address)

            engine_specific_df.to_csv(f"{output_folder}/tp_engine_specific_physical_values_{engine_model}_{source_address}.csv")

        unique_time_stamp_list = modified_df['TimeStamp'].unique() ## getting unique time stamp to group one row with signal values

        new_db_modified = pd.DataFrame() ## creating new df for output csv and adjusting

        engine_counter = 0

        serial_number_counter = 0

        for i in unique_time_stamp_list:

            print("The program is running, next time stamp is", i)

            temp_df = modified_df[modified_df['TimeStamp'] == i][['Signal', 'Physical Value', 'CAN ID', 'Signal Source', 'Engine Model']]

            row_dict = dict()

            row_dict['TimeStamp'] = i

            for j in signals:

                if(len(temp_df[temp_df['Signal'] == j]['Physical Value'].values) > 1):

                    if (j == 'EngineModel'):

                        values = np.unique(temp_df[temp_df['Signal'] == j]['Physical Value'].values)

                        if (engine_counter >= len(values)):
                            engine_counter = 0

                        if (len(values) == 1):
                            row_dict[j] = values[0]
                        else:
                            row_dict[j] = values[engine_counter]

                        engine_counter = engine_counter + 1

                    elif (j == 'EngineFwVersion'):

                        values = np.unique(temp_df[temp_df['Signal'] == j]['Physical Value'].values)

                        if (engine_counter >= len(values)):
                            engine_counter = 0

                        if (len(values) == 1):
                            row_dict[j] = values[0]
                        else:
                            row_dict[j] = values[engine_counter]

                        engine_counter = engine_counter + 1

                    elif (j == 'EngineSwVersion'):

                        values = np.unique(temp_df[temp_df['Signal'] == j]['Physical Value'].values)

                        if (engine_counter >= len(values)):
                            engine_counter = 0

                        if(len(values)==1):

                            row_dict[j] = values[0]
                        else:
                            row_dict[j] = values[engine_counter]

                        engine_counter = engine_counter + 1

                    elif (j == 'EngineSerialnumber'):

                        values = np.unique(temp_df[temp_df['Signal'] == j]['Physical Value'].values)

                        if (serial_number_counter >= len(values)):
                            serial_number_counter = 0

                        row_dict[j] = values[serial_number_counter]

                        serial_number_counter = serial_number_counter + 1

                    else:

                        row_dict[j] = temp_df[temp_df['Signal'] == j]['Physical Value'].max()

                elif (temp_df[temp_df['Signal'] == j]['Physical Value'].empty):

                    if j == 'EngineModel':

                        row_dict[j] = str(pd.unique(temp_df['Engine Model'].values)).replace('[','').replace(']','').replace("'", '')

                    else:

                        row_dict[j] = None ## if there is no value, set it to None

                else:
                    row_dict[j] = temp_df[temp_df['Signal'] == j]['Physical Value'].values.max()

            new_db_modified = new_db_modified.append(row_dict, ignore_index=True) 

        try:

            new_db_modified.set_index('TimeStamp', inplace=True)  ## If there is no TimeStamp column, ignore that

        except KeyError:

            pass

        print("Process finished")
        new_db_modified.to_csv(f"{output_folder}/tp_physical_values_modified_format.csv")  ## output csv

        ## MICROVER POST PROCESSING END ##
        df_phys.to_csv(f"{output_folder}/tp_physical_values.csv")
        df_ascii.to_csv(f"{output_folder}/tp_physical_values_ascii.csv")

    print("Finished saving CSV output for devices [Physical Values, Physical Values ASCII, Modifyed Format of Result CSV and Engine Specific Messages CSV ]:", devices)

# ----------------------------------------
# run different TP examples

# OxeMarine - Product Information removed from dbc
#devices = ["LOG/4D7DC2F1_PI_removed"]
#dbc_paths = [r"dbc_files/canExt_PI_removed.dbc"]
#process_tp_example(devices, dbc_paths, "nmea")

# OxeMarine
devices = ["LOG/4D7DC2F1"]
dbc_paths = [r"dbc_files/canExt.dbc"]
process_tp_example(devices, dbc_paths, "nmea")

#devices = ["LOG/4D7DC2F1"]
#dbc_paths = [r"dbc_files/canExt_ascii.dbc"]
#process_tp_example(devices, dbc_paths, "asc,,")


"""
# UDS data from Hyundai Kona EV (SoC%)
devices = ["LOG/17BD1DB7"]
dbc_paths = [r"dbc_files/tp_uds.dbc"]
process_tp_example(devices, dbc_paths, "uds")

# UDS data from Nissan Leaf 2019 (SoC%)
devices = ["LOG/2F6913DB"]
dbc_paths = [r"dbc_files/tp_uds_nissan.dbc"]
process_tp_example(devices, dbc_paths, "uds")

# J1939 TP data
devices = ["LOG/FCBF0606"]
dbc_paths = [r"dbc_files/tp_j1939.dbc"]
process_tp_example(devices, dbc_paths, "j1939")

# NMEA 2000 fast packet data (with GNSS position)
devices = ["LOG/94C49784"]
dbc_paths = [r"dbc_files/tp_nmea.dbc"]
process_tp_example(devices, dbc_paths, "nmea")
"""