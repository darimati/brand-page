#!/usr/bin/env python3
"""사진 한 장 갈아끼우기.

    python3 swap.py <슬롯이름> <사진이름>

예)
    python3 swap.py c1 ls-08
    python3 swap.py cover_img kv-01

슬롯이름은 slots.html, 사진이름은 library.html 에서 보면 됩니다.
바꾸고 나면 알아서 다시 빌드까지 합니다.
"""
import os, sys, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, 'images.tsv')


def slots():
    out = []
    for raw in open(TSV, encoding='utf-8'):
        line = raw.strip()
        if line and not line.startswith('#'):
            out.append(line.replace('\t', ' ').split()[0])
    return out


def library():
    names = []
    for d in ('library', 'assets'):
        for p in sorted(glob.glob(os.path.join(HERE, d, '*.jpg'))):
            names.append((os.path.splitext(os.path.basename(p))[0], f'{d}/{os.path.basename(p)}'))
    return names


def die(msg, options=None):
    print(msg)
    if options:
        print('\n고를 수 있는 것:')
        for i, o in enumerate(options):
            end = '\n' if (i + 1) % 6 == 0 else '  '
            print(f'{o:<22}', end=end)
        print()
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        print('현재 슬롯:', ', '.join(slots()))
        sys.exit(1)

    slot, pick = sys.argv[1], os.path.splitext(sys.argv[2])[0]

    if slot not in slots():
        die(f'"{slot}" 이라는 슬롯은 없습니다.', slots())

    lib = library()
    match = [path for name, path in lib if name == pick]
    if not match:
        near = [n for n, _ in lib if pick.lower() in n.lower()]
        die(f'"{pick}" 이라는 사진을 library/ 와 assets/ 에서 못 찾았습니다.',
            near or [n for n, _ in lib])
    newpath = match[0]

    lines, changed = [], None
    for raw in open(TSV, encoding='utf-8'):
        line = raw.rstrip('\n')
        if line.strip() and not line.strip().startswith('#'):
            parts = line.replace('\t', ' ').split()
            if parts[0] == slot:
                changed = parts[1] if len(parts) > 1 else '(없음)'
                line = f'{slot}\t{newpath}'
        lines.append(line)
    open(TSV, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    print(f'{slot}:  {changed}  →  {newpath}\n')
    subprocess.run([sys.executable, os.path.join(HERE, 'build.py')])


if __name__ == '__main__':
    main()
