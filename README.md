# Controllers for iDynamic

Implementations of controlles to be used with LACI's virtual control laboratory 'iDynamic', available on https://dev-mind.blog/apps/control_systems/iDynamic/index.html

First, you should install the following libraries to run the scripts:

* pip install --upgrade pip wheel setuptools
* pip install websockets
* pip install numpy
* pip install matplotlib
* pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
* pip install kivy.deps.gstreamer
* pip install kivy.deps.angle
* pip install pandas

Included controllers:

* PID
* Linear ADRC

Inside the controllers' folder, there's two files you can execute: the 'main.py' file runs the simulation itself, and 'plot\_evaluate.py' calculates performance indexes and plot the simulation data. The perfomance indexes used are:

* IAE
* ISE
* ITAE
* Goodhart Index
* RBEMCE
* RBMSEMCE
* Variability of output signal
