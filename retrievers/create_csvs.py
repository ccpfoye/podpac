import os
import csv

def md_files_to_csv(input_dir, output_file):
    if not os.path.exists(input_dir):
        raise ValueError("Input directory does not exist")

    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        writer.writerow(['title', 'text'])

        for file_name in os.listdir(input_dir):
            if file_name.endswith('.md'):
                file_path = os.path.join(input_dir, file_name)

                with open(file_path, mode='r', encoding='utf-8') as md_file:
                    title = os.path.splitext(file_name)[0]
                    text = md_file.read().replace('\n', ' ').replace('\r', ' ').strip()
                    writer.writerow([title, text])

# Example usage
input_dir = '/home/cfoye/Personal/podpac/doc/source'
output_file = 'output_csv_file.csv'
md_files_to_csv(input_dir, output_file)