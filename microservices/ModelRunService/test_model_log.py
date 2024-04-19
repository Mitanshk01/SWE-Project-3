import requests
from model_run import run_id
from model_run import global_model_name
import pandas as pd
import os

# pass a dict named input_dict to the model log method below and store it
def ModelLog(input_dict):
    # extract all the key value pairs from the input_dict and store it in a dataframe
    os.makedirs(f"results/{global_model_name}", exist_ok=True) 

    path = f"results/{global_model_name}/{run_id}_data.csv"
    # Make sure the file exists, if not insert and empty dataframe as a cv
    if not os.path.exists(path):
        pd.DataFrame().to_csv(path, index=False)

    #load a dataframe from the csv file
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()

    new_row = pd.DataFrame(input_dict, index=[0])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)

    print("Log stored successfully.")

for i in range(10):
    if i % 2 == 0:
        ModelLog({'a': i, 'b': i*2})
    else:
        ModelLog({'a': i, 'b': i*2, 'c': i*3})
    print(f"Log {i} stored successfully.")