import json

with open("recipes_db.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total Recipes in File: {len(data)}")

counts = {}
for r in data:
    cat = r.get('category', 'Unknown')
    counts[cat] = counts.get(cat, 0) + 1

print("\nBreakdown by Category:")
for cat, count in counts.items():
    print(f"- {cat}: {count} recipes")