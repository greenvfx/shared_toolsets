# Shared ToolSets
# Based on Nuke's ToolSets 
# Vitaly Musatov 
# emails:
# latest.green@gmail.com
# vit.muusatov@gmail.com
# Use setSharedToolSetsPath to setup location of shared folder, folder must be called "SharedToolSets", but you can place it anywhere.
# 8 may 2016

import os
import nuke
import nukescripts
import posixpath

SHARED_TOOLSET_PATH = ""

def setSharedToolSetsPath(path):
  global SHARED_TOOLSET_PATH
  SHARED_TOOLSET_PATH = path


class CreateToolsetsPanel(nukescripts.PythonPanel):
  def __init__(self):
    nukescripts.PythonPanel.__init__( self, 'Create ToolSet', 'uk.co.thefoundry.CreateToolset')
    
    # CREATE KNOBS
    self.userFolders = []
    fullPath = SHARED_TOOLSET_PATH
    self.buildFolderList(fullPath, '')
          
    self.menuItemChoice = nuke.CascadingEnumeration_Knob('menuItemChoice','SharedToolSets menu', ['root'] + self.userFolders )
    self.menuItemChoice.setTooltip("The menu location that the ToolSet will appear in. Specify 'root' to place the SharedToolSets in the main SharedToolSets menu.")
    self.menuPath = nuke.String_Knob('itemName', 'Menu item:')
    self.menuPath.setFlag(0x00001000)  
    self.menuPath.setTooltip("ToolSet name. Use the '/' character to create a new submenu for this ToolSet, eg to create a ToolSet named 'Basic3D' and place it in a new submenu '3D', type '3D/Basic3D'. Once created the 3D menu will appear in the ToolSet menu.")
    self.okButton = nuke.PyScript_Knob ('create', 'Create')
    #self.okButton.setToolTip("Create a ToolSet from the currently selected nodes with the given name")
    self.okButton.setFlag(0x00001000)
    self.cancelButton = nuke.PyScript_Knob ('cancel', 'Cancel')
    
    # ADD KNOBS
    self.addKnob(self.menuItemChoice)
    self.addKnob(self.menuPath)
    self.addKnob(self.okButton)
    self.addKnob(self.cancelButton)
    
  # BUILD A LIST Of PRE_CREATED FOLDER LOCATIONS
  def buildFolderList(self, fullPath, menuPath):
    filecontents = sorted(os.listdir(fullPath), key=str.lower)
    for group in filecontents:
      if os.path.isdir(os.path.join(fullPath, group)):
        self.userFolders.append(menuPath + group)
        self.buildFolderList(fullPath + '/' + group, menuPath + group + '/')              

  def createPreset(self):
    if self.createSharedToolset(str(self.menuPath.value())):
      self.finishModalDialog( True )
    
  def createSharedToolset(self, name):
    ret = False
    nameList = name.split('/')
    fileName = nameList[-1]
    del nameList[-1]
    dirs = '/'.join(nameList)
    fullPath = posixpath.join(SHARED_TOOLSET_PATH, dirs)
    print fullPath 
    os.path.isdir(fullPath)
    try:
      if not os.path.isdir(fullPath):
        os.makedirs( fullPath )
      filePath = posixpath.join(fullPath, fileName + '.nk')
      
      if not os.path.exists(filePath):
        nuke.nodeCopy(filePath)

      elif nuke.ask('Overwrite existing \n %s?' % filePath):
        nuke.nodeCopy(filePath)

      ret = True
    except:
      ret = False
    return ret

  def getPresetPath(self):
    if str(self.menuItemChoice.value()) == "root":
      self.menuPath.setValue("")
    else:
      self.menuPath.setValue(self.menuItemChoice.value() + "/")

  def knobChanged( self, knob ):
    if knob == self.okButton:
      self.createPreset()
    elif knob == self.cancelButton:
      self.finishModalDialog( False )
    elif knob == self.menuItemChoice:
      self.getPresetPath()

# NUKESCRIPT FUNCTIONS	  
    
def addToolsetsPanel():
  res = False
  if nuke.nodesSelected() == True:
    res = CreateToolsetsPanel().showModalDialog()
    # now force a rebuild of the menu
    refreshToolsetsMenu()
  else:
    nuke.message("No nodes are selected")
  return res  
  
def deleteToolset(rootPath, fileName):
  if nuke.ask('Are you sure you want to delete ToolSet %s?' %fileName):
    os.remove(fileName)
    # if this was the last file in this directory, the folder will need to be deleted.
    # Walk the directory tree from the root and recursively delete empty directories
    checkForEmptyToolsetDirectories(rootPath)
    # now force a rebuild of the menu
    refreshToolsetsMenu()


def checkForEmptyToolsetDirectories(currPath):
  removed = True
  while removed == True:
    removed = False
    for root, dirs, files in os.walk(currPath):
      if files == [] and dirs == []:
        if root != SHARED_TOOLSET_PATH:
          os.rmdir(root)
          removed = True
        
def refreshToolsetsMenu():  
  toolbar = nuke.menu("Nodes")
  m = toolbar.findItem("SharedToolSets")
  if m != None:
    m.clearMenu()
    createToolsetsMenu(toolbar)

def createToolsetsMenu(toolbar):
  m = toolbar.addMenu(name = "SharedToolSets", icon = "SharedToolSets.png")
  m.addCommand("Create", "shared_toolsets.addToolsetsPanel()", "", icon="ToolsetCreate.png")
  m.addCommand("-", "", "")
  if populateToolsetsMenu(m, False):
    m.addCommand("-", "", "")  
    n = m.addMenu("Delete", "ToolsetDelete.png")
    populateToolsetsMenu(n, True)
  m.addCommand('Refresh', 'shared_toolsets.refreshToolsetsMenu()', icon = "SharedToolSets_Refresh.png")

def traversePluginPaths(m, delete, allToolsetsList, isLocal):
  ret = False
  fullPath = SHARED_TOOLSET_PATH
  if createToolsetMenuItems(m, fullPath, fullPath, delete, allToolsetsList, isLocal):
      ret = True
  return ret  

def populateToolsetsMenu(m, delete):
  ret = False
  allToolsetsList = []
  # now do shared toolsets like the local .nuke  
  if traversePluginPaths(m, delete, allToolsetsList, True):
    ret = True
  return ret   

def createToolsetMenuItems(m, rootPath, fullPath, delete, allToolsetsList, isLocal):
  #TODO: CLEAN THIS FUNCTION

  filecontents = sorted(os.listdir(fullPath), key=str.lower)
  excludePaths = nuke.getToolsetExcludePaths()
  # First list all directories
  retval = False
  if filecontents != []:
    for group in filecontents:
      newPath = "/".join([fullPath, group])
      ignore = False
      if newPath.find(".svn") != -1:
        ignore = True
      else:
        for i in excludePaths:
          i = i.replace('\\', '/')
          if newPath.find(i) != -1:
            ignore = True
            break
      if os.path.isdir(newPath) and not ignore:
        menuName = group
        if isLocal and (menuName in allToolsetsList):
          menuName = "[user] " + menuName
        elif not isLocal:
          allToolsetsList.append(menuName)
        n = m.addMenu(menuName)
        retval = createToolsetMenuItems(n, rootPath, "/".join([fullPath, group]), delete, allToolsetsList, isLocal)
        # if we are deleting, and the sub directory is now empty, delete the directory also
        if delete and os.listdir(fullPath)==[]:
          os.rmdir(fullPath)
    # Now list individual files
    for group in filecontents:
      fullFileName = "/".join([fullPath, group])
      if not os.path.isdir(fullFileName):
        extPos = group.find(".nk")
        if extPos != -1 and extPos == len(group) - 3:
          group = group.replace('.nk', '')
          if delete:
            m.addCommand(group, 'shared_toolsets.deleteToolset("%s", "%s")' % (rootPath, fullFileName), "")
            retval = True
          else:
            # get the filename below toolsets
            i = fullFileName.find("SharedToolSets/")
            if i != -1:
              subfilename = fullFileName[i:]
            else:
              # should never happen, but just in case ...
              subfilename = fullfilename
            if isLocal and (subfilename in allToolsetsList):
              # if we've already appended [user] to the menu name, don't need it on the filename
              if (i != -1) and subfilename[len("SharedToolSets/"):].find("/") == -1:
                group = "[user] " + group
            elif not isLocal:
              allToolsetsList.append(subfilename)
            m.addCommand(group, 'nuke.loadToolset("%s")' % fullFileName, "")
            retval = True
  return retval      
