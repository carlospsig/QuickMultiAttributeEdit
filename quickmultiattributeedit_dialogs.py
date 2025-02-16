# --------------------------------------------------------
#    quickmultiattributeedit_dialogs - Dialog classes for quickmultiattributeedit
#
#    begin                : 19 May 2011
#    copyright            : (c) 2011 by Marco Braida
#    email                : See marcobra.ubuntu@gmail.com
#
#   QuickMultiAttributeEdit is free software and is offered 
#   without guarantee or warranty. You can redistribute it 
#   and/or modify it under the terms of version 2 of the 
#   GNU General Public License (GPL v2) as published by the 
#   Free Software Foundation (www.gnu.org).
# --------------------------------------------------------

#import os.path
import operator
import tempfile
import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from quickmultiattributeedit_library import *

from os import path, access, R_OK

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")


# --------------------------------------------------------
#    quickmultiattributeedit_update_selected - Update selected feature field
# --------------------------------------------------------

from quickmultiattributeedit_update_selected_form import *

class quickmultiattributeedit_update_selected_dialog(QDialog, Ui_quickmultiattributeedit_update_selected_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.run)
		layer = self.iface.mapCanvas().currentLayer()
		delimchars = "#"
		if (layer):
	                provider = layer.dataProvider()
			fields = provider.fields()
			if layer.type() == QgsMapLayer.VectorLayer:
				self.QLEvalore.setText("")
				self.CBfields.clear()
                                for f in fields:
					self.CBfields.addItem(f.name(), f.name() )
					nF = layer.selectedFeatureCount()
					if (nF > 0):		
						self.label.setText("<font color='green'>For <b>" + str(nF) +  "</b> selected elements in <b>" + layer.name() + "</b> set value of field</font>" )
						self.CBfields.setFocus(True)
						rm_if_too_old_settings_file(tempfile.gettempdir() + "/QuickMultiAttributeEdit_tmp")
						if os.path.exists( tempfile.gettempdir() + "/QuickMultiAttributeEdit_tmp"):
							in_file = open(tempfile.gettempdir() + '/QuickMultiAttributeEdit_tmp', 'r')
							file_cont = in_file.read()
							in_file.close()
							file_cont_splitted = file_cont.split(delimchars)
							lastlayer = file_cont_splitted[0]
							lastfield = file_cont_splitted[1]
							lastvalue = file_cont_splitted[2]
							lkeepLatestValue = file_cont_splitted[3]
							if ( self.CBfields.findText(lastfield) > -1 ): # se esiste il nome del campo nel combobox
								self.CBfields.setCurrentIndex(self.CBfields.findText(lastfield))
								self.cBkeepLatestValue.setChecked(str2bool(lkeepLatestValue)) # read thevalue from settings
								if ( self.cBkeepLatestValue.isChecked() ): # if true to keep latest input value
									self.QLEvalore.setText(lastvalue)
									self.QLEvalore.setFocus()

					if (nF == 0):
						infoString = unicode("<font color='red'> Please select some elements into current <b>" + layer.name() + "</b> layer</font>")
						self.label.setText(infoString)
						self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
						self.QLEvalore.setEnabled(False)
						self.CBfields.setEnabled(False)
		else:
			infoString = unicode("<font color='red'> <b>No layer selected... Select a layer from the layer list...</b></font>")
			self.label.setText(infoString)
			self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
			self.QLEvalore.setEnabled(False)
			self.CBfields.setEnabled(False)

	def run(self):
	 delimchars = "#"
	 layer = self.iface.mapCanvas().currentLayer()
         if (layer == None):
		infoString = unicode("<font color='red'> <b>No layer selected... Select a layer from the layer list...</b></font>")
		self.label.setText(infoString)
	        return
         if not layer.isEditable():
		layer.startEditing()
         value = unicode(self.QLEvalore.displayText())
         nPosField = self.CBfields.currentIndex()
         f_index = self.CBfields.itemData( nPosField )[0]
         f_name = self.CBfields.itemData( nPosField )
         if len(value) <= 0:
		infoString = unicode("Warning <b> please input a value... </b>")
		self.label.setText(infoString)
         	return
	 layer = self.iface.mapCanvas().currentLayer()
	 if(layer):		
	  nF = layer.selectedFeatureCount() # numero delle features selezionate
	  if (nF > 0):		
	   oFeaIterator = layer.selectedFeatures() # give the selected feauter new in api2
	   for feature in oFeaIterator: # in oFea2 there is an iterator object (api2)
	    	   layer.changeAttributeValue(feature.id(),nPosField,value,True) 
	   infoString = unicode("<font color='green'> <b>You can save or abort changes at the end of sessions.<br>Press the Save icon to save or disable the edit mode of layer without save changes to abort...</b></font>")
           if not os.path.exists( tempfile.gettempdir() + "/QuickMultiAttributeEdit_tmp"):
              out_file = open(tempfile.gettempdir() + '/QuickMultiAttributeEdit_tmp', 'w')
              out_file.write( layer.name() + delimchars +  unicode(self.CBfields.currentText()) + delimchars + value + delimchars + bool2str(self.cBkeepLatestValue.isChecked())  )
              out_file.close()
              QMessageBox.information(self.iface.mainWindow(),"Message",infoString)
           else:
              in_file = open(tempfile.gettempdir() + '/QuickMultiAttributeEdit_tmp', 'r')
              file_cont = in_file.read()
              in_file.close()
              file_cont_splitted = file_cont.split(delimchars)
              lastlayer = file_cont_splitted[0]
              lastfield = file_cont_splitted[1] 
              lastvalue = file_cont_splitted[2] 
              if ( lastlayer != layer.name() ):
                   QMessageBox.information(self.iface.mainWindow(),"Message",infoString)
              out_file = open(tempfile.gettempdir() +  '/QuickMultiAttributeEdit_tmp', 'w')
              out_file.write( layer.name() + delimchars +  unicode(self.CBfields.currentText()) + delimchars + value + delimchars + bool2str(self.cBkeepLatestValue.isChecked())  )
              out_file.close()
	   #layer.commitChanges()
	  else:
	    QMessageBox.critical(self.iface.mainWindow(),"Error", "Please select at least one feature from <b> " + layer.name() + "</b> current layer")
	 else:
	  QMessageBox.critical(self.iface.mainWindow(),"Error","Please select a layer")

def bool2str(bVar):
	if bVar:
		return 'True'
	else:
		return 'False'

def str2bool(bVar):
	if ( bVar == 'True'):
		return True
	else:
		return False

def rm_if_too_old_settings_file(myPath_and_File):
	if os.path.exists(myPath_and_File) and os.path.isfile(myPath_and_File) and os.access(myPath_and_File, R_OK):
		now = time.time()
		tmpfileSectime = os.stat(myPath_and_File)[7] #get last modified time,[8] would be last creation time
		if( now - tmpfileSectime > 60 * 60 * 12 ): # if settings file is older than 6 hour
			os.remove( myPath_and_File )




