import pandas as pd


def top_10_player_average(arr):
    return arr


def filter_agg_tournaments(tournament_df, time_control):
    planned_classical = tournament_df[
        (tournament_df['time_control'] == time_control) & (tournament_df['status'] == 'planowany')]
    best_with_k_people = planned_classical[planned_classical['count'] >= 10].sort_values('mean', ascending=False)
    best_with_k_people = best_with_k_people.round({'mean': 1}).drop(['time_control', 'end_date', 'id'], axis=1)
    best_with_k_people = best_with_k_people.rename({"count": '#players', 'mean': 'mean rating'}, axis=1)
    df = best_with_k_people.iloc[:10]
    df["url"] = '<a href=' + df['url'] + '><div>' + df['title'] + '</div></a>'
    return df.drop(['title', 'status'], axis=1)
