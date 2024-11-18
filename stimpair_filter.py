import pandas as pd

def process_file(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Print column names
    print("Columns in the DataFrame:")
    print(df.columns)
    
    # Ask for the correct column name
    surprisal_column = input("Please enter the exact name of the column containing surprisal values: ")
    
    # Create a new empty list to store the results
    result_list = []
    
    # Process pairs of sentences
    for i in range(0, len(df), 2):
        pair = df.iloc[i:i+2]
        
        # Keep the sentence with lower surprisal
        kept_sentence = pair.loc[pair[surprisal_column].idxmin()]
        
        # Add the kept sentence to the result list
        result_list.append(kept_sentence)
    
    # Create a new DataFrame from the result list
    result_df = pd.DataFrame(result_list)
    
    # Write the result to a new CSV file
    result_df.to_csv(output_file, index=False)
    
    print(f"Processed file saved as {output_file}")
    print(f"Original sentence count: {len(df)}")
    print(f"Processed sentence count: {len(result_df)}")

# Main execution
if __name__ == "__main__":
    input_file = "paired_sentences.csv"  # Change this to your input file name
    output_file = "filtered_roberta.csv"  # Change this to your desired output file name
    
    process_file(input_file, output_file)