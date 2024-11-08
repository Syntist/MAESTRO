import os
import subprocess
import urllib.request
import tarfile
from pathlib import Path
import requests
import glob
from zipfile import ZipFile
import argparse

MODEL_URL = "https://github.com/pcdslab/ProteoRift/releases/download/V1.0.0/specollate_model_weights.pt"
MODEL_2_URL = "https://github.com/pcdslab/ProteoRift/releases/download/V1.0.0/proteorift_model_weights.pt"


url = f'https://api.github.com/repos/pcdslab/MAESTRO/releases/latest'
response = requests.get(url)
tag_name = response.json()["tag_name"]

def check_for_electron_app():
    """Check if any files match the pattern and return their paths."""
    files = glob.glob("maestro*")
    return files

def run_command(command, cwd=None):
    process = subprocess.Popen(command, shell=True, cwd=cwd)
    process.communicate()

def download_file(url, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, os.path.basename(url))
    if os.path.exists(filename):
        print(f"File {os.path.basename(url)} already exists in {directory}.")
    else:
        print(f"Downloading {os.path.basename(url)} to {directory}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check if the request was successful
            
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    
            print(f"Download completed: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    
    return filename

def extract_tar_gz(tar_gz_path, extract_to):
    with tarfile.open(tar_gz_path, "r:gz") as tar:
        tar.extractall(path=extract_to)
        
def extract_zip(zip_path, extract_to):
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def main():
    print("Installer Running")
    path = os.getcwd()
    print(path)

    # Create directories
    models_dir = Path(path) / "models"
    python_dir = Path(path) / ".python"
    models_dir.mkdir(exist_ok=True)
    python_dir.mkdir(exist_ok=True)

    # Copy SpeCollate to electron-app
    electron_app_dir = Path(path)
    spe_collate_dest = Path(path) / "SpeCollate"
    proteo_dest = Path(path) / "ProteoRift-main"
    app_name = ""
    
    if spe_collate_dest.exists():
        print("SpeCollate Exist")
    else:
        print("Specollate Doesn't Exist, Downloading")
        file = download_file(response.json()["zipball_url"], electron_app_dir)
        extract_zip(file, electron_app_dir)
        run_command(f"cd *-MAESTRO* && cp -r SpeCollate {electron_app_dir}")
        run_command(f"rm -rf {file}")
        run_command(f"rm -rf *-MAESTRO*")

    if proteo_dest.exists():
        print("ProteoRift Exist")
    else:
        print("ProteoRift Doesn't Exist, Downloading")
        file = download_file("https://github.com/pcdslab/ProteoRift/archive/refs/heads/main.zip", electron_app_dir)
        extract_zip(file, electron_app_dir)

        print(file)
        run_command(f"rm -rf {file}")
    
    if check_for_electron_app():
        app_name = check_for_electron_app()[0]
    else:
        download_file(response.json()["assets"][1]["browser_download_url"], electron_app_dir)
        app_name = check_for_electron_app()[0]
        
    # Download the model file
    model_filepath = download_file(MODEL_URL, models_dir)
    model_2_filepath = download_file(MODEL_2_URL, models_dir)

    # Install Python if not installed
    python_bin = python_dir / "bin/python3"
    if python_bin.exists():
        print("Python Installed")
    else:
        python_tar = download_file("https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz", python_dir)
        extract_tar_gz(python_tar, python_dir)
        python_src_dir = python_dir / "Python-3.10.14"
        os.chdir(python_src_dir)
        run_command(f"./configure --prefix={python_dir}")
        run_command(f"make -j{os.cpu_count()}")
        run_command("make install")

    # Install dependencies
    run_command(f"{python_bin} -m pip install -r {spe_collate_dest}/requirements.txt")

    # Set up .env file
    env_file = electron_app_dir / "env.json"
    if env_file.exists():
        env_file.write_text('')
        print(f"{env_file} has been emptied.")
    else:
        print("No .env file to empty.")

    with env_file.open("a") as f:
        f.write("{\n")
        f.write(f'"SPECOLLATE":"{python_bin} {spe_collate_dest}/run_search.py",\n')
        f.write(f'"PROTEORIFT":"{python_bin} {proteo_dest}/run_search.py",\n')
        f.write(f'"MODEL":"{model_filepath}",\n')
        f.write(f'"MODEL_2":"{model_2_filepath}",\n')
        f.write(f'"SPECOLLATE_CONFIG":"{Path(path)}/config.ini"\n')
        f.write("}")

    print(f"Environment variables written to {env_file}")

    # Install npm dependencies and start the Electron app
    os.chdir(electron_app_dir)

    parser = argparse.ArgumentParser(description="Script with --dev flag")
    parser.add_argument(
        '--dev', 
        action='store_true', 
        help='Run the script in development mode'
    )

    args = parser.parse_args()

    if args.dev:
        os.chdir(f"{electron_app_dir}/electron-app")
        run_command(f"npm run dev" )
    else:
        run_command(f"chmod +x {electron_app_dir}/{app_name}" )
        run_command(f"{electron_app_dir}/{app_name}")

if __name__ == "__main__":
    main()
