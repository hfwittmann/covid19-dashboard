import re
import pandas as pd
import numpy as np
from numba import jit
from scipy.stats import lognorm, norm
import plotly.express as px
from sub.fancy_cache import fancy_cache


# @jit(nopython=True)
def in_ex_country(TNORM, country, timehorizon):

    index_in = TNORM.country.isin([country])
    index_ex = ~index_in

    TNORM_in = TNORM.loc[index_in]
    TNORM_ex = TNORM.loc[index_ex]

    # add more days for projection
    start_projection = max(TNORM_in['T_norm_days']) + 1
    projection_days = pd.DataFrame({
        'T_norm_days':
        range(start_projection, start_projection + timehorizon)
    })

    TNORM_in = TNORM_in.append(projection_days)
    TNORM_in['T_0'] = list(TNORM_in['T_0'])[0]  #set it for new rows
    TNORM_in['country_T_0'] = list(
        TNORM_in['country_T_0'])[0]  #set it for new rows

    newdates = TNORM_in['T_0'] + TNORM_in['T_norm_days'].apply(
        lambda x: pd.Timedelta(x, unit='d'))

    index_values = ~np.isnan(TNORM_in.date)
    assert all(TNORM_in.date[index_values] == newdates[index_values]
               ), 'existing dates hould match calculated ones (if not nan)'

    TNORM_in['date'] = newdates

    return TNORM_in, TNORM_ex


@jit(forceobj=True)
def project(mean_ex, std_ex, mean_ex_future, std_ex_future, mean_in):
    '''
    walk forward in time, on the same quantile
    '''
    quantile = norm.cdf(x=mean_in, loc=mean_ex, scale=std_ex)
    projection, _ = norm.ppf(q=quantile,
                             loc=mean_ex_future,
                             scale=std_ex_future)

    projection = np.array(projection, dtype=float)

    return projection


# @jit(forceobj=True)
def __walk_forward_projection(D):
    '''
    projection normal model
    '''

    mean_ex = np.array(D['mean_ex'], dtype=float)
    std_ex = np.array(D['std_ex'], dtype=float)
    mean_ex_future = np.array(D['mean_ex_future'], dtype=float)
    std_ex_future = np.array(D['std_ex_future'], dtype=float)
    mean_in = np.array(D['mean_in'], dtype=float)

    projection = mean_in.copy()

    for ix in range(1, len(D) - 1):
        mean_in[ix] = float(mean_in[ix])
        if np.isnan(mean_in[ix]):
            mean_in[ix] = projection[ix]

        projection[ix + 1] = float(
            project(mean_ex[ix], std_ex[ix], mean_ex_future[ix],
                    std_ex_future[ix], mean_in[ix]))

    D.loc[:, 'projection'] = projection

    D = D.interpolate(method='linear', limit_direction='forward', axis=0)
    return None


@jit(forceobj=True)
def __calc_next_projected_case(cases, projected_cases, pct_change):

    # previous_values depending on whether
    previous_values = {True: cases, False: projected_cases}

    previous_measurement_is_available = not np.isnan(cases)
    previous_value = previous_values[previous_measurement_is_available]

    value = previous_value * (1 + pct_change)

    return float(value)


# %%
@jit(forceobj=True)
def __walk_forward_projected_cases(D):
    cases = np.array(D['cases'], dtype=float)
    projected_change = np.array(D['projected_change(%)'], dtype=float)

    projected_cases = cases.copy()

    for ix in range(1, len(D)):
        projected_cases[ix] = __calc_next_projected_case(
            cases[ix - 1], projected_cases[ix - 1], projected_change[ix - 1])

    D.loc[:, 'projected_cases'] = np.round(projected_cases, decimals=0)

    return None


# @jit(nopython=True)
def compose_walking_forward(TNORM,
                            forecastvariable='Change(%)_3',
                            country='Germany',
                            timehorizon=10):

    # limit to countries with sensible numbers
    TNORM = TNORM.loc[TNORM.T_norm_days > -15].copy()

    TNORM[f'{forecastvariable}_ln'] = np.log(TNORM[f'{forecastvariable}'])

    TNORM_in, TNORM_ex = in_ex_country(TNORM, country, timehorizon)

    in_ = TNORM_in.groupby('T_norm_days')[f'{forecastvariable}_ln'].agg(
        ['mean']).reset_index()

    ex = TNORM_ex.groupby('T_norm_days')[f'{forecastvariable}_ln'].agg(
        ['mean', 'std'])

    ex['mean_ex'] = ex['mean']
    ex['std_ex'] = ex['std'].mean()  # simple model

    exshifted = ex.shift(periods=-1)
    exshifted.reset_index(inplace=True)
    exshifted.columns = [c + '_future' for c in exshifted.columns]

    ex.reset_index(inplace=True)

    explus = pd.merge(left=ex,
                      right=exshifted,
                      left_on='T_norm_days',
                      right_on='T_norm_days_future')

    explusin = pd.merge(left=explus,
                        right=in_,
                        left_on='T_norm_days',
                        right_on='T_norm_days',
                        suffixes=["_ex", "_in"])

    explusin.reset_index().set_index(['T_norm_days'], inplace=True)

    # projection_var = pd.DataFrame(
    #     {'projection': explusin.apply(project, axis=1)})

    # explusin['projection'] = projection_var['projection']

    __walk_forward_projection(explusin)

    explusin['mean_in_change'] = np.exp(explusin['mean_in'])
    explusin['projected_change(%)'] = np.exp(explusin['projection'])

    TNORM_in_projection = pd.merge(TNORM_in,
                                   explusin,
                                   left_on='T_norm_days',
                                   right_on='T_norm_days')

    __walk_forward_projected_cases(TNORM_in_projection)

    TNORM_in_projection.loc[:, 'country'] = country

    types = TNORM.type.unique()
    assert len(types) == 1, 'Should only one of confirmed, deaths '

    TNORM_in_projection.loc[:, 'type'] = types[0]
    # print(TNORM_in_projection)

    return TNORM_in_projection


# %%
#
# @jit(nopython=True)
@fancy_cache(ttl=86400 / 4, unique_to_session=False, persist=True)
def get_TNORM_plus(TNORM, timehorizon):

    # countries = blub['']
    TNORM_in_projection_list = list()  # plus prediction

    for country, _ in TNORM.groupby(['country']):
        # print(country)

        # country = 'Italy'
        TNORM_in_projection = compose_walking_forward(
            TNORM,
            forecastvariable='Change(%)_3',
            country=country,
            timehorizon=timehorizon)

        TNORM_in_projection_list.append(TNORM_in_projection[[
            'T_norm_days', 'country', 'country_T_0', 'projected_change(%)',
            'projected_cases', 'date', 'type'
        ]])
        pass

    TNORM_in_projection = pd.concat(TNORM_in_projection_list, axis=0)
    # print(TNORM_in_projection.set_index(['country']).loc['Germany'])

    TNORM['measured_or_projected'] = 'measured'
    TNORM_in_projection['measured_or_projected'] = 'projected'

    TNORM_in_projection.rename(axis=1,
                               mapper={
                                   'projected_change(%)': 'change',
                                   'projected_cases': 'cases'
                               },
                               inplace=True)

    TNORM_in_projection['Absolute'] = TNORM_in_projection['cases']
    TNORM_in_projection['Change(%)'] = TNORM_in_projection['change']

    TNORM_in_projection = TNORM_in_projection.assign(
        Difference=TNORM_in_projection[['Absolute']].diff())

    TNORM_plus = pd.concat([TNORM, TNORM_in_projection], axis=0)

    return TNORM_plus, TNORM, TNORM_in_projection


# %%


def plot_cases_plus(TNORM, TNORM_in_projection, type, Types_type, AbsDiffRate,
                    show_projection):

    TNORM = TNORM.copy()
    TNORM['date'] = TNORM['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    TNORM_in_projection = TNORM_in_projection.copy()
    TNORM_in_projection['date'] = TNORM_in_projection['date'].apply(
        lambda x: x.strftime('%Y-%m-%d'))

    fig = px.scatter(TNORM,
                     x='T_norm_days',
                     y=AbsDiffRate,
                     color='country_T_0',
                     hover_name='country',
                     hover_data=['date'],
                     log_y=True)

    # print(px.colors.qualitative.Plotly)
    ncolors = len(px.colors.qualitative.Plotly)

    # fig.for_each_trace(lambda trace: print(trace.hovertemplate))

    fig.for_each_trace(lambda trace: trace.update(hovertemplate=re.sub(
        pattern='<br>country_T_0=[a-zA-Z0-9 :-]*',
        repl='',
        string=trace.hovertemplate)))

    # print(fig.data[-1])

    if show_projection:
        for ix, (country, group) in enumerate(
                TNORM_in_projection.groupby('country_T_0')):

            # group = group.assign(Difference=group[['Absolute']].diff())

            color = px.colors.qualitative.Plotly[ix % ncolors]
            fig.add_scatter(
                x=group['T_norm_days'],
                y=group[AbsDiffRate],
                name='',
                text='blub',
                marker=dict(
                    symbol='diamond',
                    opacity=0.5,
                    # size=20,
                    color=color,
                    line=dict(width=1, color='black'),
                ))

            fig.data[-1].mode = 'markers'
            fig.data[-1].legendgroup = country
            fig.data[-1].showlegend = False

            # print(group.date)
            fig.data[-1].hovertext = group['date']

            # print(fig.data[-1])

            fig.data[
                -1].hovertemplate = f'<b>Projection {country}</b><br><br>T_norm_days=%{{x}}<br>{AbsDiffRate}=%{{y}}<br>date=%{{hovertext}}'
            fig.update_layout(title_text=f'<b>{Types_type}</b>')

    return fig
