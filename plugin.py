# Plugin: zip-crack
# Author: Dragon-Black
# Description: ataque de fuerza bruta a archivos con el foformato zip
"""
libraries required
"""
from typing import Dict, Callable
import os

import zipfile
import itertools
import string
import time
from threading import Thread
import sys

class ZipCracker:
    def __init__(self, zip_file):
        """
        Initialize the ZIP cracker
        """
        self.zip_file = zip_file
        self.found = False
        self.password = None
        self.start_time = time.time()
        
    def try_password(self, zip_file, password):
        """
        Try to extract the ZIP file with a given password
        """
        try:
            zip_file.extractall(pwd=password.encode())
            return True
        except Exception:
            return False
    
    def dictionary_attack(self, dictionary_file):
        """
        Dictionary attack - try passwords from a wordlist
        """
        print("[*] Starting dictionary attack...")
        
        try:
            with open(dictionary_file, 'r', encoding='utf-8', errors='ignore') as f:
                words = f.readlines()
        except FileNotFoundError:
            print(f"[!] Dictionary file '{dictionary_file}' not found!")
            return False
        
        total_words = len(words)
        print(f"[*] Loaded {total_words} words from dictionary")
        
        with zipfile.ZipFile(self.zip_file, 'r') as zf:
            for i, word in enumerate(words, 1):
                if self.found:
                    return True
                    
                password = word.strip()
                
                # Try the word as-is
                if self.try_password(zf, password):
                    self.password = password
                    self.found = True
                    return True
                
                # Try with first letter uppercase
                if len(password) > 0:
                    capitalized = password[0].upper() + password[1:]
                    if self.try_password(zf, capitalized):
                        self.password = capitalized
                        self.found = True
                        return True
                
                # Progress update every 1000 attempts
                if i % 1000 == 0:
                    progress = (i / total_words) * 100
                    elapsed = time.time() - self.start_time
                    print(f"[*] Tried {i}/{total_words} passwords ({progress:.1f}%) - Time: {elapsed:.1f}s")
        
        print("[!] Dictionary attack completed - Password not found")
        return False
    
    def brute_force_attack(self, min_length=1, max_length=8, charset=None):
        """
        Brute force attack - try all possible combinations
        """
        print("[*] Starting brute force attack...")
        
        if charset is None:
            # Default charset: lowercase + uppercase + digits
            charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        
        print(f"[*] Character set: {len(charset)} characters")
        print(f"[*] Password length range: {min_length} to {max_length}")
        
        with zipfile.ZipFile(self.zip_file, 'r') as zf:
            for length in range(min_length, max_length + 1):
                if self.found:
                    return True
                    
                print(f"[*] Trying length {length}...")
                total_combinations = len(charset) ** length
                
                # Generate and try all combinations for current length
                combinations = itertools.product(charset, repeat=length)
                
                for i, combo in enumerate(combinations, 1):
                    if self.found:
                        return True
                    
                    password = ''.join(combo)
                    
                    if self.try_password(zf, password):
                        self.password = password
                        self.found = True
                        return True
                    
                    # Progress update every 10000 attempts
                    if i % 10000 == 0:
                        elapsed = time.time() - self.start_time
                        print(f"[*] Length {length}: Tried {i} combinations - Time: {elapsed:.1f}s")
                
                print(f"[*] Completed length {length}")
        
        print("[!] Brute force attack completed - Password not found")
        return False
    
    def hybrid_attack(self, dictionary_file, brute_min=1, brute_max=6):
        """
        Hybrid attack: dictionary first, then brute force
        """
        print(f"[*] Starting hybrid attack on: {self.zip_file}")
        print(f"[*] Dictionary file: {dictionary_file}")
        print(f"[*] Time started: {time.strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # Step 1: Dictionary attack
        if self.dictionary_attack(dictionary_file):
            elapsed = time.time() - self.start_time
            print(f"\n[+] Password found in dictionary attack!")
            print(f"[+] Password: {self.password}")
            print(f"[+] Time elapsed: {elapsed:.2f} seconds")
            return True
        
        print("\n" + "=" * 50)
        print("[*] Switching to brute force attack...")
        print("=" * 50)
        
        # Step 2: Brute force attack
        if self.brute_force_attack(min_length=brute_min, max_length=brute_max):
            elapsed = time.time() - self.start_time
            print(f"\n[+] Password found in brute force attack!")
            print(f"[+] Password: {self.password}")
            print(f"[+] Time elapsed: {elapsed:.2f} seconds")
            return True
        
        print("\n[!] Failed to find password with both attacks")
        return False

def create_sample_zip():
    """
    Create a sample ZIP file for testing (optional)
    """
    import os
    test_file = "test_file.txt"
    zip_name = "test_protected.zip"
    
    # Create a test file
    with open(test_file, 'w') as f:
        f.write("This is a test file for ZIP cracking demonstration.\n")
        f.write("Password: secret123\n")
    
    # Create password-protected ZIP
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.setpassword(b"secret123")  # Test password
        zf.write(test_file)
    
    # Create a sample dictionary
    dictionary = "wordlist.txt"
    common_passwords = [
        "password", "123456", "qwerty", "admin", "letmein",
        "welcome", "monkey", "dragon", "secret123", "hello123",
        "password123", "admin123", "test123", "root", "superman"
    ]
    
    with open(dictionary, 'w') as f:
        f.write("\n".join(common_passwords))
    
    print(f"[*] Created sample ZIP: {zip_name}")
    print(f"[*] Created dictionary: {dictionary}")
    print(f"[*] Test password: secret123")
    
    return zip_name, dictionary

def zip_crack():
    print("\nversion 1.0.1")
    """
    Main function to run the ZIP cracker
    """
    print("=" * 60)
    print("ZIP Password Cracker - Hybrid Attack (Dictionary + Brute Force)")
    print("=" * 60)
    
    # Create sample files for testing (comment out if not needed)
    # zip_file, dict_file = create_sample_zip()
    
    # For real usage, specify your files:
    zip_file = input("Enter ZIP file path: ").strip() or "test_protected.zip"
    dict_file = input("Enter dictionary file path: ").strip() or "wordlist.txt"
    
    # Validate files exist
    if not zipfile.is_zipfile(zip_file):
        print(f"[!] Error: {zip_file} is not a valid ZIP file!")
        return
    
    if not os.path.exists(dict_file):
        print(f"[!] Warning: Dictionary file {dict_file} not found!")
        create_dict = input("Create sample dictionary? (y/n): ").lower()
        if create_dict == 'y':
            dict_file = "wordlist.txt"
            with open(dict_file, 'w') as f:
                f.write("password\n123456\nsecret123\ntest\nadmin\n")
            print(f"[*] Created sample dictionary: {dict_file}")
        else:
            print("[!] Dictionary file is required for the first attack phase")
            return
    
    # Get brute force parameters
    try:
        min_len = int(input("Minimum password length for brute force (default: 1): ") or "1")
        max_len = int(input("Maximum password length for brute force (default: 6): ") or "6")
    except ValueError:
        print("[!] Invalid input, using defaults (1-6)")
        min_len, max_len = 1, 6
    
    # Create cracker instance and run hybrid attack
    cracker = ZipCracker(zip_file)
    
    try:
        success = cracker.hybrid_attack(
            dictionary_file=dict_file,
            brute_min=min_len,
            brute_max=max_len
        )
        
        if not success:
            print(f"\n[!] Failed to crack {zip_file} after exhaustive search")
            print(f"[!] Total time: {time.time() - cracker.start_time:.2f} seconds")
            
    except KeyboardInterrupt:
        print("\n\n[!] Attack interrupted by user")
        print(f"[*] Total time: {time.time() - cracker.start_time:.2f} seconds")
    except Exception as e:
        print(f"\n[!] Error occurred: {e}")



"""
Main function that runs when the plugin command is called
"""
def main():
    zip_crack()

"""
Function that runs when the plugin is loaded
"""
def install():
    print("zip-crack loaded successfully")


"""
This function shows a message when a plugin is removed or uninstalled
"""
def uninstall():    
    print("zip-crack was uninstalled correctly")

"""
This function shows a message when a plugin is removed or uninstalled
"""
def uninstall():
    print("zip-crack was uninstalled correctly")

"""
Function that registers additional plugin commands
"""
def register_commands() -> Dict[str, Callable]:
    return {
        "zipcrack": zip_crack
    }
