# import modules
import requests
import pandas as pd
from bs4 import BeautifulSoup

from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
from plotly.graph_objs import *
from plotly.subplots import make_subplots

init_notebook_mode(connected=True) 
pd.options.plotting.backend = "plotly"
# pd.options.plotting.backend = "matplotlib"

# %% read urls
df = pd.read_csv(r'sensitivity_result_urls_wx_eq.csv')
# df = pd.read_csv(r'sensitivity_result_urls_wx_eq_3.csv')
# df = pd.read_csv(r'sensitivity_result_urls_bwyeqf.csv')
# df = pd.read_csv(r'sensitivity_result_urls (3607).csv')

# df.rename(columns={'Data type':'metric'}, inplace=True)
df['metric'] = df['Result'].apply(lambda x: x.split(' for ')[0].strip())
df['region'] = df['Result'].apply(lambda x: x.split(' for ')[1].split(',')[0].strip())
# df['tech'] = df['Result'].apply(lambda x: x.split(' for ')[1].split(',')[1].strip())

def get_tech(x):
    try:
        return x.split(' for ')[1].split(',')[1].strip()
    except IndexError:
        # print(x+'------>\terror')
        return 'N/A'
    
df['tech'] = df['Result'].apply(lambda x: get_tech(x))
# %% request and parse emissions xml files into dataframe
# params = {
#     'account' :'Shell',
#     'password' : 'pv112014',
#     'resolution' : 'yearly',
#     'filter_id' : ''}
def pull_parse(df, metric, region_list, tech_list=None):
    d = {}
    i=0
    j = 0
    # df_smp = pd.DataFrame(columns=['region','tech','date_time','metric','value','units'])
    if tech_list == None:
        iter_frame = df.loc[(df.metric.str.contains(metric))&(df.region.isin(region_list))]
    else:
        # iter_frame = df.loc[(df.metric.str.contains(metric))&(df.region.isin(region_list))&(df.tech.isin(tech_list))]
        iter_frame = df.loc[(df.metric == metric)&(df.region.isin(region_list))&(df.tech.isin(tech_list))]
    for index, row in iter_frame.iterrows():
        j+=1
        address = row['URL']
        address = address.replace('account=101', 'account=Shell')
        address = address.replace('password=YOUR_PASSWORD', 'password=pv112014')
        print('pulling and parsing xml file for '+row['region']+' ('+str(j)+' of '+str(len(iter_frame['URL']))+')')
        try:
            r = requests.get(url=address)
            r.raise_for_status()
            # with open(f'data_{metric}.xml', 'w') as f:
            #     f.write(r.text)
            # r = requests.get(url=address, verify=False)
            soup = BeautifulSoup(r.text, 'xml')
            for result in soup.find_all('results'):
                for serie in result.find_all('series'):
                    for vals in serie.find_all('value'):
                        # print(result.find('assumption').text)
                        # print(serie.find('units').text)
                        # print(vals.get('date'))
                        # print(vals.text)
                        # print('--------------------\n')
                        if tech_list==None:
                            d[i] = {
                                'region': row['region'],
                                'region_xml':result.property.find('object',{'type':'country'}).text,
                                'weather_year': result.find('assumption').text.split()[-1].strip(),
                                'date_time': vals.get('date'),
                                'value': vals.text,
                                'metric': soup.results.property.find('name').text,
                                'units': serie.find('units').text,
                                'timezone': soup.sensitivities.timezone.text}
                        elif metric == 'Fuel price (original units)':
                            d[i] = {
                                    'region': row['region'],
                                    'region_xml':result.property.find('object',{'type':'country'}).text,
                                    'weather_year': result.find('assumption').text.split()[-1].strip(),
                                    'date_time': vals.get('date'),
                                    'value': vals.text,
                                    'metric': result.property.find('name').text,
                                    'units': serie.find('units').text,
                                    'fuel':result.property.find('object',{'type':'fuel'}).text,
                                    'timezone': soup.sensitivities.timezone.text}
                        elif metric == 'FX rate':
                            d[i] = {
                                    'region': row['region'],
                                    'weather_year': result.find('assumption').text.split()[-1].strip(),
                                    'date_time': vals.get('date'),
                                    'value': vals.text,
                                    'metric': result.property.find('name').text,
                                    'units': serie.find('units').text,
                                    'currency1':result.property.find('object',{'type':'currency'}).text,
                                    'currency2':result.property.find('object',{'type':'currency2'}).text,
                                    'timezone': soup.sensitivities.timezone.text}
                        else:
                            d[i] = {
                                'region': row['region'],
                                'region_xml':result.property.find('object',{'type':'country'}).text,
                                'weather_year': result.find('assumption').text.split()[-1].strip(),
                                'date_time': vals.get('date'),
                                'value': vals.text,
                                'metric': result.property.find('name').text,
                                'units': serie.find('units').text,
                                'technology':result.property.find('object',{'type':'technology'}).text,
                                'timezone': soup.sensitivities.timezone.text}          
                        i+=1
        except requests.exceptions.HTTPError as err:
            print(err)
            return None
    df_data = pd.DataFrame.from_dict(d, 'index')
    df_data['value'] = pd.to_numeric(df_data['value'])
    df_data.set_index('date_time', inplace=True)
    return df_data
    # return df_data, r

# %%
# df_smp = pd.DataFrame.from_dict(d, 'index')
# df_smp['date_time'] = pd.to_datetime(df_smp['date_time'])


# %%
# region_list = list(df.region.unique())
# region_list = [
#     'Great Britain',
#     'France',
#     'Belgium',
#     'Germany',
#     'Spain',
#     'Czech Republic',
#     'Denmark (West)',
#     'Portugal',
#     'Netherlands',
#     'Switzerland',
#     'Denmark (East)',
#     'Austria',
# ]
# region_list = ['Great Britain', 'Germany','Netherlands','France','Belgium']
# region_list = ['Great Britain']
# region_list = ['Great Britain','Spain']
# region_list = ['Germany']
region_list = ['France']
# region_list = ['Spain']
# region_list = ['Spain','Germany']
# region_list = ['Great Britain','Germany','Netherlands']
# region_list = ['Great Britain','Netherlands']
# region_list = ['Germany','Netherlands']
# region_list = ['Netherlands']
# df_smp = pull_parse(df, metric='System Marginal Price', region_list=['Great Britain', 'Germany'])
df_smp = pull_parse(df, metric='System Marginal Price', region_list=region_list)

# %%
df_smp_pivot = df_smp[['weather_year','region','value']].groupby(['date_time','region','weather_year']).mean().unstack(['region','weather_year'])
df_smp_pivot.index = pd.to_datetime(df_smp_pivot.index, utc=True)
df_smp_pivot.columns = df_smp_pivot.columns.droplevel(0)


# %%
# monthly baseload
for region in df_smp_pivot.columns.get_level_values('region').unique():
    fig = df_smp_pivot.loc[:,df_smp_pivot.columns.get_level_values('region')==region].resample('MS').mean().T.boxplot(title=region+' - baseload')
    fig.show()
    # fig = df_smp_pivot.loc[:,df_smp_pivot.columns.get_level_values('region')==region].resample('MS').mean().T.boxplot()
    # print(region)
    # plt.show()


# %%
# quarterly baseload
for region in df_smp_pivot.columns.get_level_values('region').unique():
    fig = df_smp_pivot.loc['2022-10':,df_smp_pivot.columns.get_level_values('region')==region].resample('QS').mean().T.boxplot(title=region+' - baseload')
    # fig = df_smp_pivot.loc['2022-10':,df_smp_pivot.columns.get_level_values('region')==region].resample('QS').mean().T.boxplot()
    fig.show()
    # print(region)
    # plt.show()

# %%
# df_res = pull_parse(df, metric='Generation', region_list=['Germany'], tech_list=['Wind-Onshore','Wind-Offshore','Solar'])
dict_res = {}
for region in region_list:
    dict_res[region] = pull_parse(df, metric='Generation', region_list=[region], tech_list=['Wind','Solar'])

# %%
dict_res_pivot = {'Wind':{},'Solar':{}}
for tech in ['Wind','Solar']:
    for region in dict_res.keys():
        dict_res_pivot[tech][region] = dict_res[region].loc[dict_res[region].technology==tech].groupby(['date_time','region','weather_year']).mean().unstack(['region','weather_year'])

df_wind = pd.concat(dict_res_pivot['Wind'], axis=1)
df_wind.columns = df_wind.columns.droplevel(0)
df_wind.index = pd.to_datetime(df_wind.index, utc=True)
df_wind.columns = df_wind.columns.droplevel(0)
df_solar = pd.concat(dict_res_pivot['Solar'], axis=1)
df_solar.columns = df_solar.columns.droplevel(0)
df_solar.index = pd.to_datetime(df_solar.index, utc=True)
df_solar.columns = df_solar.columns.droplevel(0)