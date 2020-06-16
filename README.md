# COVID-19 Display for Raspberry PI and I2C 16x2
This app was created to show the current cases of a selected country. It will update itself every 10 minutes with the latest data or after a given time period. 

<img src="https://raw.githubusercontent.com/maxi07/covid19-display/master/doc/IMG_4785.JPEG" align="center"/>

## Install
Please clone the repository and run the installer with
```bash
sudo ./install.sh
```
The device will reboot after completed to activate the GPIO pins.

## Wiring / Display
The script was developed for a 16x2 I2C display, which can be found for cheap on Amazon.com.
For wiring setup, please check the [wiki.](https://github.com/maxi07/speedtest-display/wiki/Connect-LCD-display)

## Run
To run the script, execute
```bash
python3 run-speedtest-display.py
```

## Options
To print all available options, use 
```bash
python3 run-speedtest-display.py --help
```

## Credits
The API used for this projects can be found at [TrackCorona](https://trackcorona.live).

## Warranty
Although we strive to have the most accurate, up-to-date information, we cannot guarantee nor be held liable for any errors.
Contact us at team@trackcorona.live if you have any questions about the data or the required attribution.
