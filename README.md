# QRCode2DXF

A small Python script that generates QR codes as DXF files with clean, closed outline contours — ready to extrude in CAD programs like Autodesk Inventor.

## Background

I needed a simple workflow to engrave QR codes into surfaces in Autodesk Inventor (e.g. for 3D printing). The most direct way in Inventor is to import a DXF into a sketch and extrude from there. This script automates that: it generates a QR code, traces the outer contours of the black regions, and writes them as closed polylines into a DXF — no internal edges, so direct extrusion just works.

![QR code extruded in Autodesk Inventor](images/inventor-extrude-preview.webp)

## Dependencies

- [qrcode](https://pypi.org/project/qrcode/) — QR code generator
- [ezdxf](https://ezdxf.readthedocs.io/) — DXF library for Python

## Setup

```bash
# Clone the repository
git clone https://github.com/mgiesen/QRCode2DXF.git

# Open the repository
cd QRCode2DXF

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Single QR code (default 30x30mm)
python qr2dxf.py "https://example.com" -o example.dxf

# With edge length in mm
python qr2dxf.py "https://example.com" -o example.dxf --size 50

# Batch: text file with one URL per line
python qr2dxf.py --batch urls.txt --size 40
```
