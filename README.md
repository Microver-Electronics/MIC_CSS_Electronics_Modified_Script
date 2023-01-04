# Microver CSS Electronics API Script Fixing

![Microver](/microver.jpeg "Microver")

## Modified Files

- utils.py
- process_tp_data.py

## What We Have Done?

- Firstly, we solved the problem of not being able to convert ascii data from log file to result csv -> utils.py 101:325
- Secondly, we change the result csv to one row per event with data in columns. -> process_tp_data.py 36:130
- Lastly, we setting the granularity to adjust to minimum of 0.1 second. -> process_tp_data.py 36:130

## Run

- pip install -r requirements.txt

*if you installed required packages*
- python process_to_data.py

## Output Files

- \output\LOG\4D7DC2F1\00000002\00000002-63878C18\tp_physical_values_modified_format.csv
- \output\LOG\4D7DC2F1\00000002\00000002-63878C18\tp_physical_values_ascii.csv