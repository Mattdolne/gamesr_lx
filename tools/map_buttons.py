#!/usr/bin/env python3
"""Map only physically verified G7 SE inputs; never grab the gamepad."""
import argparse
import fcntl
import json
import os
import select
import signal
import time
from pathlib import Path

from evdev import InputDevice, UInput, ecodes, list_devices


def load(path):
    data = json.loads(Path(path).read_text())
    if data.get('output_mode', 'hold') not in ('hold', 'tap'):
        raise ValueError('output_mode deve ser hold ou tap')
    sources = data['verified_sources']
    mapping = data['mapping']
    allowed = {'Share': 'KEY_RECORD'}
    for button, source in sources.items():
        if allowed.get(button) != source:
            raise ValueError(f'{button}: origem independente não validada: {source}')
    keys = {}
    for button, target in mapping.items():
        if button not in sources:
            raise ValueError(f'{button}: sem origem independente validada')
        if not target.startswith('KEY_') or target not in ecodes.ecodes:
            raise ValueError(f'Tecla inválida: {target}')
        keys[ecodes.ecodes[sources[button]]] = ecodes.ecodes[target]
    if len(set(keys.values())) != len(keys):
        raise ValueError('Destinos duplicados não são suportados')
    return data, keys


class KeyState:
    def __init__(self, mapping, mode, emit):
        self.mapping, self.mode, self.emit = mapping, mode, emit
        self.down = set()
        self.held = set()

    def event(self, source, value):
        if source not in self.mapping:
            return
        key = self.mapping[source]
        if value == 1 and source not in self.down:
            self.down.add(source)
            self.held.add(key)
            self.emit(key, 1)
            if self.mode == 'tap':
                self.emit(key, 0)
                self.held.remove(key)
        elif value == 0:
            self.down.discard(source)
            if key in self.held:
                self.emit(key, 0)
                self.held.remove(key)

    def release_all(self):
        for key in sorted(self.held):
            self.emit(key, 0)
        self.held.clear()
        self.down.clear()


def find_device(data, mapping, paths=None, opener=InputDevice):
    """Publish a device only after capabilities and initial state are readable."""
    for path in list_devices() if paths is None else paths:
        found = None
        try:
            found = opener(path)
            if ((found.info.vendor, found.info.product) == (data['vendor'], data['product'])
                    and set(mapping) <= set(found.capabilities().get(ecodes.EV_KEY, []))):
                blocked = set(found.active_keys()) & set(mapping)
                return found, blocked
        except OSError:
            pass
        if found is not None:
            found.close()
    return None, set()


def run(path, seconds=None):
    data, mapping = load(path)
    mode = data.get('output_mode', 'hold')
    print(f'output_mode={mode}', flush=True)
    for button in ('L4', 'R4', 'Share'):
        if button not in data['mapping']:
            print(f'{button}: sem mapeamento; captura independente pendente '
                  f'({data["vendor"]:04x}:{data["product"]:04x}, GIP)', flush=True)
    stopped = False

    def stop(*_):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    device = None
    started = time.monotonic()
    with UInput({ecodes.EV_KEY: sorted(set(mapping.values()))},
                name='G7 SE verified keyboard', vendor=0x1209, product=0x0001) as ui:
        def emit(key, value):
            ui.write(ecodes.EV_KEY, key, value)
            ui.syn()
            print(f'{ecodes.KEY[key]} {value}', flush=True)

        state = KeyState(mapping, mode, emit)

        try:
            while not stopped and (seconds is None or time.monotonic() - started < seconds):
                if device is None:
                    # A held button at reconnect is ignored until released.
                    device, blocked = find_device(data, mapping)
                    if device is None:
                        time.sleep(0.2)
                        continue
                    print(f'connected {device.path}; blocked={sorted(blocked)}', flush=True)
                try:
                    if not select.select([device.fd], [], [], 0.2)[0]:
                        continue
                    for event in device.read():
                        if event.type == ecodes.EV_SYN and event.code == ecodes.SYN_DROPPED:
                            state.release_all()
                            device.close()
                            device = None
                            break
                        if event.type != ecodes.EV_KEY or event.code not in mapping:
                            continue
                        if event.code in blocked:
                            if event.value == 0:
                                blocked.remove(event.code)
                            continue
                        state.event(event.code, event.value)
                except OSError as exc:
                    print(f'disconnected: {exc}', flush=True)
                    state.release_all()
                    device.close()
                    device = None
        finally:
            state.release_all()
            if device is not None:
                device.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(Path(__file__).resolve().parents[1] / 'config/mapping.json'))
    parser.add_argument('--seconds', type=float)
    args = parser.parse_args()
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/tmp/gamesr-{os.getuid()}'))
    runtime.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (runtime / 'gamesr-mapper.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Uma instância do mapeador já está em execução')
        run(args.config, args.seconds)
