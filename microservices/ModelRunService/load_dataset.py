import requests


def LoadDataset(dataset_name):
    # Make an HTTP GET request to the API endpoint with the dataset_name as a parameter
    response = requests.get(f"https://api.example.com/datasets/{dataset_name}")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the directory information from the response
        directory = response.json()["directory"]

        # Continue with the rest of your code using the directory information
        # ...

    else:
        # Handle the case when the request fails
        print("Failed to retrieve the directory information from the API.")

# Call the LoadDataset function with the dataset_name parameter
LoadDataset("example_dataset")




