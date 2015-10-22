pyPEGS party shades Python utilities
====================================

Open source, platform agnostic utilites for the flashy PEGS LED sunglasses made by Infinite Reach (www.infinitereachsc.com). Finally a way to upload animations without a Windows computer, and designing animations using any GIF-outputting software of your choice!

This software was designed without consent from Infinite Reach, to move forward when the promised open-sourcing of their OEM software never materialized. IRSC, if you are reading this, do I have questions for you! Anyone else using this, I would love some feedback of your success or problems - and be aware that it's a sketchy piece of software since it was all designed from reverse engineering USB traffic with barely any specification.

__Please be aware that you are using this software at your own risk. There are possibilities of irreversibly damaging PEGS hardware from the use of this software.__

### Parts
1. `pypegs` module that handles conversion of animation data and communication with PEGS
1. scripts to upload animations from your computer into PEGS

Requirements
------------
* [Future Technology Devices International drivers](http://www.ftdichip.com/FTDrivers.htm) (comes __pre-installed__ on Mac OSX 10.9 or later)
* External Python modules:
`PIL` (Python Imaging Library)
`bitstring`
`pyserial`
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
