import pandas as pd
import os


def ModelLog(input_dict, run_id):
    print("Printing run_id: ", run_id)
    
    logs_path = f"results/{run_id}/logs.csv"
    os.makedirs(f"results/{run_id}", exist_ok=True) 

    if not os.path.exists(logs_path):
        pd.DataFrame().to_csv(logs_path, index=False)

    try:
        df = pd.read_csv(logs_path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()
    
    print("Input dictionary: ", input_dict)
    # access the new row from the input dictionary and keep it at first position
    new_row = pd.DataFrame([input_dict])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(logs_path, index=False)

    print("Log stored successfully.")
    print("Logs: ", df)
