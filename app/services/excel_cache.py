from pathlib import Path
import pandas as pd

def get_excel_dataframe(file_path: Path, sheet_name: str, header_row: int, removeCols: list[str], renameCols: dict[str, str], verbose: bool = False) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row - 1).fillna("")
    df = df.drop(columns=removeCols)
    df = df.rename(columns=renameCols)

    if verbose:
        print("Sample row:", df.iloc[5].to_dict())
        print("Columns:", df.columns.tolist())

    return df