from __future__ import print_function

# Kivy Imports
# =============================================================================
try:
    # Python 2
    import Tkinter
except ImportError:
    # Python 3
    import tkinter

try:
    tkroot = Tkinter.Tk()
except:
    try:
        tkroot = tkinter.Tk()
    except:
        raise ImportError("TKinter can't be loaded")
    
res_width = tkroot.winfo_screenwidth()
res_height = tkroot.winfo_screenheight()
tkroot.withdraw()
tkroot.update()
tkroot.destroy()

win_height = 800
win_width = 1000

from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', (res_height - win_height)/2)
Config.set('graphics', 'left', (res_width - win_width)/2)
Config.set('widgets', 'scroll_timeout', 55)
Config.set('widgets', 'scroll_distance', 100)
Config.set('kivy', 'keyboard_mode', '')
Config.set('kivy', 'exit_on_escape', '1')
Config.set('graphics', 'width', win_width)
Config.set('graphics', 'height', win_height)

from kivy.lang import Builder
Builder.load_file('./kv/window.kv')

from kivy.app import App

from kivy.properties import (StringProperty, NumericProperty)

from kivy.uix.screenmanager import (ScreenManager, Screen, SlideTransition)
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.actionbar import (ActionBar, ActionView, ActionButton)
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput

from progressbar import NewProgressBar
from kivy.clock import Clock
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color
from kivy.graphics import Rectangle

from kivy.core.window import Window
from kivy.core.window import WindowBase
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex('#FFFFFF')

import os
import re
import time
from functools import partial
import json
import glob
from os.path import join, isdir
import sys
import prtscript
import threading
from desktop_file_dialogs import Desktop_FileDialog, FileGroup
from desktop_file_dialogs import Desktop_FolderDialog

# Application
# =============================================================================

global config_loaded
config_loaded = False

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='#'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))

class MainBox(BoxLayout):
    pass
    
class ErrPop(Popup):
    pass
    
class SavePop(Popup):
    def __init__(self, **kwargs):
        super(SavePop, self).__init__(**kwargs)
        for key in kwargs:
            if key == 'parentval':
                self.root = kwargs[key]
            if key == 'path':
                self.ids.mainchooser.path = kwargs[key]
    def is_dir(self, directory, filename):
        return isdir(join(directory, filename))
    def update_label(self):
        self.ids.indicator.text = self.ids.mainchooser.path
    def on_touch_up(self,touch):
        try:
            self.ids.indicator.text = self.ids.mainchooser.selection[0]
        except IndexError:
            pass
    def save_data(self):
        global loaded_path
        
        if not self.ids.jsonsavename.text:
            tempPop = ErrPop()
            tempPop.open()
        else:
            configOut = {}
            dataPath = self.ids.mainchooser.path
            
            for object_key, object_val in self.root['settab'].ids.items():
                if 'input' in object_key:
                    if object_val.text:
                        outputText = object_val.text
                        configOut[object_key] = outputText
                if 'switch' in object_key:
                    configOut[object_key] = object_val.active
            
            jsonOut = json.dumps(configOut)
            titleout = self.ids.jsonsavename.text   
            f = open(os.path.join(dataPath, titleout + '.json'),'w+')
            loaded_path = os.path.join(dataPath, titleout + '.json')
            f.write(jsonOut)
            f.close()
            self.dismiss()
        
class CoreLabel(Label):
    pass

class SettingsTab(TabbedPanel):
    pass
    
class Tooltip(Label):
    pass
    
class BasicInput(TextInput):
    tooltipExists = NumericProperty(0)
    tooltiptext = StringProperty()
    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(BasicInput, self).__init__(**kwargs)
    def on_text(self, *args):
        Clock.schedule_once(self.remove_tooltip, 0)
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        Clock.unschedule(self.display_tooltip)
        if self.collide_point(*self.to_widget(*pos)):
            self.tooltip = Tooltip(text='')
            if pos[0] + 300 < 1000:
                self.tooltip.x = pos[0]
            else:
                self.tooltip.x = pos[0] - 300
            self.tooltip.y = pos[1]
            self.tooltip.color = (0, 0, 0, 1)
            self.tooltip.text = self.tooltiptext
            Clock.schedule_once(self.display_tooltip, 1.5)

        if not self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.remove_tooltip, 0)
        if not self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.remove_tooltip, 0)
    def display_tooltip(self,*args):
        Window.add_widget(self.tooltip)
        self.tooltipExists = 1
    def remove_tooltip(self, *args):
        if self.tooltipExists == 1:
            for item in Window.children:
                if 'Tooltip' in str(item):
                    Window.remove_widget(item)
    
class InputLabel(Label):
    pass
    
class IntInput(TextInput):
    pat = re.compile('[^0-9]')
    tooltipExists = NumericProperty(0)
    tooltiptext = StringProperty()
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat,'',substring)
        return super(IntInput, self).insert_text(s, from_undo=from_undo)
    def __init__(self,**kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(IntInput,self).__init__(**kwargs)
    def on_text(self, *args):
        Clock.schedule_once(self.remove_tooltip,0)
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        Clock.unschedule(self.display_tooltip)
        if self.collide_point(*self.to_widget(*pos)):
            self.tooltip = Tooltip(text='')
            if pos[0]+300<1000:
                self.tooltip.x = pos[0]
            else:
                self.tooltip.x = pos[0] - 300
            self.tooltip.y = pos[1]
            self.tooltip.color = (0,0,0,1)
            self.tooltip.text = self.tooltiptext
            Clock.schedule_once(self.display_tooltip,1.5)
            
        if not self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.remove_tooltip,0)
            
        if not self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.remove_tooltip,0)
    def display_tooltip(self,*args):
        Window.add_widget(self.tooltip)
        self.tooltipExists = 1
    def remove_tooltip(self,*args):
        if self.tooltipExists == 1:
            for item in Window.children:
                if 'Tooltip' in str(item):
                    Window.remove_widget(item)
    
class ButtonTab(TabbedPanelItem):
    pass
    
class FilePopup(Popup):
    def __init__(self,**kwargs):
        super(FilePopup,self).__init__(**kwargs)
        self.pulldir = False
        for key in kwargs:
            if key == 'path':
                self.ids.mainchooser.path = kwargs[key]
            if key == 'manager':
                self.screenchanger = kwargs[key]
            if key == 'pulldir':
                self.pulldir = True
    def on_touch_up(self,touch):
        try:
            self.ids.indicator.text = self.ids.mainchooser.selection[0]
        except IndexError:
            pass
    def load_data(self):
        if not self.pulldir:
            dataPath = self.ids.mainchooser.selection
            global loaded_path, config_loaded
            config_loaded = True
            loaded_path = dataPath[0]
            f = open(dataPath[0],'r')
            dataJSON = json.load(f)
            self.screenchanger.current = 'ConfigScreen'
            for key,value in self.screenchanger.children[0].ids.settab.ids.items():
                if '_input' in key:
                    if key in dataJSON:
                        value.text = dataJSON[key]
                if 'switch' in key:
                    if key in dataJSON:
                        value.active = dataJSON[key]
            for key in dataJSON:
                if key == 'colors_config':
                    self.screenchanger.config = dataJSON[key]
            self.dismiss()
        else:
            dataJSON = {}
            for key,value in self.screenchanger.children[0].ids.settab.ids.items():
                if '_input' in key:
                    if value.text:
                        dataJSON[key] = value.text
                if 'switch' in key:
                    dataJSON[key] = value.active
                    
            try:
                dataJSON['colors_config'] = self.screenchanger.config
            except:
                pass
                
            for key in dataJSON:
                if key == 'onsetcolumn_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                elif key == 'parametricweights_input':
                    dataJSON[key] = dataJSON[key].split('\n')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                    tempDict = {}
                    for item in dataJSON[key]:
                        valSplit = item.split(':')
                        tempDict[valSplit[0]] = valSplit[1]
                    dataJSON[key] = tempDict
                elif key == 'error_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                elif key == 'gapcolnames_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                elif key == 'grouping_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
            dataPath = self.ids.mainchooser.selection[0]
            csvFiles = glob.glob(dataPath+'\\*.csv')
            dataJSON['csv_files'] = csvFiles
            self.screenchanger.add_widget(ProcessScreen(name='ProcessScreen',config_parameters=dataJSON,scr_manager=self.screenchanger))
            self.screenchanger.current = 'ProcessScreen'
            self.dismiss()

class ProcessProgressBar(NewProgressBar):
    pass
            
class ProcessScreen(Screen):
    def __init__(self,**kwargs):
        global loaded_path
        super(ProcessScreen, self).__init__(**kwargs)
        for key in kwargs:
            if key == 'config_parameters':
                self.config_parameters = kwargs[key]
            if key == 'scr_manager':
                scr_manager = kwargs[key]
        try:
            self.config_parameters['colors_config'] = scr_manager.config
        except AttributeError:
            pass
            
        if 'colors_config' not in self.config_parameters:
            f = open(loaded_path,'r')
            dataJSON = json.load(f)
            dataJSON['colors_config'] = {}
            f.close()
            f = open(loaded_path,'w')
            f.write(json.dumps(dataJSON))
            f.close()
            self.color_config_exists = False
            self.config_parameters['color_config_exists'] = False
        else:
            self.color_config_exists = True
            self.config_parameters['color_config_exists'] = True
            
        self.my_prbar = NewProgressBar(id='process_bar')
        self.my_prbar.min = 0
        self.my_prbar.max = 100
        self.my_prbar.bar_value = 0
        self.my_prbar.color = '#43d5e0'
        
        self.complete_label = Label(id='donelabel',color=(0.196,0.196,0.196,1),font_size=40,font='./helvetica.ttf')
        self.ids.process_layout.add_widget(Label(text=''))
        self.ids.process_layout.add_widget(self.complete_label)
        self.ids.process_layout.add_widget(self.my_prbar)
        self.sub_box = FinalBox()
        self.ids.process_layout.add_widget(self.sub_box)
        
        self.config_parameters['path'] = loaded_path
    def on_enter(self):
        self.config_parameters['object_id'] = self
        prt_thread = threading.Thread(target=prtscript.createPRTs,kwargs=self.config_parameters)
        prt_thread.start()

class FinalBox(BoxLayout):
    def close(self):
        App.get_running_app().stop()
        
class BigButton(Button):
    def proceed_screen(self, ScrnMgr):
        ScrnMgr.current = 'ConfigScreen'
    def back(self, ScrnMgr):
        ScrnMgr.transition = SlideTransition(direction='right',duration=0.4)
        ScrnMgr.current = ScrnMgr.previous()
    def save_config(self):
        filepath = os.getcwd()
        tempPop = SavePop(parentval=self.parent.parent.parent.ids,path=filepath)
        tempPop.open()
    def setattrs(self,filepath):
        setattr(self,'file_path',filepath)
        setattr(self,'proceed',True)
    def load_file(self,ScrnMgr):
        filepath = os.getcwd()
        fd = Desktop_FileDialog(
            title = "Select Config File",
            initial_directory = filepath,
            on_accept = lambda file_path: self.setattrs(file_path),
            on_cancel = lambda *args: setattr(BigButton,'proceed',False),
            file_groups = [
            FileGroup(name = "JSON Files", extensions = ["json"]),
            FileGroup.All_FileTypes,
            ],
        )
        fd.show()
        if self.proceed:
            for key,value in ScrnMgr.screens[1].ids.settab.ids.items():
                if '_input' in key:
                    value.text = ''
                if 'switch' in key:
                    value.active = False
            self.pulldir = False
            self.load_data(self.file_path,ScrnMgr)
    def load_data(self,dataPath,ScrnMgr):
        if not self.pulldir:
            dataPath = dataPath
            global loaded_path
            loaded_path = dataPath
            f = open(dataPath,'r')
            dataJSON = json.load(f)
            ScrnMgr.current = 'ConfigScreen'
            for key,value in ScrnMgr.children[0].ids.settab.ids.items():
                if '_input' in key:
                    if key in dataJSON:
                        value.text = dataJSON[key]
                if 'switch' in key:
                    if key in dataJSON:
                        value.active = dataJSON[key]
            for key in dataJSON:
                if key == 'colors_config':
                    ScrnMgr.config = dataJSON[key]
        else:
            print('yes', self.file_path)
            dataJSON = {}
            for key,value in ScrnMgr.children[0].ids.settab.ids.items():
                if '_input' in key:
                    if value.text:
                        dataJSON[key] = value.text
                if 'switch' in key:
                    dataJSON[key] = value.active
                    
            try:
                dataJSON['colors_config'] = ScrnMgr.config
            except:
                pass
                
            for key in dataJSON:
                if key == 'onsetcolumn_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                elif key == 'parametricweights_input':
                    dataJSON[key] = dataJSON[key].split('\n')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                    tempDict = {}
                    for item in dataJSON[key]:
                        valSplit = item.split(':')
                        tempDict[str(valSplit[0])] = str(valSplit[1])
                    dataJSON[key] = tempDict
                elif key == 'error_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                elif key == 'gapcolnames_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
                elif key == 'grouping_input':
                    dataJSON[key] = dataJSON[key].split(',')
                    dataJSON[key] = [x.strip(' ') for x in dataJSON[key]]
            dataPath = dataPath
            csvFiles = glob.glob(dataPath+'/*.csv')
            dataJSON['csv_files'] = csvFiles
            print(dataJSON)
            print(csvFiles)
            ScrnMgr.add_widget(ProcessScreen(name='ProcessScreen',config_parameters=dataJSON,scr_manager=ScrnMgr))
            ScrnMgr.current = 'ProcessScreen'
    def choose_dir(self,ScrnMgr):
        filepath = os.getcwd()
        fd =Desktop_FolderDialog(
            title             = "Select Output Folder",
            initial_directory = filepath,
            on_accept = lambda file_path: self.setattrs(file_path),
            on_cancel = lambda *args: setattr(BigButton,'proceed',False),
        )
        fd.show()
        if self.proceed:
            self.pulldir = True
            self.load_data(self.file_path,ScrnMgr)
    
class LoadScreen(Screen):
    def on_enter(self):
        ScrnMgr = self.parent
        ScrnMgr.transition = SlideTransition(direction='left',duration=0.4)
    
class ConfigScreen(Screen):
    pass
    
class PadLayout(BoxLayout):
    pass
    
class BlackLabel(Label):
    pass
    
class ButtonUp(Button):
    pass
    
class ButtonDown(Button):
    pass

class Tooltip(Label):
    pass

class InputSwitch(Switch):
    def disable(self,**kwargs):
        for target in kwargs.iteritems():
            if self.active:
                target[1].disabled = False
            else:
                target[1].disabled = True

class RootBox(BoxLayout):
    def __init__(self, **kwargs):
        super(RootBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.content = ScreenManager(id='mainscreen')
        self.content.transition = SlideTransition(
            direction='left',duration=0.4)
        self.content.add_widget(LoadScreen(name='LoadScreen'))
        self.content.add_widget(ConfigScreen(name='ConfigScreen'))
        self.add_widget(self.content)

class PRTGEN(App):
    def build(self):
        return RootBox()

if __name__ == '__main__':
    PRTGEN().run()