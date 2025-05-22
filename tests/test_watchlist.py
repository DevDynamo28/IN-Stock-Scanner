import os
import tempfile
from tools import watchlist


def test_load_latest_watchlist(tmp_path):
    # create two watchlist files
    f1 = tmp_path / "tv_watchlist_2024-01-01.txt"
    f1.write_text("AAPL\nMSFT")
    f2 = tmp_path / "tv_watchlist_2024-01-02.txt"
    f2.write_text("GOOG")

    # patch module directory to our temp dir
    original_dir = watchlist.WATCHLIST_DIR
    watchlist.WATCHLIST_DIR = str(tmp_path)
    try:
        symbols = watchlist.load_latest_watchlist()
        assert symbols == ["GOOG"]
    finally:
        watchlist.WATCHLIST_DIR = original_dir

