# src/tools/wifi.py
import subprocess

def show_wifi_passwords() -> str:
    """
    Retrieves all saved Wi-Fi profiles and their passwords on Windows.
    """
    try:
        # Step 1: Get all Wi-Fi profile names
        profiles_data = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'],
            shell=True,
            text=True
        )
        profiles = []
        for line in profiles_data.splitlines():
            if "All User Profile" in line:
                name = line.split(":")[1].strip()
                profiles.append(name)

        if not profiles:
            return "No Wi-Fi profiles found."

        # Step 2: Retrieve password for each profile
        result = ""
        for profile in profiles:
            try:
                password_data = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                    shell=True,
                    text=True
                )
                password = "None"
                for line in password_data.splitlines():
                    if "Key Content" in line:
                        password = line.split(":")[1].strip()
                        break
                result += f"Wi-Fi: {profile} | Password: {password}\n"
            except subprocess.CalledProcessError:
                result += f"Wi-Fi: {profile} | Password: Unable to retrieve\n"
        
        return result.strip()

    except subprocess.CalledProcessError:
        return "Error: Unable to access Wi-Fi profiles. Are you running this as administrator?"
