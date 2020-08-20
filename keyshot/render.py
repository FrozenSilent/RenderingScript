# -*- coding: cp936 -*-

import os,sys,re
def cleanExt(ext):
    while ext.startswith("."):
        ext = ext[1:]
    return ext
def main():
    pt = lux.getCameraLookAt()
    cameraDistance = lux.getCameraDistance()
    cameraSpherical = lux.getSphericalCamera()
    values = [("folder", lux.DIALOG_FOLDER, "Folder to import from:", "./recon_chair/"),
              ("output", lux.DIALOG_FOLDER, "Folder to outut:", "./recon_chair/"),
              ("iext", lux.DIALOG_TEXT, "Input file format to read:", "obj"),
              ("oext", lux.DIALOG_TEXT, "Output image format:", "png"),
              # ("alpha", lux.DIALOG_INTEGER, "alpha channel:", 1),
              ("width", lux.DIALOG_INTEGER, "Output width:", 1920),
              ("height", lux.DIALOG_INTEGER, "Output height:", 1080),
              ("time", lux.DIALOG_INTEGER, "render time second:", 10),
              ("num", lux.DIALOG_INTEGER, "number of image:", 1),
              ("dis", lux.DIALOG_DOUBLE, "distance:", cameraDistance),
              ("azimuth", lux.DIALOG_DOUBLE, "Camera Spherical azimuth:", cameraSpherical[0]),
              ("incl", lux.DIALOG_DOUBLE, "Camera Spherical incl:", cameraSpherical[1]),
              ("twist", lux.DIALOG_DOUBLE, "Camera Spherical twist:", cameraSpherical[2]),
              ("light_rot", lux.DIALOG_DOUBLE, "light_rotation:", 0.),
              ("cemera_lookat_x", lux.DIALOG_DOUBLE, "cemera_focus:", pt[0]),
              ("cemera_lookat_y", lux.DIALOG_DOUBLE, "cemera_focus:", pt[1]),
              ("cemera_lookat_z", lux.DIALOG_DOUBLE, "cemera_focus:", pt[2])
              ]

    opts = lux.getInputDialog(title = "Render",
                              desc = "Render model",
                              values = values)



    if not opts: 
        return

    if len(opts["folder"]) == 0:
        raise Exception("Folder cannot be empty!")
    fld = opts["folder"]
    if len(opts["iext"]) == 0:
        raise Exception("Input extension cannot be empty!")
    iext = cleanExt(opts["iext"])
    reFiles = re.compile(".*{}".format(iext))
    found = False
    for f in os.listdir(fld):
        if reFiles.match(f):
            found = True
            break
    if not found:
        raise Exception("Could not find any input files matching the extension \"{}\" in \"{}\"!"
                        .format(iext, fld))

    if len(opts["oext"]) == 0:
        raise Exception("Output extension cannot be empty!")
    oext = cleanExt(opts["oext"])

    width = opts["width"]
    height = opts["height"]
    time = opts["time"]
    # alpha = opts['alpha']
    num = opts["num"]
    output_path = opts['output']
    dis = opts["dis"]
    azimuth = opts['azimuth']
    incl = opts['incl']
    twist = opts['twist']
    light_rot = opts['light_rot']
    cemera_lookat_x = opts['cemera_lookat_x']
    cemera_lookat_y = opts['cemera_lookat_y']
    cemera_lookat_z = opts['cemera_lookat_z']
    idx = 0
    env = lux.getActiveEnvironment()
    env.setBackgroundColor((255,255,255))
    env.setRotation(light_rot)
    opts = lux.getRenderOptions()
    opts.setMaxTimeRendering(time)
    # if alpha:
    #     opts.setOutputAlphaChannel()

    for f in [f for f in os.listdir(fld) if f.endswith(iext)]:
    # dirs = os.listdir(fld)
    # dirs_obj = [objs for objs in dirs if objs.endswith(iext)]
    # dirs_obj.sort(key = lambda x: int(x[:-4]))
    # for f in dirs_obj:
        path = fld + '/' + f
        opp = lux.getImportOptions()
        # opp['retain_materials']=True
        opp['snap_to_ground'] = True
        opp['center_geometry'] = False
        opp['separate_materials']=True
        opp['separate_parts'] = True
        opp['up_vector'] = 1
        opp['adjust_camera_look_at'] = True
        lux.importFile(path, showOpts = False,opts = opp)
        root = lux.getSceneTree()
        obj=root.find(name = f[:-4])[0]
        lux.setSphericalCamera(azimuth,incl,twist)
        lux.setCameraDistance(dis)
        lux.setCameraLookAt(pt=(cemera_lookat_x,cemera_lookat_y,cemera_lookat_z))
        
        

        lux.renderImage(output_path+"/"+f[:-4]+'_'+str(0)+'.png', width = width, height = height, opts = opts)
        for i in range(1,num+1):
            mat = luxmath.Matrix().makeIdentity()
            mat = mat.rotateAroundAxis(luxmath.Vector((0, 1, 0)), 360/num)
            obj.applyTransform(mat)
            lux.renderImage(output_path+"/"+f[:-4]+'_'+str(i)+'.png', width = width, height = height, opts = opts)
        obj.hide()
main()
