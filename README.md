# RockBLOCK Serial
A Python curses chat program for RockBLOCk serial communication

"The [RockBLOCK](http://www.rock7mobile.com/products-rockblock) Mk 2
allows you to send and receive short messages from anywhere on Earth with a 
clear view of the sky. It works far beyond the reach of WiFi and GSM networks."

This Python curses chat client sends and receives messages through a serial-connected
RockBLOCK Mk2.

# Assumptions

You have a RockBLOCK Mk2 that's registered, an account with Rock Seven, you've
paid for monthly use and have credits for sending/receiving data, and you've
configured what to do once Rock Seven receives a message from your RockBLOCK
(either email, or call a web service URL that you've set up).

On that last topic, I've been developing some code [here](https://github.com/shimniok/rockblock)
that permits web-based chat that receives your RockBLOCK messages and permits
replies to it, but it is very much a work in progress and not anywhere near
ready for release.

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
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 │                                                                            │
 └────────────────────────────────────────────────────────────────────────────┘
 ┌──────────────[q] quit | [s] send message | [r] receive message─────────────┐
 │                                                                            │
 └────────────────────────────────/dev/ttyUSB0────────────────────────────────┘

 ┌────────────────────────────────────────────────────────────────────────────┐
 │                                                                            │
 │                                                                            │
 └────────────────────────────────────────────────────────────────────────────┘
```
