"""
Created on 24-Aug-2018

@author: Jaideep Khadilkar
"""
import hou
import time
import textwrap
import logging

import demobox

logging.basicConfig()
logger = logging.getLogger('Hython_Demo')
logger.setLevel(logging.INFO)


def create_cam():
    obj = hou.node('/obj')
    cam = obj.createNode('cam', 'cam1')
    cur_desktop = hou.ui.curDesktop()
    scene_viewer = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
    persp = scene_viewer.findViewport('persp1')
    persp.home()
    persp.saveViewToCamera(cam)
    time.sleep(0.1)
    persp.setCamera(cam)
    logger.info('Created camera')


def create_mantra():
    out = hou.node('/out')
    mantra = out.createNode('ifd', 'mantra1')
    mantra.parm('vm_picture').set('$TEMP/box.jpeg')
    mantra.parm('execute').pressButton()
    logger.info('Created mantra node')


def create_cop():
    cop = hou.node('/obj').createNode('cop2net')
    file_node = cop.createNode('file')
    file_node.parm('filename1').set('$TEMP/box.jpeg')
    logger.info('Created copnet')


def scene_event_callback(event_type):
    if event_type == hou.hipFileEventType.AfterClear:
        message = """
                  This is a hython demo by Jaideep Khadilkar.
                  https://github.com/jaideep-khadilkar/sandbox_hython
                  """
        response = hou.ui.displayMessage(textwrap.dedent(message), buttons=('OK', 'Source Code'))
        if response:
            import webbrowser
            webbrowser.open('https://github.com/jaideep-khadilkar/sandbox_hython')


def run():
    hou.hipFile.addEventCallback(scene_event_callback)
    hou.hipFile.clear(suppress_save_prompt=False)
    with hou.undos.group("Demo"):
        hou.setUpdateMode(hou.updateMode.Manual)
        demobox.DemoBox()
        create_cam()
        hou.setUpdateMode(hou.updateMode.AutoUpdate)
        hou.playbar.setRealTime(True)
        hou.setFrame(25)
        create_mantra()
        create_cop()
        hou.node('/obj').layoutChildren()
    hou.hipFile.removeEventCallback(scene_event_callback)
    hou.hipFile.save(hou.hscriptExpandString('$TEMP') + '/demo.hip')
