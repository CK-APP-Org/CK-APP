# Legacy manual tool. The maintained version runs as a GitHub Action in the Data repo (scripts/).
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import List, Dict
import cairosvg  # You'll need to install this package

def get_monday_date(date: datetime) -> datetime:
    """Returns the Monday of the week for any given date"""
    print(f"DEBUG: Getting Monday date for {date}")
    print(f"DEBUG: Date type is {type(date)}")
    if not date:
        raise ValueError("Date cannot be None")
    return date - timedelta(days=date.weekday())

def create_menu_svg(date: datetime, menu_items: List[Dict], highlight_after_item: int = 4) -> str:  # Changed from 5 to 4
    """Creates an SVG visualization for a day's menu with proper support for Chinese characters"""
    print(f"\nDEBUG: Creating SVG for date {date}")
    print(f"DEBUG: Number of menu items: {len(menu_items)}")
    print(f"DEBUG: Sample menu item: {menu_items[0] if menu_items else 'No items'}")
    
    if not date:
        raise ValueError("Date cannot be None")
    
    # Format date as "月日" (e.g., "2月24日")
    formatted_date = f"{date.month}月{date.day}日"
    
    # Adjusted starting position for menu items (moved up)
    initial_y_position = 120
    
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="420" height="1000" viewBox="0 0 420 1000" xmlns="http://www.w3.org/2000/svg">
    <!-- Fonts for CJK character support -->
    <defs>
        <style type="text/css">
            @font-face {{
                font-family: 'Microsoft JhengHei';
                src: local('Microsoft JhengHei'), local('微軟正黑體'), local('Noto Sans TC'), local('Source Han Sans TC');
                font-weight: normal;
                font-style: normal;
            }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="420" height="1000" fill="#f8f9fa"/>
    
    <!-- Header with date -->
    <rect x="0" y="0" width="420" height="80" fill="#9C9C9C"/>
    <text x="30" y="52" font-family="'Microsoft JhengHei', '微軟正黑體', sans-serif" font-size="36" fill="white" font-weight="bold" dominant-baseline="middle">
        {formatted_date} 菜單
    </text>
    
    <!-- Menu items -->'''

    print("DEBUG: Created SVG header")

    # Add menu items
    y_position = initial_y_position
    row_height = 80
    for idx, item in enumerate(menu_items):
        print(f"DEBUG: Processing menu item {idx + 1}: {item}")
        price = int(float(item['price']))
        text_y = y_position + (row_height / 2)
        
        svg += f'''
    <!-- Item {idx + 1} -->
    <g>
        <!-- Item number and name - vertically centered -->
        <text x="40" y="{text_y}" font-family="'Microsoft JhengHei', '微軟正黑體', sans-serif" font-size="28" fill="#333" font-weight="500" dominant-baseline="middle">
            {int(item['dish_number'])}. {item['dish_name']}
        </text>
        <!-- Price - moved further right and vertically centered -->
        <text x="380" y="{text_y}" font-family="'Microsoft JhengHei', '微軟正黑體', sans-serif" font-size="28" fill="#c10015" font-weight="bold" text-anchor="end" dominant-baseline="middle">
            ${price}
        </text>
        <!-- Divider line - darker and longer for specified position -->
        <line x1="{20 if idx == highlight_after_item else 40}" 
            y1="{y_position + row_height}" 
            x2="{400 if idx == highlight_after_item else 380}" 
            y2="{y_position + row_height}" 
            stroke="{('#333' if idx == highlight_after_item else '#dee2e6')}" 
            stroke-width="{2.5 if idx == highlight_after_item else 1.5}"/>
    </g>'''
        y_position += row_height

    svg += '\n</svg>'
    print("DEBUG: Completed SVG creation")
    return svg

def create_empty_menu_svg(date: datetime) -> str:
    """Creates an SVG for days with no menu"""
    if not date:
        raise ValueError("Date cannot be None")
    
    # Format date as "月日"
    formatted_date = f"{date.month}月{date.day}日"
    
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="420" height="1000" viewBox="0 0 420 1000" xmlns="http://www.w3.org/2000/svg">
    <!-- Fonts for CJK character support -->
    <defs>
        <style type="text/css">
            @font-face {{
                font-family: 'Microsoft JhengHei';
                src: local('Microsoft JhengHei'), local('微軟正黑體'), local('Noto Sans TC'), local('Source Han Sans TC');
                font-weight: normal;
                font-style: normal;
            }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="420" height="1000" fill="#f8f9fa"/>
    
    <!-- Header with date -->
    <rect x="0" y="0" width="420" height="80" fill="#9C9C9C"/>
    <text x="30" y="52" font-family="'Microsoft JhengHei', '微軟正黑體', sans-serif" font-size="36" fill="white" font-weight="bold" dominant-baseline="middle">
        {formatted_date} 菜單
    </text>
    
    <!-- No menu message -->
    <text x="210" y="500" font-family="'Microsoft JhengHei', '微軟正黑體', sans-serif" font-size="36" fill="#333" font-weight="bold" text-anchor="middle" dominant-baseline="middle">
        本日無菜單
    </text>
</svg>'''
    return svg

def save_menu_visualizations(menu_data: List[Dict], use_previous_date: bool = False) -> None:
    """Saves menu visualizations as PNG files converted from SVG"""
    print("\nDEBUG: Starting save_menu_visualizations")
    print(f"DEBUG: Received {len(menu_data)} menu items")
    print(f"DEBUG: Using previous date: {use_previous_date}")

    # Group menu items by date
    menu_by_date = {}
    for item in menu_data:
        date = item['date']
        if date:
            if date not in menu_by_date:
                menu_by_date[date] = []
            menu_by_date[date].append(item)

    if not menu_by_date:
        print("DEBUG: No valid menu data found!")
        return

    # Get Monday of the week and the date range for the week
    first_date = min(menu_by_date.keys())
    monday_date = get_monday_date(first_date)
    week_dates = [monday_date + timedelta(days=i) for i in range(5)]  # Monday to Friday
    
    # Calculate the date to use in filenames
    filename_base_date = monday_date - timedelta(days=1) if use_previous_date else monday_date

    # Create directory for output
    output_dir = "menu_visualizations"
    os.makedirs(output_dir, exist_ok=True)

    # Create and save visualizations for each day of the week
    for date in week_dates:
        try:
            day_number = date.weekday() + 1  # 1 for Monday, 2 for Tuesday, etc.
            
            # Check if we have menu items for this day
            items = menu_by_date.get(date, [])
            
            # Create appropriate SVG content
            if items:
                svg_content = create_menu_svg(date, items)
            else:
                print(f"DEBUG: No menu items found for {date}, creating empty menu visualization")
                svg_content = create_empty_menu_svg(date)
            
            # Define filenames using the Monday date (or Sunday for previous date set)
            svg_filename = os.path.join(output_dir, f"{filename_base_date.strftime('%Y-%m-%d')}_{day_number}.svg")
            png_filename = os.path.join(output_dir, f"{filename_base_date.strftime('%Y-%m-%d')}_{day_number}.png")
            
            # Save SVG (temporary)
            with open(svg_filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            # Convert SVG to PNG
            cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=png_filename)
            
            # Remove temporary SVG file if PNG conversion was successful
            if os.path.exists(png_filename):
                os.remove(svg_filename)
                print(f"Created {png_filename}")
            else:
                print(f"WARNING: PNG conversion may have failed for {svg_filename}")
            
        except Exception as e:
            print(f"ERROR: Failed to create visualization for {date}: {str(e)}")
            import traceback
            print(traceback.format_exc())

def process_and_visualize_menu(file_path: str, sheet_name: str = "週菜單", create_previous_date_set: bool = False) -> None:
    """Main function to process menu data and create visualizations"""
    print("\nDEBUG: Starting process_and_visualize_menu")
    print(f"DEBUG: File path: {file_path}")
    print(f"DEBUG: Sheet name: {sheet_name}")
    print(f"DEBUG: Create previous date set: {create_previous_date_set}")
    
    try:
        # Import and use the scraping function
        from menu_scraper import scrape_menu
        
        # Scrape menu data
        menu_data = scrape_menu(file_path, sheet_name)
        
        # Validate menu data
        if not menu_data:
            raise ValueError("No menu data was scraped from the file")
            
        # Create visualizations with current date
        save_menu_visualizations(menu_data)
        
        # Create additional set with previous date if requested
        if create_previous_date_set:
            save_menu_visualizations(menu_data, use_previous_date=True)
        
        print("DEBUG: Process completed successfully!")
        
    except Exception as e:
        print(f"ERROR: Failed to process menu: {str(e)}")
        import traceback
        print(traceback.format_exc())

# Example usage
if __name__ == "__main__":
    process_and_visualize_menu("menu.xlsx", create_previous_date_set=True)
