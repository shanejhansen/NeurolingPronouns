import csv
import random
from collections import defaultdict

def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        return list(reader)

def write_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['number', 'verb1', 'connector', 'verb2'])
        writer.writerows(data)

def distribute_with_guaranteed_completion(data):
    # Group data by connector
    connector_groups = defaultdict(list)
    for row in data:
        connector_groups[row[1]].append(row)
    
    # Shuffle each group
    for group in connector_groups.values():
        random.shuffle(group)
    
    # Create a list of all connectors, repeated based on their frequency
    all_connectors = []
    for connector, group in connector_groups.items():
        all_connectors.extend([connector] * len(group))
    
    # Shuffle the list of all connectors
    random.shuffle(all_connectors)
    
    result = []
    connector_index = {}
    total_items = len(data)
    
    for i, connector in enumerate(all_connectors):
        # Try to maintain some distance between same connectors
        if i > 0 and connector == all_connectors[i-1]:
            # If we have a repeat, try to swap with a nearby different connector
            for j in range(i+1, min(i+5, len(all_connectors))):
                if all_connectors[j] != connector:
                    all_connectors[i], all_connectors[j] = all_connectors[j], all_connectors[i]
                    connector = all_connectors[i]
                    break
        
        # Get the next row for this connector
        row = connector_groups[connector][connector_index.get(connector, 0)]
        connector_index[connector] = connector_index.get(connector, 0) + 1
        
        # Add to result with a number
        result.append((i+1, *row))
        
        # Print progress
        if (i+1) % 10 == 0 or i+1 == total_items:
            print(f"Progress: {i+1}/{total_items} items processed")
    
    return result

def main():
    input_file = 'optimized_items_full_uniqueness.csv'
    output_file = 'guaranteed_completion_distributed_items.csv'

    data = read_csv(input_file)
    print(f"Total items to process: {len(data)}")
    distributed_data = distribute_with_guaranteed_completion(data)
    write_csv(output_file, distributed_data)

    print(f"Guaranteed completion distributed data has been written to {output_file}")

if __name__ == "__main__":
    main()