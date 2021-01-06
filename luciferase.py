"""\U0001F525\U0001FAB0 Luciferase conversion script.

The luciferase machine outputs a txt file that usually has to be converted to useful output manually.
This script simplifies the entire process by combining a "format.csv" file containing information on which well (96-well plate) has which sample and the "output.txt" file from the luciferase machine.

This is the proposed workflow:
* Create the format.csv file using `python luciferase.py --create_format`
* Use your editor of choice (excel, numbers) to fill in the rows and columns matching with your samples
* Save the output as .csv file (excel / numbers will suggest you to use their own formats)
* Merge the output.txt and format.csv file using `python luciferase.py -v PATH/TO/output.txt -f PATH/TO/format.csv`
"""

import argparse
import os
import re
import string

import pandas as pd


def create_format(name: str = "format.csv") -> None:
    """Create format.csv with rows and columns matching a 96-well plate."""
    columns = list(range(1, 13))
    index = re.findall("[A-H]", string.printable)
    df = pd.DataFrame(index=index, columns=columns)
    df.at["A", 1] = "Sample Name in A1"
    df.to_csv(name)
    print(f"Empty format file saved to {name}.")


def parse_files(file_values: str, file_format: str) -> None:
    """Parse the machines csv file and the """
    if (not os.path.isfile(file_values)) or (not file_values.lower().endswith(".txt")):
        raise ValueError(
            f"Make sure the value.txt file exists and is txt. {file_values} does not!"
        )
    if (not os.path.isfile(file_format)) or (not file_format.lower().endswith(".csv")):
        raise ValueError(
            f"Make sure the format.csv file exists and is csv. {file_format} does not!"
        )

    # Create output file path
    file_output = f"{os.path.splitext(file_values)[0]}.csv"
    if os.path.isfile(file_output):
        raise ValueError(
            "The output.csv file already exists. "
            f"I don't want to overwrite {file_output}!"
        )

    # Open txt value file
    with open(file_values, "r") as f:
        data = f.readlines()

    # Open csv format file
    df = pd.read_csv(file_format, header=0, index_col=0)
    not_column_numbers = any([str(i) for i in range(1, 13)] != df.columns.values)
    not_index_letters = any(re.findall("[A-H]", string.printable) != df.index.values)
    if not_column_numbers or not_index_letters:
        raise ValueError(
            "The provided format.csv file wasn't formatted properly. "
            "Make sure it has the same format as the output from `python luciferase.py --create_format`"
        )

    # Create save file
    with open(file_output, "w") as f:
        f.write("location, name, value\n")

        for item in data:
            # Check if item is empty
            if item.isspace():
                continue

            # Pattern match string
            if reg := re.search(r"^([A-H])(\d+)\s*(\d+).*$", item):
                row = reg[1]
                col = int(reg[2])
                value = reg[3]
            else:
                continue

            # Get name from indices
            name = df.loc[row][col - 1]
            if "," in str(name):
                raise ValueError(
                    "The value from the csv file had a comma. "
                    "Make sure to pass names without commas!"
                )

            f.write(f"{row}{col}, {name}, {value}\n")
    print(f"Formatted file saved to {file_output}.")


def main():
    parser = argparse.ArgumentParser(
        prog="luciferase",
        usage="python luciferase.py --values output.txt --format format.csv",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )
    parser.add_argument(
        "--create_format",
        action="store_true",
        help="Create the format csv file to fill in your sample names.",
    )
    parser.add_argument(
        "-v",
        "--values",
        type=str,
        required=False,
        help="Path to the txt output file from the luciferase machine.",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        required=False,
        help=(
            "Path to the csv format file using "
            "the template from --create_format above."
        ),
    )
    parser._optionals.title = "Arguments"
    args = parser.parse_args()

    if args.create_format:
        create_format()
    elif (args.values is None) or (args.format is None):
        parser.print_help()
    else:
        parse_files(file_values=args.values, file_format=args.format)


if __name__ == "__main__":
    main()
