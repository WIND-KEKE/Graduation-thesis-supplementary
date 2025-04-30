import os
import csv
import re

def read_csv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        return list(reader)

def find_sus_pairs(sus_data):
    sus_pairs = []
    for i in range(len(sus_data) - 1):
        if len(sus_data[i]) < 2 or len(sus_data[i + 1]) < 2:
            continue  # Skip if data row is incomplete
        
        protein_number = int(sus_data[i][0].split('_')[-1])
        next_protein_number = int(sus_data[i + 1][0].split('_')[-1])
        
        if next_protein_number == protein_number + 1:
            sus_type = sus_data[i][1]
            next_sus_type = sus_data[i + 1][1]
            if (sus_type == 'SusC' and next_sus_type == 'SusD') or (sus_type == 'SusD' and next_sus_type == 'SusC'):
                sus_pairs.append((sus_data[i], sus_data[i + 1]))
    return sus_pairs

def process_files():
    directory = os.path.dirname(os.path.abspath(__file__))

    # Get all files in the directory
    files = os.listdir(directory)
    csv_files = [f for f in files if f.endswith('.csv') and not f.endswith('_sus_pairs.csv')]

    for csv_file in csv_files:
        base_name = re.match(r'(.+?)\.csv$', csv_file).group(1)
        output_file = os.path.join(directory, f'{base_name}_sus_pairs.csv')

        print(f'Processing {csv_file}...')

        sus_data = read_csv(os.path.join(directory, csv_file))
        sus_pairs = find_sus_pairs(sus_data)

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Protein', 'Type'])
            for pair in sus_pairs:
                writer.writerow(pair[0])  # Write first protein of the pair
                writer.writerow(pair[1])  # Write second protein of the pair
                writer.writerow([])  # Write empty row to separate pairs

        print(f'Finished processing {csv_file}. Results saved in {output_file}')

if __name__ == "__main__":
    process_files()
