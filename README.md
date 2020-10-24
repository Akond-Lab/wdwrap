
A Wilson-Devinney Code wrapper
==============================

This Project is in early stage, please do not submit issues.
If you are interesting in using and/or contributing please contact me.

Qt GUI entry point:
```
    wdwrap/qtgui/wd.py
```


[1] ftp://ftp.astro.ufl.edu/pub/wilson


## Installation
#### 0. Wilson-Devinney Code
You need Wilson-Devinney Code installed (download from here: ftp://ftp.astro.ufl.edu/pub/wilson).
The framework is ment to be compatible with multiple version of WD code, but currently only 2015 version
is supported.

**You need to have LC executable, named or symlinked as `lc2015` in your path.**

  
#### 1. Python version
`wdwrap` requires Python 3.8. If your python 3 is not the default one, you may change `python` to `python3` in
invocations below.  
#### 2. Clone the repository
Below, we suppose that the installation directory is `~/src/wdwrap`, change `~/src/` to your home directory for 
projects or endure that `~/src/` exists.
```
    cd ~/src
    git clone https://github.com/Akond-Lab/wdwrap.git
    cd wdwrap
```
#### 3. Make virtual environment
Optional, but project uses Qt5 among other heavy packages, so it's good to isolate it from your other projects
```
python -m venv venv
source venv/bin/activate
``` 
#### 4. Install dependencies and project
```
pip install -r requirements.txt
pip install -e .
```

## Updating
```
cd ~/src/wdwrap
git pull
pip install -r requirements.txt
```

## Configuration
The package reads configuration files in following order, overwriting duplicated settings:
*   `<wdw-install-dir>/wdwrap/config/wdwrap.ini`
*   `/etc/wdwrap/config/wdwrap.ini`
*   `<wdw-install-dir>/wdwrap.ini`
*   `~/.config/wdwrap/wdwrap.ini`

After install only first one exists. In order to have own configuration file,
one may copy the first one to one of the later destinations, then edit it. E.g.:
```
mkdir -p ~/.config/wdwrap
cp ~/src/wdwrap/wdwrap/config/wdwrap.ini  ~/.config/wdwrap
vi  ~/.config/wdwrap/wdwrap.ini
``` 
The only important option to be changed is the pathname to the WD `lc` executable.
Default one is `lc2015`, overwrite it in your config file.

Note that current version of WDW is designed to work with 2015 version of `lc`,
with limited support for reading/writing lc.in files of 2007 version. 


## Running GUI
```
cd ~/src/wdwrap 
source venv/bin/activate
python wdwrap/qtgui/wd.py
```

