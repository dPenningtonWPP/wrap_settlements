from ftplib import FTP
import requests
from datetime import datetime, timedelta
import os


def list_or_download_from_powerdex_ftp(hostname, username, password, remote_filepath=None, local_filepath=None):
    """
    Connects to an FTP server. If no remote_filepath is provided, lists files in the current directory.
    If remote_filepath is provided, downloads the file.

    :param hostname: The FTP server hostname.
    :param username: The username to authenticate with.
    :param password: The password to authenticate with.
    :param remote_filepath: The path of the file on the FTP server (optional).
    :param local_filepath: The path where the file should be saved locally (optional).
    """
    try:
        # Connect to the FTP server
        ftp = FTP(hostname)
        print(f"Connecting to FTP server at {hostname}...")
        ftp.login(user=username, passwd=password)
        print("Login successful.")

        if not remote_filepath:
            # List files and directories in the current directory
            print(ftp.pwd())
            ftp.cwd("/")  # Change to the root directory
            print("Root directory:", ftp.pwd())
            ftp.retrlines("LIST")  # List the contents of the root directory
            print("No file specified. Listing contents of the current directory:")
            ftp.retrlines("LIST")
            return

        # If no local filepath is provided, use the remote file's name in the current directory
        if not local_filepath:
            local_filepath = os.path.basename(remote_filepath)

        # Change to the directory containing the file (optional)
        remote_dir = os.path.dirname(remote_filepath)
        if remote_dir:
            ftp.cwd(remote_dir)
            print(f"Changed directory to: {remote_dir}")

        # Download the file
        with open(local_filepath, 'wb') as local_file:
            print(f"Downloading {remote_filepath} to {local_filepath}...")
            ftp.retrbinary(f"RETR {os.path.basename(remote_filepath)}", local_file.write)

        print(f"File downloaded successfully: {local_filepath}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'ftp' in locals():
            ftp.quit()
            print("Disconnected from FTP server.")

# Example usage
if __name__ == "__main__":
    FTP_HOST = "ftp.example.com"       # Replace with your FTP server
    FTP_USER = "username"              # Replace with your username
    FTP_PASS = "password"              # Replace with your password

    # Case 1: List directory contents
    list_or_download_from_powerdex_ftp(FTP_HOST, FTP_USER, FTP_PASS)

    # Case 2: Download a specific file
    list_or_download_from_powerdex_ftp(FTP_HOST, FTP_USER, FTP_PASS, "/path/to/remote/file.txt", "downloaded_file.txt")


def download_caiso_shaping_factors_zip(start_date=None):
    """
    Downloads a zip file from the CAISO OASIS API and saves it to the "input_data/caiso_shaping_factors" folder.
    If no start_date is provided, it defaults to yesterday's date.

    :param start_date: (Optional) A string representing the start date in "YYYY-MM-DD" format.
    """
    try:
        # Determine the start_date
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Create the target directory if it doesn't exist
        save_dir = "input_data/caiso_shaping_factors"
        os.makedirs(save_dir, exist_ok=True)
        
        # Convert start_date to the required format
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        formatted_date = start_datetime.strftime("%Y%m%dT08:00-0000")
        
        # Construct the URL
        url = f"http://oasis.caiso.com/oasisapi/GroupZip?version=12&resultformat=6&groupid=DAM_HRLY_ENE_SHAPING_FCTR_GRP&startdatetime={formatted_date}"
        
        # Make the request
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        # Extract filename from Content-Disposition header, fallback to a default name
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = (
            content_disposition.split("filename=")[-1].split(";")[0].strip('"') if "filename=" in content_disposition
            else f"{start_date}_shaping_factors.zip"
        )
        
        # Full path to save the file
        save_path = os.path.join(save_dir, filename)
        
        # Save the zip file
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"File successfully downloaded and saved to {save_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # Explicit date
    download_caiso_shaping_factors_zip("2024-11-19")

    # Default to yesterday
    download_caiso_shaping_factors_zip()


def download_caiso_location_margin_prices(
    start_date=None,
    start_time="08:00",
    end_time="09:00",
    market_run_id="RTPD",
    node="PALOVRDE_ASR-APND",
):
    """
    Downloads a zip file from the CAISO OASIS SingleZip API and saves it to a specified folder.
    Defaults to yesterday's date for the time range if start_date is not provided.

    :param start_date: (Optional) A string representing the start date in "YYYY-MM-DD" format.
    :param start_time: (Optional) Start time in "HH:MM" format (defaults to "08:00").
    :param end_time: (Optional) End time in "HH:MM" format (defaults to "09:00").
    :param market_run_id: (Optional) Market run ID (defaults to "RTPD").
    :param node: (Optional) Node identifier (defaults to "PALOVRDE_ASR-APND").
    """
    try:
        # Determine the start_date
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Format start and end datetime
        start_datetime = f"{start_date}T{start_time}-0000"
        end_datetime = f"{start_date}T{end_time}-0000"
        
        # Construct the URL
        url = (
            f"http://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_SPTIE_LMP"
            f"&version=5&startdatetime={start_datetime}&enddatetime={end_datetime}"
            f"&market_run_id={market_run_id}&node={node}"
        )
        
        # Create the target directory if it doesn't exist
        save_dir = "input_data/caiso_lmp"
        os.makedirs(save_dir, exist_ok=True)
        
        # Make the request
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        # Extract filename from Content-Disposition header, fallback to a default name
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = (
            content_disposition.split("filename=")[-1].split(";")[0].strip('"') if "filename=" in content_disposition
            else f"{start_date}_SingleZip_{start_time}_{end_time}.zip"
        )
        
        # Full path to save the file
        save_path = os.path.join(save_dir, filename)
        
        # Save the zip file
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"File successfully downloaded and saved to {save_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    # Download for a specific date and time
    download_caiso_location_margin_prices("2024-11-19", "08:00", "10:00")

    # Default to yesterday with standard times
    download_caiso_location_margin_prices()
