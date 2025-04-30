import os

def process_faa_files(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.faa'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.splitext(input_file)[0] + '.out'
            with open(input_file, 'r') as input_faa, open(output_file, 'w') as output_faa:
                writing_sequence = False
                for line in input_faa:
                    if line.startswith('>'):
                        if 'SusC' in line or 'SusD' in line:
                            writing_sequence = True
                            output_faa.write(line)
                        else:
                            writing_sequence = False
                    elif writing_sequence:
                        output_faa.write(line)

if __name__ == '__main__':
    input_folder = '/home/caoke/CKK/susCD'
    process_faa_files(input_folder)

