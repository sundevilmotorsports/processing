import pandas as pd

def generate_report(path: str, session: str):
    df = pd.read_csv(path)
    print(df["flsg (adc)"].describe())


generate_report("processed/evening/data197.csv", "evening")


