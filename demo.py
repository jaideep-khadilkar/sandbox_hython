'''
Created on 24-Aug-2018

@author: Jaideep Khadilkar
'''
import sys
sys.path.append('/opt/houdini/houdini/python2.7libs')
import hou
import time

def create_box_subnet():
    obj = hou.node('/obj')
    box_geo = obj.createNode('geo','box_geo',run_init_scripts=False)
    
    box1 = box_geo.createNode('box','box1')
    box1.parm('scale').set(0.8)
    
    box2 = box_geo.createNode('box','box2')
    box2.parmTuple('size').set((0.5,0.5,0.5))
    
    copy = box_geo.createNode('copytopoints','copy')
    copy.parm('transform').set(False)
    copy.setInput(0,box2)
    copy.setInput(1,box1)
    
    python_code = """
node = hou.pwd()
geo = node.geometry()
vol = geo.createVolume(100,100,100,geo.boundingBox())
vol.setAllVoxels([1]*1000000)
    """
    python = box_geo.createNode('python','python')
    python.parm('python').set(python_code)
    python.setInput(0,copy)
    
    xform = box_geo.createNode('xform','xform')
    xform_r = xform.parmTuple('r')
    keyframe = hou.Keyframe()
    keyframe.setExpression('$FF',hou.exprLanguage.Hscript)
    xform_r[0].setKeyframe(keyframe)
    xform_r[1].setKeyframe(keyframe)
    xform_r[2].setKeyframe(keyframe)    
    xform.setInput(0,python)
    
    out = box_geo.createNode('null','OUT')
    out.setInput(0,xform)
    out.setDisplayFlag(True)
    out.setRenderFlag(True)
    
    box_subnet = box_geo.collapseIntoSubnet((box1,box2,copy,python,xform,out)
                                            ,subnet_name='box_subnet')
    box_subnet.layoutChildren()
    return box_subnet
    
def create_hda(subnet,hda_name):
    tmp = subnet.createDigitalAsset(name=hda_name)
    parent = tmp.parent()
    tmp.destroy()
    return parent.createNode(hda_name,hda_name)
    
def create_cam():
    obj = hou.node('/obj')
    cam = obj.createNode('cam','camera')
    cur_desktop = hou.ui.curDesktop()
    scene_viewer = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
    persp = scene_viewer.findViewport('persp1')
    persp.home()
    persp.saveViewToCamera(cam)
    time.sleep(0.1)
    persp.setCamera(cam)
    
def run():
    hou.hipFile.clear(suppress_save_prompt=False)
    box_subnet = create_box_subnet()
    demo_box = create_hda(box_subnet,'demo_box')
    create_cam()
    hou.node('/obj').layoutChildren()
    
    hou.playbar.setRealTime(True)