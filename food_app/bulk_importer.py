import pandas as pd
import json
import ast
import os

# --- CONFIGURATION ---
BLACKLIST = ["Fish", "Seafood", "Shrimp", "Prawn", "Salmon", "Tuna", "Onion", "Ginger", "Mushroom", "Pepper", "Lettuce", "Tomato"]
TARGET_COUNT = 10000 
INPUT_FILE = "RAW_recipes.csv"

def convert_and_merge():
    print(f"--- 📂 Loading {INPUT_FILE} ---")
    try:
        # 1. Load your existing 606 recipes so we don't lose them
        existing_recipes = []
        if os.path.exists("recipes_db.json"):
            with open("recipes_db.json", "r", encoding="utf-8") as f:
                existing_recipes = json.load(f)
            print(f"✅ Found {len(existing_recipes)} existing recipes. Preparing to merge...")

        # 2. Process the new CSV data
        df = pd.read_csv(INPUT_FILE)
        new_safe_recipes = []
        count = 0

        for index, row in df.iterrows():
            if count >= TARGET_COUNT:
                break
            
            raw_ingredients = ast.literal_eval(row['ingredients'])
            ingredients_text = " ".join(raw_ingredients).lower()
            
            if not any(bad.lower() in ingredients_text for bad in BLACKLIST):
                steps = ast.literal_eval(row['steps'])
                instructions = "\n".join([f"{i+1}. {step.capitalize()}" for i, step in enumerate(steps)])
                
                new_safe_recipes.append({
                    "id": f"food-{row['id']}",
                    "title": str(row['name']).title(),
                    "category": "Dinner",
                    "ingredients": [i.capitalize() for i in raw_ingredients],
                    "instructions": instructions,
                    "image_url": "https://via.placeholder.com/400x300?text=Recipe+Image",
                    "time": f"{row['minutes']} mins"
                })
                count += 1

        # 3. Combine them: [Old 606] + [New 10,000]
        final_database = existing_recipes + new_safe_recipes

        # 4. Save the combined total back to the file
        with open("recipes_db.json", "w", encoding="utf-8") as f:
            json.dump(final_database, f, indent=4)

        print(f"\n🎉 SUCCESS! You now have {len(final_database)} total recipes in your library.")

    except FileNotFoundError:
        print(f"⚠️ Error: Could not find {INPUT_FILE}.")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    convert_and_merge()