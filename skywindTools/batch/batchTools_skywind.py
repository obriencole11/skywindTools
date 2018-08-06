import batchTools
import os
from skywindTools.retargeter import retargeter
import pymel.core as pmc

class skywindBatchConfig(batchTools.batchConfig):

    def __init__(self, sourceFiles, directory, rigFile, scriptFile, root_name):

        self.sourceFiles = sourceFiles
        self.destinationDir = directory
        self.rigFile = rigFile
        self.scriptFile = scriptFile
        self.root_name = root_name

    def _clear_scene(self, targets):

        for obj in pmc.ls(dag=True):
            if not obj in targets:
                if pmc.objExists(obj):

                    pmc.delete(obj)

    def batch(self):

        for fileDir in self.sourceFiles:

            self._open(self.rigFile)
            self._import(fileDir)

            if self.scriptFile:
                execfile(self.scriptFile)

            try:
                retargeter.bakeBindTargets()
            except Exception as e:
                print 'Could not bake bind targets:\n%s' % e

            if self.root_name:
                root = pmc.PyNode(self.root_name)

                start = pmc.playbackOptions(minTime=True, q=True)
                end = pmc.playbackOptions(maxTime=True, q=True)
                targets = [root] + pmc.listRelatives(root, ad=True)
                targets = [target for target in targets if isinstance(target, pmc.nodetypes.Joint)]
                pmc.bakeResults(targets, t=(start, end), simulation=True)

                # Remove all rig controls and bind nodes
                self._clear_scene(targets)

                destination = self.destinationDir + '//'

                self._exportTarget(os.path.basename(fileDir), destination, targets)
            else:
                self._exportAll(os.path.basename(fileDir), self.destinationDir)