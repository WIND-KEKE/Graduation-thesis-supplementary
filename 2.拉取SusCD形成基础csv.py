import os
import csv

def process_faa_files():
    directory = os.path.dirname(os.path.abspath(__file__))

    for filename in os.listdir(directory):
        if filename.endswith(".faa"):
            output_file = os.path.join(directory, f'{os.path.splitext(filename)[0]}_protein_tags.csv')
            
            with open(output_file, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Protein Tag', 'Contains SusC/SusD', 'Protein Number'])
                
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as file:
                    for line in file:
                        if line.startswith(">"):
                            parts = line[1:].strip().split()
                            protein_tag = parts[0]
                            
                            contains_SusC = 'SusC' in line
                            contains_SusD = 'SusD' in line
                            
                            if contains_SusC or contains_SusD:
                                sus_type = 'SusC' if contains_SusC else 'SusD'
                                protein_number = protein_tag.split('_')[-1]
                                csvwriter.writerow([protein_tag, sus_type, protein_number])

if __name__ == "__main__":
    process_faa_files()
