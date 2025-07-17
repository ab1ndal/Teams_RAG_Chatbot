from pathlib import Path
import pandas as pd

def get_excel_dataframe(parquet_path: Path, excel_path: Path, sheet_name: str, header_row: int, removeCols: list[str], renameCols: dict[str, str], verbose: bool = False, usecols: str = None) -> pd.DataFrame:
    if parquet_path.exists():
        print("Parquet file exists. Loading from parquet...")
        df = pd.read_parquet(parquet_path)
        print("Parquet file loaded.")
        if verbose:
            print("Sample row:", df.iloc[0].to_dict())
            print("Columns:", df.columns.tolist())
            print("Number of records:", len(df))
    else:
        if not excel_path.exists():
            raise FileNotFoundError(f"File not found: {excel_path}")

        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row - 1, usecols=usecols).fillna("")
        df.drop(columns=removeCols, errors="ignore", inplace=True)
        df.rename(columns=renameCols, inplace=True)
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str)

        if verbose:
            print("Sample row:", df.iloc[0].to_dict())
            print("Columns:", df.columns.tolist())
            print("Number of records:", len(df))
        df.to_parquet(parquet_path, index=False)
    return df