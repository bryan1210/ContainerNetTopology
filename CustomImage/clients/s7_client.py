# clients/s7_client.py
import sys
import struct
import snap7
from snap7.util import get_word

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 102
    db   = int(sys.argv[3]) if len(sys.argv) > 3 else 1   # DB number
    size = int(sys.argv[4]) if len(sys.argv) > 4 else 10  # bytes to read

    client = snap7.client.Client()
    # rack/slot don't matter for the server emulator; use 0/1
    client.connect(host, 0, 1, port)
    if not client.get_connected():
        raise SystemExit("S7: failed to connect")

    # Read DB <db> from byte 0, length <size>
    data = client.db_read(db, 0, size)

    # Show raw bytes and first 16-bit word at offset 0
    word0 = get_word(data, 0) if len(data) >= 2 else None
    print(f"S7 DB{db} raw bytes: {list(data)}")
    print(f"S7 DB{db} word@0: {word0}")

    client.disconnect()

if __name__ == "__main__":
    main()
