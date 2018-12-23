
**SAMSUNGCTL**
==========

OK so first thing is first.
I want to give a special thanks to the people that helped in the bug testing
of this version. It has been a bit of a challenge because of the different
devices/OS's that samsungctl is running on. In no special order I want to say
TY for the help. If I have missed mentioning ya. let me know. That was one
really long issue thread. and Github likes to collapse the thing. I could have
missed expanding one or 2 of the sections.

* @eclair4151
* @fluxdigital
* @DJPsycho82
* @sebdbr
* @Murph24
* @davidgurr
* @vitalets
* @msvinth
* @dcorsus


Onto the library.

samsungctl is a library and a command line tool for remote controlling Samsung
televisions via a TCP/IP connection. It currently supports both pre-2014 and
2016+ TVs as well most of the modern Tizen-OS TVs with Ethernet or Wi-Fi
connectivity.

UPDATE: This library supports 2016+ TV's running the latest firmware. Samsung
has changed it's websocket connection to now use SSL encryption. We have this
all sorted out.

If the TV kicks back an error when connecting the program will then try the
SSL connection. The SSL connection uses a token based system. What this
means is, there will be only one thing you need to do if your TV uses this
kind of a connection. You will get a message on the TV to pair a remote. You
will need to click on the "Accept" button. You have 30 seconds to do this
before the program will error out.

There is a flat text file that is used to store the token between uses of the
program. This is so that you will not have to go through the above process
each and every time you use the program. This file is going to be different
for each user that can be logged into the computer.micro controller.

On NIX systems the file is stored in
```~/.samsungctl```

On Windows the file is stored in
```%appdata%\samsungctl```

Both of the locations are specific to the profile of the user that is logged
in. I placed the file in these locations as to avoid any permissions related
issues.

This program IS NOT the same one that is available on the
Python Packaging Index (Pypi). I do not have access to that and unfortunatly
the original author Ape has been on hiatus for some time. He may no longer
be maintaining the library.


So for the time being you will need to clone this repository and install it
using the directions below.


More Changes:

Python 2.7+ compatible
Better logging
Adds additional keycodes (A LOT)
The websocket-client library a requirement not an option


Things to come
Expanded control and notifications from the TV
Automatic discovery of the TV
Support for other Samsung devices

<br></br>
***Dependencies***
------------------

- Python 2.7+
- `websocket-client`
- `curses` (optional, for the interactive mode)

<br></br>
***Installation***
------------------

```python setup.py install```

It's possible to use the command line tool without installation:

```python -m samsungctl```

<br></br>
***Command line usage***
------------------------

You can use `samsungctl` command to send keys to a TV:

```samsungctl --host <host> [options] <key> [key ...]```

`host` is the hostname or IP address of the TV. `key` is a key code, e.g.
`KEY_VOLDOWN`. See Key codes.

There is also an interactive mode (ncurses) for sending the key presses:

```samsungctl --host <host> [options] --interactive```

Use `samsungctl --help` for more information about the command line
arguments:

```
usage: samsungctl [-h] [--version] [-v] [-q] [-i] [--host HOST] [--port PORT]
                  [--method METHOD] [--name NAME] [--description DESC]
                  [--id ID] [--timeout TIMEOUT] [--key-help]
                  [key [key ...]]

Remote control Samsung televisions via TCP/IP connection

positional arguments:
  key                 keys to be sent (e.g. KEY_VOLDOWN)
```


optional argument|description
-- | --
-h, --help|show this help message and exit
--version|show program's version number and exit
-v, --verbose|increase output verbosity
-q, --quiet|suppress non-fatal output
-i, --interactive|interactive control
--host HOST|TV hostname or IP address
--port PORT|TV port number (TCP)
--method METHOD|Connection method (legacy or websocket)
--name NAME|remote control name
--description DESC|remote control description
--id ID|remote control id
--timeout TIMEOUT|socket timeout in seconds \(0 = no timeout\)
--key-help {OPTIONAL KEYS}|prints out key help

```
samsungctl --host 192.168.0.10 --name myremote KEY_VOLDOWN
```


To obtain a list of all of the known keys.
```samsungctl --help-keys```

You can also get help on a specific key
```samsungctl --key-help KEY_16_9```

or if you wanted to list more then one key
```samsungctl --key-help KEY_16_9 KEY_TTX_MIX```

The settings can be loaded from a configuration file. The file is searched from

* `$XDG_CONFIG_HOME/samsungctl.conf`
* `~/.config/samsungctl.conf`
* `/etc/samsungctl.conf`

in this order. A simple default configuration is
bundled with the source as

* `samsungctl.conf <samsungctl.conf>`


<br></br>
***Library usage***
-------------------

samsungctl can also be used as a python package.
```python
    import samsungctl
```

A context managed remote controller object of class `Remote` can be
constructed using the `with` statement:

```python
    with samsungctl.Remote(config) as remote:
        # Use the remote object
```

The constructor takes a configuration dictionary as a parameter. All
configuration items must be specified.


Key|Type|Description
---|----|-----------
host|string|Hostname or IP address of the TV.
port|int|TCP port number. \(Default: `55000`\)
method|string|Connection method \(`legacy` or `websocket`\)
name|string|Name of the remote controller.
description|string|Remote controller description.
id|string|Additional remote controller ID.
timeout|int|Timeout in seconds. `0` means no timeout.


The `Remote` object is very simple and you only need the `control(key)`
method. The only parameter is a string naming the key to be sent (e.g.
`KEY_VOLDOWN`). See `Key codes`_. You can call `control` multiple times
using the same `Remote` object. The connection is automatically closed when
exiting the `with` statement.

When something goes wrong you will receive an exception:

Exception|Description
---------|-----------
AccessDenied|The TV does not allow you to send keys.
ConnectionClosed|The connection was closed.
UnhandledResponse|An unexpected response was received.
socket.timeout|The connection timed out.

<br></br>
***Example program***
---------------------

This simple program opens and closes the menu a few times.

```python
import samsungctl
import time

config = {
    "name": "samsungctl",
    "description": "PC",
    "id": "",
    "host": "192.168.0.10",
    "port": 55000,
    "method": "legacy",
    "timeout": 0,
}

with samsungctl.Remote(config) as remote:
    for i in range(10):
        remote.control("KEY_MENU")
        time.sleep(0.5)
```


<br></br>
***Mouse Control***
---------------------

Mouse control can only be done by using samsungctl as a python module.
Mouse command are built. this way you can accomplish multiple movements
in a single "command" and the movement set can be stored for later use.
depending on how long it takes to accomplish a movement
(distance traveled) you will need to insert a wait period in between
each movement.

```python
import samsungctl

config = {
    "name": "samsungctl",
    "description": "PC",
    "id": "",
    "host": "192.168.0.10",
    "port": 8002,
    "method": "websocket",
    "timeout": 0,
}

with samsungctl.Remote(config) as remote:
    mouse = remote.mouse
    mouse.move(x=100, y=300)
    mouse.wait(0.5)
    mouse.left_click()
    mouse.run()
    mouse.clear()
```

I designed this to all be thread safe. so only one mouse command set
can be run at a single time. So if you have the mouse running in a
thread and you need to stop the movement from another. or you simply
want to terminate the program gracefully. you would call `mouse.stop()`


I will be at a later date adding the wait periods on the mouse movements
so it will be done automatically. I do not own one of the TV's so I do
not know how long it takes to move the mouse different distances. I
also do not know if the time it takes to move the mouse is linear. An
example of linear movement would be it takes 1 second to move the
mouse 100 pixels so to move it 200 pixels it would take 2 seconds.
most devices that have mouse control also have acceleration and a
min/max speed which would be non linear movement. An example of non
linear is, if it took 1 second to move the mouse 100 pixels, to move it
200 it would take 1.5 seconds. You can run the code below and report
the output to me. that will aide in making this all automatic. I need
this data form several TV models and years. as Samsung could have
changed the mouse speed and acceleration between years/models.


```python
import samsungctl

config = {
    "name": "samsungctl",
    "description": "PC",
    "id": "",
    "host": "192.168.0.10",
    "port": 8002,
    "method": "websocket",
    "timeout": 0,
}

with samsungctl.Remote(config) as remote:
    mouse = remote.mouse

    def move_mouse(_x, _y):
        mouse.move(x=x, y=y)
        start = time.time()
        mouse.run()
        stop = time.time()
        print('x:', x, 'y:', y, 'time:', (stop - start) * 1000)
        mouse.clear()
        mouse.move(x=-x, y=-y)
        mouse.run()
        mouse.clear()

    for x in range(1920):
        move_mouse(x, 0)

        for y in range(1080):
            move_mouse(0, y)
            move_mouse(x, y)
```

<br></br>
***Key codes***
---------------
Here is the new list of keycodes that are supported.

<br></br>
*Power Keys*
____________

Key|Description
---|-----------
KEY_POWEROFF|PowerOFF
KEY_POWERON|PowerOn
KEY_POWER|PowerToggle

<br></br>
*Input Keys*
____________

Key|Description
---|-----------
KEY_SOURCE|Source
KEY_COMPONENT1|Component1
KEY_COMPONENT2|Component2
KEY_AV1|AV1
KEY_AV2|AV2
KEY_AV3|AV3
KEY_SVIDEO1|SVideo1
KEY_SVIDEO2|SVideo2
KEY_SVIDEO3|SVideo3
KEY_HDMI|HDMI
KEY_HDMI1|HDMI1
KEY_HDMI2|HDMI2
KEY_HDMI3|HDMI3
KEY_HDMI4|HDMI4
KEY_FM_RADIO|FMRadio
KEY_DVI|DVI
KEY_DVR|DVR
KEY_TV|TV
KEY_ANTENA|AnalogTV
KEY_DTV|DigitalTV

<br></br>
*Number Keys*
_____________

Key|Description
---|-----------
KEY_1|Key1
KEY_2|Key2
KEY_3|Key3
KEY_4|Key4
KEY_5|Key5
KEY_6|Key6
KEY_7|Key7
KEY_8|Key8
KEY_9|Key9
KEY_0|Key0

<br></br>
*Misc Keys*
___________

Key|Description
---|-----------
KEY_PANNEL_CHDOWN|3D
KEY_ANYNET|AnyNet+
KEY_ESAVING|EnergySaving
KEY_SLEEP|SleepTimer
KEY_DTV_SIGNAL|DTVSignal

<br></br>
*Channel Keys*
______________

Key|Description
---|-----------
KEY_CHUP|ChannelUp
KEY_CHDOWN|ChannelDown
KEY_PRECH|PreviousChannel
KEY_FAVCH|FavoriteChannels
KEY_CH_LIST|ChannelList
KEY_AUTO_PROGRAM|AutoProgram
KEY_MAGIC_CHANNEL|MagicChannel

<br></br>
*Volume Keys*
_____________

Key|Description
---|-----------
KEY_VOLUP|VolumeUp
KEY_VOLDOWN|VolumeDown
KEY_MUTE|Mute

<br></br>
*Direction Keys*
________________

Key|Description
---|-----------
KEY_UP|NavigationUp
KEY_DOWN|NavigationDown
KEY_LEFT|NavigationLeft
KEY_RIGHT|NavigationRight
KEY_RETURN|NavigationReturn/Back
KEY_ENTER|NavigationEnter

<br></br>
*Media Keys*
____________

Key|Description
---|-----------
KEY_REWIND|Rewind
KEY_STOP|Stop
KEY_PLAY|Play
KEY_FF|FastForward
KEY_REC|Record
KEY_PAUSE|Pause
KEY_LIVE|Live
KEY_QUICK_REPLAY|fnKEY_QUICK_REPLAY
KEY_STILL_PICTURE|fnKEY_STILL_PICTURE
KEY_INSTANT_REPLAY|fnKEY_INSTANT_REPLAY

<br></br>
*Picture in Picture*
____________________

Key|Description
---|-----------
KEY_PIP_ONOFF|PIPOn/Off
KEY_PIP_SWAP|PIPSwap
KEY_PIP_SIZE|PIPSize
KEY_PIP_CHUP|PIPChannelUp
KEY_PIP_CHDOWN|PIPChannelDown
KEY_AUTO_ARC_PIP_SMALL|PIPSmall
KEY_AUTO_ARC_PIP_WIDE|PIPWide
KEY_AUTO_ARC_PIP_RIGHT_BOTTOM|PIPBottomRight
KEY_AUTO_ARC_PIP_SOURCE_CHANGE|PIPSourceChange
KEY_PIP_SCAN|PIPScan

<br></br>
*Modes*
_______

Key|Description
---|-----------
KEY_VCR_MODE|VCRMode
KEY_CATV_MODE|CATVMode
KEY_DSS_MODE|DSSMode
KEY_TV_MODE|TVMode
KEY_DVD_MODE|DVDMode
KEY_STB_MODE|STBMode
KEY_PCMODE|PCMode

<br></br>
*Color Keys*
____________

Key|Description
---|-----------
KEY_GREEN|Green
KEY_YELLOW|Yellow
KEY_CYAN|Cyan
KEY_RED|Red

<br></br>
*Teletext*
__________

Key|Description
---|-----------
KEY_TTX_MIX|TeletextMix
KEY_TTX_SUBFACE|TeletextSubface

<br></br>
*AspectRatio*
______________

Key|Description
---|-----------
KEY_ASPECT|AspectRatio
KEY_PICTURE_SIZE|PictureSize
KEY_4_3|AspectRatio4:3
KEY_16_9|AspectRatio16:9
KEY_EXT14|AspectRatio3:4(Alt)
KEY_EXT15|AspectRatio16:9(Alt)


*Picture Mode*
______________

Key|Description
---|-----------
KEY_PMODE|PictureMode
KEY_PANORAMA|PictureModePanorama
KEY_DYNAMIC|PictureModeDynamic
KEY_STANDARD|PictureModeStandard
KEY_MOVIE1|PictureModeMovie
KEY_GAME|PictureModeGame
KEY_CUSTOM|PictureModeCustom
KEY_EXT9|PictureModeMovie(Alt)
KEY_EXT10|PictureModeStandard(Alt)

<br></br>
*Menus*
_______

Key|Description
---|-----------
KEY_MENU|Menu
KEY_TOPMENU|TopMenu
KEY_TOOLS|Tools
KEY_HOME|Home
KEY_CONTENTS|Contents
KEY_GUIDE|Guide
KEY_DISC_MENU|DiscMenu
KEY_DVR_MENU|DVRMenu
KEY_HELP|Help

<br></br>
*OSD*
_____

Key|Description
---|-----------
KEY_INFO|Info
KEY_CAPTION|Caption
KEY_CLOCK_DISPLAY|ClockDisplay
KEY_SETUP_CLOCK_TIMER|SetupClock
KEY_SUB_TITLE|Subtitle

<br></br>
*Zoom*
______

Key|Description
---|-----------
KEY_ZOOM_MOVE|ZoomMove
KEY_ZOOM_IN|ZoomIn
KEY_ZOOM_OUT|ZoomOut
KEY_ZOOM1|Zoom1
KEY_ZOOM2|Zoom2

<br></br>
*Other Keys*
____________

Key|Description
---|-----------
KEY_WHEEL_LEFT|WheelLeft
KEY_WHEEL_RIGHT|WheelRight
KEY_ADDDEL|Add/Del
KEY_PLUS100|Plus100
KEY_AD|AD
KEY_LINK|Link
KEY_TURBO|Turbo
KEY_CONVERGENCE|Convergence
KEY_DEVICE_CONNECT|DeviceConnect
KEY_11|Key11
KEY_12|Key12
KEY_FACTORY|KeyFactory
KEY_3SPEED|Key3SPEED
KEY_RSURF|KeyRSURF
KEY_FF_|FF_
KEY_REWIND_|REWIND_
KEY_ANGLE|Angle
KEY_RESERVED1|Reserved1
KEY_PROGRAM|Program
KEY_BOOKMARK|Bookmark
KEY_PRINT|Print
KEY_CLEAR|Clear
KEY_VCHIP|VChip
KEY_REPEAT|Repeat
KEY_DOOR|Door
KEY_OPEN|Open
KEY_DMA|DMA
KEY_MTS|MTS
KEY_DNIe|DNIe
KEY_SRS|SRS
KEY_CONVERT_AUDIO_MAINSUB|ConvertAudioMain/Sub
KEY_MDC|MDC
KEY_SEFFECT|SoundEffect
KEY_PERPECT_FOCUS|PERPECTFocus
KEY_CALLER_ID|CallerID
KEY_SCALE|Scale
KEY_MAGIC_BRIGHT|MagicBright
KEY_W_LINK|WLink
KEY_DTV_LINK|DTVLink
KEY_APP_LIST|ApplicationList
KEY_BACK_MHP|BackMHP
KEY_ALT_MHP|AlternateMHP
KEY_DNSe|DNSe
KEY_RSS|RSS
KEY_ENTERTAINMENT|Entertainment
KEY_ID_INPUT|IDInput
KEY_ID_SETUP|IDSetup
KEY_ANYVIEW|AnyView
KEY_MS|MS
KEY_MORE|
KEY_MIC|
KEY_NINE_SEPERATE|
KEY_AUTO_FORMAT|AutoFormat
KEY_DNET|DNET

<br></br>
*Auto Arc Keys*
_______________

Key|Description
---|-----------
KEY_AUTO_ARC_C_FORCE_AGING|
KEY_AUTO_ARC_CAPTION_ENG|
KEY_AUTO_ARC_USBJACK_INSPECT|
KEY_AUTO_ARC_RESET|
KEY_AUTO_ARC_LNA_ON|
KEY_AUTO_ARC_LNA_OFF|
KEY_AUTO_ARC_ANYNET_MODE_OK|
KEY_AUTO_ARC_ANYNET_AUTO_START|
KEY_AUTO_ARC_CAPTION_ON|
KEY_AUTO_ARC_CAPTION_OFF|
KEY_AUTO_ARC_PIP_DOUBLE|
KEY_AUTO_ARC_PIP_LARGE|
KEY_AUTO_ARC_PIP_LEFT_TOP|
KEY_AUTO_ARC_PIP_RIGHT_TOP|
KEY_AUTO_ARC_PIP_LEFT_BOTTOM|
KEY_AUTO_ARC_PIP_CH_CHANGE|
KEY_AUTO_ARC_AUTOCOLOR_SUCCESS|
KEY_AUTO_ARC_AUTOCOLOR_FAIL|
KEY_AUTO_ARC_JACK_IDENT|
KEY_AUTO_ARC_CAPTION_KOR|
KEY_AUTO_ARC_ANTENNA_AIR|
KEY_AUTO_ARC_ANTENNA_CABLE|
KEY_AUTO_ARC_ANTENNA_SATELLITE|

<br></br>
*Panel Keys*
____________

Key|Description
---|-----------
KEY_PANNEL_POWER|
KEY_PANNEL_CHUP|
KEY_PANNEL_VOLUP|
KEY_PANNEL_VOLDOW|
KEY_PANNEL_ENTER|
KEY_PANNEL_MENU|
KEY_PANNEL_SOURCE|
KEY_PANNEL_ENTER|

<br></br>
*Extended Keys*
_______________

Key|Description
---|-----------
KEY_EXT1|
KEY_EXT2|
KEY_EXT3|
KEY_EXT4|
KEY_EXT5|
KEY_EXT6|
KEY_EXT7|
KEY_EXT8|
KEY_EXT11|
KEY_EXT12|
KEY_EXT13|
KEY_EXT16|
KEY_EXT17|
KEY_EXT18|
KEY_EXT19|
KEY_EXT20|
KEY_EXT21|
KEY_EXT22|
KEY_EXT23|
KEY_EXT24|
KEY_EXT25|
KEY_EXT26|
KEY_EXT27|
KEY_EXT28|
KEY_EXT29|
KEY_EXT30|
KEY_EXT31|
KEY_EXT32|
KEY_EXT33|
KEY_EXT34|
KEY_EXT35|
KEY_EXT36|
KEY_EXT37|
KEY_EXT38|
KEY_EXT39|
KEY_EXT40|
KEY_EXT41|


Please note that some codes are different on the 2016+ TVs. For example,
`KEY_POWEROFF` is `KEY_POWER` on the newer TVs.

<br></br>
***References***
----------------

I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
- https://github.com/kyleaa/homebridge-samsungtv2016
