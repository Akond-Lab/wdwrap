
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
#### 1. Python version
`wdwrap` requires Python 3.8. If your python 3 is not the default one, you may change `python` to `python3` in
invocations below.  
#### 2. Clone the repository
```
    git clone git@github.com:Akond-Lab/wdwrap.git
    cd wdwrap
```
#### 3. Make virtual environment
Optional, but project uses Qt5 among other heavy packages, so it's good to isolate it from your other projects
```
python venv venv
source venv/bin/activate
``` 
#### 4. Install dependencies
```
pip install -r requirements.txt
```

## Updating
```
cd myrpojectsdir/wdwrap
git pull
pip install -r requirements.txt
```

## Running GUI
```
cd myrpojectsdir/wdwrap 
source venv/bin/activate
pyhon wdwrap/qtgui/wd.py
```

#### Server extension for jupiter GUI:
Jupyter GUI is under construction and not usable yet
```
    jupyter serverextension enable voila --sys-prefix
```