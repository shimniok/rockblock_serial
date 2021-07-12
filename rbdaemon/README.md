# RockBlock Daemon

A Python daemon for your serial-connected RockBLOCK 9602 device that sends and receves 
Short Burst Data (SBD) messages and reports signal strength. Intended to run on a 
Raspberry Pi of some sort.

"The [RockBLOCK](http://www.rock7mobile.com/products-rockblock) Mk 2
allows you to send and receive short messages from anywhere on Earth with a 
clear view of the sky. It works far beyond the reach of WiFi and GSM networks."

# Assumptions

You have a RockBLOCK Mk2 that's registered, an account with Rock Seven, you've
paid for monthly use and have credits for sending/receiving data.  

I've been developing a web-based chat program [here](https://github.com/shimniok/rockblock)
that interfaces with Rock7 and enables your person-at-home to chat with you in the field. It 
is still early in development and not ready for release.

# Install

Clone the repository or download as zip and extract into a folder/directory (`rockblock_serial`)

Install the packages listed in requirements.txt (optional: you can use this file with [virtualenv](https://virtualenv.pypa.io/en/latest/))

`pip install -r requirements.txt`

Change directory into `rockblock_serial` and launch the app:

`./rock.py`

# Usage

Run the python script rock.py

`python rock.py` or `./rock.py`

Press s to send a message; type in the message and press return to send it
Press r to attempt receiving messages sent to your RockBLOCK
Press q to quit the program

Sent and received messages appear in the topmost window, similar to text messaging
applications.

The input window appears directly below the message window. When you're ready to
send a message and press `s`, the message prompt (`Message>`) will be displayed
and you can type your message. This window also diplsays the list of available
commands at the top and the current serial device at the bottom.

The status window is below the input window. It displays text indicating the status
of commands, such as "TX Started", "RX Started", and any failure messages.

Finally, the raw text window is at the bottom. It displays all text received from
the RockBLOCK module so you can better diagnose failures.

```
