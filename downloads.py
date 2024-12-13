import requests
from config import ya_token, link_to_ya
import os

def download_files_from_yandex(public_url, oauth_token, save_folder):
    """
    Download files from a public folder on Yandex Disk using OAuth token.

    :param public_url: URL of the public folder on Yandex Disk
    :param oauth_token: OAuth token for accessing Yandex Disk API
    :param save_folder: Local folder to save the downloaded files
    """
    # Step 1: Get public resources metadata
    base_url = "https://cloud-api.yandex.net/v1/disk/public/resources"
    params = {"public_key": public_url, "limit": 100}  # Limit can be adjusted
    headers = {"Authorization": f"OAuth {oauth_token}"}

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching metadata: {response.status_code}, {response.text}")

    metadata = response.json()

    # Ensure save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Step 2: Iterate over items in the public folder
    items = metadata.get("_embedded", {}).get("items", [])
    if not items:
        raise Exception("No files found in the public folder.")

    for item in items:
        file_name = item["name"]
        file_url = item.get("file")

        if file_url:
            # Step 3: Download each file
            download_response = requests.get(file_url)
            if download_response.status_code == 200:
                file_path = os.path.join(save_folder, file_name)
                with open(file_path, "wb") as file:
                    file.write(download_response.content)
                print(f"File downloaded successfully to {file_path}")
            else:
                print(f"Error downloading file {file_name}: {download_response.status_code}, {download_response.text}")
        else:
            print(f"Skipping {file_name}: No downloadable URL.")


# Usage example
public_url = link_to_ya  # Replace with your public folder URL
oauth_token = ya_token  # Replace with your OAuth token
save_path = "temp/123"     # Replace with your desired save path

try:
    download_files_from_yandex(public_url, oauth_token, save_path)
except Exception as e:
    print(f"Error: {e}")