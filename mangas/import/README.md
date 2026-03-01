# Import — Run Once Only

This directory contains one-time import scripts. **Do not run these again after the import is confirmed.**

## Steps

```bash
# 1. Parse Mangas.md → SQLite
python import/parse_mangas_md.py

# 2. Review what was imported
python import/validate_import.py

# 3. Confirm — locks the import permanently
python import/validate_import.py --confirm
```

After step 3, `data/import/RETIRED` is created. SQLite (`data/mangas.db`) is now the single source of truth. `Mangas.md` is retired.
