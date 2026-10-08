# claude-skills

Claude skills by markslad, published as a Claude Code plugin marketplace.

## Install
```
/plugin marketplace add markslad/claude-skills
/plugin install zzk-form-filler@markslad-skills
```

## Skills
| Plugin | What it does |
|---|---|
| [zzk-form-filler](plugins/zzk-form-filler/skills/zzk-form-filler/SKILL.md) | Fills the Czech employee card application PDF (Žádost o zaměstnaneckou kartu, "VZOR ZZK") once per worker from a masterlist spreadsheet; outputs stay fillable PDFs. Bring your own template PDF. The bundled `fill_zzk.py` also runs without Claude (`pip install pypdf openpyxl`). |
