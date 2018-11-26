import pandas as pd
import sys
import pymysql


# Helper function to load a table
def load_fingerpatch(table, dbname = "fingerpatch", parse_children = "All"):
    """Load table in the dbname and format it"""
    modes = ["Depends", "Recommends", "Suggests"]

    connection = pymysql.connect(host='localhost',
                                 user='fingerpatch',
                                 password='fingerpatch',
                                 db=dbname,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    df = pd.read_sql("SELECT * FROM `"+table+"` ",connection)
    connection.close()

    if table == "ubuntu_packets":
        df = df.set_index("id")

    if table == "ubuntu_cleaned_packets":
        df = df.set_index("id")

        if "Childrens" in df.columns:
            df["Childrens"] = df["Childrens"].map(eval)

        for m in modes:
            attr = m + "_Childrens"
            if attr in df.columns and (m == parse_children or  parse_children == "All"):
                df[attr] = df[attr].map(eval)

    if table == "ubuntu_captures":
        df = df.set_index("capture_id")
        df["HTTP_Seq"] = df["HTTP_Seq"].map(eval)
        df["Payload_received"] = df["Payload_received"].map(eval)
        df["Payload_sent"] = df["Payload_sent"].map(eval)
        df["Flows"] = df["Flows"].map(eval)

    return df
