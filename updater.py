import requests
import os
import subprocess

# Configuration
minecraft_version = "1.21.4"
fabric_folder = os.path.expanduser("~/fabric")
mod_ids = {
    "lithium": "gvQqBUqZ",
    "carpet": "TQTTVgYE",
    "carpet_extra": "VX3TgwQh",
    "ferritecore": "uXXizFIs"
}

def get_latest_fabric_version():
    response = requests.get("https://maven.fabricmc.net/net/fabricmc/fabric-installer/maven-metadata.xml")
    body = response.text
    start = body.find("<latest>") + len("<latest>")
    end = body.find("</latest>")
    version = body[start:end]
    return version

def download_fabric():
    version = get_latest_fabric_version()
    filename = f"fabric-installer-{version}.jar"
    response = requests.get(f"https://maven.fabricmc.net/net/fabricmc/fabric-installer/{version}/fabric-installer-{version}.jar")
    if response.status_code == 200:
        os.makedirs(fabric_folder, exist_ok=True)
        file_path = os.path.join(fabric_folder, filename)
        with open(file_path, "wb") as file:
            file.write(response.content)
        subprocess.run(["java", 
                        "-jar", 
                        file_path, 
                        "server",
                        "-mcversion", minecraft_version,
                        "-dir", fabric_folder,
                        "-downloadMinecraft"])
    else:
        print(f"Fabric download failed with status code {response.status_code}")

def check_mod_version(mod_name, mod_id):
    headers = {
        "User-Agent": "Server Updater"
    }
    response = requests.get(f"https://api.modrinth.com/v2/project/{mod_id}/version", headers=headers)
    if response.status_code != 200:
        print(f"Failed to check mod '{mod_name}' with status code {response.status_code}")
        return False

    data = response.json()
    for item in data:
        if (minecraft_version in item['game_versions']) and ('fabric' in item ['loaders']):
            print(f"Mod '{mod_name}' for version {minecraft_version} found.")
            return True

    print(f"Mod '{mod_name}' for version {minecraft_version} not found.")
    return False

def download_mod(mod_name, mod_id):
    headers = {
        "User-Agent": "Server Updater"
    }
    response = requests.get(f"https://api.modrinth.com/v2/project/{mod_id}/version", headers=headers)
    if response.status_code != 200:
        print(f"Failed to download mod '{mod_name}' with status code {response.status_code}")
        return

    data = response.json() 
    download_url = None
    for item in data:
        if (minecraft_version in item['game_versions']) and ('fabric' in item['loaders']):
            download_url = item['files'][0]['url']
            break

    if download_url:
        os.makedirs(os.path.join(fabric_folder, "mods"), exist_ok=True)
        filename = os.path.basename(download_url)
        file_path = os.path.join(fabric_folder, "mods", filename)
        response = requests.get(download_url)
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Mod '{mod_name}' downloaded to {file_path}")
    else:
        print(f"Download URL not found for mod '{mod_name}'.")

if all(check_mod_version(name, id) for name, id in mod_ids.items()):
    print("All mods are available for this version. Starting download...")
    download_fabric()
    for name, id in mod_ids.items():
        download_mod(name, id)
else:
    print("Not all mods are available for this version. Download cancelled.")

print("Done")

