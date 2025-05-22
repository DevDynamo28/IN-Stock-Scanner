import os
import glob

# Directory where watchlist text files are saved
WATCHLIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'watchlist'))


def load_latest_watchlist():
    """Return a list of symbols from the most recent watchlist file.

    If no watchlist files exist, an empty list is returned.
    """
    pattern = os.path.join(WATCHLIST_DIR, 'tv_watchlist_*.txt')
    files = glob.glob(pattern)
    if not files:
        return []
    latest = max(files, key=os.path.getmtime)
    with open(latest, 'r') as fh:
        symbols = [line.strip() for line in fh if line.strip()]
    return symbols
