from bs4 import BeautifulSoup
import requests
import json
import os


def getCatagoryURLs(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    catagoryURLs = []
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('https://www.allrecipes.com/recipes'):
            catagoryURLs.append(a['href'])
            print(f"Found catagory: {a['href']}")
    return catagoryURLs

def getRecipeURLs(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    recipeURLs = []
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('https://www.allrecipes.com/recipe'):
            recipeURLs.append(a['href'])
            print(f"Found recipe: {a['href']}")
    return recipeURLs

def getRecipeInfo(url):
    print(f"getting recipe info for {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    recipeInfo = {}
    
    recipe_name = soup.find('h1', {'id': 'article-heading_1-0'})
    recipeInfo['name'] = recipe_name.text if recipe_name else None
    if recipeInfo['name']:
        recipeInfo['name'] = recipeInfo['name'].replace('\\n', '').strip()

    if recipeInfo['name'] is None:
        return None
    
    print(f"Found the name: {recipeInfo['name']}")

    recipeInfo['catagory'] = []
    breadcrumb_items = soup.find_all('li', {'class': 'comp mntl-breadcrumbs__item mntl-block'})
    for item in breadcrumb_items:
        text = item.find('span', {'class': 'link__wrapper'}).text
        recipeInfo['catagory'].append(text)
    print(f"Found the catagories: {recipeInfo['catagory']}")

    recipe_details_items = soup.find_all('div', {'class': 'mntl-recipe-details__item'})

    recipe_details = {}
    for item in recipe_details_items:
        label = item.find('div', {'class': 'mntl-recipe-details__label'}).text.strip()
        value = item.find('div', {'class': 'mntl-recipe-details__value'}).text.strip()
        print(f"Found {label}: {value}")
        recipe_details[label] = value

    ingredient_list = soup.find('ul', {'class': 'mntl-structured-ingredients__list'})

    ingredients = []
    if ingredient_list:
        for item in ingredient_list.find_all('li', {'class': 'mntl-structured-ingredients__list-item'}):
            quantity = item.find('span', {'data-ingredient-quantity': 'true'}).text if item.find('span', {'data-ingredient-quantity': 'true'}) else ''
            unit = item.find('span', {'data-ingredient-unit': 'true'}).text if item.find('span', {'data-ingredient-unit': 'true'}) else ''
            name = item.find('span', {'data-ingredient-name': 'true'}).text if item.find('span', {'data-ingredient-name': 'true'}) else ''
            
            # Combine the quantity, unit, and name to form the complete ingredient
            complete_ingredient = f"{quantity} {unit} {name}".strip()
            ingredients.append(complete_ingredient)
            print(f"Found ingredients: {ingredients}")
            recipeInfo['ingredients'] = ingredients

    if 'ingredients' in recipeInfo:
        recipeInfo['ingredients'] = [ingredient.encode('utf-8').decode('unicode_escape') for ingredient in recipeInfo['ingredients']]

    directions_list = soup.find('ol', {'class': 'comp mntl-sc-block-group--OL mntl-sc-block mntl-sc-block-startgroup'})

    directions = []
    if directions_list:
        for item in directions_list.find_all('li', {'class': 'comp mntl-sc-block-group--LI mntl-sc-block mntl-sc-block-startgroup'}):
            direction_text = item.find('p', {'class': 'comp mntl-sc-block mntl-sc-block-html'}).text if item.find('p', {'class': 'comp mntl-sc-block mntl-sc-block-html'}) else ''
            
            directions.append(direction_text.strip())
            print(f"Found directions: {directions}")
            recipeInfo['directions'] = directions

    # Scrape the summary table
    nutrition_summary_tbody = soup.find('tbody', {'class': 'mntl-nutrition-facts-summary__table-body'})
    nutrition_facts = {}
    if nutrition_summary_tbody:
        for row in nutrition_summary_tbody.find_all('tr', {'class': 'mntl-nutrition-facts-summary__table-row'}):
            amount = row.find('td', {'class': 'mntl-nutrition-facts-summary__table-cell type--dog-bold'}).text.strip() if row.find('td', {'class': 'mntl-nutrition-facts-summary__table-cell type--dog-bold'}) else ''
            name = row.find('td', {'class': 'mntl-nutrition-facts-summary__table-cell type--dogg'}).text.strip() if row.find('td', {'class': 'mntl-nutrition-facts-summary__table-cell type--dogg'}) else ''
            nutrition_facts[name] = amount

    # Scrape the detailed table
    nutrition_detailed_tbody = soup.find('tbody', {'class': 'mntl-nutrition-facts-label__table-body type--cat'})
    if nutrition_detailed_tbody:
        for row in nutrition_detailed_tbody.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                name = cells[0].text.strip()
                amount = cells[1].text.strip()
                nutrition_facts[name] = amount
            elif len(cells) == 1:
                name_and_amount = cells[0].text.strip().split('\n')
                if len(name_and_amount) == 2:
                    name, amount = name_and_amount
                    nutrition_facts[name.strip()] = amount.strip()

    print(f"Found nutrition facts: {nutrition_facts}")
    recipeInfo['nutrition'] = nutrition_facts

    img_tag = soup.find('img', {'class': 'primary-image__image'})
    if img_tag and 'src' in img_tag.attrs:
        img_url = img_tag['src']
        
        output_folder = 'output\\imgs'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        img_filename = os.path.basename(img_url)
        full_path = os.path.join(output_folder, img_filename)
        recipeInfo['image'] = full_path
        
        # Check if the image already exists
        if not os.path.exists(full_path):
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open(full_path, 'wb') as img_file:
                    img_file.write(img_response.content)

    append_to_json_file('.\\output\\data\\recipeInfo.json', recipeInfo)
    
    return recipeInfo

def append_to_json_file(filepath, new_data):
    try:
        # Read existing data
        with open(filepath, 'r') as infile:
            existing_data = json.load(infile)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {'recipes': {'recipe': []}}

    # Append new data
    existing_data['recipes']['recipe'].append(new_data)

    # Write updated data back to file
    with open(filepath, 'w') as outfile:
        json.dump(existing_data, outfile, indent=4)

def main():
    recipeURL = "https://www.allrecipes.com/recipes-a-z-6735880"

    catagoryURLs = getCatagoryURLs(recipeURL)
    recipeURLs = []
    for catagoryURL in catagoryURLs:
        recipeURLs = getRecipeURLs(catagoryURL)

        recipeInfo = []
        for recipeURL in recipeURLs:
            print(f"getting recipe info for {recipeURL}")
            recipeInfo.append(getRecipeInfo(recipeURL))

if __name__ == "__main__":
    main()