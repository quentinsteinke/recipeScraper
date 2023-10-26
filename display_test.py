import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import random

# Load JSON data
with open('output/data/recipeInfo.json', 'r') as f:
    data = json.load(f)
    recipes = data['recipes']['recipe']

def show_random_recipe():
    random_recipe = random.choice(recipes)
    name.set(random_recipe['name'])
    ingredients.set('\n'.join(random_recipe['ingredients']))
    nutrition.set('\n'.join([f"{k}: {v}" for k, v in random_recipe['nutrition'].items()]))
    catagory.set(random_recipe['catagory'])
    directions.set('\n'.join(random_recipe['directions']))
    image_path = random_recipe['image']
    img = Image.open(image_path)
    img = img.resize((200, 200))
    img = ImageTk.PhotoImage(img)
    panel.config(image=img)
    panel.image = img

# Initialize Tkinter window
root = tk.Tk()
root.title("Random Recipe Display")
root.geometry("800x600")

name = tk.StringVar()
ingredients = tk.StringVar()
nutrition = tk.StringVar()
catagory = tk.StringVar()
directions = tk.StringVar()

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Recipe:").grid(row=0, column=0, sticky=tk.W)
ttk.Label(frame, textvariable=name).grid(row=0, column=1, sticky=tk.W)

ttk.Label(frame, text="catagory:").grid(row=0, column=0, sticky=tk.W)
ttk.Label(frame, textvariable=catagory).grid(row=0, column=1, sticky=tk.W)

ttk.Label(frame, text="Ingredients:").grid(row=1, column=0, sticky=tk.W)
ttk.Label(frame, textvariable=ingredients).grid(row=1, column=1, sticky=tk.W)

ttk.Label(frame, text="Nutrition Facts:").grid(row=2, column=0, sticky=tk.W)
ttk.Label(frame, textvariable=nutrition).grid(row=2, column=1, sticky=tk.W)

ttk.Label(frame, text="Directions:").grid(row=3, column=0, sticky=tk.W)
ttk.Label(frame, textvariable=directions).grid(row=3, column=1, sticky=tk.W)

panel = ttk.Label(frame)
panel.grid(row=2, columnspan=2)

ttk.Button(frame, text="Show Random Recipe", command=show_random_recipe).grid(row=3, columnspan=2)

root.mainloop()
