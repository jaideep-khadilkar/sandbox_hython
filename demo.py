"""
Created on 24-Aug-2018

@author: Jaideep Khadilkar
"""
import sys
import hou
import time
import textwrap


class DemoBox(object):
    def __init__(self):
        box_subnet = self.create_box_subnet()
        demo_box = self.create_hda(box_subnet, hda_name='demo_box')
        self.add_shading_component(demo_box)

    @staticmethod
    def create_box_subnet():
        obj = hou.node('/obj')
        box_geo = obj.createNode('geo', 'box_geo', run_init_scripts=False)

        box1 = box_geo.createNode('box', 'box1')
        box1.parm('scale').set(0.8)

        box2 = box_geo.createNode('box', 'box2')
        box2.parmTuple('size').set((0.5, 0.5, 0.5))

        copy = box_geo.createNode('copytopoints', 'copy')
        copy.parm('transform').set(False)
        copy.setInput(0, box2)
        copy.setInput(1, box1)

        python_code = """
                      node = hou.pwd()
                      geo = node.geometry()
                      vol = geo.createVolume(100,100,100,geo.boundingBox())
                      vol.setAllVoxels([10]*1000000)
                      """
        python = box_geo.createNode('python', 'python')
        python.parm('python').set(textwrap.dedent(python_code))
        python.setInput(0, copy)

        xform = box_geo.createNode('xform', 'xform')
        xform.setInput(0, python)
        xform.setDisplayFlag(True)
        xform.setRenderFlag(True)

        note = box_geo.createStickyNote('test_note')
        note.setText('This is a test note')

        box_subnet = box_geo.collapseIntoSubnet((box1, box2, copy, python, xform, note)
                                                , subnet_name='box_subnet')
        box_subnet.layoutChildren()
        #         box_subnet.node().setPosition(box1.position()+hou.Vector2((5,-2)))
        return box_subnet

    @staticmethod
    def create_hda(subnet, hda_name='default'):
        tmp = subnet.createDigitalAsset(name=hda_name, description=hda_name)
        parent = tmp.parent()
        tmp.destroy()

        hda_instance = parent.createNode(hda_name, hda_name)
        source_tuple = hda_instance.parmTuple('./xform/r')
        definition = hda_instance.type().definition()
        definition.addParmTuple(source_tuple.parmTemplate())
        target_tuple = hda_instance.parmTuple('r')

        hda_instance.allowEditingOfContents()
        source_tuple.set(target_tuple)
        definition.updateFromNode(hda_instance)

        keyframe = hou.Keyframe()
        keyframe.setExpression('$FF', hou.exprLanguage.Hscript)
        target_tuple[0].setKeyframe(keyframe)
        target_tuple[1].setKeyframe(keyframe)
        target_tuple[2].setKeyframe(keyframe)
        hda_instance.matchCurrentDefinition()
        return hda_instance

    @staticmethod
    def add_shading_component(hda_instance):
        hda_instance.allowEditingOfContents()
        display_node = hda_instance.displayNode()

        shopnet = hda_instance.createNode('shopnet', 'shopnet')
        plastic = shopnet.createNode('v_plastic')
        plastic.parmTuple('diff').set((1, 0, 0))
        volumecloud = shopnet.createNode('v_volumecloud')
        volumecloud.parmTuple('diff').set((0, 0, 1))
        shopnet.layoutChildren()

        group_poly = hda_instance.createNode('groupcreate', 'group_poly')
        group_poly.parm('groupname').set('group_poly')
        group_poly.parm('geotype').set('poly')
        group_poly.setInput(0, display_node)

        group_volume = hda_instance.createNode('groupcreate', 'group_volume')
        group_volume.parm('groupname').set('group_volume')
        group_volume.parm('geotype').set('volume')
        group_volume.setInput(0, group_poly)

        material = hda_instance.createNode('material', 'material')
        material.parm('num_materials').set(2)
        material.parm('group1').set(group_poly.name())
        material.parm('shop_materialpath1').set(material.relativePathTo(plastic))
        material.parm('group2').set(group_volume.name())
        material.parm('shop_materialpath2').set(material.relativePathTo(volumecloud))
        material.setInput(0, group_volume)

        out = hda_instance.createNode('null', 'OUT')
        out.setInput(0, material)
        out.setDisplayFlag(True)
        out.setRenderFlag(True)

        hda_instance.layoutChildren()
        definition = hda_instance.type().definition()
        definition.updateFromNode(hda_instance)
        hda_instance.matchCurrentDefinition()


def create_cam():
    obj = hou.node('/obj')
    cam = obj.createNode('cam', 'camera')
    cur_desktop = hou.ui.curDesktop()
    scene_viewer = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
    persp = scene_viewer.findViewport('persp1')
    persp.home()
    persp.saveViewToCamera(cam)
    time.sleep(0.1)
    persp.setCamera(cam)


def run():
    hou.hipFile.clear(suppress_save_prompt=False)
    hou.setUpdateMode(hou.updateMode.Manual)
    DemoBox()
    create_cam()
    hou.node('/obj').layoutChildren()
    hou.setUpdateMode(hou.updateMode.AutoUpdate)
    hou.playbar.setRealTime(True)
