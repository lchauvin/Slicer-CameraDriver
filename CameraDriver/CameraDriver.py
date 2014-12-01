import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# CameraDriver
#

class CameraDriver:
  def __init__(self, parent):
    parent.title = "CameraDriver" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['CameraDriver'] = self.runTest

  def runTest(self):
    tester = CameraDriverTest()
    tester.runTest()

#
# CameraDriverWidget
#

class CameraDriverWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "CameraDriver Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.cameraSelector = slicer.qMRMLNodeComboBox()
    self.cameraSelector.nodeTypes = ( ("vtkMRMLCameraNode"), "" )
    self.cameraSelector.selectNodeUponCreation = True
    self.cameraSelector.addEnabled = False
    self.cameraSelector.removeEnabled = False
    self.cameraSelector.noneEnabled = True
    self.cameraSelector.showHidden = False
    self.cameraSelector.showChildNodeTypes = False
    self.cameraSelector.setMRMLScene( slicer.mrmlScene )
    self.cameraSelector.setToolTip( "Select camera to drive." )
    parametersFormLayout.addRow("Camera: ", self.cameraSelector)

    #
    # output volume selector
    #
    self.transformSelector = slicer.qMRMLNodeComboBox()
    self.transformSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.transformSelector.selectNodeUponCreation = True
    self.transformSelector.addEnabled = True
    self.transformSelector.removeEnabled = True
    self.transformSelector.renameEnabled = True
    self.transformSelector.noneEnabled = True
    self.transformSelector.showHidden = False
    self.transformSelector.showChildNodeTypes = False
    self.transformSelector.setMRMLScene( slicer.mrmlScene )
    self.transformSelector.setToolTip( "Select camera driving transform node." )
    parametersFormLayout.addRow("Transform: ", self.transformSelector)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableCameraDrivingCheckBox = qt.QCheckBox()
    self.enableCameraDrivingCheckBox.checked = 0
    self.enableCameraDrivingCheckBox.setToolTip("If checked, Slicer camera will be driven by selected transform node.")
    parametersFormLayout.addRow("Drive Camera", self.enableCameraDrivingCheckBox)

    # connections
    self.cameraSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.transformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.enableCameraDrivingCheckBox.connect("toggled(bool)", self.onDrivingToggled)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    if self.cameraSelector.currentNode() == None or self.transformSelector.currentNode() == None:
      self.enableCameraDrivingCheckBox.checked = 0

  def onDrivingToggled(self,enable):
    logic = CameraDriverLogic()
    logic.run(self.cameraSelector.currentNode(), self.transformSelector.currentNode(), enable)

  def onReload(self,moduleName="CameraDriver"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="CameraDriver"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# CameraDriverLogic
#

class CameraDriverLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def run(self,camera,transform,enable):
    """
    Run the actual algorithm
    """
    self.camera = camera
    self.transform = transform
    self.enable = enable
    
    if enable:
      # Observer Transform modification and update camera
      self.transform.AddObserver(self.transform.TransformModifiedEvent,self.onTransformModified)

      # Call it manually for the first time
      self.onTransformModified(self,self.transform)
    else:
      self.transform.RemoveAllObservers()

    return True

  def onTransformModified(self,obj,callData):
    matrix = vtk.vtkMatrix4x4()
    self.transform.GetMatrixTransformToWorld(matrix)
    self.camera.SetPosition(matrix.GetElement(0,3),
                            matrix.GetElement(1,3),
                            matrix.GetElement(2,3))

    initFocalDistance = [0.0, 500.0, 0.0, 1.0]
    transformedFocalDistance = [0.0, 0.0, 0.0, 0.0]
    transformedFocalDistance = matrix.MultiplyDoublePoint(initFocalDistance)
    self.camera.SetFocalPoint(transformedFocalDistance[0],
                              transformedFocalDistance[1],
                              transformedFocalDistance[2])
    viewUp = [matrix.GetElement(2,0), matrix.GetElement(2,1), matrix.GetElement(2,2)]
    self.camera.SetViewUp(viewUp)
