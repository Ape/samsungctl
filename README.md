
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

    ~/.samsungctl

On Windows the file is stored in

    %appdata%\samsungctl

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

***Dependencies***
------------------

- Python 2.7+
- `websocket-client`
- `curses` (optional, for the interactive mode)

***Installation***
------------------

    # python setup.py install

It's possible to use the command line tool without installation:

    $ python -m samsungctl

***Command line usage***
------------------------

You can use `samsungctl` command to send keys to a TV:

    $ samsungctl --host <host> [options] <key> [key ...]

`host` is the hostname or IP address of the TV. `key` is a key code, e.g.
`KEY_VOLDOWN`. See Key codes.

There is also an interactive mode (ncurses) for sending the key presses:

    $ samsungctl --host <host> [options] --interactive

Use `samsungctl --help` for more information about the command line
arguments:


    usage: samsungctl [-h] [--version] [-v] [-q] [-i] [--host HOST] [--port PORT]
                      [--method METHOD] [--name NAME] [--description DESC]
                      [--id ID] [--timeout TIMEOUT]
                      [key [key ...]]

    Remote control Samsung televisions via TCP/IP connection

    positional arguments:
      key                 keys to be sent (e.g. KEY_VOLDOWN)

    optional arguments:
      -h, --help                   show this help message and exit
      --version                    show program's version number and exit
      -v, --verbose                increase output verbosity
      -q, --quiet                  suppress non-fatal output
      -i, --interactive            interactive control
      --host HOST                  TV hostname or IP address
      --port PORT                  TV port number (TCP)
      --method METHOD              Connection method (legacy or websocket)
      --name NAME                  remote control name
      --description DESC           remote control description
      --id ID                      remote control id
      --timeout TIMEOUT            socket timeout in seconds (0 = no timeout)
      --key-help {OPTIONAL KEYS}   prints out key help

    E.g. samsungctl --host 192.168.0.10 --name myremote KEY_VOLDOWN

The settings can be loaded from a configuration file. The file is searched from

   `$XDG_CONFIG_HOME/samsungctl.conf`
   `~/.config/samsungctl.conf`
and
   `/etc/samsungctl.conf`

in this order. A simple default configuration is
bundled with the source as
   `samsungctl.conf <samsungctl.conf>`



***Library usage***
-------------------

samsungctl can be imported as a Python 3 library:

    import samsungctl

A context managed remote controller object of class `Remote` can be
constructed using the `with` statement:

    with samsungctl.Remote(config) as remote:
        # Use the remote object

The constructor takes a configuration dictionary as a parameter. All
configuration items must be specified.

    ===========  ======  ===========================================
    Key          Type    Description
    ===========  ======  ===========================================
    host         string  Hostname or IP address of the TV.
    port         int     TCP port number. (Default: `55000`)
    method       string  Connection method (`legacy` or `websocket`)
    name         string  Name of the remote controller.
    description  string  Remote controller description.
    id           string  Additional remote controller ID.
    timeout      int     Timeout in seconds. `0` means no timeout.
    ===========  ======  ===========================================

The `Remote` object is very simple and you only need the `control(key)`
method. The only parameter is a string naming the key to be sent (e.g.
`KEY_VOLDOWN`). See `Key codes`_. You can call `control` multiple times
using the same `Remote` object. The connection is automatically closed when
exiting the `with` statement.

When something goes wrong you will receive an exception:

    =================  =======================================
    Exception          Description
    =================  =======================================
    AccessDenied       The TV does not allow you to send keys.
    ConnectionClosed   The connection was closed.
    UnhandledResponse  An unexpected response was received.
    socket.timeout     The connection timed out.
    =================  =======================================

***Example program***
---------------------

This simple program opens and closes the menu a few times.

.. code-block:: python

    #!/usr/bin/env python3

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

You Can obtain a list of the keys by adding the

    --help-keys

command line switch

You can also get help on specific keys

    --key-help KEY_16_9

or if you wanted to list more then one key

    --key-help KEY_16_9 KEY_TTX_MIX


***Key codes***
---------------
Here is the new list of keycodes that are supported.


*Power Keys*
____________
    KEY_POWEROFF                    Power OFF
    KEY_POWERON                     Power On
    KEY_POWER                       Power Toggle


*Input Keys*
____________
    KEY_SOURCE                      Source
    KEY_COMPONENT1                  Component 1
    KEY_COMPONENT2                  Component 2
    KEY_AV1                         AV 1
    KEY_AV2                         AV 2
    KEY_AV3                         AV 3
    KEY_SVIDEO1                     S Video 1
    KEY_SVIDEO2                     S Video 2
    KEY_SVIDEO3                     S Video 3
    KEY_HDMI                        HDMI
    KEY_HDMI1                       HDMI 1
    KEY_HDMI2                       HDMI 2
    KEY_HDMI3                       HDMI 3
    KEY_HDMI4                       HDMI 4
    KEY_FM_RADIO                    FM Radio
    KEY_DVI                         DVI
    KEY_DVR                         DVR
    KEY_TV                          TV
    KEY_ANTENA                      Analog TV
    KEY_DTV                         Digital TV


*Number Keys*
_____________
    KEY_1                           Key1
    KEY_2                           Key2
    KEY_3                           Key3
    KEY_4                           Key4
    KEY_5                           Key5
    KEY_6                           Key6
    KEY_7                           Key7
    KEY_8                           Key8
    KEY_9                           Key9
    KEY_0                           Key0


*Misc Keys*
___________
    KEY_PANNEL_CHDOWN               3D
    KEY_ANYNET                      AnyNet+
    KEY_ESAVING                     Energy Saving
    KEY_SLEEP                       Sleep Timer
    KEY_DTV_SIGNAL                  DTV Signal


*Channel Keys*
______________
    KEY_CHUP                        Channel Up
    KEY_CHDOWN                      Channel Down
    KEY_PRECH                       Previous Channel
    KEY_FAVCH                       Favorite Channels
    KEY_CH_LIST                     Channel List
    KEY_AUTO_PROGRAM                Auto Program
    KEY_MAGIC_CHANNEL               Magic Channel


*Volume Keys*
_____________
    KEY_VOLUP                       Volume Up
    KEY_VOLDOWN                     Volume Down
    KEY_MUTE                        Mute


*Direction Keys*
________________
    KEY_UP                          Navigation Up
    KEY_DOWN                        Navigation Down
    KEY_LEFT                        Navigation Left
    KEY_RIGHT                       Navigation Right
    KEY_RETURN                      Navigation Return/Back
    KEY_ENTER                       Navigation Enter


*Media Keys*
____________
    KEY_REWIND                      Rewind
    KEY_STOP                        Stop
    KEY_PLAY                        Play
    KEY_FF                          Fast Forward
    KEY_REC                         Record
    KEY_PAUSE                       Pause
    KEY_LIVE                        Live
    KEY_QUICK_REPLAY                fnKEY_QUICK_REPLAY
    KEY_STILL_PICTURE               fnKEY_STILL_PICTURE
    KEY_INSTANT_REPLAY              fnKEY_INSTANT_REPLAY


*Picture in Picture*
____________________
    KEY_PIP_ONOFF                   PIP On/Off
    KEY_PIP_SWAP                    PIP Swap
    KEY_PIP_SIZE                    PIP Size
    KEY_PIP_CHUP                    PIP Channel Up
    KEY_PIP_CHDOWN                  PIP Channel Down
    KEY_AUTO_ARC_PIP_SMALL          PIP Small
    KEY_AUTO_ARC_PIP_WIDE           PIP Wide
    KEY_AUTO_ARC_PIP_RIGHT_BOTTOM   PIP Bottom Right
    KEY_AUTO_ARC_PIP_SOURCE_CHANGE  PIP Source Change
    KEY_PIP_SCAN                    PIP Scan


*Modes*
_______
    KEY_VCR_MODE                    VCR Mode
    KEY_CATV_MODE                   CATV Mode
    KEY_DSS_MODE                    DSS Mode
    KEY_TV_MODE                     TV Mode
    KEY_DVD_MODE                    DVD Mode
    KEY_STB_MODE                    STB Mode
    KEY_PCMODE                      PC Mode


*Color Keys*
____________
    KEY_GREEN                       Green
    KEY_YELLOW                      Yellow
    KEY_CYAN                        Cyan
    KEY_RED                         Red


*Teletext*
__________
    KEY_TTX_MIX                     Teletext Mix
    KEY_TTX_SUBFACE                 Teletext Subface


*Aspect Ratio*
______________
    KEY_ASPECT                      Aspect Ratio
    KEY_PICTURE_SIZE                Picture Size
    KEY_4_3                         Aspect Ratio 4:3
    KEY_16_9                        Aspect Ratio 16:9
    KEY_EXT14                       Aspect Ratio 3:4 (Alt)
    KEY_EXT15                       Aspect Ratio 16:9 (Alt)


*Picture Mode*
______________
    KEY_PMODE                       Picture Mode
    KEY_PANORAMA                    Picture Mode Panorama
    KEY_DYNAMIC                     Picture Mode Dynamic
    KEY_STANDARD                    Picture Mode Standard
    KEY_MOVIE1                      Picture Mode Movie
    KEY_GAME                        Picture Mode Game
    KEY_CUSTOM                      Picture Mode Custom
    KEY_EXT9                        Picture Mode Movie (Alt)
    KEY_EXT10                       Picture Mode Standard (Alt)


*Menus*
_______
    KEY_MENU                        Menu
    KEY_TOPMENU                     Top Menu
    KEY_TOOLS                       Tools
    KEY_HOME                        Home
    KEY_CONTENTS                    Contents
    KEY_GUIDE                       Guide
    KEY_DISC_MENU                   Disc Menu
    KEY_DVR_MENU                    DVR Menu
    KEY_HELP                        Help


*OSD*
_____
    KEY_INFO                        Info
    KEY_CAPTION                     Caption
    KEY_CLOCK_DISPLAY               ClockDisplay
    KEY_SETUP_CLOCK_TIMER           Setup Clock
    KEY_SUB_TITLE                   Subtitle


*Zoom*
______
    KEY_ZOOM_MOVE                   Zoom Move
    KEY_ZOOM_IN                     Zoom In
    KEY_ZOOM_OUT                    Zoom Out
    KEY_ZOOM1                       Zoom 1
    KEY_ZOOM2                       Zoom 2


*Other Keys*
____________
    KEY_WHEEL_LEFT                  Wheel Left
    KEY_WHEEL_RIGHT                 Wheel Right
    KEY_ADDDEL                      Add/Del
    KEY_PLUS100                     Plus 100
    KEY_AD                          AD
    KEY_LINK                        Link
    KEY_TURBO                       Turbo
    KEY_CONVERGENCE                 Convergence
    KEY_DEVICE_CONNECT              Device Connect
    KEY_11                          Key 11
    KEY_12                          Key 12
    KEY_FACTORY                     Key Factory
    KEY_3SPEED                      Key 3SPEED
    KEY_RSURF                       Key RSURF
    KEY_FF_                         FF_
    KEY_REWIND_                     REWIND_
    KEY_ANGLE                       Angle
    KEY_RESERVED1                   Reserved 1
    KEY_PROGRAM                     Program
    KEY_BOOKMARK                    Bookmark
    KEY_PRINT                       Print
    KEY_CLEAR                       Clear
    KEY_VCHIP                       V Chip
    KEY_REPEAT                      Repeat
    KEY_DOOR                        Door
    KEY_OPEN                        Open
    KEY_DMA                         DMA
    KEY_MTS                         MTS
    KEY_DNIe                        DNIe
    KEY_SRS                         SRS
    KEY_CONVERT_AUDIO_MAINSUB       Convert Audio Main/Sub
    KEY_MDC                         MDC
    KEY_SEFFECT                     Sound Effect
    KEY_PERPECT_FOCUS               PERPECT Focus
    KEY_CALLER_ID                   Caller ID
    KEY_SCALE                       Scale
    KEY_MAGIC_BRIGHT                Magic Bright
    KEY_W_LINK                      W Link
    KEY_DTV_LINK                    DTV Link
    KEY_APP_LIST                    Application List
    KEY_BACK_MHP                    Back MHP
    KEY_ALT_MHP                     Alternate MHP
    KEY_DNSe                        DNSe
    KEY_RSS                         RSS
    KEY_ENTERTAINMENT               Entertainment
    KEY_ID_INPUT                    ID Input
    KEY_ID_SETUP                    ID Setup
    KEY_ANYVIEW                     Any View
    KEY_MS                          MS
    KEY_MORE
    KEY_MIC
    KEY_NINE_SEPERATE
    KEY_AUTO_FORMAT                 Auto Format
    KEY_DNET                        DNET


*Auto Arc Keys*
_______________
    KEY_AUTO_ARC_C_FORCE_AGING
    KEY_AUTO_ARC_CAPTION_ENG
    KEY_AUTO_ARC_USBJACK_INSPECT
    KEY_AUTO_ARC_RESET
    KEY_AUTO_ARC_LNA_ON
    KEY_AUTO_ARC_LNA_OFF
    KEY_AUTO_ARC_ANYNET_MODE_OK
    KEY_AUTO_ARC_ANYNET_AUTO_START
    KEY_AUTO_ARC_CAPTION_ON
    KEY_AUTO_ARC_CAPTION_OFF
    KEY_AUTO_ARC_PIP_DOUBLE
    KEY_AUTO_ARC_PIP_LARGE
    KEY_AUTO_ARC_PIP_LEFT_TOP
    KEY_AUTO_ARC_PIP_RIGHT_TOP
    KEY_AUTO_ARC_PIP_LEFT_BOTTOM
    KEY_AUTO_ARC_PIP_CH_CHANGE
    KEY_AUTO_ARC_AUTOCOLOR_SUCCESS
    KEY_AUTO_ARC_AUTOCOLOR_FAIL
    KEY_AUTO_ARC_JACK_IDENT
    KEY_AUTO_ARC_CAPTION_KOR
    KEY_AUTO_ARC_ANTENNA_AIR
    KEY_AUTO_ARC_ANTENNA_CABLE
    KEY_AUTO_ARC_ANTENNA_SATELLITE


*Panel Keys*
____________
    KEY_PANNEL_POWER
    KEY_PANNEL_CHUP
    KEY_PANNEL_VOLUP
    KEY_PANNEL_VOLDOW
    KEY_PANNEL_ENTER
    KEY_PANNEL_MENU
    KEY_PANNEL_SOURCE
    KEY_PANNEL_ENTER


*Extended Keys*
_______________
    KEY_EXT1
    KEY_EXT2
    KEY_EXT3
    KEY_EXT4
    KEY_EXT5
    KEY_EXT6
    KEY_EXT7
    KEY_EXT8
    KEY_EXT11
    KEY_EXT12
    KEY_EXT13
    KEY_EXT16
    KEY_EXT17
    KEY_EXT18
    KEY_EXT19
    KEY_EXT20
    KEY_EXT21
    KEY_EXT22
    KEY_EXT23
    KEY_EXT24
    KEY_EXT25
    KEY_EXT26
    KEY_EXT27
    KEY_EXT28
    KEY_EXT29
    KEY_EXT30
    KEY_EXT31
    KEY_EXT32
    KEY_EXT33
    KEY_EXT34
    KEY_EXT35
    KEY_EXT36
    KEY_EXT37
    KEY_EXT38
    KEY_EXT39
    KEY_EXT40
    KEY_EXT41


Please note that some codes are different on the 2016+ TVs. For example,
`KEY_POWEROFF` is `KEY_POWER` on the newer TVs.

***References***
----------------

I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
- https://github.com/kyleaa/homebridge-samsungtv2016
