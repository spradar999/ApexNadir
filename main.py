# -*- coding: utf-8 -*-

import os
import numpy as np
from osgeo import gdal

from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, 
                       QgsGeometry, QgsPointXY, QgsCoordinateTransform, 
                       QgsCoordinateReferenceSystem, QgsMapLayerProxyModel)
from PyQt5.QtCore import QVariant, QCoreApplication
from PyQt5 import QtWidgets  # FIXED: Correct way to import the namespace for Python 3.12
from PyQt5.QtWidgets import QAction, QMessageBox  # FIXED: Explicit PyQt5 clean imports
from PyQt5.QtGui import QIcon

# FIXED: Import the brand new ApexNadir dialog module class instead of vertigo
from .apex_nadir_dialog import ApexNadirDialog

class ApexNadir:  
    def __init__(self, iface):
        """Constructor to store the QGIS application environment interface reference."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.dlg = None

    def tr(self, message):
        """Translates strings for internationalization requirements."""
        return QCoreApplication.translate('ApexNadir', message)

    def initGui(self):
        """Constructs the visual UI toolbar hooks and sets up the plugin menu shortcuts."""
        icon_path = os.path.join(self.plugin_dir, 'logo.png')
        
        if os.path.exists(icon_path):
            plugin_icon = QIcon(icon_path)
        else:
            plugin_icon = self.iface.mainWindow().style().standardIcon(
                QtWidgets.QStyle.SP_FileDialogContentsView)

        self.action = QAction(
            plugin_icon,
            self.tr('ApexNadir - Extreme Points Explorer'),
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        
        # FIXED: Changed to the correct native PyQGIS method names
        self.iface.addToolBarIcon(self.action)                         # <-- FIXED (was addPluginToolBarIcon)
        self.iface.addPluginToMenu(self.tr('&ApexNadir'), self.action) # <-- Safe universal Plugins Menu
        self.actions.append(self.action)

    def unload(self):
        """Removes the custom action buttons safely when the plugin is deactivated."""
        for action in self.actions:
            # FIXED: Matching cleanup methods
            self.iface.removePluginMenu(self.tr('&ApexNadir'), action)
            self.iface.removeToolBarIcon(action)                      # <-- FIXED (was removePluginToolBarIcon)


    def run(self):
        """Bridges user inputs to the core terrain-masking raster calculation engine."""
        # Initialize dialog on the very first button click execution lifecycle
        if self.dlg is None:
            self.dlg = ApexNadirDialog()  # FIXED: Updated dialog reference
            
            # Configure UI component proxy filters to restrict layer choosing
            self.dlg.polygon_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
            self.dlg.raster_combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
            
            # Repopulate choice items into the UI dropdown box
            self.dlg.mode_combo.clear()
            self.dlg.mode_combo.addItems([self.tr('Maximum Point'), self.tr('Minimum Point')])

        # Display window
        self.dlg.show()
        result = self.dlg.exec_()

        # Run calculation code if the user commits the form panel window dialog
        if result:
            poly_layer = self.dlg.polygon_combo.currentLayer()
            raster_layer = self.dlg.raster_combo.currentLayer()
            mode_text = self.dlg.mode_combo.currentText()
            
            if not poly_layer or not raster_layer:
                QMessageBox.warning(self.iface.mainWindow(), "ApexNadir Error", 
                                    "Please specify both a valid vector Polygon and a DEM Raster layer.")
                return

            # Map the text string to our processing parameter configuration keyword
            mode = 'max' if 'Maximum' in mode_text else 'min'

            # Define projection parameters
            raster_crs = raster_layer.crs()
            poly_crs = poly_layer.crs()
            wgs84_crs = QgsCoordinateReferenceSystem("EPSG:4326")

            transform_to_raster = QgsCoordinateTransform(poly_crs, raster_crs, QgsProject.instance())
            transform_to_wgs84 = QgsCoordinateTransform(raster_crs, wgs84_crs, QgsProject.instance())

            # Map raster layer path into the underlying GDAL pipeline layout
            raster_path = raster_layer.source()
            ds = gdal.Open(raster_path)
            if not ds:
                QMessageBox.critical(self.iface.mainWindow(), "ApexNadir Error", 
                                     "GDAL backend could not access the selected raster dataset directly.")
                return
                
            band = ds.GetRasterBand(1)
            geotransform = ds.GetGeoTransform()
            nodata_val = band.GetNoDataValue()
            x_origin, pixel_width, _, y_origin, _, pixel_height = geotransform

            # Create output temporary memory vector container point layer structure 
            output_name = f"ApexNadir_{mode.upper()}_WGS84"
            output_layer = QgsVectorLayer("Point?crs=EPSG:4326", output_name, "memory")
            provider = output_layer.dataProvider()
            provider.addAttributes([
                QgsField("poly_id", QVariant.Int),
                QgsField("elev_val", QVariant.Double)
            ])
            output_layer.updateFields()

            output_features = []

            # Step through each individual spatial polygon boundaries row record loop
            for poly_feature in poly_layer.getFeatures():
                poly_id = poly_feature.id()
                poly_geom = QgsGeometry(poly_feature.geometry())
                poly_geom.transform(transform_to_raster)
                
                bbox = poly_geom.boundingBox()
                
                # Transform map dimensional extents down to grid array index bounds
                x_min_idx = int((bbox.xMinimum() - x_origin) / pixel_width)
                x_max_idx = int((bbox.xMaximum() - x_origin) / pixel_width)
                
                if pixel_height < 0:
                    y_min_idx = int((bbox.yMaximum() - y_origin) / pixel_height)
                    y_max_idx = int((bbox.yMinimum() - y_origin) / pixel_height)
                else:
                    y_min_idx = int((bbox.xMinimum() - y_origin) / pixel_height)
                    y_max_idx = int((bbox.yMaximum() - y_origin) / pixel_height)
                    
                if y_min_idx > y_max_idx:
                    y_min_idx, y_max_idx = y_max_idx, y_min_idx

                x_min_idx = max(0, min(x_min_idx, ds.RasterXSize - 1))
                x_max_idx = max(0, min(x_max_idx, ds.RasterXSize - 1))
                y_min_idx = max(0, min(y_min_idx, ds.RasterYSize - 1))
                y_max_idx = max(0, min(y_max_idx, ds.RasterYSize - 1))
                
                x_size = (x_max_idx - x_min_idx) + 1
                y_size = (y_max_idx - y_min_idx) + 1
                
                if x_size <= 0 or y_size <= 0:
                    continue
                    
                # Read bounding window array grid subset directly into system RAM memory
                raster_block = band.ReadAsArray(x_min_idx, y_min_idx, x_size, y_size)
                target_val = float('-inf') if mode == 'max' else float('inf')
                target_pixel_raster_crs = None
                
                for r in range(y_size):
                    for c in range(x_size):
                        pixel_val = float(raster_block[r, c])
                        if pixel_val == nodata_val or np.isnan(pixel_val):
                            continue
                            
                        # Recalculate geographic coordinate positioning centers 
                        map_x = x_origin + ((x_min_idx + c) * pixel_width) + (pixel_width / 2.0)
                        map_y = y_origin + ((y_min_idx + r) * pixel_height) + (pixel_height / 2.0)
                        pixel_point = QgsPointXY(map_x, map_y)
                        pixel_geom = QgsGeometry.fromPointXY(pixel_point)
                        
                        # Apply geographic containment validation checks
                        if poly_geom.contains(pixel_geom) or poly_geom.intersects(pixel_geom):
                            if mode == 'max' and pixel_val > target_val:
                                target_val = pixel_val
                                target_pixel_raster_crs = pixel_point
                            elif mode == 'min' and pixel_val < target_val:
                                target_val = pixel_val
                                target_pixel_raster_crs = pixel_point

                # FIXED: Restored the truncated tracking section to map and project to WGS84
                if target_pixel_raster_crs is not None:
                    wgs84_point = transform_to_wgs84.transform(target_pixel_raster_crs)
                    new_feat = QgsFeature()
                    new_feat.setGeometry(QgsGeometry.fromPointXY(wgs84_point))
                    new_feat.setAttributes([poly_id, target_val])
                    output_features.append(new_feat)

            # FIXED: Restored the loading logic to append spatial points to the workspace canvas
            if output_features:
                provider.addFeatures(output_features)
                QgsProject.instance().addMapLayer(output_layer)
                QMessageBox.information(self.iface.mainWindow(), "ApexNadir Success", 
                                        f"Successfully extracted {len(output_features)} extreme locations to WGS84 point layout layer.")
            else:
                QMessageBox.warning(self.iface.mainWindow(), "ApexNadir Complete", 
                                    "Analysis finished, but zero raster cells were captured overlapping the input polygon configurations.")
