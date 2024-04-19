import requests
from model_run import run_id
from model_run import global_model_name
import pandas as pd
import os

def ModelLog():

    # combime two dictionaries globals() and locals()
    variables = {**locals(), **globals()}
    print(variables)

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

    print(df)

    # Every variable in variables is a column in the dataframe, if the variable is not in the dataframe, it will be added as a new column
    df = df.append(variables, ignore_index=True)

    print(df)


    # Save the dataframe to the csv file
    df.to_csv(path, index=False)
    



    print("Log stored successfully.")


for i in range(10):
    ModelLog()