import datetime
import json
from itertools import product

import networkx as nx
import numpy as np
import pandas as pd


def get_day_avg_shortest_path(df, filter_inf=True):
    df = df[['day', 'src', 'dst', 'value']]
    days, dist = [], []
    for day in df.day.unique():
        print(day)
        subset = df[df.day == day].copy()
        subset = subset[['src', 'dst', 'value']]
        G = nx.DiGraph()
        G.add_weighted_edges_from(subset.values)
        dist.append(nx.average_shortest_path_length(G, weight="weight"))
        days.append(day)

    days, dist = np.array(days), np.array(dist)
    if filter_inf:
        return days[dist != np.inf], dist[dist != np.inf]
    return days, dist


def get_df_first(fname):
    with open(fname) as f:
        data = json.load(f)

    location_list = list(product(data['locations'], data['locations']))

    values = np.array(data['data'])

    df = pd.DataFrame()
    df['src'] = [i[0] for i in location_list]
    df['dst'] = [i[1] for i in location_list]

    for idx, date in enumerate(data['dates']):
        df[date] = values[:, idx]
    df = df.melt(id_vars=['src', 'dst'], var_name='day')
    df['inversed'] = 1 / df.value
    df.inversed = df.inversed / np.max(df.inversed[df.inversed != np.inf])
    df.value = df.inversed
    return df


def get_muni_cases(fname):
    mun = pd.read_csv('../data/Municipality_cases_time_series.csv', sep=';')
    mun.set_index('SampleDate', inplace=True)
    mun['total'] = mun.sum(axis=1)
    return mun


def get_muni_tests(fname):
    tests = pd.read_csv('../data/Municipality_tested_persons_time_series.csv', sep=';')
    tests.set_index('PrDate_adjusted', inplace=True)
    tests['total'] = tests.sum(axis=1)
    return tests


def get_lockdown_dates():
    return pd.to_datetime(['2020-03-11', '2020-12-25'])


def get_cases_per_tests(cases_fname, tests_fname):
    cases = get_muni_cases(cases_fname)
    tests = get_muni_tests(tests_fname)
    tests['cases_per_tests'] = cases.total / tests.total
    return tests


def get_perc(time, series, lags, t0):
    def get_average(time, series, lag, t0):
        time = pd.to_datetime(time)
        t1 = t0 + datetime.timedelta(days=lag)
        if lag > 0:
            idx = (time <= t1) & (time >= t0)
        else:
            idx = (time >= t1) & (time <= t0)
        return np.mean(series[idx])
    a = get_average(time, series, lags[0], t0)
    b = get_average(time, series, lags[1], t0)
    return round((b - a) / a * 100, 1)
