from subs.access_backend import get_countries
from subs.colors import get_relative_Number

_, countries = get_countries()

countries['color'] = countries['COUNTRY'].apply(get_relative_Number)

df.set_index('COUNTRY')['color'].to_dict()

if __name__=='__main__':
    print(countries)