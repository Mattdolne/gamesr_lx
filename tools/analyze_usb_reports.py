#!/usr/bin/env python3
"""Summarize tshark TSV: time, endpoint, URB type, usb.capdata.

GIP byte offsets are report offsets (including the four-byte GIP header).
The decoder describes observed data; it never infers a missing button.
"""
import argparse
from collections import Counter
import json
from pathlib import Path


def analyze(path, markers=None):
    records = []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        stamp, endpoint, urb, hexadecimal = line.split('\t')
        raw = bytes.fromhex(hexadecimal.replace(':', ''))
        if not raw:
            continue
        record = {'time': float(stamp), 'endpoint': endpoint, 'urb': urb,
                  'command': f'{raw[0]:02x}', 'hex': raw.hex()}
        if raw[0] == 0x20 and len(raw) >= 4:
            record['payload_nonzero_by_report_offset'] = {
                str(offset): f'{value:02x}'
                for offset, value in enumerate(raw[4:], 4) if value}
        records.append(record)
    result = {'packet_count': len(records),
              'commands': dict(Counter(r['command'] for r in records)),
              'records': records}
    if markers:
        marks = [json.loads(line) for line in Path(markers).read_text().splitlines()]
        result['isolated_windows'] = {}
        for button in ('L4', 'R4'):
            start = next(m['time'] for m in marks if m['phase'] == f'{button}-only-start')
            end = next(m['time'] for m in marks if m['phase'] == f'{button}-only-confirmed')
            window = [r for r in records if start <= r['time'] <= end]
            result['isolated_windows'][button] = {
                'start': start, 'end': end,
                'commands': dict(Counter(r['command'] for r in window)),
                'input_report_count': sum(r['command'] == '20' for r in window)}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tsv')
    parser.add_argument('--markers')
    args = parser.parse_args()
    print(json.dumps(analyze(args.tsv, args.markers), indent=2))
