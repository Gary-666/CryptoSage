from datetime import datetime
import time


def iso_to_timestamp(iso_string):
    """
    Convert ISO format time string to a UNIX timestamp.
    """
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))  # Handle UTC time
        return int(dt.timestamp())
    except Exception as e:
        print(f"Error converting ISO to timestamp: {e}")
        return None


