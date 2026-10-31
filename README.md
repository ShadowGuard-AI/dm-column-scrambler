![Banner](banner.png)

# dm-column-scrambler
Scrambles the order of columns in a CSV file while preserving headers, to obscure data relationships.  Uses `csv` module. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowStrikeHQ/dm-column-scrambler`

## Usage
`./dm-column-scrambler [params]`

## Parameters
- `-h`: Show help message and exit
- `input_file`: The input CSV file
- `output_file`: The output CSV file. It must not be the input file: if the output path resolves to the input file, through the same spelling, a `./` spelling, an absolute path, or a symlink, the run refuses and exits 1 before any file is written.
- `--seed`: No description provided

## Row width rules
- A data row with more fields than the header is refused: the run exits 1 naming the row and its field count, so no field is silently discarded.
- A data row with fewer fields than the header is padded with empty fields, and the run logs a warning naming the count and the padded rows.

## License
Copyright (c) ShadowStrikeHQ
