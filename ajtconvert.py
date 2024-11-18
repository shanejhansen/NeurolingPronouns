import pandas as pd
import re
import os

def get_image_name(condition_number, first_word, third_word):
    image_mapping = {
        1: 'Jf', 2: 'Jf', 3: 'Gf', 4: 'Gf', 5: 'Af', 6: 'Af',
        9: 'Je', 10: 'Je', 11: 'Ge', 12: 'Ge', 13: 'Ae', 14: 'Ae'
    }
    
    if condition_number in [7, 8, 15, 16]:
        suffix = 'f' if condition_number in [7, 8] else 'e'
        if first_word == 'Alex':
            return f"A{'G' if third_word == 'George' else 'J'}{suffix}"
        else:
            return f"GJ{suffix}"
    
    return image_mapping.get(condition_number, '')

def transform_excel(input_file, output_file):
    # Read the input Excel file
    df = pd.read_excel(input_file)

    # Create a list to store the output rows
    output_rows = []

    # Process each row in the input DataFrame
    for _, row in df.iterrows():
        item_number = row['Item Number']
        condition_number = row['Condition Number']
        stimulus = row['Stimulus'].strip()  # Remove leading/trailing whitespace

        # Split the stimulus into words
        words = re.findall(r'\b\w+\b', stimulus)

        # Add period to the last word if it's missing
        if not stimulus.endswith('.'):
            words[-1] += '.'
        elif words[-1].endswith('.'):
            # If the last word already has a period, remove it temporarily
            words[-1] = words[-1][:-1]

        # Get image name
        image_name = get_image_name(condition_number, words[0] if words else '', words[2] if len(words) > 2 else '')

        # Create a new row for the output DataFrame
        new_row = {
            'Item:': item_number,
            'StimNum': item_number,
            'StimType': condition_number,
            'Image': image_name,
            'Probe': '???',
            'Cresp': 1 if condition_number % 2 == 0 else 5  # Keep this as is
        }

        # Process each word in the stimulus
        pronoun_found = False
        for i in range(8):  # Always process 8 word columns
            word_column = f'{["First", "Sec", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth"][i]}Word'
            code_column = f'code{i+1}'

            if i < len(words):
                word = words[i]
                if i == len(words) - 1:
                    word += '.'  # Add period to the last word
                new_row[word_column] = word
                
                # Apply code only before pronoun
                if word.lower().rstrip('.') in ['he', 'she', 'they', 'il', 'elle', 'iel'] and not pronoun_found:
                    new_row[code_column] = item_number + 10
                    pronoun_found = True
                else:
                    new_row[code_column] = 0
            else:
                new_row[word_column] = 'x'  # Fill empty word columns with 'x'
                new_row[code_column] = 0  # Fill empty code columns with 0

        # Add the new row to the output rows list
        output_rows.append(new_row)

    # Create the output DataFrame from the list of rows
    output_df = pd.DataFrame(output_rows)

    # Ensure all columns are present, even if they weren't used
    all_columns = [
        'Item:', 'StimNum', 'StimType', 'Image', 'code1', 'FirstWord', 'code2', 'SecWord',
        'code3', 'ThirdWord', 'code4', 'FourthWord', 'code5', 'FifthWord', 'code6', 'SixthWord',
        'code7', 'SeventhWord', 'code8', 'EighthWord', 'Probe', 'Cresp'
    ]
    for col in all_columns:
        if col not in output_df.columns:
            output_df[col] = ''

    # Reorder columns to match the desired output
    output_df = output_df[all_columns]

    # Fill empty cells with empty strings
    output_df = output_df.fillna('')

    # Write the output DataFrame to an Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        output_df.to_excel(writer, index=False)
        
        # Auto-adjust column widths
        for column in output_df:
            column_width = max(output_df[column].astype(str).map(len).max(), len(column))
            col_idx = output_df.columns.get_loc(column)
            writer.sheets['Sheet1'].column_dimensions[chr(65 + col_idx)].width = column_width

def process_all_files():
    input_files = [
        'stimuli_list_CQ.xlsx', 
    ]
    
    for input_file in input_files:
        # Correctly extract the file identifier (A1, A2, B1, etc.)
        file_id = input_file.split('_')[-1].split('.')[0]
        output_file = f"AJT{file_id}.xlsx"  # e.g., AJTA1.xlsx
        print(f"Processing {input_file}...")
        transform_excel(input_file, output_file)
        print(f"Completed. Output saved as {output_file}")

# Usage
if __name__ == "__main__":
    process_all_files()