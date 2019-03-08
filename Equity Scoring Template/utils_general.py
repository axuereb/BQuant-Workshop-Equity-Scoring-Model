import pandas as pd

import bql


# Override Parameters

current = {'FPT':'A', 'FPO':'0'}
prev = {'FPT':'A', 'FPO':'-1'}
fy1 = {'FPT':'A', 'FPO':'1'}
fy2 = {'FPT':'A', 'FPO':'2'}
ltm = {'FPT':'BT', 'FPO':'0'}
ntm = {'FPT':'BT', 'FPO':'1'}
sntm = {'FPT':'BT', 'FPO':'2'}
trail12m = {'FPO':'0', 'FPT':'LTM'}


# Functions

def format_floats(val):
    try:
        return int(val*100)/100.
    except:
        return val


def group_rank_ties(bq_connection, field, ties='max', null_value=0):
    f = bq_connection.func
    return f.replacenonnumeric(f.ungroup(f.rank(f.group(field), ties='MAX')), null_value)


def get_score_data(connection, universe, fields, with_params=None, preferences=None):
    if with_params is None:
        with_params = {}
    if preferences is None:
        preferences = {}
    request = bql.Request(universe, fields, with_params=with_params, preferences=preferences)
    responses = connection.execute(request)
    df = pd.DataFrame({response.name: response.df()[response.name] for response in responses})[[f for f in fields.keys()]]
    return df.applymap(format_floats)


def get_fundamental_data(bq_connection, field):
    f = bq_connection.func
    u = bq_connection.univ
    return f.value(field, u.translatesymbols(TARGETIDTYPE='FUNDAMENTALTICKER'), MAPBY='LINEAGE')


def get_single_field_request(connection, universe, field, field_name, with_params=None, preferences=None):
    if with_params is None:
        with_params = {}
    if preferences is None:
        preferences = {}
    request = bql.Request(universe, {field_name: field}, with_params=with_params, preferences=preferences)
    responses = connection.execute(request)
    return responses[0].df()
        