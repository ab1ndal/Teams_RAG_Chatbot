from pathlib import Path
import pandas as pd

def get_excel_dataframe(parquet_path: Path, excel_path: Path, sheet_name: str, header_row: int, removeCols: list[str], renameCols: dict[str, str], verbose: bool = False) -> pd.DataFrame:
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    else:
        if not excel_path.exists():
            raise FileNotFoundError(f"File not found: {excel_path}")

        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row - 1).fillna("")
        df.drop(columns=removeCols, errors="ignore", inplace=True)
        df.rename(columns=renameCols, inplace=True)

        if verbose:
            print("Sample row:", df.iloc[5].to_dict())
            print("Columns:", df.columns.tolist())
        df.to_parquet(parquet_path, index=False)
    return df