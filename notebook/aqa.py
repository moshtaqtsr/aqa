#!/usr/bin/env python3

import os
import argparse
from datetime import datetime
from Bio import SeqIO
import pandas as pd
from jinja2 import Template
from openpyxl import Workbook

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

# Define function for calculating GC content
def calculate_gc_content(sequence):
    gc_count = sequence.count('G') + sequence.count('C')
    total_count = len(sequence)
    gc_content = (gc_count / total_count) * 100
    return round(gc_content, 2)

# Define function for assessing eligibility
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
    
    return n50, l50, num_contigs, contigs_shorter_than_limit, genome_size, gc_content_rounded

# Function to generate text report
def generate_text_report(data, output_file_txt):
    with open(output_file_txt, 'w') as f_out:
        f_out.write(f"Assembly Assessment Report\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f_out.write("File\tN50\tL50\tNum Contigs\tContigs < 500 bp\tContigs Quality\tGenome Size\tGenome Size Quality\tGC Content\tGC Content Range\tEligibility\n")
        for item in data:
            f_out.write(f"{item['File']}\t{item['N50']}\t{item['L50']}\t{item['Num_Contigs']}\t{item['Contigs_Shorter_Than_500']}\t{item['Contigs_Quality']}\t{item['Genome_Size']}\t{item['Genome_Size_Quality']}\t{item['GC_Content']}\t{item['GC_Content_Range']}\t{item['Eligibility']}\n")

# Function to generate Excel report
def generate_excel_report(data, output_file_xlsx):
    df = pd.DataFrame(data)
    df.to_excel(output_file_xlsx, index=False)

# Function to generate HTML report
def generate_html_report(data, output_file_html, current_time):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Assembly Report</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            .eligible {
                background-color: #c8e6c9;
            }
            .not-eligible {
                background-color: #ffcdd2;
            }
        </style>
    </head>
    <body>
        <h1>Assembly Assessment Report</h1>
        <p>Report generated on {{ current_time }}</p>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>N50</th>
                    <th>L50</th>
                    <th>Num Contigs</th>
                    <th>Contigs &lt; 500 bp</th>
                    <th>Contigs Quality</th>
                    <th>Genome Size</th>
                    <th>Genome Size Quality</th>
                    <th>GC Content</th>
                    <th>GC Content Range</th>
                    <th>Eligibility</th>
                </tr>
            </thead>
            <tbody>
                {% for item in data %}
                <tr class="{{ 'eligible' if item.Eligibility == 'Eligible' else 'not-eligible' }}">
                    <td>{{ item.File }}</td>
                    <td>{{ item.N50 }}</td>
                    <td>{{ item.L50 }}</td>
                    <td>{{ item.Num_Contigs }}</td>
                    <td>{{ item.Contigs_Shorter_Than_500 }}</td>
                    <td>{{ item.Contigs_Quality }}</td>
                    <td>{{ item.Genome_Size }}</td>
                    <td>{{ item.Genome_Size_Quality }}</td>
                    <td>{{ item.GC_Content }}</td>
                    <td>{{ item.GC_Content_Range }}</td>
                    <td>{{ item.Eligibility }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    template = Template(html_template)
    rendered_html = template.render(data=data, current_time=current_time)

    with open(output_file_html, 'w') as f_out:
        f_out.write(rendered_html)

# Main function
def main(args):
    input_files = []
    if args.input_file:
        input_files = [args.input_file]
    else:
        input_dir = os.getcwd()
        input_files = [os.path.join(input_dir, file_name) for file_name in os.listdir(input_dir) if file_name.endswith('.fasta')]

    data = []
    fasta_file_count = 0  # Counter for counting FASTA files processed
    
    # Get current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    output_file_txt = f"aqa_{current_date}.txt"
    output_file_xlsx = f"aqa_{current_date}.xlsx"
    output_file_html = f"aqa_{current_date}.html"
    
    for file_path in input_files:
        fasta_file_count += 1  # Increment the counter for each FASTA file found
        n50, l50, num_contigs, contigs_shorter_than_limit, genome_size, gc_content_rounded = process_fasta_file(file_path)
        contigs_quality = '' if args.con_cut is None else ('Yes' if num_contigs <= args.con_cut else 'No')
        genome_size_quality = '' if args.size_min is None or args.size_max is None else ('Yes' if args.size_min <= genome_size <= args.size_max else 'No')
        gc_content_range = '' if args.gc_min is None or args.gc_max is None else ('Warning' if not (args.gc_min <= gc_content_rounded <= args.gc_max) else '-')
        eligibility = assess_eligibility(num_contigs, genome_size, gc_content_rounded, args.con_cut, args.size_min, args.size_max, args.gc_min, args.gc_max)
        data.append({
            'File': os.path.basename(file_path),
            'N50': n50,
            'L50': l50,
            'Num_Contigs': num_contigs,
            'Contigs_Shorter_Than_500': contigs_shorter_than_limit,
            'Contigs_Quality': contigs_quality,
            'Genome_Size': genome_size,
            'Genome_Size_Quality': genome_size_quality,
            'GC_Content': gc_content_rounded,
            'GC_Content_Range': gc_content_range,
            'Eligibility': eligibility
        })

    # Generate reports
    generate_text_report(data, output_file_txt)
    generate_excel_report(data, output_file_xlsx)
    generate_html_report(data, output_file_html, current_time)
    
    print(f"Reports generated: {output_file_txt}, {output_file_xlsx}, {output_file_html}")
    print(f"Number of FASTA files processed: {fasta_file_count}")

# Argument parser setup
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assess genome assemblies.")
    parser.add_argument('-cc', '--con-cut', type=int, help="Contig cutoff for eligibility")
    parser.add_argument('--smin', '--size_min', type=int, help="Minimum genome size for eligibility")
    parser.add_argument('--smax', '--size_max', type=int, help="Maximum genome size for eligibility")
    parser.add_argument('--gcmin', '--gc_min', type=float, help="Minimum GC content for eligibility")
    parser.add_argument('--gcmax', '--gc_max', type=float, help="Maximum GC content for eligibility")
    parser.add_argument('-cl', '--contig-lim', type=int, default=500, help="Threshold for counting contigs shorter than the specified size (default: 500 bp)")
    parser.add_argument('-i', '--input-file', type=str, help="Specify a single input file (optional)")

    args = parser.parse_args()
    main(args)
