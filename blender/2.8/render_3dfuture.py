import sys
sys.path.append('D:\\tools\\RenderingScript\\blender\\2.8') # your path to “BlenderToolbox/cycles”
from include import *
import os
cwd = os.getcwd()

'''
Follow the instructions in "tutorial.py" if you want to adjust the model
'''

outputPath = 'D:\\tools\\RenderingScript\\blender\\2.8\\results' # make it abs path for windows

## initialize blender
imgRes_x = 500 # recommend > 2000 (UI: Scene > Output > Resolution X)
imgRes_y = 500 # recommend > 2000 (UI: Scene > Output > Resolution Y)
numSamples = 50 # recommend > 200 for paper images (UI: Scene > Render > Sampling > Render)
exposure = 1.5 # exposure of the entire image (UI: Scene > Render > Film > Exposure)
blenderInit(imgRes_x, imgRes_y, numSamples, exposure)

## read mesh (choose either readPLY or readOBJ)
meshPath = '../../meshes/normalized_model.obj'
location = (-0.4, -0.4, 0.8) # (UI: click mesh > Transform > Location)
rotation = (90, 0, 135) # (UI: click mesh > Transform > Rotation)
scale = (0.6,0.6,0.6) # (UI: click mesh > Transform > Scale)
# mesh = readPLY(meshPath, location, rotation, scale)
mesh = readOBJ(meshPath, location, rotation, scale) 

## set shading (choose one of them)
bpy.ops.object.shade_smooth() # Option1: Gouraud shading
# bpy.ops.object.shade_flat() # Option2: Flat shading
# edgeNormals(mesh, angle = 10) # Option3: Edge normal shading

## subdivision 
## Warning: may cause visual artifacts for 3D-FUTURE!
# subdivision(mesh, level = 2)

###########################################
## Set your material here (see other demo scripts)

# colorObj(RGBA, H, S, V, Bright, Contrast)
# For single color
RGBA = (144.0/255, 210.0/255, 236.0/255, 1)
meshColor = colorObj(RGBA, 0.5, 1.0, 1.0, 0.0, 2.0)
setMat_singleColor(mesh, meshColor, AOStrength = 0.5)

# For texture image
# useless = (0,0,0,1)
# meshColor = colorObj(useless, 0.5, 1.0, 1.0, 0.0, 0.0)
# texturePath = '../../meshes/texture.png' 
# # using relative path gives us weired bug...
# setMat_texture(mesh, texturePath, meshColor)

## End material
###########################################

## set invisible plane (shadow catcher)
invisibleGround(shadowBrightness=0.8)

## set camera (recommend to change mesh instead of camera, unless you want to adjust the Elevation)
camLocation = (2,2,2)
lookAtLocation = (0,0,0.5)
focalLength = 45 # (UI: click camera > Object Data > Focal Length)
cam = setCamera(camLocation, lookAtLocation, focalLength)

## set light
## Option1: Three Point Light System 
# setLight_threePoints(radius=4, height=10, intensity=1700, softness=6, keyLoc='left')
## Option2: simple sun light
lightAngle = (-15,-34,-155) 
strength = 2
shadowSoftness = 0.1
sun = setLight_sun(lightAngle, strength, shadowSoftness)

## set ambient light
setLight_ambient(color=(0.1,0.1,0.1,1)) # (UI: Scene > World > Surface > Color)

## set gray shadow to completely white with a threshold (optional)
alphaThreshold = 0.05
shadowThreshold(alphaThreshold, interpolationMode = 'CARDINAL')

## save blender file so that you can adjust parameters in the UI
bpy.ops.wm.save_mainfile(filepath='./test.blend')

## save rendering
renderImage(outputPath, cam)