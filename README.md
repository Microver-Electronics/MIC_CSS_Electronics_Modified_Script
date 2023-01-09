# Microver CSS Electronics API Script Fixing

![Microver](/microver.jpeg "Microver")

## Modified Files

- utils.py
- process_tp_data.py

## What We Have Done?

- Firstly, we solved the problem of not being able to convert ascii data from log file to result csv -> utils.py 101:325
- Secondly, we change the result csv to one row per event with data in columns. -> process_tp_data.py 45:204
- Lastly, we setted the granularity to adjust to minimum of 100 milisecond. -> process_tp_data.py 36:130
- Null engine model column fill -> process_tp_data.py 45:220

**If you want to change the granularity to 1 second, please check the lines 60:60 in the process_tp_data.py**

## Run

- pip install -r requirements.txt

*if you installed required packages*
- python process_to_data.py


## Output Files

- \output\LOG\4D7DC2F1\[LOG]\[LOG_]\tp_physical_values_modified_format.csv
- \output\LOG\4D7DC2F1\[LOG]\[LOG_]\tp_engine_specific_physical_values_[Engine Model]_[Source Address].csv
- \output\LOG\4D7DC2F1\00000002\00000002-63878C18\tp_physical_values_ascii.csv