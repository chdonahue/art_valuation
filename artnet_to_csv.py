"""  
Parses artnet pdf pages and extracts the data into a csv file.
"""
import os
import re
from datetime import datetime
import pandas as pd
import fitz

ARTNET_CATEGORIES = ['Title', 'Description', 'Medium', 'Year of Work', 
              'Size', 'Sale of', 'Estimate', 'Sold For', 'Misc.']


def find_artnet_separators(doc):
    """ 
    Each entry is separated by horizontal lines. 
    This finds the page number and y-coordinate of each separator so each entry can be parsed.

    Parameters:
        doc (fitz.fitz.Document): The document to parse.

    Returns:
        separator (list): A list of dictionaries, each containing the page number and y-coordinate of a separator line
    """
    separators = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()   
        # Find separator lines
        for drawing in drawings:
            if drawing['items'][0][0] == 're':  # It's a rectangle
                rect = drawing['items'][0][1]
                if abs(rect.y1 - rect.y0) < 1 and rect.width > 100:
                    # Store both page number and y-coordinate
                    separators.append({
                        'page': page_num,
                        'y': rect.y0
                    })    
    # Remove the page border rectangles (usually at the top of pages)
    separators = [sep for sep in separators if sep['y'] > 50]
    return separators

def get_artwork_info(doc, start_sep, end_sep):
    """ 
    Extracts artwork info between two separators.

    Parameters:
        doc (fitz.fitz.Document): The document to parse.
        start_sep (dict): The starting separator.
        end_sep (dict): The ending separator.

    Returns:
        artwork (dict): The text between the separators.
    """
    text = ""
    # If separators are on the same page
    if start_sep['page'] == end_sep['page']:
        page = doc[start_sep['page']]
        rect = fitz.Rect(0, start_sep['y'], page.rect.width, end_sep['y'])
        text = page.get_text("text", clip=rect).strip()
    else:
        # Handle text spanning multiple pages
        # Get text from first page (from separator to bottom)
        first_page = doc[start_sep['page']]
        rect = fitz.Rect(0, start_sep['y'], first_page.rect.width, first_page.rect.height)
        text = first_page.get_text("text", clip=rect).strip()
        
        # Get text from any middle pages (full page)
        for page_num in range(start_sep['page'] + 1, end_sep['page']):
            middle_page = doc[page_num]
            text += "\n" + middle_page.get_text("text").strip()
        
        # Get text from last page (from top to separator)
        if start_sep['page'] != end_sep['page']:
            last_page = doc[end_sep['page']]
            rect = fitz.Rect(0, 0, last_page.rect.width, end_sep['y'])
            text += "\n" + last_page.get_text("text", clip=rect).strip()
    

    if text:
        artwork = {}
        current_field = None
        lines = text.split('\n')
        
        # Process each line
        for idx, line in enumerate(lines):
            line = line.strip()
            
            # Look for Title field, and get the line before it as the artist
            if line.startswith('Title'):
                if idx > 0:
                    artist_line = lines[idx-1].strip()
                    if not any(artist_line.startswith(field) for field in ARTNET_CATEGORIES):
                        artwork['Artist'] = artist_line
            
            for field in ARTNET_CATEGORIES:
                if line.startswith(field):
                    current_field = field
                    value = line[len(field):].strip()
                    if value.startswith(':'):
                        value = value[1:].strip()
                    artwork[field] = value
                    break
            else:
                if current_field and current_field in artwork:
                    artwork[current_field] += " " + line       
    return artwork

def parse_sale_of_column(entry):
    """ 
    Parses each sale_of column entry to extract auction house, sale date, lot number, and online status.
    """
    pattern = r"^(.*?):\s*(.*?)\s*\[(Lot\s*[0-9A-Za-z\s]+)\](.*?)$"
    
    try:
        match = re.match(pattern, str(entry))
        if not match:
            return pd.Series({
                'auction_house': None,
                'sale_date': None,
                'lot_number': None,
                'is_online': False
            })
        
        auction_house, date_str, lot_number, description = match.groups()
        
        date = datetime.strptime(date_str.strip(), "%A, %B %d, %Y")
        
        is_online = bool(re.search(r'online', description, re.IGNORECASE))
        lot_number = re.sub(r'Lot\s*', '', lot_number).strip()
        
        return pd.Series({
            'auction_house': auction_house.strip(),
            'sale_date': date,
            'lot_number': lot_number,
            'is_online': is_online
        })
    except:
        return pd.Series({
            'auction_house': None,
            'sale_date': None,
            'lot_number': None,
            'is_online': False
        })


def main():
    pdf_files = [f for f in os.listdir('data') if f.endswith('.pdf')]
    results = []
    for file in pdf_files: # Loop through all PDF files
        print(f"Processing {file}")
        doc = fitz.open(os.path.join('data',file))
        separators = find_artnet_separators(doc)
        for i in range(len(separators) - 1):
            start_sep = separators[i]
            end_sep = separators[i + 1]
            artwork = get_artwork_info(doc, start_sep, end_sep)
            results.append(artwork)
    df = pd.DataFrame(results)
    # Parse the 'Sale of' column to extract auction house, sale date, lot number, and online status:
    parsed_columns = df['Sale of'].apply(parse_sale_of_column)
    df['auction_house'] = parsed_columns.apply(lambda x: x.get('auction_house', None), axis=1)
    df['sale_date'] = parsed_columns.apply(lambda x: x.get('sale_date', None), axis=1)
    df['lot_number'] = parsed_columns.apply(lambda x: x.get('lot_number', None), axis=1)
    df['is_online'] = parsed_columns.apply(lambda x: x.get('is_online', False), axis=1)
    df.to_csv('artnet_results.csv', index=False)


if __name__ == "__main__":
    main()