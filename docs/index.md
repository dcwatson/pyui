# Welcome to PyUI

PyUI is a declarative, cross-platform GUI framework modeled after SwiftUI. It uses the excellent
[PySDL2](https://github.com/marcusva/py-sdl2) ctypes wrapper around the also excellent [SDL2](https://www.libsdl.org)
library.


## Getting Started

The quickest way to get started on Mac or Windows is to clone this repository, and with an activated virtualenv:

```python
pip install -r requirements.txt
python -m examples.demo
```

The same applies to Linux, but you will need to make sure you use your package manager of choice to install all the
SDL2 libraries.


## Diving In

PyUI includes a [TodoMVC](http://todomvc.com) example application
([source](https://github.com/dcwatson/pyui/blob/master/examples/todo.py)). Tutorial forthcoming.

![PyUI TodoMVC](images/pyui-todomvc.png)
