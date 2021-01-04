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

    # Create save file
    with open(file_output, "w") as f:
        f.write("location, name, value\n")

        for item in data:
            # Check if item is empty
            if item.isspace():
                continue

            # Pattern match string
            if reg := re.search(r"^([A-H])(\d+)\s(\d+)\s.+$", item):
                row = reg[1]
                col = int(reg[2])
                value = reg[3]
            else:
                continue

            # Get name from indices
            name = df.loc[row][col]
            if "," in str(name):
                raise ValueError(
                    "The value from the csv file had a comma. "
                    "Make sure to pass names without commas!"
                )

            f.write(f"{row}{col}, {name}, {value}\n")
    print(f"Formatted file saved to {file_output}.")


def main():
    parser = argparse.ArgumentParser(
        prog="Luciferase",
        usage="python luciferase.py --values output.txt --format format.csv",
        description="Convert Luciferase output a bit faster.",
        add_help=True,
    )
    parser.add_argument(
        "--create_format",
        required=False,
        help="Create the format csv file to fill in your sample names.",
    )
    parser.add_argument(
        "-v", "--values",
        type=str,
        required=False,
        help="Path to the txt output file from the luciferase machine.",
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        required=False,
        help=(
            "Path to the csv format file using "
            "the template from --create_format above."
        ),
    )
    args = parser.parse_args()

    if args.create_format:
        create_format()
    elif (args.values is None) or (args.format is None):
        parser.print_help()
    else:
        parse_files(file_values=args.values, file_format=args.format)


if __name__ == "__main__":
    main()
