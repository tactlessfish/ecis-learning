from .data_processor import DataProcessor
import numpy as np
import pandas as pd


class MedicationDataProcessor(DataProcessor):
    def __init__(self, allscripts_json_file, epic_json_file, soarian_json_file):
        df_allscripts = self.get_initial_df(
            allscripts_json_file,
            "LastUpDate",
            "PAT_ID",
            "MedicationName",
            "NDC",
            "MedStatus",
            "AS",
        )
        df_epic = self.get_initial_df(
            epic_json_file,
            "start_date",
            "P_ID",
            "Name",
            None,
            "Active",
            "E"
        )
        df_soarian = self.get_initial_df(
            soarian_json_file,
            "StartDateTime",
            "PAT_ID",
            "GenericDrugName",
            "DrugCode",
            None,
            "S",
        )

        super().__init__(pd.concat([df_allscripts, df_epic, df_soarian], ignore_index=True))

    @staticmethod
    def get_initial_df(
            json_file, time_key: str, id_key: str, name_key: str, code_key: str, status_key: str, source: str
    ) -> pd.DataFrame:
        """
        Extract medication data from json into an initial, unprocessed DataFrame.

        :param json_file: the json file to read
        :param time_key: the key of the time key/value pair
        :param id_key: the key of the patient id key/value pair
        :param name_key: the key of the medication name key/value pair
        :param code_key: the key of the medication code key/value pair
        :param status_key: the key of the status key/value pair
        :param source: the source of the data
        :return: initial DataFrame containing only relevant information
        """
        df: pd.DataFrame = pd.read_json(json_file)
        df = df.join(df["data"].apply(pd.Series))
        df[time_key] = pd.DatetimeIndex(df[time_key]).year

        df_new: pd.DataFrame = df[[time_key, id_key, name_key]].copy()
        df_new["code"] = df[code_key] if code_key is not None else "N/A"
        if status_key == "Active":
            # Special case for Epic data
            df_new["status"] = np.where(
                df["Active"] == "Active Medication", "Active", df["Status"]
            )
        elif status_key is not None:
            df_new["status"] = df[status_key]
        else:
            df_new["status"] = "N/A"
        df_new["source"] = source
        df_new.columns = ["year", "patient_id", "rx_name", "rx_code", "rx_status", "source"]
        return df_new


