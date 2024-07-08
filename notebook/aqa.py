#!/usr/bin/env python3

# Check for necessary libraries
required_libraries = {
    'Bio': 'biopython',
    'pandas': 'pandas',
    'matplotlib': 'matplotlib',
    'argparse': 'argparse',
    'xlsxwriter': 'xlsxwriter'
}

all_installed = True

for lib, install_name in required_libraries.items():
    try:
        __import__(lib)
    except ImportError:
        print(f"Error: The library '{lib}' is not installed. You can install it using the command:\n")
        print(f"pip install {install_name}")
        all_installed = False

if all_installed:
    print("All required libraries are installed.")

# Import necessary libraries
import os
from datetime import datetime
from Bio import SeqIO
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Define functions for calculating N50 and L50
def calculate_N50(sequence_lengths):
    total_length = sum(sequence_lengths)
    half_length = total_length / 2

    sorted_lengths = sorted(sequence_lengths)
    cumulative_length = 0
    for length in sorted_lengths:
        cumulative_length += length
        if cumulative_length >= half_length:
            return length

def calculate_L50(sequence_lengths):
    total_length = sum(sequence_lengths)
    half_length = total_length / 2

    sorted_lengths = sorted(sequence_lengths, reverse=True)
    cumulative_length = 0
    for idx, length in enumerate(sorted_lengths):
        cumulative_length += length
        if cumulative_length >= half_length:
            return length, idx + 1  # Return L50 length and the number of contigs included

# Define function for calculating genome size
def calculate_genome_size(sequence_lengths):
    return sum(sequence_lengths)

# Define functions for calculating GC content
def calculate_gc_content(sequence):
    gc_count = sequence.count('G') + sequence.count('C')
    total_count = len(sequence)
    gc_content = (gc_count / total_count) * 100
    return round(gc_content, 2)

# Define functions for assessing eligibility
def assess_eligibility(num_contigs, genome_size, gc_content, contig_cutoff, genome_size_min, genome_size_max, gc_content_min, gc_content_max):
    if contig_cutoff is None or genome_size_min is None or genome_size_max is None or gc_content_min is None or gc_content_max is None:
        return ''
    if num_contigs <= contig_cutoff and genome_size_min <= genome_size <= genome_size_max and gc_content_min <= gc_content <= gc_content_max:
        return 'Eligible'
    else:
        return 'Not Eligible'

# Function to process each FASTA file
def process_fasta_file(file_path, cont_size_limit=500):
    n50_list = []
    l50_list = []
    num_contigs_list = []
    genome_size_list = []
    gc_content_list = []
    contigs_shorter_than_limit = 0
    
    for record in SeqIO.parse(file_path, 'fasta'):
        sequence_length = len(record.seq)
        n50_list.append(sequence_length)
        num_contigs_list.append(1)
        genome_size_list.append(sequence_length)
        gc_content_list.append(round(calculate_gc_content(record.seq), 2))
        
        if sequence_length < cont_size_limit:
            contigs_shorter_than_limit += 1

    n50 = calculate_N50(n50_list)
    l50, num_contigs_included = calculate_L50(n50_list)
    num_contigs = sum(num_contigs_list)
    genome_size = calculate_genome_size(genome_size_list)
    gc_content_rounded = round(sum(gc_content_list) / len(gc_content_list), 2)
    
    return n50, l50, num_contigs, genome_size, gc_content_rounded, gc_content_list, contigs_shorter_than_limit

# Main function
def main(contig_cutoff, genome_size_min, genome_size_max, gc_content_min, gc_content_max, output_file_txt, output_file_excel, cont_size_limit):
    input_dir = os.getcwd()
    data = []
    fasta_file_count = 0  # Counter for counting FASTA files processed
    
    # Get current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Header information
    header_txt = f"Title: Assembly Assessment Report\nInstitute: The Arctic University of Norway - Tromsø\nWritten by: Mushtaq T. S. AL-Rubaye\nTime: {current_time}\n\n"
    header_excel = f"Assembly Assessment Report\n\nInstitute: The Arctic University of Norway - Tromsø\nWritten by: Mushtaq T. S. AL-Rubaye\nTime: {current_time}"
    
    with open(output_file_txt, 'w') as f_out:
        f_out.write(header_txt)
        f_out.write("File\tN50\tL50\tNum Contigs\tContigs Quality\tGenome Size\tGenome Size Quality\tGC Content\tGC Content range\tEligibility\tContigs < {cont_size_limit} bp\n".format(cont_size_limit=cont_size_limit))
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.fasta'):
                fasta_file_count += 1  # Increment the counter for each FASTA file found
                file_path = os.path.join(input_dir, file_name)
                n50, l50, num_contigs, genome_size, gc_content_rounded, gc_content_list, contigs_shorter_than_limit = process_fasta_file(file_path, cont_size_limit)
                contigs_quality = '' if contig_cutoff is None else ('Yes' if num_contigs <= contig_cutoff else 'No')
                genome_size_quality = '' if genome_size_min is None or genome_size_max is None else ('Yes' if genome_size_min <= genome_size <= genome_size_max else 'No')
                gc_content_range = '' if gc_content_min is None or gc_content_max is None else ('Warning' if not (gc_content_min <= gc_content_rounded <= gc_content_max) else '-')
                eligibility = assess_eligibility(num_contigs, genome_size, gc_content_rounded, contig_cutoff, genome_size_min, genome_size_max, gc_content_min, gc_content_max)
                data.append([file_name, n50, l50, num_contigs, contigs_quality, genome_size, genome_size_quality, gc_content_rounded, gc_content_range, eligibility, contigs_shorter_than_limit])
                f_out.write(f"{file_name}\t{n50}\t{l50}\t{num_contigs}\t{contigs_quality}\t{genome_size}\t{genome_size_quality}\t{gc_content_rounded}\t{gc_content_range}\t{eligibility}\t{contigs_shorter_than_limit}\n")

    # Write data to Excel file
    df = pd.DataFrame(data, columns=["File", "N50", "L50", "Num Contigs", "Contigs Quality", "Genome Size", "Genome Size Quality", "GC Content", "GC Content range", "Eligibility", "Contigs < {cont_size_limit} bp".format(cont_size_limit=cont_size_limit)])
    with pd.ExcelWriter(output_file_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, header=False, startrow=3)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.write('A1', header_excel)
    
    # Generate and save plot if cutoffs are specified
    if all(v is not None for v in [contig_cutoff, genome_size_min, genome_size_max, gc_content_min, gc_content_max]):
        labels = ['Eligible', 'Not Eligible']
        sizes = [df['Eligibility'].value_counts().get('Eligible', 0), df['Eligibility'].value_counts().get('Not Eligible', 0)]
        colors = ['#66b3ff', '#ff9999']
        explode = (0.1, 0)  # explode the 1st slice

        plt.figure(figsize=(7, 5))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)  # corrected autopct format
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Assembly Eligibility Distribution')
        current_date = datetime.now().strftime("%Y-%m-%d")
        plt.savefig(f'assembly_eligibility_distribution_{current_date}.jpg')
        plt.close()  # Close the plot to avoid blocking

    # Print the count of FASTA files processed
    print(f"Number of FASTA files assessed: {fasta_file_count}")

# Main block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assess the quality of genome assemblies.")
    parser.add_argument('--con-cut', type=int, help='Contig cutoff for eligibility')
    parser.add_argument('--size_min', type=int, help='Minimum genome size for eligibility')
    parser.add_argument('--size_max', type=int, help='Maximum genome size for eligibility')
    parser.add_argument('--gc_min', type=float, help='Minimum GC content for eligibility')
    parser.add_argument('--gc_max', type=float, help='Maximum GC content for eligibility')
    parser.add_argument('--contig-lim', type=int, default=500, help='Threshold for counting contigs shorter than the specified size (default: 500 bp)')
    
    args = parser.parse_args()
    
    current_date = datetime.now().
