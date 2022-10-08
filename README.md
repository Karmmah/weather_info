# weather_info
Python script to get weather data from openweathermap.com and display it on an e-paper display attached to a raspberrypi.

Installation Guide:
0. Install Raspberry OS on your Raspberry Pi (the Lite version works, too)
1. Enable SPI-Interface in "sudo raspi-config"
2. Reboot Pi
3. Install BCM2835 libraries in home directory
```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```
4. Install WiringPi libraries
```
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
#(Version 2.52 should show up)
```
5. Install Python3 libraries
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
```
6. Clone weather_info repo
```
git clone https://github.com/Karmmah/weather_info
```
7. Create "openweathermap_token.txt" with your personal Token
8. Create "town.txt" with your town name
9. Copy "weather_info.service" to /etc/systemd/system
10. Enable the Weather-Info Unit
```
systemctl enable weather_info
```
11. (check if the Unit is running with "systemctl status weather_info")
