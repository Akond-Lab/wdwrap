
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

## Running GUI
```
cd ~/src/wdwrap 
source venv/bin/activate
python wdwrap/qtgui/wd.py
```

#### Server extension for jupiter GUI:
Jupyter GUI is under construction and not usable yet
```
    jupyter serverextension enable voila --sys-prefix
```