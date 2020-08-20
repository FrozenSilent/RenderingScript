# Blender rendering (2.79)
The code produces the rendering results that are similar with the rendering dataset of ShapeNet offered by [3D-R2N2](https://github.com/chrischoy/3D-R2N2). The original rendering code from 3D-R2N2 have some missing variables and don't save those camera parameters, and I have fixed those bugs and output those parameters.

## Usage
1. Modify `MAX_CAMERA_DIST` to a suitable number in `config.py`.
2. Modify `dn` to your data dir in `blender_renderer.py`. Note that the model should be named as "normalized_model.obj" (if not you can change the code) and put in the folder named by model id.
3. Run `blender --backgound --python blender_renderer.py`.

## Others
- The code is borrowed from [3D-R2N2](https://github.com/chrischoy/3D-R2N2). You should cite their paper if you use the code.
- The rendering image and txt file produced by this code can be further used in some single view reconstruction methods directly. Such as [Pixel2Mesh](https://github.com/nywang16/Pixel2Mesh), [Occupancy Network](https://github.com/autonomousvision/occupancy_networks), [DISN](https://github.com/Xharlie/DISN)