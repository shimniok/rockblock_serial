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

# Usage

Run the python script rock.py

Press s to send a message; type in the message and press return to send it
Press r to attempt receiving messages sent to your RockBLOCK
Press q to quit the program

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
```


# Dependencies

The code requires the following Python packages to be installed:
 * pyserial
 * curses
 * signal
 * sys
 * threading
 * argparse
 * glob
 * time

