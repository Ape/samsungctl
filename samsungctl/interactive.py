import curses

_mappings = {
	"p":    "KEY_POWEROFF",
	"KEY_UP":    "KEY_UP",
	"KEY_DOWN":  "KEY_DOWN",
	"KEY_LEFT":  "KEY_LEFT",
	"KEY_RIGHT": "KEY_RIGHT",
	"KEY_PPAGE": "KEY_CHUP",
	"KEY_NPAGE": "KEY_CHDOWN",
	"\n":        "KEY_ENTER",
	"\x7f":      "KEY_RETURN",
	"l":         "KEY_CH_LIST",
	"m":         "KEY_MENU",
	"s":         "KEY_SOURCE",
	"g":         "KEY_GUIDE",
	"t":         "KEY_TOOLS",
	"i":         "KEY_INFO",
	"z":         "KEY_RED",
	"x":         "KEY_GREEN",
	"c":         "KEY_YELLOW",
	"v":         "KEY_BLUE",
	"d":         "KEY_PANNEL_CHDOWN", # 3D
	"+":         "KEY_VOLUP",
	"-":         "KEY_VOLDOWN",
	"*":         "KEY_MUTE",
	"0":         "KEY_0",
	"1":         "KEY_1",
	"2":         "KEY_2",
	"3":         "KEY_3",
	"4":         "KEY_4",
	"5":         "KEY_5",
	"6":         "KEY_6",
	"7":         "KEY_7",
	"8":         "KEY_8",
	"9":         "KEY_9",
	"KEY_F(1)":  "KEY_DTV",
	"KEY_F(2)":  "KEY_HDMI",
}

def run(remote):
	curses.wrapper(control, remote)

def control(stdscr, remote):
	stdscr.addstr("Running interactive mode\n\n")
	stdscr.addstr("Press 'q' to exit.\n")

	running = True
	while running:
		key = stdscr.getkey()

		if key == "q":
			running = False

		if key in _mappings:
			stdscr.addstr(".")
			remote.control(_mappings[key])
