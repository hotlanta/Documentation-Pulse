"""Fetch feeds.yml -> docs/data/items.json. Failed sources keep their previous items."""
import json, re, html, time, datetime as dt, pathlib, yaml, feedparser

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/data/items.json"
MAX_AGE_DAYS, MAX_ITEMS = 45, 500
UA = "docs-pulse/1.0 (+https://github.com)"

def clean(s, n=280):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"

def when(e):
    t = e.get("published_parsed") or e.get("updated_parsed")
    return dt.datetime.fromtimestamp(time.mktime(t), dt.timezone.utc).isoformat() if t else None

cfg = yaml.safe_load((ROOT / "feeds.yml").read_text())
old = json.loads(OUT.read_text()) if OUT.exists() else {"items": []}
cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=MAX_AGE_DAYS)
items, status = [], []

for f in cfg.get("feeds", []):
    if f.get("enabled") is False:
        continue
    try:
        d = feedparser.parse(f["url"], agent=UA)
        if d.bozo and not d.entries:
            raise ValueError(str(d.get("bozo_exception", "feed unreadable")))
        n = 0
        for e in d.entries[:f.get("limit", cfg.get("default_limit", 3))]:
            if not e.get("link"):
                continue
            items.append({"id": e.get("id") or e["link"], "title": clean(e.get("title"), 200),
                          "link": e["link"], "source": f["name"], "topic": f.get("topic", "Other"),
                          "published": when(e), "summary": clean(e.get("summary"))})
            n += 1
        status.append({"name": f["name"], "ok": True, "count": n})
    except Exception as ex:  # keep what we had
        kept = [i for i in old["items"] if i["source"] == f["name"]]
        items += kept
        status.append({"name": f["name"], "ok": False, "count": len(kept), "error": str(ex)[:120]})

# keep a rolling archive: earlier items from sources still in feeds.yml
active = {f["name"] for f in cfg.get("feeds", []) if f.get("enabled") is not False}
items += [i for i in old["items"] if i["source"] in active and not i.get("pinned")]

# manual items (pinned: never expire; delete the line in manual.yml to remove)
mf = ROOT / "manual.yml"
for m in (yaml.safe_load(mf.read_text()) or {}).get("items", []) if mf.exists() else []:
    d0 = m.get("date") or dt.date.today()
    items.append({"id": m["url"], "title": m["title"], "link": m["url"], "source": m.get("source", "Manual"),
                  "topic": m.get("topic", "Community"), "summary": m.get("note", ""), "pinned": True,
                  "published": dt.datetime.combine(d0, dt.time(12), dt.timezone.utc).isoformat()})

seen, out = set(), []
for i in sorted(items, key=lambda x: x["published"] or "", reverse=True):
    if i["id"] in seen or (not i.get("pinned") and i["published"] and dt.datetime.fromisoformat(i["published"]) < cutoff):
        continue
    seen.add(i["id"]); out.append(i)

OUT.write_text(json.dumps({"updated": dt.datetime.now(dt.timezone.utc).isoformat(),
    "sources": status, "voices": cfg.get("voices", []), "items": out[:MAX_ITEMS]},
    ensure_ascii=False, indent=1))
print(f"{len(out)} items, {sum(not s['ok'] for s in status)} failing sources")
