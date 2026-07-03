# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore
from qgis.gui import QgsMapLayerComboBox

class ApexNadirDialog(QtWidgets.QDialog): # ApexNadirDialog
    def __init__(self, parent=None):
        """Constructor setting up a native Python window layout."""
        super(ApexNadirDialog, self).__init__(parent)
        
        # 1. Window Configurations
        self.setWindowTitle("ApexNadir - Extreme Points Explorer")
        self.setMinimumWidth(380)
        self.resize(380, 220)
        
        # 2. Main Vertical Layout setup Container
        main_layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()
        
        # 3. Create UI Interactive Input Elements
        self.polygon_combo = QgsMapLayerComboBox(self)
        self.raster_combo = QgsMapLayerComboBox(self)
        self.mode_combo = QtWidgets.QComboBox(self)
        
        # 4. Group elements nicely with clean, structured text labels
        form_layout.addRow("Select Polygon Layer:", self.polygon_combo)
        form_layout.addRow("Select DEM Raster Layer:", self.raster_combo)
        form_layout.addRow("Target Operation Point:", self.mode_combo)
        main_layout.addLayout(form_layout)
        
        # 5. Visual spacing separator element
        main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            10, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        
        # 6. Standard Dialog Windows Action Buttons Form (OK / Cancel)
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, 
            QtCore.Qt.Horizontal, self)
        
        main_layout.addWidget(self.button_box)
        
        # 7. Connect action click states to native execution frameworks
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
