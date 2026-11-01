import argparse
import csv
import logging
import random
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command line interface.
    """
    parser = argparse.ArgumentParser(description='Scrambles the order of columns in a CSV file.')
    parser.add_argument('input_file', help='The input CSV file.')
    parser.add_argument('output_file', help='The output CSV file. It must not resolve to the input file.')
    parser.add_argument('--seed', type=int, help='Optional seed for the random number generator (for reproducibility).')
    return parser

def scramble_columns(input_file, output_file, seed=None):
    """
    Scrambles the columns of the input CSV file and writes the result to the output CSV file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
        seed (int, optional): Seed for the random number generator. Defaults to None.
    """
    try:
        with open(input_file, 'r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader, None)  # Read the header row
            if header is None:
                logging.error(f"Error: Input file is empty, no header row: {input_file}")
                sys.exit(1)
            data = list(reader)  # Read all the data rows

        # Seed the random number generator if a seed is provided
        # The seed is set on the shared random module, and the only
        # draw after it is the one shuffle, so a seeded run repeats
        # exactly for a file with the same number of columns. A file
        # with a different column count draws a different permutation
        # from the same seed, which is expected, not a mismatch.
        if seed is not None:
            random.seed(seed)
            logging.info(f"Using seed: {seed}")

        # Generate a random permutation of column indices
        # One permutation list is applied to the header and to every
        # row below. That sharing is the whole correctness of the tool:
        # shuffle the header and the rows separately and the values
        # would land under the wrong names with no error anywhere.
        column_indices = list(range(len(header)))
        random.shuffle(column_indices)

        # Create the scrambled header
        scrambled_header = [header[i] for i in column_indices]

        # Create the scrambled data. Hand edited CSVs often carry ragged
        # rows; indexing a short row used to abort the whole run with
        # "list index out of range". Short rows are padded with empty
        # fields and counted in a warning. Long rows are refused: cutting
        # them to the header width would silently discard values, so the
        # run exits 1 naming the row and its field count instead.
        scrambled_data = []
        padded_rows = []
        for row_number, row in enumerate(data, start=2):
            if len(row) > len(header):
                logging.error(
                    f"Error: Row {row_number} has {len(row)} fields but the header has "
                    f"{len(header)} fields. Refusing to discard the extra fields."
                )
                sys.exit(1)
            if len(row) < len(header):
                padded_rows.append(row_number)
            padded = (row + [''] * len(header))[:len(header)]
            scrambled_row = [padded[i] for i in column_indices]
            scrambled_data.append(scrambled_row)
        if padded_rows:
            logging.warning(
                f"Padded {len(padded_rows)} short row(s) with empty fields: "
                f"row(s) {', '.join(str(n) for n in padded_rows)}"
            )

        # Write the scrambled data to the output file
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(scrambled_header)  # Write the scrambled header
            writer.writerows(scrambled_data)  # Write the scrambled data

        logging.info(f"Successfully scrambled columns from {input_file} to {output_file}")

    except FileNotFoundError:
        logging.error(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

def main():
    """
    Main function to parse arguments and call the scrambling function.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Input validation: refuse when the output resolves to the input file,
    # whatever spelling, relative form, or symlink names it.
    if Path(args.input_file).resolve() == Path(args.output_file).resolve():
        logging.error("Error: Input and output files cannot be the same.")
        sys.exit(1)
        
    scramble_columns(args.input_file, args.output_file, args.seed)


if __name__ == "__main__":
    main()


# Usage Examples:
# 1. Scramble columns of input.csv and save to output.csv:
#    python main.py input.csv output.csv
#
# 2. Scramble columns with a specific seed for reproducibility:
#    python main.py input.csv output.csv --seed 42
#
# 3. If the input file doesn't exist:
#    python main.py nonexistent_file.csv output.csv
#    # This will log an error message and exit.
#
# 4. If the input and output files are the same:
#    python main.py input.csv input.csv
#    # This will log an error message and exit.