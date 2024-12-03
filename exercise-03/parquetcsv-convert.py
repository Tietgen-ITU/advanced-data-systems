import sys
import pandas as pd

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python parquetcsv-convert.py <filename.parquet> <filename.csv>')
        sys.exit(1)

    df = pd.read_parquet(sys.argv[1])
    df.to_csv(sys.argv[2], index=False)