# shared_toolsets
import shared_toolsets
toolbar = nuke.menu("Nodes")
sharedToolSetsPath = "C:\\nuke_plugins\\SharedToolSets"
shared_toolsets.setSharedToolSetsPath(sharedToolSetsPath)
shared_toolsets.createToolsetsMenu(toolbar)
