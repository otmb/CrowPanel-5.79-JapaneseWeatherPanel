from tools import get_now

WEEEKDAY = ['月', '火', '水', '木', '金', '土', '日']

def get_weekday(day: int):
    day = int(day)
    for i in range(0,8):
        now = get_now(i*86400)
        if day == now[2]:
            return WEEEKDAY[now[6]]
    return ""

def parse_date(date_text):
    _date, _time = date_text.split('T')
    year, month, day = _date.split('-')
    hour = _time.split(':')[0]
    weekday = get_weekday(day)
    return year, month, day, hour, weekday

def set_dict_format(time_defines, items, dict_format):
    datas = {}
    for date_text in time_defines:
        _, _, day, _, _ = parse_date(date_text)
        datas[day] = dict_format
    
    for i, date_text in enumerate(time_defines):
        _, _, day, hour, _ = parse_date(date_text)
        datas[day][hour] = items[i]

    return datas

def get_three_forecast(time_series, area_code, temp_area_code):
    forecast = {
        'description': None,
        'times': {},
        'pops': {},
        'temps': {},
    }
    for series in time_series:
        for item in series['areas']:
            if item['area']['code'] == str(area_code):
                if 'pops' in item.keys():
                    dict_format = { "00": "-", "06": "-", "12": "-", "18": "-"}
                    forecast['pops'] = set_dict_format(series['timeDefines'], item['pops'], dict_format)
                else:
                    forecast['description'] = item
                    forecast['times'] = series['timeDefines']
        for item in series['areas']:
            if item['area']['code'] == str(temp_area_code):
                dict_format = {"00": "-", "09": "-"}
                forecast['temps'] = set_dict_format(series['timeDefines'], item['temps'], dict_format)
    return forecast

def get_week_forecast(time_series):
    forecast = {
        'times': {},
        'weatherCodes': {},
        'pops': {},
        'temps': {},
    }
    for series in time_series:
        for item in series['areas']:
            for i, date_text in enumerate(series['timeDefines']):
                _, _, day, _, _ = parse_date(date_text)  
                if 'weatherCodes' in item.keys():
                    forecast['weatherCodes'][day] = item['weatherCodes'][i]
                if 'pops' in item.keys():
                    forecast['pops'][day] = item['pops'][i]
                if 'tempsMin' in item.keys():
                    forecast['temps'][day] = {
                        'tempsMin': item['tempsMin'][i],
                        'tempsMinUpper': item['tempsMinUpper'][i],
                        'tempsMinLower': item['tempsMinLower'][i],
                        'tempsMax': item['tempsMax'][i],
                        'tempsMaxUpper': item['tempsMaxUpper'][i],
                        'tempsMaxLower': item['tempsMaxLower'][i],
                    }
        forecast['times'] = series['timeDefines']
    return forecast


def get_area_code(time_series):
    pops_area_code = []
    temps_area_code = []
    for series in time_series:
        for item in series['areas']:
            if 'pops' in item.keys():
                pops_area_code.append(item['area']['code'])
            if 'temps' in item.keys():
                temps_area_code.append(item['area']['code'])
            if 'tempsMin' in item.keys():
                temps_area_code.append(item['area']['code'])
    return {'pops': pops_area_code, 'temps': temps_area_code }
