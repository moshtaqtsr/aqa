#!/usr/bin/env python3

import os
from datetime import datetime
from Bio import SeqIO
import argparse
from jinja2 import Environment, FileSystemLoader

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
    
    return n50, l50, num_contigs, contigs_shorter_than_limit, genome_size, gc_content_rounded

# Main function to generate HTML report
def generate_html_report(input_dir, args):
    data = []
    fasta_file_count = 0  # Counter for counting FASTA files processed
    
    # Get current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    output_file_html = f"aqa_{current_date}.html"
    
    # Prepare Jinja2 template environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.fasta'):
            fasta_file_count += 1  # Increment the counter for each FASTA file found
            file_path = os.path.join(input_dir, file_name)
            n50, l50, num_contigs, contigs_shorter_than_limit, genome_size, gc_content_rounded = process_fasta_file(file_path)
            contigs_quality = '' if args.con_cut is None else ('Yes' if num_contigs <= args.con_cut else 'No')
            genome_size_quality = '' if args.size_min is None or args.size_max is None else ('Yes' if args.size_min <= genome_size <= args.size_max else 'No')
            gc_content_range = '' if args.gc_min is None or args.gc_max is None else ('Warning' if not (args.gc_min <= gc_content_rounded <= args.gc_max) else '-')
            eligibility = assess_eligibility(num_contigs, genome_size, gc_content_rounded, args.con_cut, args.size_min, args.size_max, args.gc_min, args.gc_max)
            data.append({
                'File': file_name,
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
    
    # Render the HTML template with data
    html_output = template.render(data=data, current_time=current_time)
    
    # Write the rendered HTML to a file
    with open(output_file_html, 'w') as f_out:
        f_out.write(html_output)
    
    # Print the count of FASTA files processed
    print(f"Number of FASTA files assessed: {fasta_file_count}")
    print(f"HTML report generated: {output_file_html}")

# Main block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assess the quality of genome assemblies.")
    parser.add_argument('--con-cut', type=int, help='Contig cutoff for eligibility')
    parser.add_argument('--size-min', type=int, help='Minimum genome size for eligibility')
    parser.add_argument('--size-max', type=int, help='Maximum genome size for eligibility')
    parser.add_argument('--gc-min', type=float, help='Minimum GC content for eligibility')
    parser.add_argument('--gc-max', type=float, help='Maximum GC content for eligibility')
    parser.add_argument('--contig-lim', type=int, default=500, help='Threshold for counting contigs shorter than the specified size (default: 500 bp)')
    
    args = parser.parse_args()
    
    # Run the HTML report generation function
    generate_html_report(os.getcwd(), args)

    # HTML template for the report
    template_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Assembly Assessment Report</title>
        <style>
            /* Add CSS styles for table headers and rows */
            th {
                background-color: #f2f2f2;
                text-align: left;
                padding: 8px;
            }
            td {
                padding: 8px;
            }
            .eligible {
                background-color: #c8e6c9; /* Light green */
            }
            .not-eligible {
                background-color: #ffcdd2; /* Light red */
            }
        </style>
    </head>
    <body>
        <h1>Assembly Assessment Report</h1>
        <p>Generated at {{ current_time }}</p>
        <table>
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
            {% for item in data %}
            <tr class="{% if item.Eligibility == 'Not Eligible' %}not-eligible{% else %}eligible{% endif %}">
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
        </table>
    </body>
    </html>
    """

    # Write the template HTML to a file
    with open('template.html', 'w') as f_template:
        f_template.write(template_html)
