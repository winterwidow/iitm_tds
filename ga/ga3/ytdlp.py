import json
import subprocess
import sys

with open(
    r"C:\Users\naija\iitm\iitm_tds\ga\ga3\q-youtube-metadata-filter-server.json"
) as f:
    params = json.load(f)

rows = []

for url in params["source_urls"]:
    try:
        raw = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "yt_dlp",
                "--dump-json",
                "--skip-download",
                url,
            ],
            text=True,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(
            f"[FETCH FAILED] {url}\n  stderr: {e.stderr.strip()[:300]}", file=sys.stderr
        )
        continue

    data = json.loads(raw)

    vid_id = data.get("id") or ""
    title = data.get("title", "")
    description = data.get("description", "")
    duration = data.get("duration")
    upload_date = data.get("upload_date")

    duration_val = duration if duration is not None else 0
    duration_ok = (
        params["min_duration_seconds"] <= duration_val <= params["max_duration_seconds"]
    )

    text = f"{title} {description}".lower()
    matched_required = [w for w in params["required_words"] if w.lower() in text]
    required_ok = len(matched_required) == len(params["required_words"])

    matched_forbidden = [w for w in params["forbidden_words"] if w.lower() in text]
    forbidden_ok = len(matched_forbidden) == 0

    included = duration_ok and required_ok and forbidden_ok

    rows.append(
        {
            "url": url,
            "id": vid_id,
            "title": title,
            "duration": duration,
            "duration_ok": duration_ok,
            "required_ok": required_ok,
            "matched_forbidden": matched_forbidden,
            "forbidden_ok": forbidden_ok,
            "upload_date": upload_date,
            "included": included,
        }
    )

# Print a full diagnostic table for every URL, in source order
print("=" * 100)
print("DIAGNOSTIC: every source URL and why it was kept/dropped")
print("=" * 100)
for r in rows:
    status = "KEEP" if r["included"] else "DROP"
    reason = []
    if not r["duration_ok"]:
        reason.append(f"duration={r['duration']} out of range")
    if not r["required_ok"]:
        reason.append("missing required word(s)")
    if not r["forbidden_ok"]:
        reason.append(f"forbidden word(s) found: {r['matched_forbidden']}")
    print(
        f"[{status}] id={r['id']} upload_date={r['upload_date']} duration={r['duration']} "
        f"title={r['title'][:60]!r}"
    )
    if reason:
        print(f"       reason: {'; '.join(reason)}")

# Now build the actual filtered+sorted result
videos = [r for r in rows if r["included"] and r["upload_date"] is not None]
videos.sort(key=lambda v: (-int(v["upload_date"]), v["id"]))

print("=" * 100)
print("FINAL SORTED ORDER (before limit):")
for v in videos:
    print(f"  {v['upload_date']}  {v['id']}  {v['url']}")

result = {"urls": [v["url"] for v in videos[: params["limit"]]]}

print("=" * 100)
print(json.dumps(result, indent=2))
