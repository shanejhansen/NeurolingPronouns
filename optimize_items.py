import csv
from collections import Counter, defaultdict
import random
import math

def load_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        return list(reader)

def count_verbs_and_connectors(data):
    verbs = Counter()
    connectors = Counter()
    for item in data:
        verbs[item[1]] += 1
        verbs[item[3]] += 1
        connectors[item[2]] += 1
    return verbs, connectors

def calculate_target_distribution(verbs, connectors, num_items):
    total_verbs = sum(verbs.values())
    total_connectors = sum(connectors.values())
    target_verbs = {v: min((count / total_verbs) * num_items * 2, num_items * 0.2) for v, count in verbs.items()}
    target_connectors = {c: (count / total_connectors) * num_items for c, count in connectors.items()}
    return target_verbs, target_connectors

def initial_selection(data, num_items):
    return random.sample(data, num_items)

def score_selection(selection, target_verbs, target_connectors, num_items):
    current_verbs = Counter()
    current_connectors = Counter()
    full_combinations = Counter()
    verb1_counts = Counter()
    verb2_counts = Counter()

    for item in selection:
        current_verbs[item[1]] += 1
        current_verbs[item[3]] += 1
        current_connectors[item[2]] += 1
        full_combinations[(item[1], item[2], item[3])] += 1
        verb1_counts[item[1]] += 1
        verb2_counts[item[3]] += 1

    # Penalize verbs that appear in more than 10% of items
    max_verb_count = num_items * 0.1
    over_limit_penalty = sum(max(0, count - max_verb_count) ** 2 for count in current_verbs.values())

    # Penalize repeated full combinations
    repeat_penalty = sum(count - 1 for count in full_combinations.values() if count > 1)

    verb_score = sum((min(current_verbs[v], target_verbs[v]) - target_verbs[v]) ** 2 for v in target_verbs)
    connector_score = sum((current_connectors[c] - target_connectors[c]) ** 2 for c in target_connectors)
    combination_score = len(full_combinations)
    position_score = sum((verb1_counts[v] - verb2_counts[v]) ** 2 for v in target_verbs)

    return -(verb_score + connector_score * 2 - combination_score * 10 + position_score + over_limit_penalty * 100 + repeat_penalty * 50)

def simulated_annealing(data, num_items, target_verbs, target_connectors, initial_temp=100, cooling_rate=0.995, iterations=20000):
    current_selection = initial_selection(data, num_items)
    current_score = score_selection(current_selection, target_verbs, target_connectors, num_items)
    best_selection = current_selection[:]
    best_score = current_score
    temperature = initial_temp

    for i in range(iterations):
        if i % 1000 == 0:
            print(f"Iteration {i}, Temperature: {temperature:.2f}, Score: {current_score:.2f}")

        # Choose an item to remove and an item to add
        remove_index = random.randint(0, num_items - 1)
        add_item = random.choice([item for item in data if item not in current_selection])

        # Create new selection
        new_selection = current_selection[:]
        new_selection[remove_index] = add_item

        # Calculate new score
        new_score = score_selection(new_selection, target_verbs, target_connectors, num_items)

        # Decide whether to accept the new selection
        if new_score > current_score or random.random() < math.exp((new_score - current_score) / temperature):
            current_selection = new_selection
            current_score = new_score

            if current_score > best_score:
                best_selection = current_selection[:]
                best_score = current_score

        # Cool down
        temperature *= cooling_rate

    return best_selection

def write_results_to_csv(optimized_items, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Original Item Number', 'Verb1', 'Connector', 'Verb2'])
        writer.writerows(optimized_items)

    print(f"Results written to {filename}")

def print_statistics(selection, target_verbs, target_connectors, num_items):
    current_verbs = Counter()
    current_connectors = Counter()
    full_combinations = Counter()

    for item in selection:
        current_verbs[item[1]] += 1
        current_verbs[item[3]] += 1
        current_connectors[item[2]] += 1
        full_combinations[(item[1], item[2], item[3])] += 1

    print("\nVerb Distribution:")
    for verb in sorted(current_verbs, key=current_verbs.get, reverse=True):
        percentage = (current_verbs[verb] / (num_items * 2)) * 100
        print(f"{verb}: {current_verbs[verb]} ({percentage:.2f}%) (Target: {target_verbs[verb]:.2f})")

    print("\nConnector Distribution:")
    for connector in sorted(current_connectors, key=current_connectors.get, reverse=True):
        percentage = (current_connectors[connector] / num_items) * 100
        print(f"{connector}: {current_connectors[connector]} ({percentage:.2f}%) (Target: {target_connectors[connector]:.2f})")

    print(f"\nTotal number of items: {num_items}")
    print(f"Unique full combinations (Verb1 + Connector + Verb2): {len(full_combinations)}")
    repeated_combinations = sum(count - 1 for count in full_combinations.values() if count > 1)
    print(f"Repeated full combinations: {repeated_combinations}")

    if repeated_combinations > 0:
        print("\nRepeated combinations:")
        for combination, count in full_combinations.items():
            if count > 1:
                print(f"{combination[0]} {combination[1]} {combination[2]}: {count} times")

    over_limit = [v for v, count in current_verbs.items() if count > num_items * 0.2]
    if over_limit:
        print("\nVerbs over 10% limit:")
        for verb in over_limit:
            percentage = (current_verbs[verb] / (num_items * 2)) * 100
            print(f"{verb}: {current_verbs[verb]} ({percentage:.2f}%)")
    else:
        print("\nNo verbs exceed the 10% limit.")

def main():
    data = load_data('items2.csv')
    num_items = 250

    verbs, connectors = count_verbs_and_connectors(data)
    target_verbs, target_connectors = calculate_target_distribution(verbs, connectors, num_items)

    optimized_items = simulated_annealing(data, num_items, target_verbs, target_connectors)

    write_results_to_csv(optimized_items, 'optimized_items_full_uniqueness.csv')
    print_statistics(optimized_items, target_verbs, target_connectors, num_items)

if __name__ == "__main__":
    main()