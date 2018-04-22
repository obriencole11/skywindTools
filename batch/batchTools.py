import pymel.core as pmc
import os

PATH = None

class batchConfig(object):

    def __init__(self, sourceFiles, destinationDir):
        self.sourceFiles = sourceFiles
        self.destinationDir = destinationDir

    def batch(self):

        for fileDir in self.sourceFiles:
            print fileDir
            self._newFile()
            self._import(fileDir)
            self._exportAll(os.path.basename(fileDir), self.destinationDir)

    @staticmethod
    def getSelected():
        if len(pmc.selected()) > 0:
            return pmc.selected()[0].name()
        else:
            return ''

    def _import(self, path):
        global PATH
        PATH = path
        pmc.mel.eval('FBXImportFillTimeline -v true')
        pmc.mel.eval('FBXImportMode -v Exmerge')
        print PATH
        pmc.mel.eval('FBXImport -f `python "batchTools.PATH"`')

    def _open(self, path):
        pmc.openFile(path, force=True)

    def _exportAll(self, name, directory):
        path = os.path.join(directory, name)
        pmc.exportAll(path, force=True)

    def _newFile(self):
        pmc.newFile(force=True)

    def _exportTarget(self, name, directory, target):
        path = os.path.join(directory, name)
        pmc.select(clear=True)
        pmc.select(target)
        pmc.exportSelected(path, force=True, type='FBX')

    def _save(self):
        pmc.saveFile()

    def _saveAs(self, name, directory):
        pmc.exportAll(os.path.join(directory, name), type='mayaAscii')