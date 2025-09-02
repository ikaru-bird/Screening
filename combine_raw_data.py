import pandas as pd
import glob
import os
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine raw data pickle files.")
    parser.add_argument("input_dir", help="Directory containing the pickle files.")
    parser.add_argument("output_pickle_file", help="Path to save the combined pickle file.")
    parser.add_argument("--pattern", default="*.pkl", help="Pattern to match files in the input directory.")
    args = parser.parse_args()

    pickle_files = glob.glob(os.path.join(args.input_dir, args.pattern))
    if not pickle_files:
        print(f"No pickle files found in {args.input_dir} matching pattern {args.pattern}")
        sys.exit(0)

    print(f"Combining {len(pickle_files)} raw data files from {args.input_dir}...")

    df_list = []
    for f in pickle_files:
        try:
            df = pd.read_pickle(f)
            if not df.empty:
                df_list.append(df)
        except Exception as e:
            print(f"Could not read pickle file {f}: {e}")

    if not df_list:
        print("No data to combine.")
        sys.exit(0)

    combined_df = pd.concat(df_list, axis=1)

    if isinstance(combined_df.columns, pd.MultiIndex):
        combined_df = combined_df.loc[:,~combined_df.columns.duplicated()]

    print(f"Saving combined raw data to {args.output_pickle_file}")
    combined_df.to_pickle(args.output_pickle_file)
