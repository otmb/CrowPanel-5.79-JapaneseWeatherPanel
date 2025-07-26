## About

CrowPanel ESP32 E-Paper HMI 5.79-inch Displayをベースに、お天気情報のデジタルサイネージを作成しました。  
気象庁のJsonを読み込んで天気情報を表示します。

## Instration

```bash
$ curl -LO https://micropython.org/resources/firmware/ESP32_GENERIC_S3-SPIRAM_OCT-20250415-v1.25.0.bin

$ pip install esptool
$ esptool.py erase_flash
$ esptool.py --baud 460800 write_flash 0 ESP32_GENERIC_S3-SPIRAM_OCT-20250415-v1.25.0.bin
```

環境はVSCodeに[MicroPico](https://github.com/paulober/MicroPico)拡張を利用しました。

### VScodeでMicroPicoの操作

- config.py.sampleを別名でコピーしてWiFi情報を設定してください。
    - `$ cp config.py.sample config.py`
    - edit config.py
- CrowPanelには自動で接続できていると思います。以下は接続後の操作になります。
- エクスプローラーを左クリックで「Upload project to Pico」を実行します。
    - この操作により、*.py ファイルは全てアップロードされます。
- 最後にmain.pyを開いた状態で左下の「▷Run」を実行します。
    - うまくいけば画面が表示され、インストールは完了です。

##  開発の参考情報

### CrowPanelでMicroPythonの導入の手引き
- [Elecrow 5.79" screen library for Micropython](https://www.elecrow.com/sharepj/elecrow-579-screen-library-for-micropython-513.html)
- [Elecrow CrowPanel 5.79" E-Paper display](https://www.bukys.eu/components/crowpanel_5_79)
- [MicroPython-ESP32-S3](https://micropython.org/download/ESP32_GENERIC_S3/)

### カスタムフォントの作成

- fonts.googleから[さわらびフォント](https://fonts.google.com/specimen/Sawarabi+Gothic)をダウンロード 
- 必要となるキャラクターのフォントを作成
```
$ curl -LO https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/c24761448e6ef1c40716b9b2b629e6fa37b2c9d2/font_to_py.py

$ python font_to_py.py -c " 0123456789.C°℃:%％" SawarabiGothic-Regular.ttf 32 SawarabiGothicRegularNumeric32.py 
```

- 参考: [peterhinch/micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py)
- [dev](dev)にフォルダにJupyterNoteがあるので参考にしてください。

### モノクロ画像の作成

#### 利用している天気のアイコン

- [erikflowers/weather-icons](https://github.com/erikflowers/weather-icons)
- [icooon-mono](https://icooon-mono.com/14253-%e9%9b%aa%e3%81%a0%e3%82%8b%e3%81%be%e3%82%a2%e3%82%a4%e3%82%b3%e3%83%b34/)

#### モノクロ画像の変換処理

ImageMagickのconvertコマンドでsvgをpngに変換した後、icons.py にアイコンファイルをまとめます。  

1. ImageMagickのconvertコマンドでsvgをpngに変換  
```shell
$ for i in `ls *.svg`; convert -size 128x128 $i $i.png
```

2. icons.py にアイコンファイルをまとめる処理
 
CrowPanel用のモノクロ画像の作成には[TimHanewich/MicroPython-SSD130](https://github.com/TimHanewich/MicroPython-SSD1306)のコードを利用しました。  

下記からダウンロードして利用します。
```shell
$ curl -LO https://raw.githubusercontent.com/TimHanewich/MicroPython-SSD1306/refs/heads/master/src/convert.py
```

- [dev](dev)にフォルダにJupyterNoteがあるので参考にしてください。
