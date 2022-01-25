import pandas as pd

df = pd.read_csv("chess_calendar/chess_calendar/full_data.csv")

df = df[df['type'] == 'klasyczne']
print(df.dropna().sort_values("avg_rating").iloc[-5:]['url'].values)
