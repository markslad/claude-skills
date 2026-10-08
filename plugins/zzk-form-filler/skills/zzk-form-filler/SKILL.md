---
name: zzk-form-filler
description: This skill should be used when the user asks to "fill the ZZK forms", "fill zaměstnanecká karta applications", "vyplnit žádosti o zaměstnaneckou kartu", or to fill the VZOR ZZK / employee card PDF for workers from a masterlist spreadsheet. Produces one fillable PDF per worker in an Output folder.
---

# ZZK form filler

Fill the fillable PDF template "VZOR ZZK" (Žádost o zaměstnaneckou kartu / Request for Employee Card, form 19 09 01 853) once per worker from a source data file (xlsx or csv). The template is the same every time; the data source differs (columns, sheet names, value spellings), so the main job is building the column mapping. A tested script does the filling and verification.

Bundled files (relative to this skill's directory):
- `scripts/fill_zzk.py` – filling script (Python 3, needs `pypdf` >= 5 and `openpyxl`; install with `pip install pypdf openpyxl`). Its docstring documents the mapping JSON format.
- `references/field-reference.md` – meaning of every PDF field and its quirks. Read it before building a mapping.

The template PDF is not bundled; the user provides it (file name usually starts with "VZOR ZZK"). If it is missing, ask for it. Confirm it is the expected form: 168 form fields including `ocupation`, `K_1`, `M_29`, `vacancy_number`.

## Rules
- Write one output PDF per worker into a folder named `Output` next to the source file, named `ZZK_<SURNAME>_<FIRSTNAME>.pdf`.
- Keep outputs as fillable forms; never flatten.
- For each PDF field, take the value from the source when a matching column exists; when none exists, keep the template's default value.
- Always leave the applicant's Occupation field (`ocupation`) empty, even if the source has a profession column. Fill spouse/child/parent/sibling occupations normally.
- Convert nationality words to 3-letter country codes (e.g. FILIPINO / PILIPINO → PHL) via `value_maps`.
- Never modify the user's source file or template. When data needs reshaping (e.g. two children in one cell), write a cleaned copy and use that.
- Never set NeedAppearances=true on outputs: viewers then redraw template fields and drop Czech diacritics (Ě, Ř, Č). The script already handles this.

## Workflow
1. **Locate inputs.** Find the template and the source data file in the user's folder. Copy `scripts/fill_zzk.py` next to the source if it is not already there.
2. **Analyze the source.** List sheets and find the one with worker rows (others may be empty), the header row, row count, each column's distinct values and spelling variants, empty columns, and cells holding several people (several children/siblings separated by newline, `;` or `/`). Also list the template's pre-filled values.
3. **Build the mapping** `mapping_<client>.json` (format in the script docstring), matching columns by meaning, not exact name. Typical mapping: applicant names, contact, birth data, nationality, education, marital status (`marital_column`), passport; spouse (J), child 1 (K_1–K_8), father (L), mother (M), sibling 1 (N_1–N_8). Before filling anything, show the user:
   - a table of PDF section → field → source column;
   - gaps: fields with no source column that keep the template default or stay blank (often gender, relatives' nationality, relatives' street/No./post code, sections D, G, H);
   - batch values pre-filled in the template that may change per batch: vacancy number, employer block (C), Czech residence address (E), anticipated arrival date, place and date of application, attachments. Ask whether to keep or override them (`overrides` in the mapping).
4. **Test one worker.** Run with `--dry-run --only 1`, then `--only 1`. Render pages 1–4 of the output to images and inspect them (diacritics, checkboxes, text fit). Name the worker filled and ask the user to review. Apply adjustments to the mapping and repeat.
5. **Run all** after approval. Each worker takes ~4 s and yields a ~6 MB PDF. When the shell has a per-command time limit, run with `--skip-existing` repeatedly until done; writes are atomic, so an interrupted run never leaves a broken file.
6. **Verify.** Run with `--verify-only`; it compares every mapped field and checkbox in each output with the source. Report the file count, problems (expect 0) and remaining gaps.

## Several children or siblings
The form has 4 child blocks (`K_1`–`K_32`) and 4 sibling blocks (`N_1`–`N_32`; sibling 4's place of birth is `M_29`). When a worker has more than one child or sibling, map blocks 2–4 too (e.g. `"K_9": "child2_surname"`), splitting multi-value cells into extra columns in a cleaned copy of the source.

## Commands
```
python fill_zzk.py --template "<template.pdf>" --source "<data.xlsx>" --mapping mapping.json --dry-run --only 1
python fill_zzk.py --template ... --source ... --mapping ... --only 1
python fill_zzk.py --template ... --source ... --mapping ... --skip-existing
python fill_zzk.py --template ... --source ... --mapping ... --verify-only
```
Optional: `--out DIR` to change the output folder.
