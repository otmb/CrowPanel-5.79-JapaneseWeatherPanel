import network
import time
import ntptime
import utime

# rename config.py.sample -> config.py
from config import (
    ssid, password, ntp_host, utc_hour
)

# WiFiに接続
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    
    print('network config:', wlan.ifconfig())
    return wlan.isconnected()


def disconnect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
    if wlan.active():
        wlan.active(False)
    
    print('disconnect wifi')
    time.sleep(1)

def get_now(sec=0):
    return utime.localtime(utime.time() + utc_hour * 60 * 60 + sec)

def set_time():
    ntptime.host = ntp_host
    time.sleep(0.1)
    ntptime.settime()
    print("Time set from NTP server.")
    now = get_now()
    print("Current time:", "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(now[0], now[1], now[2], now[3], now[4], now[5]))
