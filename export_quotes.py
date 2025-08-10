import json
import csv

def main():
    try:
        # Read the JSON file with explicit UTF-8 encoding
        with open('quote_token_mapping.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Prepare CSV data
        rows = []
        for quote, token_ids in data.items():
            for token_id in token_ids:
                rows.append({
                    'quote': quote,
                    'token_id': token_id
                })
        
        # Sort by token_id
        rows.sort(key=lambda x: x['token_id'])
        
        # Write to CSV
        with open('quote_token_mapping.csv', 'w', newline='', encoding='utf-8') as f:
            if rows:  # Only write if we have data
                writer = csv.DictWriter(f, fieldnames=['quote', 'token_id'])
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"Successfully exported {len(rows)} quote mappings to quote_token_mapping.csv")
        print(f"Number of unique quotes: {len(data)}")
        print(f"Total token mappings: {len(rows)}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
