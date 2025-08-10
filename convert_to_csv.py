import json
import csv

def main():
    # Read the JSON file
    with open('quote_token_mapping.json', 'r') as json_file:
        data = json.load(json_file)

    # Create a list of (quote, token_id) pairs
    quote_token_pairs = []
    for quote, token_ids in data.items():
        for token_id in token_ids:
            quote_token_pairs.append((quote, token_id))

    # Sort by token_id for better readability
    quote_token_pairs.sort(key=lambda x: x[1])

    # Write to CSV
    with open('quote_token_mapping.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write header
        writer.writerow(['quote', 'token_id'])
        # Write data
        for quote, token_id in quote_token_pairs:
            writer.writerow([quote, token_id])

    print("CSV file 'quote_token_mapping.csv' has been created successfully.")

if __name__ == "__main__":
    main()
