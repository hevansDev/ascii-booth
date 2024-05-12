# ASCII Booth

## Disclaimer

This is my code for my ASCII Booth Installation at EMF code 2024. This is not intended as a guide or tutorial (for notebooks on making ASCII Art with Python see the Workshop section of this repo).

## Setup

If you'd like to have a go at setting up your own photo booth based on this code you can try following the steps below. 

Be aware that you will need to make some changes to the configuration in the Printer class to match your particular receipt printer.

1. Install 32 bit (recommended version) bookworm for Raspberry Pi 3 with network settings pre-configured if you plan on using your booth headless

2. Install python dependencies, I would recommend [creating a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
) first.

`python3 -m pip install -r requirements.txt`

3. Install relevant receipt printer drivers, I have included the drivers for the printer I am using in the repo which can be installed like so

`sudo bash install install58`

4. Connect a button to GPIO pin 17 on your Raspberry Pi (or change the code to use a different trigger)

5. Clone this repo to your raspberry pi

`git clone https://github.com/hevansDev/ascii-booth.git`

6. In the `asciiBooth/Booth` directory create a file called `config.ini` with the following contents if you would like to use the Mastodon feature
```
[mastodon]
client_id = <your client ID here>
client_secret= <your client secret here>
access_token = <your access token here>
enabled = True
```

If you don't want to use Mastodon to post pictures taken by the booth set the config file contents as follows

```
[mastodon]
enabled = False
```

7. Set the following in cron

`@reboot python3 /home/<your user i.e pi>/asciiBooth/Booth/main.py`