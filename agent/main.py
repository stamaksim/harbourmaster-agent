import sys, json

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    q = json.loads(line)
    print(json.dumps({
        "id": q["id"],
        "answer": "TODO",
        "citations": [],
        "abstained": True
    }))
