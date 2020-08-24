#!/usr/bin/env python3

import sys
sys.path.append('D:\\tools\\RenderingScript\\blender\\2.7')
import _init_paths
import time
import os
import contextlib
from math import radians
import numpy as np
# from PIL import Image
# from tempfile import TemporaryFile
from utils import stdout_redirected
from config import cfg
import bpy


def voxel2mesh(voxels):
    cube_verts = [[0, 0, 0],
                  [0, 0, 1],
                  [0, 1, 0],
                  [0, 1, 1],
                  [1, 0, 0],
                  [1, 0, 1],
                  [1, 1, 0],
                  [1, 1, 1]]  # 8 points

    cube_faces = [[0, 1, 2],
                  [1, 3, 2],
                  [2, 3, 6],
                  [3, 7, 6],
                  [0, 2, 6],
                  [0, 6, 4],
                  [0, 5, 1],
                  [0, 4, 5],
                  [6, 7, 5],
                  [6, 5, 4],
                  [1, 7, 3],
                  [1, 5, 7]]  # 12 face

    cube_verts = np.array(cube_verts)
    cube_faces = np.array(cube_faces) + 1

    l, m, n = voxels.shape

    scale = 0.01
    cube_dist_scale = 1.1
    verts = []
    faces = []
    curr_vert = 0
    for i in range(l):
        for j in range(m):
            for k in range(n):
                # If there is a non-empty voxel
                if voxels[i, j, k] > 0:
                    verts.extend(scale * (cube_verts + cube_dist_scale * np.array([[i, j, k]])))
                    faces.extend(cube_faces + curr_vert)
                    curr_vert += len(cube_verts)

    return np.array(verts), np.array(faces)


def write_obj(filename, verts, faces):
    """ write the verts and faces on file."""
    with open(filename, 'w') as f:
        # write vertices
        f.write('g\n# %d vertex\n' % len(verts))
        for vert in verts:
            f.write('v %f %f %f\n' % tuple(vert))

        # write faces
        f.write('# %d faces\n' % len(faces))
        for face in faces:
            f.write('f %d %d %d\n' % tuple(face))


class BaseRenderer:
    model_idx   = 0

    def __init__(self):
        # bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.context.scene.render.engine = 'CYCLES'
        for object in bpy.context.scene.objects:
            if object.name in ['Camera']:
                object.select = False
            else:
                object.select = False
                object.cycles_visibility.shadow = False
        # bpy.context.scene.cycles.device = 'GPU'
        # bpy.context.user_preferences.system.compute_device_type = 'CUDA'
        # bpy.context.user_preferences.system.compute_device = 'CUDA_1'

        # changing these values does affect the render.

        # remove the default cube
        bpy.ops.object.select_pattern(pattern="Cube")
        bpy.ops.object.delete()

        render_context = bpy.context.scene.render
        world  = bpy.context.scene.world
        camera = bpy.data.objects['Camera']
        light_1  = bpy.data.objects['Lamp']
        light_1.data.type = 'HEMI'

        # set the camera postion and orientation so that it is in
        # the front of the object
        camera.location       = (1, 0, 0)
        camera.rotation_mode  = 'ZXY'
        camera.rotation_euler = (0, radians(90), radians(90))

        # parent camera with a empty object at origin
        org_obj                = bpy.data.objects.new("RotCenter", None)
        org_obj.location       = (0, 0, 0)
        org_obj.rotation_euler = (0, 0, 0)
        bpy.context.scene.objects.link(org_obj)

        camera.parent = org_obj  # setup parenting

        # render setting
        render_context.resolution_percentage = 100
        world.horizon_color = (1, 1, 1)  # set background color to be white

        # set file name for storing rendering result
        self.result_fn = '%s/render_result_%d.png' % (RENDERING_PATH, os.getpid())
        bpy.context.scene.render.filepath = self.result_fn

        self.render_context = render_context
        self.org_obj = org_obj
        self.camera = camera
        self.light = light_1
        self._set_lighting()

    def initialize(self, models_fn, viewport_size_x, viewport_size_y):
        self.models_fn = models_fn
        self.render_context.resolution_x = viewport_size_x
        self.render_context.resolution_y = viewport_size_y

    def _set_lighting(self):
        pass

    def setViewpoint(self, azimuth, altitude, yaw, distance_ratio, fov):
        self.org_obj.rotation_euler = (0, 0, 0)
        self.light.location = (distance_ratio *
                               (MAX_CAMERA_DIST + 2), 0, 0)
        self.camera.location = (distance_ratio *
                                MAX_CAMERA_DIST, 0, 0)
        self.org_obj.rotation_euler = (radians(-yaw),
                                       radians(-altitude),
                                       radians(-azimuth))

    def setTransparency(self, transparency):
        """ transparency is either 'SKY', 'TRANSPARENT'
        If set 'SKY', render background using sky color."""
        self.render_context.alpha_mode = transparency

    def selectModel(self):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="RotCenter")
        bpy.ops.object.select_pattern(pattern="Lamp*")
        bpy.ops.object.select_pattern(pattern="Camera")
        bpy.ops.object.select_all(action='INVERT')

    def printSelection(self):
        print(bpy.context.selected_objects)

    def clearModel(self):
        self.selectModel()
        bpy.ops.object.delete()

        # The meshes still present after delete
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)
        for item in bpy.data.materials:
            bpy.data.materials.remove(item)

    def setModelIndex(self, model_idx):
        self.model_idx = model_idx

    def loadModel(self, file_path=None):
        if file_path is None:
            file_path = self.models_fn[self.model_idx]
            print(file_path.encode())

        if file_path.endswith('obj'):
            bpy.ops.import_scene.obj(filepath=file_path)
        elif file_path.endswith('3ds'):
            bpy.ops.import_scene.autodesk_3ds(filepath=file_path)
        elif file_path.endswith('dae'):
            # Must install OpenCollada. Please read README.md
            bpy.ops.wm.collada_import(filepath=file_path)
        else:
            raise Exception("Loading failed: %s Model loading for type %s not Implemented" %
                            (file_path, file_path[-4:]))

        # load texture 
        bpy.data.materials.new('UVTexture')
        bpy.data.materials['UVTexture'].use_nodes = True
        texture_tree = bpy.data.materials['UVTexture'].node_tree
        texture_links = texture_tree.links
        texture_node = texture_tree.nodes.new("ShaderNodeTexImage")
        texture_file = file_path.replace('normalized_model.obj', 'texture.png')
        texture_node.image = bpy.data.images.load(texture_file)
        texture_links.new(texture_node.outputs[0], texture_tree.nodes['Diffuse BSDF'].inputs[0])
        bpy.data.scenes['Scene'].render.layers['RenderLayer'].material_override = bpy.data.materials['UVTexture']

    def render(self, load_model=True, clear_model=True, resize_ratio=None,
               return_image=True, image_path = ''):
        """ Render the object """
        if load_model:
            self.loadModel()

        # resize object
        self.selectModel()
        if resize_ratio:
            bpy.ops.transform.resize(value=resize_ratio)

        self.result_fn = image_path
        bpy.context.scene.render.filepath = image_path
        bpy.ops.render.render(write_still=True)  # save straight to file

        if resize_ratio:
            bpy.ops.transform.resize(value=(1/resize_ratio[0],
                1/resize_ratio[1], 1/resize_ratio[2]))

        if clear_model:
            self.clearModel()

        # if return_image:
        #     im = np.array(Image.open(self.result_fn))  # read the image

            # Last channel is the alpha channel (transparency)
            return im[:, :, :3], im[:, :, 3]


class ShapeNetRenderer(BaseRenderer):

    def __init__(self):
        super().__init__()
        self.setTransparency('TRANSPARENT')

    def _set_lighting(self):
        # Create new lamp datablock
        light_data = bpy.data.lamps.new(name="New Lamp", type='HEMI')

        # Create new object with our lamp datablock
        light_2 = bpy.data.objects.new(name="New Lamp", object_data=light_data)
        bpy.context.scene.objects.link(light_2)

        # put the light behind the camera. Reduce specular lighting
        self.light.location       = (0, -2, 2)
        self.light.rotation_mode  = 'ZXY'
        self.light.rotation_euler = (radians(45), 0, radians(90))
        self.light.data.energy = 0.7

        light_2.location       = (0, 2, 2)
        light_2.rotation_mode  = 'ZXY'
        light_2.rotation_euler = (-radians(45), 0, radians(90))
        light_2.data.energy = 0.7


class VoxelRenderer(BaseRenderer):

    def __init__(self):
        super().__init__()
        self.setTransparency('SKY')

    def _set_lighting(self):
        self.light.location       = (0, 3, 3)
        self.light.rotation_mode  = 'ZXY'
        self.light.rotation_euler = (-radians(45), 0, radians(90))
        self.light.data.energy = 0.7

        # Create new lamp datablock
        light_data = bpy.data.lamps.new(name="New Lamp", type='HEMI')

        # Create new object with our lamp datablock
        light_2 = bpy.data.objects.new(name="New Lamp", object_data=light_data)
        bpy.context.scene.objects.link(light_2)

        light_2.location       = (4, 1, 6)
        light_2.rotation_mode  = 'XYZ'
        light_2.rotation_euler = (radians(37), radians(3), radians(106))
        light_2.data.energy = 0.7

    def render_voxel(self, pred, thresh=0.4,
                     image_path=''):
        # Cleanup the scene
        self.clearModel()
        out_f = 'tmp.obj'
        occupancy = pred > thresh
        vertices, faces = voxel2mesh(occupancy)
        with contextlib.suppress(IOError):
            os.remove(out_f)
        write_obj(out_f, vertices, faces)

        # Load the obj
        bpy.ops.import_scene.obj(filepath=out_f)
        bpy.context.scene.render.filepath = image_path
        bpy.ops.render.render(write_still=True)  # save straight to file

        # im = np.array(Image.open(image_path))  # read the image

        # Last channel is the alpha channel (transparency)
        return im[:, :, :3], im[:, :, 3]


def main():
    """Test function"""
    # Modify the following file to visualize the model
    dn = 'D:\\3D-FUTURE-model'
    # model_id = [line.strip('\n') for line in open(dn + 'models.txt')]
    model_id = os.listdir(dn)
    file_paths = [os.path.join(dn, line, 'normalized_model.obj') for line in model_id]
    sum_time = 0
    renderer = ShapeNetRenderer()
    renderer.initialize(file_paths, 256, 256)
    num_view = 24
    for i, curr_model_id in enumerate(model_id):
        # if os.path.exists(os.path.join(dn, curr_model_id, 'image', '23.png')):
        #     continue
        if os.path.exists(file_paths[i]):
            start = time.time()
            # image_path = '%s/%s.png' % ('/tmp', curr_model_id[:-4])
            if not os.path.exists(os.path.join(dn, curr_model_id, 'image')):
                os.mkdir(os.path.join(dn, curr_model_id, 'image'))
            savefile = open(os.path.join(dn, curr_model_id, 'image', 'rendering_metadata.txt'), 'w')
            namefile = open(os.path.join(dn, curr_model_id, 'image', 'renderings.txt'), 'w')
            for j in range(num_view):
                az, el, depth_ratio = list(
                    *([360, 5, 0.3] * np.random.rand(1, 3) + [0, 25, 0.65]))
                image_path = os.path.join(dn, curr_model_id, 'image', '%02d.png'%(j))

                renderer.setModelIndex(i)
                # renderer.setViewpoint(30, 30, 0, 0.7, 25)
                renderer.setViewpoint(az, el, 0, depth_ratio, 25)
                savefile.write('%f %f 0 %f 25\n' % (az, el, depth_ratio))
                namefile.write('%02d.png\n'%(j))

                # with TemporaryFile() as f, stdout_redirected(f):
                # rendering, alpha = renderer.render(load_model=True,
                #     clear_model=True, image_path=image_path)
                renderer.render(load_model=True, clear_model=True, image_path=image_path, return_image=False)

                print('id: %d Saved at %s' % (i, image_path))

            savefile.close()
            namefile.close()

            end = time.time()
            sum_time += end - start
            if i % 10 == 0:
                print(sum_time/(10))
                sum_time = 0


if __name__ == "__main__":
    main()
