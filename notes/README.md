# notes/

Drop your markdown files here — then run:

```bash
docker compose exec app korely-graphrag ingest /notes
```

Or, instead of copying files into this directory, point `HOST_NOTES_PATH`
at your real vault before `docker compose up`:

```bash
export HOST_NOTES_PATH=~/my-obsidian-vault
docker compose up -d
```

This file exists so `docker compose up` doesn't fail on a fresh clone.
It's ignored by the ingestion pipeline (only `*.md` / `*.markdown` with
real content are picked up) and the directory itself is in `.gitignore`
below this README.
