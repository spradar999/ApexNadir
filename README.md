# 🏔️ ApexNadir — QGIS Extreme Points Explorer

[![QGIS Version](https://img.shields.io/badge/QGIS-3.0%2B-blue.svg?logo=qgis&logoColor=white)](https://qgis.org)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)](#)

**ApexNadir** is a high-performance QGIS plugin written in Python. It bridges native vector geometry spatial processing with raw raster calculations using GDAL. It allows GIS professionals, surveyors, and terrain analysts to effortlessly locate, extract, and map the absolute highest elevation peaks (**Apex**) or lowest elevation valleys (**Nadir**) within complex vector polygon boundaries.

---

## 📖 Table of Contents
- [✨ Key Features](#-key-features)
- [⚙️ How It Works](#%EF%B8%8F-how-it-works)
- [📋 System Requirements](#-system-requirements)
- [🚀 Installation](#-installation)
  - [Manual Installation](#manual-installation)
  - [Distribution Packages (ZIP)](#distribution-packages-zip)
- [📖 Step-by-Step Usage](#-step-by-step-usage)
- [🛠️ Development & Packaging](#%EF%B8%8F-development--packaging)
- [📄 License](#-license)

---

## ✨ Key Features

- **Extreme Terrain Pinpointing:** Automatically maps and converts raw digital elevation model (DEM) pixels inside vector polygons into an output vector point layer.
- **Dual Analytical Modes:** Toggle between locating **Maximum Point (Apex)** or **Minimum Point (Nadir)** in a single click.
- **Geographic Containment Validation:** Performs spatial intersection checks to ensure selected elevation cells fall strictly inside or intersect polygon boundaries.
- **Coordinate Reference System (CRS) Safety:** On-the-fly coordinate transformation from the vector's spatial CRS directly to the raster's grid layout, and outputs coordinates projected to standard **WGS84 (EPSG:4326)**.
- **High-Performance Processing:** Leverages GDAL and NumPy for fast cell processing in RAM, avoiding expensive filesystem reads.

---

## ⚙️ How It Works

```
[ Vector Polygons ]         [ DEM Raster (elevation) ]
         │                              │
         ▼                              ▼
  CRS Projection   ────────►   Coordinate Mapping
         │                              │
         └─────────────┬────────────────┘
                       ▼
            GDAL Cell-by-Cell Scan
       (Filters NoData & intersection)
                       │
                       ▼
         Identify Max (Apex) / Min (Nadir)
                       │
                       ▼
       Convert Coordinates to WGS 84
                       │
                       ▼
      [ Output Point Layer (with Elev) ]
```

1. **Spatial Alignment:** Translates the vector boundary's geometry into the raster's native coordinate system.
2. **Sub-grid Scanning:** Calculates index bounds for the raster subset intersected by the polygon. Reads the data block directly into memory via GDAL.
3. **Terrain Masking:** Filters out null `NoData` raster cells and performs ray-casting containment tests to ensure matched raster cell center points lie inside the polygon boundary.
4. **Extreme Point Identification:** Evaluates the array using NumPy arrays to identify the global minimum/maximum, then projects the coordinate of that pixel to WGS84 (EPSG:4326) and appends attributes containing the source `poly_id` and calculated `elev_val`.

---

## 📋 System Requirements

* **QGIS Version:** 3.0 or later (Fully supports PyQt5, Python 3.12+, and Qt6 environments)
* **Libraries:** `gdal`, `numpy` (both are shipped natively with QGIS)

---

## 🚀 Installation

### Manual Installation
You can deploy this plugin locally on your computer using these simple steps:

1. Locate your QGIS profile plugins directory:
   * **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   * **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   * **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

2. Inside this folder, create a directory named `ApexNadir`.
3. Copy the following files from this repository directly into that folder:
   * `__init__.py`
   * `apex_nadir_dialog.py`
   * `main.py`
   * `metadata.txt`
   * `logo.png`

4. Restart QGIS. Open **Plugins ➔ Manage and Install Plugins...** and search for **ApexNadir**. Check the box to activate the plugin.

### Distribution Packages (ZIP)
To install from a packaged archive:
1. Obtain the packaged `ApexNadir.zip` file (see [Development & Packaging](#%EF%B8%8F-development--packaging)).
2. In QGIS, navigate to **Plugins ➔ Manage and Install Plugins...**
3. Select the **Install from ZIP** tab.
4. Browse to select your downloaded `ApexNadir.zip` and click **Install Plugin**.

---

## 📖 Step-by-Step Usage

1. Load your spatial datasets into QGIS:
   * A **Vector Polygon** layer representing your analysis zones (e.g., watersheds, property lines, administrative boundaries).
   * A **DEM Raster** layer containing elevation grid data (e.g., GeoTIFF).

2. Click on the 🏔️ **ApexNadir** icon in the main QGIS toolbar, or navigate to **Plugins ➔ ApexNadir ➔ ApexNadir - Extreme Points Explorer**.

3. In the dialog box that appears:
   * Select your **Polygon Layer**.
   * Select your **DEM Raster Layer**.
   * Select the **Target Operation Point** (`Maximum Point` for highest peaks or `Minimum Point` for lowest points).

   <p align="center">
     <em>Dialog UI showing clean selection layout</em>
   </p>

4. Click **OK** to run.
5. The calculations will run, and a brand new memory point vector layer named **`ApexNadir_MAX_WGS84`** or **`ApexNadir_MIN_WGS84`** will automatically load onto your canvas, styled with:
   * `poly_id`: The ID of the matching boundary polygon.
   * `elev_val`: The exact elevation value of that peak/valley cell.

---

## 🛠️ Development & Packaging

A packaging script `package.py` is included at the root to bundle your development files into a QGIS-compliant ZIP package ready for distribution.

### Packaging the Plugin
To package the plugin, execute this command from your terminal:
```bash
python package.py
```
This will automatically parse the workspace files, package them inside a root-level `ApexNadir` folder, and generate a clean **`ApexNadir.zip`** ready to be uploaded to QGIS repositories or distributed directly.

---

## 📄 License

This project is licensed under the **GNU General Public License (GPL) Version 3** or later. See the [LICENSE](LICENSE) file for the full license text. Feel free to copy, modify, and redistribute this software in accordance with GPL copyleft provisions.

---
*Developed by [Raghavendra S P](mailto:spradar999@gmail.com)*
