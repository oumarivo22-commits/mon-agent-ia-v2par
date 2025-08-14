import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time

def scrape_product_hunt():
    """
    Scrapes the Product Hunt homepage for new products by finding and
    parsing an embedded Apollo SSR JSON data blob.
    """
    print("Scraping Product Hunt...", file=sys.stderr)
    url = "https://www.producthunt.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    apollo_script_content = None
    for script in soup.find_all('script'):
        if script.string and 'ApolloSSRDataTransport' in script.string:
            apollo_script_content = script.string
            break

    if not apollo_script_content:
        print("Error: Could not find the ApolloSSRDataTransport script tag.", file=sys.stderr)
        return []

    try:
        start_marker = '.push('
        start_index = apollo_script_content.find(start_marker)
        if start_index == -1:
            return []

        start_index += len(start_marker)
        end_index = apollo_script_content.rfind(')')
        if end_index == -1:
            return []

        json_str = apollo_script_content[start_index:end_index]
        json_str = json_str.replace(':undefined', ':null')

    except Exception as e:
        print(f"Error during string manipulation: {e}", file=sys.stderr)
        return []

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse the JSON data. Error: {e}", file=sys.stderr)
        return []

    try:
        homefeed_data = None
        rehydrated_data = data.get('rehydrate', {})

        for value in rehydrated_data.values():
            if isinstance(value, dict):
                data_dict = value.get('data')
                if isinstance(data_dict, dict) and 'homefeed' in data_dict:
                    if data_dict['homefeed'] is not None:
                        homefeed_data = data_dict['homefeed']
                        break

        if not homefeed_data:
             print("Error: Could not find 'homefeed' in the Apollo JSON data.", file=sys.stderr)
             return []

        for edge in homefeed_data.get('edges', []):
            node = edge.get('node', {})
            if node is not None and node.get('__typename') == 'HomefeedPage':
                for item in node.get('items', []):
                    if item is not None and item.get('__typename') == 'Post':
                        name = item.get('name')
                        tagline = item.get('tagline')
                        if name and tagline:
                            products.append({'name': name, 'description': tagline})

        if not products:
            print("Warning: No products found in the homefeed data.", file=sys.stderr)

    except (KeyError, TypeError) as e:
        print(f"Error: The structure of the JSON data is not as expected. Error: {e}", file=sys.stderr)
        return []

    return products

def simulated_check_for_competitors(product_name, product_description):
    """
    Simulates checking for competitors.
    Returns True (competitor found) for products with even-length names (ignoring spaces),
    and False (no competitor) for products with odd-length names.
    This provides a mix of results for demonstration.
    """
    print(f"  -> Simulating search for '{product_name}'...", file=sys.stderr)
    time.sleep(0.1) # Add a small delay to make the simulation look more realistic

    # Simple, deterministic logic for simulation
    if len(product_name.replace(" ", "")) % 2 == 0:
        print(f"  -> Simulation result: Competitor FOUND for '{product_name}'.", file=sys.stderr)
        return True
    else:
        print(f"  -> Simulation result: No competitor found for '{product_name}'. This is an opportunity!", file=sys.stderr)
        return False

def main():
    """
    Main function for the Opportunity Detector Agent.
    1. Scrapes products from Product Hunt.
    2. Simulates checking for competitors in France.
    3. Presents a final report of opportunities.
    """
    print("--- Opportunity Detector Agent ---", file=sys.stderr)
    print("\\nStep 1: Scraping latest products from Product Hunt...", file=sys.stderr)
    scraped_products = scrape_product_hunt()

    if not scraped_products:
        print("Could not retrieve products. Exiting.", file=sys.stderr)
        return

    print(f"\\nStep 2: Found {len(scraped_products)} products. Now checking for competitors in France (simulation)...", file=sys.stderr)
    opportunities = []
    for product in scraped_products:
        has_competitors = simulated_check_for_competitors(product['name'], product['description'])
        if not has_competitors:
            opportunities.append(product)

    print("\\n-------------------------------------------", file=sys.stdout)
    print("--- Final Report: Business Opportunities ---", file=sys.stdout)
    print("The following US business ideas appear to have no direct competitors in France (based on simulation):", file=sys.stdout)

    if not opportunities:
        print("\\nNo opportunities found in this batch.", file=sys.stdout)
    else:
        for i, opportunity in enumerate(opportunities, 1):
            print(f"\\n{i}. {opportunity['name']}", file=sys.stdout)
            print(f"   Description: {opportunity['description']}", file=sys.stdout)

    print("\\n-------------------------------------------", file=sys.stdout)


if __name__ == "__main__":
    main()
