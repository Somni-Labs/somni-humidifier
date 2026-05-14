"""Render a CadQuery design file to STL.

The design files in `designs/` import `from cq_server.ui import ui, show_object`
to be loadable by cadquery-server. That package is unmaintained and breaks
on modern pip. This script provides a lightweight equivalent: it stubs
`cq_server.ui`, runs the design module, captures every object passed to
`show_object()`, and exports each as STL.

Usage:
    python tools/render_design.py designs/v1-humidifier-base.py
    # → writes designs/stl/v1-humidifier-base__<name>.stl for each show_object call

By default outputs go to designs/stl/. Pass --out-dir to override.
"""

import argparse
import importlib
import os
import runpy
import sys
import types
from pathlib import Path


def install_stub(captured: list) -> None:
    """Install a fake cq_server.ui module whose show_object appends to
    `captured` as (name, options, shape) tuples."""

    cq_server = types.ModuleType("cq_server")
    ui_mod = types.ModuleType("cq_server.ui")

    def show_object(shape, name=None, options=None, **kwargs):
        captured.append((name or f"object_{len(captured) + 1}",
                         options or {},
                         shape))

    # The original ui object is used as a decorator/marker by cq-server.
    # A no-op callable is sufficient for our purposes.
    def ui(*_args, **_kwargs):
        return None

    ui_mod.show_object = show_object
    ui_mod.ui = ui
    cq_server.ui = ui_mod
    sys.modules["cq_server"] = cq_server
    sys.modules["cq_server.ui"] = ui_mod


def shape_to_compound(shape):
    """Return an OCP TopoDS shape for export. Handles cadquery Workplane,
    Shape, and Compound inputs."""
    # Late import — cadquery is heavy and may not be present in some
    # subprocess contexts.
    import cadquery as cq
    if isinstance(shape, cq.Workplane):
        return shape.val()
    return shape


def export_stl(shape, out_path: Path, tolerance: float, angular_tolerance: float) -> None:
    import cadquery as cq
    s = shape_to_compound(shape)
    cq.exporters.export(
        s,
        str(out_path),
        exportType="STL",
        tolerance=tolerance,
        angularTolerance=angular_tolerance,
    )


def render(design_path: Path, out_dir: Path, tolerance: float,
           angular_tolerance: float) -> list[Path]:
    captured: list = []
    install_stub(captured)

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = design_path.stem

    # runpy executes the design file in its own globals, exactly like
    # `python <file>` would, with the stubbed cq_server.ui already in
    # sys.modules.
    runpy.run_path(str(design_path), run_name="__main__")

    written: list[Path] = []
    for name, _opts, shape in captured:
        # Sanitize name for filesystem.
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        out = out_dir / f"{stem}__{safe}.stl"
        print(f"  exporting → {out}")
        export_stl(shape, out, tolerance, angular_tolerance)
        written.append(out)
    return written


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("design", type=Path, help="path to the CadQuery design .py file")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="output directory (default: designs/stl/)")
    p.add_argument("--tolerance", type=float, default=0.1,
                   help="STL linear tolerance in mm (default 0.1)")
    p.add_argument("--angular-tolerance", type=float, default=0.1,
                   help="STL angular tolerance in radians (default 0.1)")
    args = p.parse_args()

    design = args.design.resolve()
    if not design.exists():
        print(f"error: {design} not found", file=sys.stderr)
        return 2

    out_dir = (args.out_dir or design.parent / "stl").resolve()

    print(f"rendering {design.name}")
    print(f"  output dir: {out_dir}")
    written = render(design, out_dir, args.tolerance, args.angular_tolerance)
    if not written:
        print("warning: no show_object() calls captured — nothing to export",
              file=sys.stderr)
        return 1
    print(f"done — {len(written)} STL file(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
