import requests 
import zipfile
import io
import os


def LoadModel(model_name):
    # API endpoint URL
    api_url = 'http://your_api_endpoint_here'
    
    # Parameters to be sent with the request
    params = {'model_name': model_name}
    
    try:
        # Sending GET request to the API endpoint
        response = requests.get(api_url, params=params)
        
        # Checking if request was successful (status code 200)
        if response.status_code == 200:
            link = response.json()['link']
            # Sending GET request to the link provided in the response
            response = requests.get(link)

            if response.status_code != 200:
                print("Failed to load dataset '{}'. Status code: {}".format(model_name, response.status_code))
                return

            # Create a zipfile object from the response content
            with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
                # Extract all the contents of the zip file
                os.makedirs(f'./data/{model_name}', exist_ok=True)
                zip_ref.extractall(f'./data/{model_name}')  
                # You can specify the directory where you want to store the files
            print("Dataset '{}' successfully loaded and extracted.".format(model_name))
        else:
            print("Failed to load dataset '{}'. Status code: {}".format(model_name, response.status_code))
    except Exception as e:
        print("An error occurred:", e)