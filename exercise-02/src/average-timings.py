
from dataclasses import dataclass
import sys


@dataclass
class ParsedArgs:
    file_path: str = ""

    def validate(self):
        if self.file_path == "":
            return False
        
        return True

def main(arguments):
    elapsed_times = []

    with open(arguments.file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            elapsed_times.append(float(line.replace("\n", "")))
    
    average_time = sum(elapsed_times) / len(elapsed_times)
    print(f"{average_time} Seconds")
            

def parse_args(arguments):
    
    args = ParsedArgs()
    i = 1
    while(i < len(arguments)):
        if arguments[i] == "--file" or arguments[i] == "-f":
            i += 1 # Move index to the value position
            args.file_path = arguments[i]
        
        i += 1 # Go to the next argument

    return args


if __name__ == "__main__":

    parsed_args = parse_args(sys.argv)

    if not parsed_args.validate():
        print("Missing arguemnts")
        print("Usage: python average-timings.py <-f | --file> <file_path>")
        sys.exit(1)

    main(parsed_args)