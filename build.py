#!/usr/bin/env python3
"""DARIMATI 브랜드 페이지 빌드.

    python3 build.py

    template.html + images.tsv  →  index.html   (배포용 단일 파일)
                                →  slots.html   (슬롯 확인용)

표준 라이브러리만 씁니다. 맥/윈도/리눅스 어디서든 `python3 build.py` 한 줄이면 됩니다.
assets/ 안의 이미지가 크면(>600KB) 가능한 도구로 자동 축소하고, 도구가 없으면 경고만 합니다.
"""
import base64, html, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOFT_LIMIT = 600 * 1024        # 이 크기를 넘으면 축소 시도
TARGET_LONGEST = 1400          # 축소 목표 긴 변(px)
TOTAL_WARN_MB = 15             # Artifact/브라우저 부담 경고선


# ---------- 이미지 축소 (있는 도구를 알아서 사용) ----------

def _shrink(src, dst):
    """sips(macOS) → ImageMagick → Pillow 순으로 시도. 전부 없으면 False."""
    if shutil.which('sips'):
        r = subprocess.run(['sips', '-Z', str(TARGET_LONGEST), '-s', 'format', 'jpeg',
                            '-s', 'formatOptions', '72', src, '--out', dst],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(dst):
            return True
    for exe in ('magick', 'convert'):
        if shutil.which(exe):
            r = subprocess.run([exe, src, '-resize', f'{TARGET_LONGEST}x{TARGET_LONGEST}>',
                                '-quality', '72', dst], capture_output=True)
            if r.returncode == 0 and os.path.exists(dst):
                return True
    try:
        from PIL import Image
        im = Image.open(src).convert('RGB')
        im.thumbnail((TARGET_LONGEST, TARGET_LONGEST))
        im.save(dst, 'JPEG', quality=72)
        return True
    except Exception:
        return False


def load_image(slot, rel):
    path = os.path.join(HERE, rel)
    if not os.path.exists(path):
        sys.exit(f'[{slot}] 파일이 없습니다: {rel}')

    data = open(path, 'rb').read()
    note = ''
    if len(data) > SOFT_LIMIT:
        tmp = os.path.join(tempfile.gettempdir(), f'dmbuild_{slot}.jpg')
        if _shrink(path, tmp):
            small = open(tmp, 'rb').read()
            if len(small) < len(data):
                note = f'  (축소 {len(data)//1024}KB→{len(small)//1024}KB)'
                data = small
            os.remove(tmp)
        else:
            note = '  !! 용량이 큽니다. 직접 줄여 주세요 (축소 도구 없음)'

    ext = os.path.splitext(rel)[1].lower()
    mime = {'.png': 'image/png', '.webp': 'image/webp',
            '.gif': 'image/gif'}.get(ext, 'image/jpeg')
    uri = f'data:{mime};base64,' + base64.b64encode(data).decode()
    return uri, len(data), note


# ---------- 매니페스트 ----------

def read_manifest():
    rows, seen = [], set()
    path = os.path.join(HERE, 'images.tsv')
    for lineno, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p for p in line.replace('\t', ' ').replace(',', ' ').split() if p]
        if len(parts) < 2:
            sys.exit(f'images.tsv {lineno}행: 슬롯 이름과 사진 경로, 두 개가 필요합니다 → {line}')
        slot, rel = parts[0], parts[1]
        if slot in seen:
            sys.exit(f'images.tsv {lineno}행: 슬롯 이름이 중복됩니다 → {slot}')
        seen.add(slot)
        rows.append((slot, rel))
    return rows


# ---------- 빌드 ----------

def main():
    rows = read_manifest()
    tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    needed = set(re.findall(r'\{\{(\w+)\}\}', tpl))
    have = {s for s, _ in rows}

    missing = needed - have
    if missing:
        sys.exit('template.html 이 쓰는데 images.tsv 에 없는 슬롯: ' + ', '.join(sorted(missing)))
    unused = have - needed
    if unused:
        print('note) images.tsv 에 있지만 페이지에서 안 쓰는 슬롯: ' + ', '.join(sorted(unused)))

    # index.html — assets/ 를 그대로 참조 (GitHub Pages 에서 가볍게 열림)
    linked, embedded, total, cards = tpl, tpl, 0, []
    for slot, rel in rows:
        uri, size, note = load_image(slot, rel)
        used = slot in needed
        if used:
            total += size
            linked = linked.replace('{{%s}}' % slot, html.escape(rel, quote=True))
            embedded = embedded.replace('{{%s}}' % slot, uri)
        print(f'{slot:11} {size/1024:6.0f} KB  {rel}{note}')
        cards.append((slot, rel, used))

    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(linked)
    print(f'\n→ index.html          ({os.path.getsize(os.path.join(HERE,"index.html"))/1024:.0f} KB'
          f' + assets/ {total/1024/1024:.2f} MB)  ← GitHub Pages / 브라우저 미리보기')

    os.makedirs(os.path.join(HERE, 'dist'), exist_ok=True)
    single = os.path.join(HERE, 'dist', 'shopify.html')
    open(single, 'w', encoding='utf-8').write(embedded)
    mb = os.path.getsize(single) / 1024 / 1024
    print(f'→ dist/shopify.html   ({mb:.2f} MB)  ← Shopify 에 붙여넣는 단일 파일')
    if mb > TOTAL_WARN_MB:
        print(f'!! {TOTAL_WARN_MB}MB 를 넘었습니다. assets/ 의 이미지를 더 줄여 주세요.')

    items = []
    for slot, rel, used in cards:
        tag = '' if used else ' <b class="unused">미사용</b>'
        items.append(f'<figure><img src="{html.escape(rel, quote=True)}" '
                     f'alt="{html.escape(slot)}" loading="lazy">'
                     f'<figcaption><b>{html.escape(slot)}</b>{tag}<br>'
                     f'<span>{html.escape(rel)}</span></figcaption></figure>')
    slots_doc = (
        '<!-- 자동 생성 파일입니다. 직접 고치지 마세요 (build.py 가 다시 씁니다) -->'
        '<title>Image slots — DARIMATI</title><meta charset="utf-8">'
        '<style>'
        'body{font:13px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
        'margin:0;padding:24px;background:#fafafa;color:#111}'
        'h1{font-size:14px;letter-spacing:.16em;text-transform:uppercase;margin:0 0 6px}'
        'p.hint{color:#666;margin:0 0 22px;max-width:70ch}'
        'code{background:#eee;padding:1px 5px}'
        '.grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}'
        'figure{margin:0;background:#fff;border:1px solid #e3e3e3}'
        'img{width:100%;height:190px;object-fit:cover;display:block;background:#eee}'
        'figcaption{padding:8px 10px}figcaption b{font-size:12px}'
        '.unused{color:#b00}'
        'figcaption span{color:#777;font-size:11px;word-break:break-all}'
        '</style>'
        '<h1>Image slots</h1>'
        '<p class="hint">바꾸고 싶은 사진의 <b>슬롯 이름</b>을 확인한 뒤 '
        '<code>images.tsv</code> 에서 경로만 바꾸고 <code>python3 build.py</code> 를 실행하세요.</p>'
        f'<div class="grid">{"".join(items)}</div>')
    open(os.path.join(HERE, 'slots.html'), 'w', encoding='utf-8').write(slots_doc)
    print('→ slots.html  (지금 페이지에 쓰인 사진)')

    # library.html — 쓸 수 있는 사진 전체 목록
    import glob
    lib = []
    for d in ('library', 'assets'):
        for p in sorted(glob.glob(os.path.join(HERE, d, '*.jpg'))):
            name = os.path.splitext(os.path.basename(p))[0]
            lib.append((name, f'{d}/{os.path.basename(p)}'))
    litems = ''.join(
        f'<figure><img src="{html.escape(rel, quote=True)}" alt="{html.escape(n)}" loading="lazy">'
        f'<figcaption><b>{html.escape(n)}</b></figcaption></figure>' for n, rel in lib)
    lib_doc = (
        '<!-- 자동 생성 파일입니다 (build.py) -->'
        '<title>Image library — DARIMATI</title><meta charset="utf-8">'
        '<style>'
        'body{font:13px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
        'margin:0;padding:24px;background:#fafafa;color:#111}'
        'h1{font-size:14px;letter-spacing:.16em;text-transform:uppercase;margin:0 0 6px}'
        'p.hint{color:#666;margin:0 0 22px;max-width:76ch}'
        'code{background:#eee;padding:1px 6px}'
        '.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(190px,1fr))}'
        'figure{margin:0;background:#fff;border:1px solid #e3e3e3}'
        'img{width:100%;height:230px;object-fit:cover;display:block;background:#eee}'
        'figcaption{padding:8px 10px;font-size:12px}'
        '</style>'
        '<h1>Image library</h1>'
        f'<p class="hint">쓸 수 있는 사진 {len(lib)}장입니다. 마음에 드는 사진 아래 <b>이름</b>을 확인한 뒤, '
        '터미널에서 <code>python3 swap.py &lt;슬롯이름&gt; &lt;사진이름&gt;</code> 을 실행하세요. '
        '슬롯 이름은 <code>slots.html</code> 에 있습니다.</p>'
        f'<div class="grid">{litems}</div>')
    open(os.path.join(HERE, 'library.html'), 'w', encoding='utf-8').write(lib_doc)
    print(f'→ library.html  (쓸 수 있는 사진 {len(lib)}장)')


if __name__ == '__main__':
    main()
