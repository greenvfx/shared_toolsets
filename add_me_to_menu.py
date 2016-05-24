# shared_toolsets
# Setup your SharedToolSets folder here
if nuke.GUI:
	import shared_toolsets
	toolbar = nuke.menu("Nodes")
	sharedToolSetsPath = "C:/some/path/SharedToolSets" # or "/some/path/SharedToolSets"
	shared_toolsets.setSharedToolSetsPath(sharedToolSetsPath)
	shared_toolsets.createToolsetsMenu(toolbar)
