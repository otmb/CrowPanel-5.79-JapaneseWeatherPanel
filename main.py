# CrowPanel ESP32 5.79" E-paper Display with 272*792 Resolution
import time
time.sleep(1)

import urequests
# E-Paper display
import CrowPanel as eink
from writer import Writer
import framebuf
import machine
import SawarabiGothicRegular18, SawarabiGothicRegular24, SawarabiGothicRegular32
from icons import weather_icons32, weather_icons64, weather_icons128
from weather_config import weather_code, weather_icon_combin
from tools import connect_wifi, disconnect_wifi, set_time, get_now
from forecast import get_three_forecast, get_week_forecast, parse_date
from config import forest_code, area_code, temp_area_code
machine.freq(240000000) # High Power 240MHz

# Instantiate a Screen
screen = eink.Screen_579()
sawarabi18 = Writer(screen, SawarabiGothicRegular18)
sawarabi24 = Writer(screen, SawarabiGothicRegular24)
sawarabi32 = Writer(screen, SawarabiGothicRegular32)

# エラー追跡用のグローバル変数
error_flag = False
error_time = None

import requests
# APIで天候情報取得
# - 天気の取得に失敗すると10秒待機して10回繰り返します
def get_weather():
    url = f'https://www.jma.go.jp/bosai/forecast/data/forecast/{forest_code}.json'
    print("Get Weahter Request Start.")

    error = None
    for i in range(10):
        try:
            response = urequests.get(url, timeout=10)
            if response.reason != b"OK" or response.status_code >= 400:
                raise Exception(f"HTTP Request failed. Status Code: {response.status_code}")
            error = None
            break
        except Exception as e:
            error = e
            time.sleep(10)
            print(f"request retry: {i}, error: {e}")
            continue

    if error is not None:
        raise Exception(f"request error: {error}")

    print("Get Weahter Request Success.")
    data = response.json()
    response.close()
    return data

def get_weather_icon_name(code) -> tuple:
    code = int(code)
    if code not in weather_code:
        return None, None
    w_code = int(weather_code[code][0])
    if w_code not in weather_icon_combin:
        return None, None
    combination = weather_icon_combin[w_code]
    icons = combination.split(',')
    icon_name = icons[0].lower()
    half_icon_name = None
    is_later = False
    if len(icons) > 1:
        half_icon_name = icons[1].lower()
    is_later = len(icons) > 2
    return icon_name, half_icon_name, is_later

def create_weather_icon_large(code: int, offset = (0,0)):
    icon_name, half_icon_name, _ = get_weather_icon_name(code)

    if icon_name:
        size = 128
        img_data = bytearray(weather_icons128[icon_name])
        img_buf = framebuf.FrameBuffer(img_data, size, size, framebuf.MONO_HLSB)
        screen.blit(img_buf, offset[0], offset[1])

    if half_icon_name:
        size = 64
        img_data = bytearray(weather_icons64[half_icon_name])
        img_buf = framebuf.FrameBuffer(img_data, size, size, framebuf.MONO_HLSB)
        screen.blit(img_buf, 114 + offset[0], 64 + offset[1])

def create_weather_icon(code: int, offset = (0,0)):
    icon_name, half_icon_name, _ = get_weather_icon_name(code)

    if icon_name:
        size = 64
        img_data = bytearray(weather_icons64[icon_name])
        img_buf = framebuf.FrameBuffer(img_data, size, size, framebuf.MONO_HLSB)
        screen.blit(img_buf, offset[0], offset[1])

    if half_icon_name:
        size = 32
        img_data = bytearray(weather_icons32[half_icon_name])
        img_buf = framebuf.FrameBuffer(img_data, size, size, framebuf.MONO_HLSB)
        screen.blit(img_buf, 56 + offset[0], 26 + offset[1])

def write_forecast_sort_data(datas, day, x, y , end_symble = ""):
    if day in datas:
        sorted_items = sorted(datas[day].items())
        sorted_values = [value for _, value in sorted_items]
        text = "/".join(sorted_values)
        Writer.set_textpos(screen, x, y)
        sawarabi24.printstring(f"{text}{end_symble}", True)

def screen_rendering(data):

    three_data, week_data = data
    three_forecast = get_three_forecast(three_data['timeSeries'], area_code, temp_area_code)
    week_forecast = get_week_forecast(week_data['timeSeries'])

    # 3日間の天気
    col_x = int(792 / 2)
    offset_x = 10
    offset_y = 28

    max_rows = 2
    if len(three_forecast['times']) < max_rows:
        raise Exception("There is an insufficient amount of data")

    screen.fill(eink.COLOR_WHITE)

    for i in range(0,max_rows):
        _, _, day, hour, weekday = parse_date(three_forecast['times'][i])
        
        text = f"{day}日({weekday})"
        Writer.set_textpos(screen, offset_x + col_x * i, offset_y)
        sawarabi32.printstring(f"{text}", True)

        # 天気アイコンはY軸のオフセットは別で設定
        desc = three_forecast['description']
        code = int(desc['weatherCodes'][i])
        create_weather_icon_large(code, (offset_x + col_x * i + 128, 10))
        
        # 天気のテキストはY軸のオフセットは別で設定
        text = weather_code[code][2]
        Writer.set_textpos(screen, offset_x + col_x * i + 10, 120 + 10)
        sawarabi32.printstring(f"{text}", True)

        write_forecast_sort_data(three_forecast['temps'], day,
                                x = offset_x + col_x * i + 10,
                                y = 32 + offset_y + 4,
                                end_symble = "℃")
        write_forecast_sort_data(three_forecast['pops'], day,
                                x = offset_x + col_x * i + 10,
                                y = 32 + 24 + offset_y + 4)
       
    # 一週間の天気
    cel_x = 130
    offset_x = 10
    offset_y = 170

    min_rows = 1
    if len(three_forecast['times']) == 2:
        min_rows = 2

    for i in range(min_rows, len(week_forecast['times'])):
        p = i - min_rows
        _, _, day, _, weekday = parse_date(week_forecast['times'][i])
        text = f"{day}日({weekday})"
        Writer.set_textpos(screen, cel_x * p + offset_x, offset_y)
        sawarabi18.printstring(f"{text}", True)

        create_weather_icon(int(week_forecast['weatherCodes'][day]), (cel_x * p + offset_x + 10, offset_y + 18))

        texts = []
        temps = week_forecast['temps']
        if day in temps:
            temps = temps[day]
            texts.append(temps['tempsMinLower'] + '/' + temps['tempsMaxUpper'] + "℃")
        
        pops = week_forecast['pops']
        if day in pops:
            texts.append(pops[day] + "%")
        
        text = " ".join(texts)
        Writer.set_textpos(screen, cel_x * p + offset_x, offset_y + 18 + 64)
        sawarabi18.printstring(f"{text}", True)
    
    # 気象台テキスト
    text = three_data['publishingOffice']
    year, month, day, hour, weekday = parse_date(three_data['reportDatetime'])
    text += f" {year}年{month}月{day}日 {hour}時 発表"

    pos_x = int(792 * 0.55)
    Writer.set_textpos(screen, pos_x , 0)
    sawarabi18.printstring(f"{text}", True)

    prefecture_name = week_data['timeSeries'][0]['areas'][0]['area']['name'] 
    areat_name = three_data['timeSeries'][0]['areas'][0]['area']['name']
    Writer.set_textpos(screen, 10 , 0)
    sawarabi18.printstring(f"表示エリア: {prefecture_name} {areat_name}", True)

    screen.show()

def run():
    global error_flag, error_time
    try:
        machine.freq(240000000) # High Power 240MHz
        print("freq: ", machine.freq())
        if connect_wifi():
            print("is connected wifi")
            set_time()
            data = get_weather()
            screen_rendering(data)
            # 正常完了時はエラーフラグをクリア
            error_flag = False
            error_time = None
    except Exception as e:
        print("error: ", e)
        # エラー時はフラグを立てて、エラー発生時刻を記録
        error_flag = True
        error_time = time.time()
        # 画面は更新しない
    finally:
        disconnect_wifi()
        machine.freq(20000000) # Low Power 20MHz

# 起動時実行
run()

# 1分に1度だけ実行でかつ、気象庁の更新がある 5時, 11時, 17時に実行
try:
    while True:
        hour, min = get_now()[3:5]
        
        # エラー状態で10分以上経過している場合は再度実行
        if error_flag and error_time is not None:
            elapsed_time = time.time() - error_time
            if elapsed_time >= 600:  # 600秒 = 10分
                print("Retry after error (1 hour elapsed)")
                run()
        
        # 通常の定時実行（エラーフラグが立っていない場合）
        if not error_flag and min == 1 and hour in [5, 11, 17]:
            run()
        
        time.sleep(60)
except KeyboardInterrupt:
    pass