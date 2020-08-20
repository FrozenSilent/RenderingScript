# Blender rendering
The codes produce the rendering results that are similar with the rendering dataset of ShapeNet offered by [3D-R2N2](https://github.com/chrischoy/3D-R2N2). The original rendering codes from 3D-R2N2 have some missing variables and don't save those camera parameters.

## Usage
1. Modify `MAX_CAMERA_DIST` to a suitable number in `config.py`.
2. Modify `dn` to your data dir. Note that the model should be named as "normalized_model.obj" (if not you can change the code) and put in the folder named by model id.
3. Run `blender --backgound --python blender_renderer.py`.