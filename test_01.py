'''
Created on 24-Aug-2018

@author: user
'''
import sys
sys.path.append('/opt/houdini/houdini/python2.7libs')


import hou

def create_nodes():
    hou.hipFile.clear(suppress_save_prompt=False)
    obj = hou.node('/obj')
    box_geo = obj.createNode('geo','box_geo',run_init_scripts=False)
    box = box_geo.createNode('box','box')
    box.parmTuple('size').set((3,3,3))
    xform = box_geo.createNode('xform','xform')
    xform.setInput(0,box)
    box_geo.layoutChildren()
    xform.setDisplayFlag(True)
    xform.setRenderFlag(True)