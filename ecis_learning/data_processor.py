import pandas as pd
from typing import List


class DataProcessor:
    def __init__(self, df):
        self.Data = df

    def process_data(self):
        # Create rows for new DataFrame, one for each patient
        rows: List[list] = []
        patient_ids: List[str] = self.Data["patient_id"].unique()
        for patient_id in patient_ids:
            rows.append([patient_id])

        # Get earliest year and latest year
        earliest_year: int = min(self.Data["year"])
        latest_year: int = max(self.Data["year"])

        # Iterate through year intervals and add data to rows
        # Also get names of columns
        column_names: List[str] = ["patient_id"]
        for current_year in range(earliest_year, latest_year + 1, 2):
            column_names.append(
                f"DX{current_year}–{current_year + 1}"
                if current_year != latest_year
                else str(latest_year)
            )
            for row in rows:
                interval_df: pd.DataFrame = self.Data.query(
                    "patient_id == @row[0] and (year == @current_year or year == @current_year + 1)"
                )
                if interval_df.empty:
                    row.append(None)
                else:
                    # TODO: add parameters to make this part universal
                    result = [
                        f"{code}⁠—{name}"
                        for code, name in zip(
                            interval_df["DX_CODE"], interval_df["DX_NM"]
                        )
                    ]
                    row.append(";".join(result))

        return pd.DataFrame(rows, columns=column_names)