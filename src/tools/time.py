from datetime import datetime

def get_time():
    """Return the current time in a nice format."""
    return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
