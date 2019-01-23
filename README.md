# Spelling Test

## Overview

This **Python** program performs a spelling test. The words to be spelled are "spoken" and have to be typed in correctly in lower-case, with capitals and other punctuation only as required.

## Requirements

### Git

There is no binary installer for this (very!) simple program. You need to download the necessary files from GitHub. Since the easiest way to do this is with **Git** itself, installing the **Git** package is very useful.

* [Git Downloads](https://git-scm.com/downloads)

### Python 3

The program was written in Python v3 and is **not** compatible with Python v2.

### Libraries

The following python libraries must be installed:

* [gTTS](https://pypi.org/project/gTTS/)
* [jsonpath](https://pypi.org/project/jsonpath/)
* [pygame](https://pypi.org/project/Pygame/)

If in doubt, these can be installed with **pip**, for example:

~~~bash
pip3 install gTTS
~~~

### Gotchas

#### Linux installation of gTTS

At the time of writing there seems to be a problem with the installation of the gTTS library, acknowledged in [gTTS issue 158](https://github.com/pndurette/gTTS/issues/158#issuecomment-446411841) on GitHub. The work-around suggested in that thread worked for me, although I had to update the path to reflect my version of Python 3.5:

~~~bash
cd ~/.local/lib/python3.5/site-packages/
mv UNKNOWN-2.0.3.dist-info/ gTTS-2.0.3.dist-info/
pip install --user --force-reinstall --ignore-installed --no-binary :all: gTTS
~~~

## Download

This program is provided as a GitHub repo. It is expected that you will be able to download (clone) the necessary files using **git**. Use the instructions below to perform the necessary steps.

If you don't want to use **git** you must download the following files from this site and put them in a folder named, e.g. "spelling_test":

* dictionary.json
* main.py

### Linux

The following commands will create a folder called **Git** in your home directory on Linux when run from a terminal prompt:

~~~bash
cd ~
mkdir Git
cd Git
git clone https://github.com/cjj1977/spelling_test.git
~~~
