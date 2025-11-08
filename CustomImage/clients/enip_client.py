# client_enip.py
import sys
from contextlib import closing
from cpppo.server.enip import client

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 44818
    timeout = 3.0

    # 1) TCP connector (opens/closes the socket)
    with closing(client.connector(host=host, port=port, timeout=timeout)) as conn:
        # 2) Wrap in a SimpleClient (request queue/handler)
        with client.queue.SimpleClient(connection=conn) as simple:

            # --- Read Pump1:Speed ---
            print("[ENIP] Reading Pump1:Speed ...")
            ops = [client.read_tag("Pump1:Speed")]
            for req, reply, status in simple.synchronous(ops, timeout=timeout):
                if status is None and reply is not None:
                    print("  Pump1:Speed =", reply)
                else:
                    print("  Read failed:", status)

            # --- Write Pump1:Running = True (BOOL) ---
            print("[ENIP] Writing Pump1:Running = True ...")
            ops = [client.write_tag("Pump1:Running", True, dtype=client.BOOL)]
            for req, reply, status in simple.synchronous(ops, timeout=timeout):
                if status is None:
                    print("  Write OK")
                else:
                    print("  Write failed:", status)

            # --- Read Pump1:Running and Tank1:Level ---
            print("[ENIP] Reading Pump1:Running and Tank1:Level ...")
            ops = [
                client.read_tag("Pump1:Running"),
                client.read_tag("Tank1:Level"),
            ]
            for idx, (req, reply, status) in enumerate(simple.synchronous(ops, timeout=timeout)):
                name = getattr(req, "tag", f"op{idx}")
                if status is None and reply is not None:
                    print(f"  {name} =", reply)
                else:
                    print(f"  {name} read failed:", status)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
