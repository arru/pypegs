pyPEGS party shades Python utilities
====================================

Open source, platform agnostic utilites for the flashy PEGS LED sunglasses made by Infinite Reach (www.infinitereachsc.com). Finally a way to upload animations without a Windows computer, and designing animations using any GIF-outputting software of your choice!

This software was designed without consent from Infinite Reach, to move forward when the promised open-sourcing of their OEM software never materialized. IRSC, if you are reading this, do I have questions for you! Anyone else using this, I would love some feedback of your success or problems - and be aware that it's a sketchy piece of software since it was all designed from reverse engineering USB traffic with barely any specification.

__Please be aware that you are using this software at your own risk. There are possibilities of irreversibly damaging PEGS hardware from the use of this software.__

### Parts
1. `pypegs` module that handles conversion of animation data and communication with PEGS
1. script to upload animations from your computer into PEGS

Features
--------
* One-line upload script supports GIF animations (and PEGS designer .txt) files as input
* Heavily error-checking PEGS upload library
* Fully automatic serial port detection on POSIX systems
* Works on Mac OS X, and probably any other platform supporting Python and required libraries

upload.py usage
---------------
```
upload.py [-h] [-p PORT] [-f FPS] [--invert] [--test] slot file

Upload animations to PEGS party shades

positional arguments:
  slot                  Animation slot (1-8) to upload to
  file                  Input file (24x7 or 30x7 .gif, or glasses designer
                        .txt)

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Use the serial port PORT instead of auto-connect
  -f FPS, --framerate FPS
                        Framerate in frames per second. Overrides any value
                        present in input file.
  --invert              Swap light/dark in animation
  --test                Run entire program through a dummy terminal instead of
                        hardware PEGS
```

Requirements
------------
* [Future Technology Devices International drivers](http://www.ftdichip.com/FTDrivers.htm) (comes __pre-installed__ on Mac OSX 10.9 or later)
* External Python modules:
    * `PIL` (Python Imaging Library)
    * `bitstring`
    * `pyserial`
* PEGS shades B-)

Compatibility
-------------
Designed for and tested with PEGS party shades with firmware version 1.0.

This is third party hobbyist software created by reverse engineering. No guarantee is made about its accuracy, quality or feature-coverage. __There are possibilities of irreversibly damaging PEGS hardware from the use of this software. Use at your own risk.__ See license file for full disclaimer.

License
-------
PyPegs project copyright © 2015 Arvid Rudling.

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

All trademarks are the property of their respective owners.

The software is developed without any affiliation to Infinite Reach.
