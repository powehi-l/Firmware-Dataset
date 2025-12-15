import requests
import os
from ftplib import FTP
from urllib.parse import urlparse

def download_http(url, full_save_path):
    """Downloads a file from an HTTP or HTTPS URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        with open(full_save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)
        print(f"Firmware downloaded successfully via HTTP/S and saved to {full_save_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the firmware from {url}: {e}")
        return False

def download_ftp(url, full_save_path):
    """Downloads a file from an FTP URL."""
    try:
        parsed_url = urlparse(url)
        ftp = FTP(parsed_url.hostname)
        ftp.login()  # Anonymous login
        
        # It's necessary to specify the full path for the retrbinary command
        ftp.cwd(os.path.dirname(parsed_url.path))
        
        with open(full_save_path, 'wb') as file:
            ftp.retrbinary(f"RETR {os.path.basename(parsed_url.path)}", file.write)
            
        ftp.quit()
        print(f"Firmware downloaded successfully via FTP and saved to {full_save_path}")
        return True
    except Exception as e:
        print(f"Failed to download the firmware from {url} via FTP: {e}")
        # Clean up partially downloaded file
        if os.path.exists(full_save_path):
            os.remove(full_save_path)
        return False

def download_firmware(url_list, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)  # Create the folder if it doesn't exist

    for url in url_list:
        original_filename = os.path.basename(url)
        if not original_filename:
            print(f"Could not determine filename from URL: {url}")
            continue
            
        full_save_path = os.path.join(save_path, original_filename)
        
        if url.startswith('ftp://'):
            download_ftp(url, full_save_path)
        else:
            download_http(url, full_save_path)


if __name__ == '__main__':
    firmware_urls = [
        "https://static.tp-link.com/TL-WR940N(US)_V4_160617_1476690524248q.zip",
        "https://static.tp-link.com/resources/software/TL-WR1043ND_V1_140319.zip",
        "https://static.tp-link.com/resources/software/TL-WA801ND_V1_130131_beta.zip",
        "ftp://ftp.dlink.ru/pub/Router/DSR-1000AC/Firmware/DSR-1000_500_AC_A1_FW2.00.B012.zip"
    ]
    save_path = "../fws"
    download_firmware(firmware_urls, save_path)
