# Blender rendering (2.79)
The code produces the rendering results that are similar with the rendering dataset of ShapeNet offered by [3D-R2N2](https://github.com/chrischoy/3D-R2N2). The original rendering code from 3D-R2N2 have some missing variables and don't save those camera parameters, and I have fixed those bugs and output those parameters.

## Dependencies
- [Blender 2.79](https://download.blender.org/release/Blender2.79/)
- numpy
- easydict

## Blender python
Blender has its own built-in python, so you may need install python packages for blender python. Some tutorials are here:

- [How to install Pip for Blender's bundled Python?](https://blender.stackexchange.com/questions/56011/how-to-install-pip-for-blenders-bundled-python)
- [Using 3rd party Python modules](https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules)
- [How to install Python modules in Blender using pip](http://www.codeplastic.com/2019/03/12/how-to-install-python-modules-in-blender/)

## Usage
1. Modify `MAX_CAMERA_DIST` to a suitable number in `config.py`.
2. Modify `dn` to your data dir in `blender_renderer.py`. Note that the model should be named as "normalized_model.obj" (if not you can change the code) and put in the folder named by model id.
3. Run `blender --backgound --python blender_renderer.py` or `blender --backgound --python blender_renderer_texture.py` for rendering with texture. The texture image should be placed in the same directory with the model and named as "texture.png".

## Others
- The code is borrowed from [3D-R2N2](https://github.com/chrischoy/3D-R2N2). You should cite their paper if you use the code.
- The rendering image and txt file produced by this code can be further used in some single view reconstruction methods directly. Such as [Pixel2Mesh](https://github.com/nywang16/Pixel2Mesh), [Occupancy Network](https://github.com/autonomousvision/occupancy_networks), [DISN](https://github.com/Xharlie/DISN)