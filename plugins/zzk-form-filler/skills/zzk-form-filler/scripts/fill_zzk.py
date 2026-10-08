"""Fill the Czech 'Žádost o zaměstnaneckou kartu' (ZZK) PDF form for every row of a data source.

Usage:
  python fill_zzk.py --template "VZOR ZZK.pdf" --source data.xlsx --mapping mapping.json [options]

Options:
  --out DIR          output folder (default: Output next to the source)
  --only N [N ...]   fill only these data rows (1-based, header excluded)
  --skip-existing    skip workers whose output file already exists and is complete
  --verify-only      do not write anything, only verify existing outputs against the source
  --dry-run          print what would be filled for each row, write nothing

mapping.json:
{
  "sheet": "Approved",                    # sheet name (xlsx) - omit for first sheet / csv
  "header_row": 1,                        # 1-based row holding the column names
  "text": { "<pdf field>": "<column>" },  # text fields filled from columns
  "value_maps": { "<pdf field>": { "FILIPINO": "PHL" } },   # optional value translation (case-insensitive)
  "marital_column": "Marital_status",     # optional -> ticks C_S / C_Ma / C_D / C_W
  "gender_column": null,                  # optional -> ticks C_M / C_F (M/MALE/MUŽ, F/FEMALE/ŽENA)
  "leave_empty": ["ocupation"],           # fields forced empty
  "overrides": { "<pdf field>": "value" },# fixed values for the whole batch (e.g. anticipated_arrival_CZ)
  "filename": "ZZK_{surname}_{first_name}"# output name pattern, {column} placeholders
}
Any PDF field not mentioned keeps the template's default value. Output stays a fillable form.
"""
import argparse, csv, json, os, re, sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject, FloatObject, BooleanObject, TextStringObject

MARITAL = {"SINGLE": "C_S", "SVOBODNÝ": "C_S", "SVOBODNA": "C_S", "SVOBODNÁ": "C_S",
           "MARRIED": "C_Ma", "ŽENATÝ": "C_Ma", "VDANÁ": "C_Ma",
           "DIVORCED": "C_D", "ROZVEDENÝ": "C_D", "ROZVEDENÁ": "C_D",
           "WIDOWED": "C_W", "WIDOW": "C_W", "WIDOWER": "C_W", "VDOVEC": "C_W", "VDOVA": "C_W"}
GENDER = {"M": "C_M", "MALE": "C_M", "MUŽ": "C_M", "MUZ": "C_M",
          "F": "C_F", "FEMALE": "C_F", "ŽENA": "C_F", "ZENA": "C_F"}
MARITAL_BOXES = ["C_S", "C_Ma", "C_D", "C_W"]
GENDER_BOXES = ["C_M", "C_F"]


def clean(v):
    if v is None:
        return None
    if hasattr(v, "strftime"):
        return v.strftime("%d.%m.%Y")
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    v = re.sub(r"\s+", " ", str(v)).strip()
    return v or None


def load_rows(source, sheet=None, header_row=1):
    if source.lower().endswith((".csv", ".txt")):
        with open(source, encoding="utf-8-sig", newline="") as fh:
            sample = fh.read(4096); fh.seek(0)
            raw = list(csv.reader(fh, csv.Sniffer().sniff(sample, ";,\t")))
    else:
        import openpyxl
        wb = openpyxl.load_workbook(source, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        raw = [list(r) for r in ws.iter_rows(values_only=True)]
    head = [clean(h) for h in raw[header_row - 1]]
    rows = []
    for r in raw[header_row:]:
        if not any(clean(c) for c in r):
            continue
        rows.append({h: clean(c) for h, c in zip(head, r) if h})
    return head, rows


def safe(s):
    return re.sub(r"[^\w\- ]", "", s or "").strip().replace(" ", "_") or "unnamed"


def build_values(row, m):
    text, buttons = {}, {}
    vmaps = {f: {k.upper(): v for k, v in d.items()} for f, d in m.get("value_maps", {}).items()}
    for f, col in m.get("text", {}).items():
        v = row.get(col)
        if v is None:
            continue                      # not in source -> template default stays
        if f in vmaps:
            v = vmaps[f].get(v.upper(), v)
        text[f] = v
    for f, v in m.get("overrides", {}).items():
        text[f] = v
    for f in m.get("leave_empty", []):
        text[f] = ""
    if m.get("marital_column"):
        box = MARITAL.get((row.get(m["marital_column"]) or "").upper())
        if box:
            buttons.update({b: "/Yes" if b == box else "/Off" for b in MARITAL_BOXES})
    if m.get("gender_column"):
        box = GENDER.get((row.get(m["gender_column"]) or "").upper())
        if box:
            buttons.update({b: "/Yes" if b == box else "/Off" for b in GENDER_BOXES})
    return text, buttons


def fill(template, text, buttons, path):
    w = PdfWriter(clone_from=PdfReader(template))
    for page in w.pages:   # template stores some /Rect values as indirect refs -> resolve
        for a in page.get("/Annots") or []:
            a = a.get_object()
            if "/Rect" in a:
                a[NameObject("/Rect")] = ArrayObject(FloatObject(float(x.get_object())) for x in a["/Rect"])
    nonempty = {k: v for k, v in text.items() if v != ""}
    for page in w.pages:
        if nonempty:
            w.update_page_form_field_values(page, nonempty)   # generates appearance streams
        for a in page.get("/Annots") or []:
            a = a.get_object()
            par = a["/Parent"].get_object() if "/Parent" in a else None
            name = a.get("/T") or (par.get("/T") if par else None)
            tgt = a if "/T" in a else par
            if name in buttons:
                st = NameObject(buttons[name])
                a[NameObject("/AS")] = st
                tgt[NameObject("/V")] = st
            elif name in text and text[name] == "":     # forced empty
                for k in ("/V", "/AP"):
                    if k in tgt: del tgt[k]
                    if k in a: del a[k]
    # keep template appearance streams (Czech diacritics); viewers must not regenerate them
    w._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(False)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        w.write(fh)
    os.replace(tmp, path)        # atomic: an interrupted run never leaves a half-written PDF


def verify(path, text, buttons):
    problems = []
    fields = PdfReader(path).get_fields() or {}
    for f, exp in text.items():
        got = fields.get(f, {}).get("/V")
        if (got or "") != exp:
            problems.append(f"{f}: expected {exp!r}, got {got!r}")
    for f, exp in buttons.items():
        got = fields.get(f, {}).get("/V") or "/Off"
        if got != exp:
            problems.append(f"{f}: expected {exp}, got {got}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--out")
    ap.add_argument("--only", nargs="*", type=int)
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    m = json.load(open(a.mapping, encoding="utf-8"))
    head, rows = load_rows(a.source, m.get("sheet"), m.get("header_row", 1))
    pdf_fields = set((PdfReader(a.template).get_fields() or {}).keys())
    missing_cols = sorted({c for c in m.get("text", {}).values() if c not in head})
    bad_fields = sorted({f for f in list(m.get("text", {})) + list(m.get("overrides", {})) + m.get("leave_empty", [])
                         if f not in pdf_fields})
    if missing_cols or bad_fields:
        sys.exit(f"Mapping error. Columns not in source: {missing_cols}. Fields not in PDF: {bad_fields}")

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.source)), "Output")
    os.makedirs(out, exist_ok=True)
    pattern = m.get("filename", "ZZK_{surname}_{first_name}")
    idx = a.only or range(1, len(rows) + 1)
    seen, total_problems = set(), 0
    for i in idx:
        row = rows[i - 1]
        name = safe(pattern.format_map({k: (v or "") for k, v in row.items()}))
        if name in seen:
            name = f"{name}_{i}"
        seen.add(name)
        path = os.path.join(out, name + ".pdf")
        text, buttons = build_values(row, m)
        if a.dry_run:
            print(f"[{i}] {name}.pdf"); [print(f"     {k} = {v!r}") for k, v in {**text, **buttons}.items()]
            continue
        if not a.verify_only and not (a.skip_existing and os.path.exists(path)):
            fill(a.template, text, buttons, path)
        if not os.path.exists(path):
            print(f"[{i}] MISSING {name}.pdf"); total_problems += 1; continue
        p = verify(path, text, buttons)
        total_problems += len(p)
        print(f"[{i}] {'OK ' if not p else 'ERR'} {name}.pdf" + "".join(f"\n      {x}" for x in p), flush=True)
    if not a.dry_run:
        print(f"Done: {len(list(idx))} worker(s), problems: {total_problems}")


if __name__ == "__main__":
    import logging; logging.getLogger("pypdf").setLevel(logging.ERROR)
    main()
