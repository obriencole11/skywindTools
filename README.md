# Skywind Tools

The following is a collection of tools for use on the TESR Skywind mod project.
For an overview of the features, there is a writeup [here](https://coleobrienart.com/2017/08/07/skywind_retargetting/)

## Retargeter

### Installation
Add the batch folder to your local Maya script directory.
Then in the python console run:
```
from skywindTools.retargeter import retargeter_main
retargeter_main.show()
```

### How To
The process involves linking two skeletons/rigs with a network of *Bind Nodes*. Bind nodes can be created by selecting two joints and hitting either *Bind Rotate*, *Bind Translate*, or *Bind Both*. In general Bind Rotate is used the most often. Bind both is for root nodes. And Bind translate is mostly for binding to rigs.

Once added you can import an fbx animation and it will be retargetted live. Use the *Bake Bind Targets* button to bake the animation to the target skeleton.

## Batch Tools

### Installation
Add the batch folder to your local Maya script directory.
Then in the python console run:
```
from skywindTools.batch import batchTools_main_skywind
batchTools_main_skywind.load()
```

### How To
This is built to batch retarget animations. To use you will need to specify a folder of fbx animations, a destination directory, an optional script, and a bind rig created with the retargetter. You will also need to add the name of the root joint in the export skeleton.


