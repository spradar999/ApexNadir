#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ApexNadir Packaging Script
This script zips the necessary files of the ApexNadir QGIS plugin into a 
distribution ZIP file. The zip contains a parent 'ApexNadir' directory, 
which is required for proper installation inside QGIS.
"""

import os
import zipfile

# Define the name of the plugin and the resulting zip file
PLUGIN_NAME = "ApexNadir"
OUTPUT_ZIP = f"{PLUGIN_NAME}.zip"

# Core files and assets that must be packaged
FILES_TO_PACKAGE = [
    "__init__.py",
    "apex_nadir_dialog.py",
    "main.py",
    "metadata.txt",
    "logo.png",
    "LICENSE",
    "README.md",
]

def create_package():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(current_dir, OUTPUT_ZIP)
    
    # Remove old package if it exists
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
            print(f"🧹 Removed existing old package: {OUTPUT_ZIP}")
        except Exception as e:
            print(f"⚠️ Error removing old package: {e}")
            return

    print(f"📦 Packaging {PLUGIN_NAME} for distribution...")
    
    try:
        # Create ZIP archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in FILES_TO_PACKAGE:
                file_path = os.path.join(current_dir, file_name)
                
                if not os.path.exists(file_path):
                    # Handle optional metadata or standard files if they don't exist
                    print(f"⚠️ Warning: File '{file_name}' not found. Skipping...")
                    continue
                
                # QGIS expects all files inside a single root folder matching the plugin name
                archive_name = os.path.join(PLUGIN_NAME, file_name)
                zipf.write(file_path, archive_name)
                print(f"  + Added {file_name} -> {archive_name}")
                
        print(f"\n🎉 Success! Created QGIS-compliant plugin package: {OUTPUT_ZIP}")
        print(f"📍 Location: {zip_path}")
        print(f"💡 To install in QGIS: Plugins -> Manage and Install Plugins -> Install from ZIP -> Select {OUTPUT_ZIP}")
        
    except Exception as e:
        print(f"❌ Failed to package plugin: {e}")

if __name__ == "__main__":
    create_package()
