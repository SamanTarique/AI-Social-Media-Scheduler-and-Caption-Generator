
"""
check_env_setup.py — Run this FIRST to debug why the Gemini key isn't found.

Usage:
    python check_env_setup.py

It checks each step separately so you can see exactly where it breaks.
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"1. This script's folder: {SCRIPT_DIR}")

env_path = os.path.join(SCRIPT_DIR, ".env")
print(f"2. Looking for .env at:  {env_path}")

if os.path.exists(env_path):
    print("   -> FOUND a file named exactly '.env'. Good.")
else:
    print("   -> NOT FOUND. Common causes:")
    print("      - It might be saved as '.env.txt' instead of '.env'")
    print("      - It might be in a different folder than this script")
    # Helpful: list anything in this folder that looks env-related
    candidates = [f for f in os.listdir(SCRIPT_DIR) if "env" in f.lower()]
    if candidates:
        print(f"      - Files with 'env' in the name found here: {candidates}")
    else:
        print("      - No env-related files found in this folder at all.")

print()
print("3. Loading .env with python-dotenv...")
from dotenv import load_dotenv
loaded = load_dotenv(dotenv_path=env_path)
print(f"   load_dotenv() returned: {loaded}  (True = it found and read a .env file)")

print()
print("4. Checking if the key is now visible in os.environ...")
raw_value = os.environ.get("Saman_Gemini_API_Key")
print(f"   os.environ.get('Saman_Gemini_API_Key') = {raw_value!r}")

if raw_value:
    print(f"\n✅ SUCCESS — key found, starts with: {raw_value[:8]}...")
else:
    print("\n❌ STILL NOT FOUND. Double-check:")
    print("   - The .env file has EXACTLY this line (no quotes, no spaces around =):")
    print("     Saman_Gemini_API_Key=your_actual_key_here")
    print("   - There's no typo in the variable name")
    print("   - You saved the file after editing it")