# PyPenwriter

  This is a simple utility to convert [vpype][1]-treated SVGs into a sequence
of serial commands for the Panasonic Penwriter line of combo typewriter and
pen plotter machines. It has been tested on an RK-P400C model, which I own.

## Usage

```pypenwriter <input.svg> <com-port> [<width-in-steps>]```

  The utility expects you to already have passed the SVG through [vpype][1]
first, it is not designed to work with every SVG standard otherwise. In
addition, you may manually edit the SVG in [Inkscape][2] after converting it
through vpype to edit the stroke colors. PyPenwriter expects:

| `stroke:` style | pen selection |
|-----------------|---------------|
| `#000000`       | black         |
| `#ff0000`       | red           |
| `#00ff00`       | green         |
| `#0000ff`       | blue          |

  The optional `<width-in-steps>` argument automatically scales your drawing to
have the width be equal to the number of steps specified. The conversion between
steps and real-world units can be found in [the manual for the RK-P400C][3].
As a rule of thumb, the total printable width of the paper carriage in an
RK-P400C is 960 steps. In case you do not specify this width, the SVG viewbox
will be scaled to the full printable width of the plotter.

  Your plotter typewriter should be set for 2400 baud, 8 bits no parity. Your
cable should be RS232-compliant and have the DTR line from the plotter wired
into the CTS line of your host machine. This setup has been tested with a
modern FTDI UART chip wired into a MAX232R for signal level conversion.

## License

  This project uses a modified Anti-Fascist MIT License and Anti-Capitalist
Software License. Please see `LICENSE` for details.

[1]:https://github.com/abey79/vpype
[2]:https://inkscape.org/
[3]:https://archive.org/details/panasonic-rk-p-400-c-manual/page/n33/mode/2up