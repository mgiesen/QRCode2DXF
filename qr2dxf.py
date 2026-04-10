#!/usr/bin/env python3
"""Generates QR codes as DXF files with clean, closed outline contours."""

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import ezdxf
import qrcode


def generate_qr(text):
    """Generates a QR code and returns the QR object, black modules grid, and grid size."""
    qr = qrcode.QRCode(border=0)
    qr.add_data(text)
    qr.make()
    matrix = qr.get_matrix()

    grid = set()
    for row, line in enumerate(matrix):
        for col, cell in enumerate(line):
            if cell:
                grid.add((col, row))

    grid_size = len(matrix)
    return qr, grid, grid_size


def trace_contours(grid):
    """Traces closed contour polygons from the module grid.

    Finds all boundary edges between black and non-black cells and chains them
    into closed polygons. Produces outer contours and hole contours (e.g. the
    white center of finder patterns).
    """
    edges = defaultdict(list)

    for (cx, cy) in grid:
        if (cx, cy - 1) not in grid:
            a, b = (cx, cy), (cx + 1, cy)
            edges[a].append(b)
        if (cx, cy + 1) not in grid:
            a, b = (cx + 1, cy + 1), (cx, cy + 1)
            edges[a].append(b)
        if (cx - 1, cy) not in grid:
            a, b = (cx, cy + 1), (cx, cy)
            edges[a].append(b)
        if (cx + 1, cy) not in grid:
            a, b = (cx + 1, cy), (cx + 1, cy + 1)
            edges[a].append(b)

    contours = []
    while edges:
        start = next(iter(edges))
        polygon = [start]
        current = start

        while True:
            targets = edges[current]
            next_pt = targets.pop()
            if not targets:
                del edges[current]
            if next_pt == start:
                break
            polygon.append(next_pt)
            current = next_pt

        contours.append(polygon)

    return contours


def write_dxf(contours, grid_size, size_mm, output_path):
    """Writes contour polygons as closed polylines into a DXF file."""
    scale = size_mm / grid_size

    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4  # mm
    msp = doc.modelspace()

    for polygon in contours:
        points = [(x * scale, (grid_size - y) * scale) for x, y in polygon]
        msp.add_lwpolyline(points, close=True)

    doc.saveas(output_path)


def write_png(qr, output_path):
    """Writes the QR code as a PNG reference image."""
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)


def process_one(text, output_dir, basename, size_mm):
    """Generates a QR code and writes DXF + PNG to output_dir."""
    qr, grid, grid_size = generate_qr(text)

    if not grid:
        print(f"No black modules found for: {text}", file=sys.stderr)
        return

    dxf_path = output_dir / f"{basename}.dxf"
    png_path = output_dir / f"{basename}.png"

    contours = trace_contours(grid)
    write_dxf(contours, grid_size, size_mm, str(dxf_path))
    write_png(qr, str(png_path))
    print(f"{dxf_path} ({len(grid)} modules -> {len(contours)} contours, {size_mm}x{size_mm}mm)")


def main():
    parser = argparse.ArgumentParser(description="QR code to DXF for Autodesk Inventor")
    parser.add_argument("text", nargs="?", help="Text/URL for the QR code")
    parser.add_argument("--size", type=float, default=30,
                        help="Edge length of the QR code in mm (default: 30)")
    parser.add_argument("--batch", help="Text file with one URL per line")
    args = parser.parse_args()

    output_dir = Path("output")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    if args.batch:
        lines = Path(args.batch).read_text().strip().splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            process_one(line, output_dir, f"qr_code_{i + 1:03d}", args.size)
    elif args.text:
        process_one(args.text, output_dir, "qr_code", args.size)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
