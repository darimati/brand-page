# DARIMATI — Brand Page

A single-page brand story for the Shopify storefront.
Live preview: **GitHub Pages** (see repo settings → Pages).

```
template.html        ← copy + layout. Edit this.
images.tsv           ← which photo goes in which slot. Edit this.
assets/              ← the photos themselves
build.py             ← run this after editing
index.html           ← [generated] preview, links to assets/
slots.html           ← [generated] shows every slot with its name
dist/shopify.html    ← [generated] single file with images embedded — for Shopify
```

## Build

```bash
python3 build.py
```

Python 3, standard library only — no install step. Then open `index.html` in a browser.

---

## Change a photo

1. Open **`slots.html`** in a browser. Every image is listed with its **slot name**.
2. Find the slot you want to change.
3. Put the new photo in `assets/` (JPG, roughly 1200px on the long edge).
4. In **`images.tsv`**, point that slot at the new file:

   ```
   st_night	assets/st_night.jpg
            ^^^^^^^^^^^^^^^^^^^ change this
   ```

   Columns are separated by a **Tab**, not spaces.
5. `python3 build.py`

To drop an image from the page entirely, delete its `<figure>` block in `template.html`.
The slot can stay in `images.tsv` — it will just be reported as unused.

## Change the copy

Everything is in **`template.html`**, below the `</style>` line. Section comments mark each part:

| Marker | Section |
|---|---|
| `<!-- COVER -->` | Opening image + headline |
| `<!-- RIVER -->` | "Many cities are shaped by a river" |
| `<!-- BRIDGE MECHANICS -->` | Tech explanation + spec list |
| `<!-- QUIET PERFORMANCE -->` | Design philosophy |
| `<!-- MAGAZINE -->` | DARI magazine + 32 bridges |
| `<!-- DARI CLUB -->` | Dari Class sessions |

Text classes:

| Class | Role |
|---|---|
| `kicker` | Small uppercase label above a heading |
| `h-xl` / `h-lg` / `h-md` | Headline sizes |
| `lede` | Opening sentence under a heading |
| `note` | Supporting paragraph (grey) |
| `cap` | Caption under a photo |

Most of the copy is taken verbatim from darimati.us so the voice matches the existing store.
Keep that in mind when rewriting.

## Move it to Shopify

1. `python3 build.py`
2. Open `dist/shopify.html`.
3. Copy everything from `<style>` to the end of the file (skip `<title>`, `<meta>`, and the
   two `<link>` font tags — the theme already loads Bricolage Grotesque and Manrope).
4. Shopify admin → **Online Store → Pages → Add page** → in the content editor switch to
   `<>` HTML view → paste.

The images are embedded as base64, so nothing else needs uploading. If the page feels heavy,
upload the files in `assets/` to Shopify **Content → Files** instead and swap the `src`
values in `index.html` for the Shopify CDN URLs.

## Fonts

`Bricolage Grotesque` (display) and `Manrope` (body) — the same faces the storefront theme uses,
loaded from Google Fonts.
