# AUTHOR yyj
# VERSION 0.0.0
# Write description of the script here, and put your code after these lines.


# -*- coding: cp936 -*-

import os,sys,re
def cleanExt(ext):
    while ext.startswith("."):
        ext = ext[1:]
    return ext
def main():

    env = lux.getActiveEnvironment()
    pt = lux.getCameraLookAt()
    d= lux.getCameraDistance()
    angle = lux.getSphericalCamera()
    r = env.getRotation()
    
    values = [("output", lux.DIALOG_FOLDER, "Folder to outut:", "./render_results"),
              ("name", lux.DIALOG_TEXT, "render obj name:", "model_normalized"),
              # ("model_num", lux.DIALOG_INTEGER, "number of models:", 50),
              ("width", lux.DIALOG_INTEGER, "Output width:", 1920),
              ("height", lux.DIALOG_INTEGER, "Output height:", 1080),
              ("time", lux.DIALOG_INTEGER, "render time second:", 10),
              ("num", lux.DIALOG_INTEGER, "number of image:", 0),
              ("dis", lux.DIALOG_DOUBLE, "distance:", d),
              ("azimuth", lux.DIALOG_DOUBLE, "Camera Spherical azimuth:", angle[0]),
              ("incl", lux.DIALOG_DOUBLE, "Camera Spherical incl:", angle[1]),
              ("twist", lux.DIALOG_DOUBLE, "Camera Spherical twist:", angle[2]),
              ("light_rot", lux.DIALOG_DOUBLE, "light_rotation:", r),
              ("cemera_lookat_x", lux.DIALOG_DOUBLE, "cemera_focus:", pt[0]),
              ("cemera_lookat_y", lux.DIALOG_DOUBLE, "cemera_focus:", pt[1]),
              ("cemera_lookat_z", lux.DIALOG_DOUBLE, "cemera_focus:", pt[2])
              ]

    opts = lux.getInputDialog(title = "Render",
                              desc = "Render model",
                              values = values)



    if not opts: 
        return

    oext = 'png'

    width = opts["width"]
    height = opts["height"]
    time = opts["time"]
    num = opts["num"]
    output_path = opts['output']
    dis = opts["dis"]
    azimuth = opts['azimuth']
    incl = opts['incl']
    twist = opts['twist']
    light_rot = opts['light_rot']
    name = opts['name']
    # model_num = opts['model_num']
    cemera_lookat_x = opts['cemera_lookat_x']
    cemera_lookat_y = opts['cemera_lookat_y']
    cemera_lookat_z = opts['cemera_lookat_z']
    
    idx = 0
    
    # env.setBackgroundColor((255,255,255))
    env.setRotation(light_rot)
    opts = lux.getRenderOptions()
    opts.setMaxTimeRendering(time)
    root = lux.getSceneTree()
    for obj in root.find(""):
      # obj_name = name + '_' + str(idx)
      # obj=root.find(name = obj_name)[0]
      if obj.getKind() != 5:
        continue
      lux.setSphericalCamera(azimuth,incl,twist)
      lux.setCameraDistance(dis)
      lux.setCameraLookAt(pt=(cemera_lookat_x,cemera_lookat_y,cemera_lookat_z))

      obj.show()
      output_name = obj.getName()
      
      lux.renderImage(output_path+"/"+output_name+'.png', width = width, height = height, opts = opts)
      for i in range(1,num+1):
          mat = luxmath.Matrix().makeIdentity()
          mat = mat.rotateAroundAxis(luxmath.Vector((0, 1, 0)), 360/num)
          obj.applyTransform(mat)
          lux.renderImage(output_path+"/"+output_name+'_'+str(i)+'.png', width = width, height = height, opts = opts)
      obj.hide()
main()
