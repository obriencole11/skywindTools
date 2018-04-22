import batchTools
import os
from retargeter.retargeter.animRetarget import retargeter
import pymel.core as pmc

class skywindBatchConfig(batchTools.batchConfig):

    def __init__(self, sourceFiles, directory, rigFile, scriptFile, root_name):

        self.sourceFiles = sourceFiles
        self.destinationDir = directory
        self.rigFile = rigFile
        self.scriptFile = scriptFile
        self.root_name = root_name

    def batch(self):

        for fileDir in self.sourceFiles:
            self._open(self.rigFile)
            self._import(fileDir)

            if self.scriptFile:
                execfile(self.scriptFile)

            try:
                retargeter.bakeBindTargets()
            except:
                pass

            if self.root_name:
                root = pmc.PyNode(self.root_name)

                start = pmc.playbackOptions(minTime=True, q=True)
                end = pmc.playbackOptions(maxTime=True, q=True)
                targets = [root] + pmc.listRelatives(root, ad=True)
                pmc.bakeResults(targets, t=(start, end), hi=True, simulation=True)

                self._exportTarget(os.path.basename(fileDir), self.destinationDir, targets)
            else:
                self._exportAll(os.path.basename(fileDir), self.destinationDir)