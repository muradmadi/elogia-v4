import sys
sys.path.insert(0, '.')

try:
    from app.core.config import Settings
    print("Settings import successful")
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()