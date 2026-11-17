#!/usr/bin/env python3
"""Bounded IN-only probe of the unbound G7 SE diagnostic interface.

Uses a pinned, separately downloaded Deadband checkout's native libusb wrapper.
GET_INTERFACE / SET_INTERFACE are used; no vendor OUT requests or writes.
"""
import argparse
import json
from pathlib import Path
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deadband', required=True)
    parser.add_argument('--sysfs', default='/sys/bus/usb/devices/1-6')
    parser.add_argument('--seconds', type=float, default=120)
    args = parser.parse_args()
    root = Path(args.sysfs)
    identity = {name: (root / name).read_text().strip()
                for name in ('idVendor', 'idProduct', 'bcdDevice', 'busnum', 'devnum')}
    if (identity['idVendor'], identity['idProduct']) != ('3537', '1010'):
        raise SystemExit('Unexpected identity; refusing probe')
    interface = root / (root.name + ':1.2')
    if (interface / 'driver').exists():
        raise SystemExit('Interface 2 has a driver; refusing detach')
    main_driver = (root / (root.name + ':1.0') / 'driver').resolve()
    sys.path.insert(0, args.deadband)
    from tools.g7se_probe import ProbeHandle
    handle = None
    packets = timeouts = 0

    def log(**data):
        print(json.dumps({'time': time.time(), **data}), flush=True)

    log(action='identity', identity=identity, main_driver=str(main_driver))
    try:
        handle = ProbeHandle.open(0x3537, (0x1010,), int(identity['busnum']),
                                  int(identity['devnum']), str(root), 2, 1, 0x81)
        log(action='reading', interface=2, endpoint='0x81',
            original_alt=handle.original_alt, seconds=args.seconds)
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            packet = handle.read(64, timeout_ms=200)
            if packet:
                packets += 1
                log(action='packet', hex=packet.hex())
            else:
                timeouts += 1
    except KeyboardInterrupt:
        log(action='interrupted')
    except Exception as exc:
        log(action='error', error=str(exc))
        raise
    finally:
        if handle is not None:
            handle.close()
            log(action='cleanup', results=handle.cleanup)
        log(action='summary', packets=packets, timeouts=timeouts,
            main_driver_unchanged=(root / (root.name + ':1.0') / 'driver').resolve() == main_driver,
            alt_after=(interface / 'bAlternateSetting').read_text().strip())


if __name__ == '__main__':
    main()
