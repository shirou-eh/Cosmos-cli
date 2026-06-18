import keyboard
import time

_key_events = []

def _key_callback(event):
    if event.event_type == keyboard.KEY_DOWN:
        _key_events.append(event.name)

try:
    keyboard.hook(_key_callback)
except Exception:
    pass # Might fail without sudo, but user requested keyboard module.

def get_key_timeout(timeout=0.1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if _key_events:
            return _key_events.pop(0)
        time.sleep(0.01)
    return None

def clear_key_queue():
    _key_events.clear()
