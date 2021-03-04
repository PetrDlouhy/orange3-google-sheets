Orange3 Google sheets Add-on
===================================

Google sheets add-on for [Orange3](http://orange.biolab.si).
It adds Google sheets export widget.

Installation
------------

To install the add-on from source run

    pip install git+https://github.com/PetrDlouhy/orange3-google-sheets#egg=orange3-google-sheets

To register this add-on with Orange, but keep the code in the development directory (do not copy it to 
Python's site-packages directory), run

    pip install -e git+https://github.com/PetrDlouhy/orange3-google-sheets#egg=orange3-google-sheets

Documentation / widget help can be built by running

    make html htmlhelp

from the doc directory.

Usage
-----

After the installation, the widget from this add-on is registered with Orange. To run Orange from the terminal,
use

    orange-canvas

or

    python -m Orange.canvas

The new widget appears in the toolbox bar under the section Example.

![screenshot](https://github.com/biolab/orange3-example-addon/blob/master/screenshot.png)
