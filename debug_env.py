import os
from dotenv import load_dotenv

def debug():
    print(f"Current CWD: {os.getcwd()}")
    env_path = os.path.join(os.getcwd(), '.env')
    print(f"Looking for .env at: {env_path}")
    print(f"File exists: {os.path.exists(env_path)}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"--- Raw Content Start ---")
            print(content)
            print(f"--- Raw Content End ---")

    load_dotenv()
    print("Called load_dotenv()")
    
    key = os.getenv("SHIOAJI_API_KEY")
    print(f"SHIOAJI_API_KEY is: {'[SET]' if key else '[NONE]'}")
    if key:
        print(f"Length: {len(key)}")
        print(f"First 3 chars: {key[:3]}")

if __name__ == "__main__":
    debug()
