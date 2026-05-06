import os
import json
from datasets import load_dataset

# Using the exact path you provided
csv_path = r"C:\Users\devin\Desktop\blue_apron\dataset\dataset\full_dataset.csv"

BLACKLIST = ["Fish", "Seafood", "Shrimp", "Prawn", "Salmon", "Tuna", "Onion", "Ginger", "Mushroom", "Pepper", "Lettuce", "Tomato"]
LIMIT = 20000 

def run_import():
    print(f"--- 📂 Target Path: {csv_path} ---")

    if not os.path.exists(csv_path):
        print("❌ ERROR: Still can't find the file at that specific path.")
        print("Double-check the folder names or 'Copy as Path' again.")
        return

    print("✅ File found! Loading 1.1GB dataset in streaming mode...")
    
    try:
        # streaming=True keeps your RAM usage low
        dataset = load_dataset("csv", data_files=csv_path, split="train", streaming=True)
        
        existing_recipes = []
        if os.path.exists("recipes_db.json"):
            with open("recipes_db.json", "r", encoding="utf-8") as f:
                existing_recipes = json.load(f)
            print(f"Found {len(existing_recipes)} existing recipes. Merging...")

        new_safe_recipes = []
        count = 0

        print(f"--- 🥣 Filtering first {LIMIT} safe recipes from RecipeNLG ---")
        for row in dataset:
            if count >= LIMIT:
                break
            
            # RecipeNLG uses 'ingredients' column
            ingredients_raw = row.get('ingredients', "[]")
            
            if not any(bad.lower() in ingredients_raw.lower() for bad in BLACKLIST):
                new_safe_recipes.append({
                    "id": f"nlg-{count}",
                    "title": row['title'].title() if row['title'] else "Untitled Recipe",
                    "category": "Other", 
                    "ingredients": eval(ingredients_raw) if ingredients_raw.startswith('[') else [ingredients_raw],
                    "instructions": row['directions'],
                    "image_url": "https://via.placeholder.com/400x300?text=Recipe+Image",
                    "time": "45 mins",
                    "refined": False # This tells your 8b model to categorize it later
                })
                count += 1
                if count % 1000 == 0:
                    print(f"   ✅ Processed {count} recipes...")

        # Final Merge
        final_db = existing_recipes + new_safe_recipes
        with open("recipes_db.json", "w", encoding="utf-8") as f:
            json.dump(final_db, f, indent=4)

        print(f"\n🎉 SUCCESS! Your library now has {len(final_db)} total recipes.")

    except Exception as e:
        print(f"❌ Error during import: {e}")

if __name__ == "__main__":
    run_import()