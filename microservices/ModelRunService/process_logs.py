import pd

def ProcessLogs(model_name):
    # Get the variables to be tracked from config file in model folder
    with open(f"models/{model_name}/config.json") as f:
        config = json.load(f)

    variables = config["variables"]

    # Get the logs from the log file
    with open(f"models/{model_name}/logs.txt") as f:
        logs = f.readlines()

    # Scrape the variables from the logs
    data = {}
    for log in logs:
        for variable in variables:
            if variable in log:
                data[variable] = log.split("=")[1]

    # Save the data to a csv file
    df = pd.DataFrame(data, index=[0])
    df.to_csv(f"models/{model_name}/data.csv", index=False)