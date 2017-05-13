# shared_toolsets
# Setup your SharedToolSets folder here

import sys

if nuke.GUI:

  import shared_toolsets
  
  sharedToolSetsPaths = {
    "linux2" : "/mnt/some/nice/place/SharedToolSets",   #LINUX
    "win32"  : "C:/some/nice/place/SharedToolSets",     #WINDOWS
    "darwin" : "/Volume/some/nice/place/SharedToolSets" #MACOS
  }

  def toolSetsFilenameFilter(filename):
      if nuke.env['MACOS']:
          # uppercase
          filename = filename.replace( 'P:', '/Volumes/Project' )
          # lowercase
          filename = filename.replace( 'p:', '/Volumes/Project' )
      elif nuke.env['WIN32']:
          # lowercase
          filename = filename.replace( 'D:', 'C:' )
          filename = filename.replace( '/Volumes/Project', 'P:' )
      elif nuke.env['LINUX']:
          filename = filename.replace( 'P:', '/mnt/project' )
          filename = filename.replace( '/Volumes/Project', '/mnt/project' )
      return filename

  platform = sys.platform

  sharedToolSetsPath = sharedToolSetsPaths[platform]
  shared_toolsets.setSharedToolSetsPath(sharedToolSetsPath)
  shared_toolsets.addFileFilter(toolSetsFilenameFilter)

  toolbar = nuke.menu("Nodes")
  shared_toolsets.createToolsetsMenu(toolbar)
