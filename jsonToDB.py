import sqlite3
import json
import logging

# Load the recipeInfo.json file
with open('output\\data\\recipeInfo.json', 'r') as f:
    data = json.load(f)

# Create a SQLite database
conn = sqlite3.connect('..\\db\\recipeInfo.db')
cursor = conn.cursor()

# Create the recipes table
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    url TEXT,
    image TEXT
);
''')

# Create the categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
''')

# Create the ingredients table
cursor.execute('''
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
''')

# Create the directions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS directions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step TEXT
);
''')

# Create the nutrition table
cursor.execute('''
CREATE TABLE IF NOT EXISTS nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    amount TEXT
);
''')

# Create the mapping tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_categories (
    recipe_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER,
    ingredient_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_directions (
    recipe_id INTEGER,
    direction_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(direction_id) REFERENCES directions(id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_nutrition (
    recipe_id INTEGER,
    nutrition_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id),
    FOREIGN KEY(nutrition_id) REFERENCES nutrition(id)
);
''')

# Populate the database from the JSON data

logging.basicConfig(filename='recipe_scraping.log', level=logging.DEBUG)

for recipe in data['recipes']['recipe']:
    # Insert recipe and get the last inserted id
    cursor.execute("INSERT INTO recipes (name, url, image) VALUES (?, ?, ?)",
                   (recipe['name'], recipe['url'], recipe.get('image', None)))
    recipe_id = cursor.lastrowid
    logging.debug(f"Inserted recipe {recipe['name']} with id {recipe_id}")

    # Insert categories
    for category in recipe.get('catagory', []):
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (?, ?)",
                       (recipe_id, category_id))
        logging.debug(f"Inserted category {category} for recipe {recipe['name']}")

    # Insert ingredients
    for ingredient in recipe.get('ingredients', []):
        cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (ingredient,))
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ingredient,))
        ingredient_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)",
                       (recipe_id, ingredient_id))
        logging.debug(f"Inserted ingredient {ingredient} for recipe {recipe['name']}")

    # Insert directions
    for direction in recipe.get('directions', []):
        cursor.execute("INSERT OR IGNORE INTO directions (step) VALUES (?)", (direction,))
        cursor.execute("SELECT id FROM directions WHERE step = ?", (direction,))
        direction_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO recipe_directions (recipe_id, direction_id) VALUES (?, ?)",
                       (recipe_id, direction_id))
        logging.debug(f"Inserted direction {direction} for recipe {recipe['name']}")

    # Insert nutrition facts
    for name, amount in recipe.get('nutrition', {}).items():
        cursor.execute("INSERT OR IGNORE INTO nutrition (name, amount) VALUES (?, ?)", (name, amount))
        cursor.execute("SELECT id FROM nutrition WHERE name = ? AND amount = ?", (name, amount))
        nutrition_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO recipe_nutrition (recipe_id, nutrition_id) VALUES (?, ?)",
                       (recipe_id, nutrition_id))
        logging.debug(f"Inserted nutrition fact {name}: {amount} for recipe {recipe['name']}")

# Commit and close the database connection
conn.commit()
conn.close()
