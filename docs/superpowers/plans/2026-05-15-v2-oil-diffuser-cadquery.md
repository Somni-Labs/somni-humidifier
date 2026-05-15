# V2 Oil Diffuser — CadQuery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete CadQuery 3D model of the V2 cyberpunk oil diffuser (base + top shell) that renders on cadquery-server and is printable on the QIDI Q2.

**Architecture:** Single CadQuery file (`designs/v2-oil-diffuser.py`) with parametric constants at the top, helper functions for reusable geometry (hex mesh, angular shell), separate `build_base()` and `build_top_shell()` functions, and `show_object()` calls at the bottom for cadquery-server rendering. Each part is displayed in a distinct color for assembly visualization.

**Tech Stack:** CadQuery 2.x, Python 3.10, cadquery-server (`show_object()` / `cq_server.ui`), math module.

**Spec:** `docs/superpowers/specs/2026-05-15-v2-oil-diffuser-redesign.md`

**Repo:** `/home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-humidifier`

---

## File Structure

| File | Purpose |
|------|---------|
| `designs/v2-oil-diffuser.py` | Complete CadQuery model — parametric constants, helpers, base build, top shell build, assembly display |

A single file keeps the model self-contained and easy to load in cadquery-server. If it exceeds ~800 lines, the hex mesh helper could be extracted, but for V2 one file is expected to suffice.

---

## Task 1: Parametric Constants and Outer Shell Foundation

**Files:**
- Create: `designs/v2-oil-diffuser.py`

This task establishes the file, all parametric constants, and the basic angular outer shell for both parts (base + top shell) — the tapered box shape with chamfered panel lines. No internal features yet, just the exterior form.

- [ ] **Step 1: Create file with docstring, imports, and all parametric constants**

```python
"""
Somni Oil Diffuser — V2 "Night City"

Cyberpunk-styled essential oil diffuser with automated scent blending.
Two-part enclosure: base (reservoir + electronics + pumps) and top shell
(bottle wells + mist channel + exhaust port), connected via magnets.

Aesthetic: angular tapered sides, hex mesh panels with LED glow-through,
panel line chamfers, chevron exhaust port.

Loadable by cadquery-server via show_object().
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Tolerances & shell ---
TOL = 0.4                # print tolerance per side (PETG)
WALL = 3.0               # outer wall thickness
WALL_INNER = 2.5         # internal divider walls
FILLET_R = 1.5            # small edge breaks (sharp cyberpunk look, not round)

# --- Overall form factor ---
# Base footprint is a square that tapers inward toward the top.
# The taper angle applies to all four sides.
BASE_W = 160             # base footprint width (X) at Z=0
BASE_D = 160             # base footprint depth (Y) at Z=0
BASE_H = 70              # base height (Z)
TOP_H = 60               # top shell height (Z)
TOTAL_H = BASE_H + TOP_H # 130mm assembled
TAPER_ANGLE = 6          # degrees inward per side

# Derived: top-of-base footprint (where the two parts meet)
import math as _m
_taper_shrink_base = BASE_H * _m.tan(_m.radians(TAPER_ANGLE))
MEETING_W = BASE_W - 2 * _taper_shrink_base  # ~145.3mm
MEETING_D = BASE_D - 2 * _taper_shrink_base

# Derived: top-of-shell footprint (smallest cross-section)
_taper_shrink_top = TOP_H * _m.tan(_m.radians(TAPER_ANGLE))
TOP_W = MEETING_W - 2 * _taper_shrink_top  # ~131.9mm
TOP_D = MEETING_D - 2 * _taper_shrink_top

# --- Panel line (horizontal chamfer break) ---
# A horizontal groove cut around the perimeter at a specific Z height
# to create the "armor seam" look.
PANEL_LINE_Z_BASE = 45       # Z height on base where the panel line sits
PANEL_LINE_Z_TOP = 30        # Z height on top shell (relative to shell bottom)
PANEL_LINE_WIDTH = 1.5       # groove width
PANEL_LINE_DEPTH = 1.0       # groove depth into the wall

# --- Base floor ---
FLOOR_H = 3.0               # solid floor thickness

# --- Wet/dry divider ---
# The base interior is split: wet zone (front/left, ~60%) and dry zone (rear/right, ~40%)
# The divider runs parallel to the Y axis (front-to-back), offset toward the right side.
DIVIDER_X = 20               # X position of divider center (positive = right of center)
                              # Wet zone: left of divider, Dry zone: right of divider

# --- Water reservoir (wet zone) ---
RESERVOIR_DEPTH = BASE_H - FLOOR_H - WALL  # usable depth inside basin
# Capacity target: 200-300ml. With ~95mm x 130mm footprint x 55mm depth ≈ 680ml max,
# so the reservoir easily hits 200-300ml even accounting for pump/atomizer intrusions.

# --- Ultrasonic atomizer ---
ATOMIZER_DIA = 20            # piezo disk diameter
ATOMIZER_DRIVER_W = 35       # driver PCB width (approximate, verify)
ATOMIZER_DRIVER_D = 25       # driver PCB depth
ATOMIZER_MOUNT_DIA = 26      # sealed mounting pad diameter (disk + o-ring)
ATOMIZER_POS_X = -30         # X position in wet zone (left of center)
ATOMIZER_POS_Y = -30         # Y position (toward front)

# --- Peristaltic pumps (5x, mounted on divider wall) ---
PUMP_BODY_W = 38             # pump body width (verify with Kamoer KFS)
PUMP_BODY_D = 58             # pump body depth/length
PUMP_BODY_H = 27             # pump body height
PUMP_COUNT = 5
PUMP_SPACING = 28            # center-to-center along Y axis
PUMP_MOUNT_DEPTH = 20        # how deep the pump pocket is

# --- Electronics bay (dry zone) ---
ESP32_W = 55                 # ESP32 DevKit C V4 footprint
ESP32_D = 28
ESP32_H = 13
MOSFET_W = 25                # IRLZ44N module footprint (each)
MOSFET_D = 20
MOSFET_H = 15
PD_TRIGGER_W = 30            # USB-C PD trigger board
PD_TRIGGER_D = 18
PD_TRIGGER_H = 10
BME280_W = 15                # BME280 breakout
BME280_D = 12
BME280_H = 5

# --- USB-C port (rear panel) ---
USBC_PORT_W = 12             # opening width
USBC_PORT_H = 7              # opening height

# --- Rubber feet ---
FOOT_DIA = 12
FOOT_DEPTH = 1.8
FOOT_INSET = 18              # distance from corner

# --- Magnet pockets (base rim + top shell) ---
MAGNET_DIA = 6               # neodymium disc magnet diameter
MAGNET_H = 3                 # magnet thickness
MAGNET_COUNT = 4             # one per side
MAGNET_INSET = 25            # distance from corners along each edge

# --- Alignment pins ---
PIN_DIA = 4                  # locating pin diameter
PIN_H = 6                    # pin protrusion height
PIN_COUNT = 4                # one per side

# --- Oil bottle wells (top shell) ---
BOTTLE_DIA = 22              # 5ml essential oil bottle diameter
BOTTLE_WELL_DIA = 25         # well diameter (bottle + clearance)
BOTTLE_WELL_DEPTH = 45       # well depth (bottle mostly contained)
BOTTLE_COUNT = 5
BOTTLE_SPACING = 28          # center-to-center
BOTTLE_ROW_Y = 30            # Y offset of bottle row center (toward front)

# --- Tube pass-throughs (base/shell interface) ---
TUBE_HOLE_DIA = 5            # hole for silicone tube + grommet
# One per bottle, positioned near each bottle well

# --- Mist channel (top shell, internal chimney) ---
MIST_CHANNEL_DIA = 30        # internal chimney diameter
MIST_CHANNEL_WALL = 2.5      # chimney wall thickness
# Position: directly above the atomizer in the base
MIST_POS_X = ATOMIZER_POS_X
MIST_POS_Y = ATOMIZER_POS_Y

# --- Water fill port (top surface) ---
FILL_PORT_DIA = 30           # silicone plug hole
FILL_PORT_POS_X = -50        # left side of top, away from bottles and exhaust
FILL_PORT_POS_Y = 30         # toward rear

# --- Exhaust port (top surface, chevron shape) ---
EXHAUST_W = 40               # chevron width
EXHAUST_D = 25               # chevron depth
EXHAUST_POS_X = MIST_POS_X  # centered above mist channel
EXHAUST_POS_Y = MIST_POS_Y

# --- Hex mesh panels ---
HEX_CELL_SIZE = 9            # flat-to-flat distance of each hex cell
HEX_WALL = 1.5               # wall between hex cells
HEX_MARGIN = 5               # margin from panel edges before hex pattern starts

# --- Bottle access hatch (side panel) ---
HATCH_W = 140                # hatch opening width (most of one side)
HATCH_H = 40                 # hatch opening height
HATCH_WALL = 2.0             # hatch panel thickness

# --- LED strip channel ---
LED_CHANNEL_W = 12           # WS2812B strip width
LED_CHANNEL_D = 4            # strip + adhesive depth
# Runs inside the base behind hex mesh panels

# --- SOMNI branding ---
BRAND_DEPTH = 0.6            # deboss depth
```

- [ ] **Step 2: Write the angular tapered shell helper function**

This function creates the core tapered box shape used by both base and top shell. It builds a lofted solid from a larger bottom rectangle to a smaller top rectangle, creating the inward taper on all four sides.

```python
# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def tapered_box(width_bottom, depth_bottom, width_top, depth_top, height):
    """Create an angular tapered box — larger at bottom, smaller at top.
    
    All four sides taper inward linearly. No fillets — sharp cyberpunk edges.
    Returns a solid centered on XY at Z=0..height.
    """
    bottom = (
        cq.Workplane("XY")
        .rect(width_bottom, depth_bottom)
    )
    top = (
        cq.Workplane("XY")
        .workplane(offset=height)
        .rect(width_top, depth_top)
    )
    return bottom.loft(top)
```

**Note:** CadQuery's `loft()` between two rectangular profiles on different Z planes produces the tapered prism. If `loft()` gives issues with rectangular wires, fall back to creating the shape via `Workplane.polyline()` for each face and using `Shell` or construct the solid from 6 planar faces. The implementer should test this first and adapt.

**Fallback approach if loft doesn't work cleanly:**

```python
def tapered_box(width_bottom, depth_bottom, width_top, depth_top, height):
    """Tapered box via polyline extrusion with draft angle."""
    hw_b, hd_b = width_bottom / 2, depth_bottom / 2
    hw_t, hd_t = width_top / 2, depth_top / 2
    
    # Build as a lofted shape between bottom and top rectangles
    result = (
        cq.Workplane("XY")
        .rect(width_bottom, depth_bottom)
        .workplane(offset=height)
        .rect(width_top, depth_top)
        .loft()
    )
    return result
```

- [ ] **Step 3: Write the base outer shell**

```python
def build_base():
    """Build the base unit — outer shell, then cut internal features."""
    
    # Outer tapered shell
    base = tapered_box(BASE_W, BASE_D, MEETING_W, MEETING_D, BASE_H)
    
    # Hollow interior — same taper but offset inward by WALL on each side
    cavity = tapered_box(
        BASE_W - WALL * 2, BASE_D - WALL * 2,
        MEETING_W - WALL * 2, MEETING_D - WALL * 2,
        BASE_H - WALL  # leave top rim solid for now
    ).translate((0, 0, FLOOR_H))
    
    base = base.cut(cavity)
    
    return base
```

- [ ] **Step 4: Write the top shell outer shell**

```python
def build_top_shell():
    """Build the top shell — outer shell, then cut internal features."""
    
    # Outer tapered shell — continues the taper from where the base left off
    shell = tapered_box(MEETING_W, MEETING_D, TOP_W, TOP_D, TOP_H)
    
    # Hollow interior
    cavity = tapered_box(
        MEETING_W - WALL * 2, MEETING_D - WALL * 2,
        TOP_W - WALL * 2, TOP_D - WALL * 2,
        TOP_H - WALL  # solid top surface
    ).translate((0, 0, WALL))  # offset up from shell floor
    
    shell = shell.cut(cavity)
    
    return shell
```

- [ ] **Step 5: Add show_object() calls and test render**

```python
# =============================================================================
# ASSEMBLY — render both parts
# =============================================================================

base = build_base()
top_shell = build_top_shell()

# Position top shell above the base
top_shell = top_shell.translate((0, 0, BASE_H))

show_object(base, name="base",
            options={"color": (0.15, 0.15, 0.18, 0.85)})

show_object(top_shell, name="top_shell",
            options={"color": (0.2, 0.2, 0.25, 0.7)})

# =============================================================================
# ASSEMBLY SUMMARY
# =============================================================================
print("=" * 60)
print("Somni Oil Diffuser V2 — Night City")
print("=" * 60)
print(f"Base:      {BASE_W}×{BASE_D}×{BASE_H}mm (bottom)")
print(f"           {MEETING_W:.1f}×{MEETING_D:.1f}mm (top of base)")
print(f"Top shell: {MEETING_W:.1f}×{MEETING_D:.1f}×{TOP_H}mm (bottom)")
print(f"           {TOP_W:.1f}×{TOP_D:.1f}mm (top)")
print(f"Total:     {TOTAL_H}mm tall")
print(f"Taper:     {TAPER_ANGLE}° per side")
```

- [ ] **Step 6: Copy file to CadQuery server and verify it renders**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null

# Create symlink in /projects root for easy access
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  ln -sf somni-humidifier/designs/v2-oil-diffuser.py /projects/v2-oil-diffuser.py

# Clear any cached pyc
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

Expected: cadquery-server shows two dark angular tapered boxes stacked — the base and top shell. No internal features yet.

- [ ] **Step 7: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): oil diffuser outer shell — tapered angular enclosure

Base and top shell tapered boxes with cyberpunk angular form factor.
160mm square footprint tapering inward at 6° per side.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Panel Lines and Base Internal Layout

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

Add the horizontal panel line grooves (armor seam aesthetic), the wet/dry divider wall inside the base, and the floor.

- [ ] **Step 1: Add panel_line_cut helper function**

```python
def panel_line_cut(body, z_height, total_height, w_bottom, d_bottom, w_top, d_top, width, depth):
    """Cut a horizontal groove around the perimeter at a given Z height.
    
    Interpolates the taper to find the correct XY dimensions at z_height,
    then cuts a shallow rectangular ring.
    """
    # Interpolate dimensions at this Z
    t = z_height / total_height
    w_at_z = w_bottom + t * (w_top - w_bottom)
    d_at_z = d_bottom + t * (d_top - d_bottom)
    
    # Outer ring
    outer = (
        cq.Workplane("XY")
        .workplane(offset=z_height - width / 2)
        .rect(w_at_z + 1, d_at_z + 1)  # slightly oversized to cut through wall
        .extrude(width)
    )
    # Inner ring (what remains after the groove)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=z_height - width / 2 - 0.1)
        .rect(w_at_z - depth * 2, d_at_z - depth * 2)
        .extrude(width + 0.2)
    )
    groove = outer.cut(inner)
    return body.cut(groove)
```

- [ ] **Step 2: Add panel lines to build_base()**

After creating the base shell, before returning:

```python
    # Panel line — horizontal armor seam groove
    base = panel_line_cut(
        base, PANEL_LINE_Z_BASE, BASE_H,
        BASE_W, BASE_D, MEETING_W, MEETING_D,
        PANEL_LINE_WIDTH, PANEL_LINE_DEPTH
    )
```

- [ ] **Step 3: Add wet/dry divider wall inside the base**

```python
    # --- Wet/dry divider wall ---
    # Runs front-to-back (along Y axis), splitting the interior into
    # wet zone (left) and dry zone (right).
    # Interpolate divider position for the taper
    divider_bottom_x = DIVIDER_X
    divider_top_x = DIVIDER_X * (MEETING_W / BASE_W)  # scale with taper
    
    divider = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(divider_bottom_x, 0)
        .rect(WALL_INNER, BASE_D - WALL * 2 - 2)
        .extrude(BASE_H - FLOOR_H - WALL - 2)  # stop below the rim
    )
    base = base.union(divider)
```

- [ ] **Step 4: Sync to CadQuery server and verify**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

Expected: base shows a visible horizontal groove around the perimeter at Z=45mm. Interior shows a divider wall splitting the cavity.

- [ ] **Step 5: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): panel lines and wet/dry divider wall

Horizontal armor seam groove at Z=45mm on base. Internal divider
separates wet zone (reservoir) from dry zone (electronics).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Hex Mesh Panel Helper

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

Create a reusable hex mesh generator that cuts a hexagonal grid of holes through a flat panel. This will be used on the base side walls for ventilation + LED glow-through.

- [ ] **Step 1: Write the hex_mesh_cutout helper function**

```python
def hex_mesh_cutout(width, height, cell_size, wall_thickness, margin):
    """Generate a hex mesh pattern as a single CadQuery solid for cutting.
    
    Creates a grid of hexagonal prisms arranged in a honeycomb pattern.
    The result is a union of all hex cells, extruded 100mm deep (to be used
    as a cutting tool through any wall thickness).
    
    - width, height: bounding rectangle of the mesh area
    - cell_size: flat-to-flat distance of each hex cell
    - wall_thickness: wall between adjacent hex cells
    - margin: inset from edges before the hex pattern starts
    
    Returns a Workplane solid centered at origin, lying in the XY plane,
    extruded along Z. Caller positions and rotates it for the target face.
    """
    pitch = cell_size + wall_thickness  # center-to-center distance
    hex_r = cell_size / 2               # "radius" (flat-to-flat / 2)
    
    # Pointy-top hex vertices (oriented for vertical printing)
    def hex_points(cx, cy):
        pts = []
        for i in range(6):
            angle = math.radians(60 * i + 30)  # pointy-top orientation
            px = cx + hex_r * math.cos(angle)
            py = cy + hex_r * math.sin(angle)
            pts.append((px, py))
        return pts
    
    usable_w = width - margin * 2
    usable_h = height - margin * 2
    
    # Hex grid layout
    row_h = pitch * math.sqrt(3) / 2
    cols = int(usable_w / pitch) + 1
    rows = int(usable_h / row_h) + 1
    
    cells = None
    for row in range(rows):
        for col in range(cols):
            cx = -usable_w / 2 + col * pitch + (pitch / 2 if row % 2 else 0)
            cy = -usable_h / 2 + row * row_h
            
            # Skip cells outside the usable area
            if abs(cx) > usable_w / 2 - hex_r or abs(cy) > usable_h / 2 - hex_r:
                continue
            
            pts = hex_points(cx, cy)
            pts_closed = pts + [pts[0]]
            
            cell = (
                cq.Workplane("XY")
                .polyline(pts_closed)
                .close()
                .extrude(100)  # deep enough to cut through any wall
            )
            
            if cells is None:
                cells = cell
            else:
                cells = cells.union(cell)
    
    if cells is None:
        # Return an empty solid if no cells fit
        return cq.Workplane("XY").box(0.1, 0.1, 0.1)
    
    return cells
```

- [ ] **Step 2: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): hex mesh panel helper function

Reusable honeycomb cutout generator for cyberpunk ventilation panels.
Pointy-top hex orientation for support-free vertical printing.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Base Internal Features — Reservoir, Atomizer, Pumps, Electronics

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

Cut all the functional pockets and mounts into the base interior.

- [ ] **Step 1: Add atomizer mount to build_base()**

```python
    # --- Ultrasonic atomizer mount ---
    # Circular pocket in the reservoir floor for the piezo disk + seal
    atomizer_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H - 0.5)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_MOUNT_DIA / 2)
        .extrude(FLOOR_H + 1)  # cut through floor for wiring
    )
    base = base.cut(atomizer_pocket)
    
    # Atomizer driver board pocket (in dry zone, near divider)
    driver_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_X + WALL_INNER / 2 + ATOMIZER_DRIVER_W / 2 + 3, ATOMIZER_POS_Y)
        .rect(ATOMIZER_DRIVER_W + TOL * 2, ATOMIZER_DRIVER_D + TOL * 2)
        .extrude(15)
    )
    base = base.cut(driver_pocket)
```

- [ ] **Step 2: Add pump mounting pockets**

```python
    # --- Peristaltic pump mounts (5x along divider wall) ---
    pump_start_y = -(PUMP_COUNT - 1) * PUMP_SPACING / 2
    for i in range(PUMP_COUNT):
        py = pump_start_y + i * PUMP_SPACING
        pump_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(DIVIDER_X, py)
            .rect(PUMP_BODY_W + TOL * 2, PUMP_BODY_D + TOL * 2)
            .extrude(PUMP_BODY_H + 2)
        )
        base = base.cut(pump_pocket)
```

- [ ] **Step 3: Add electronics bay pockets (ESP32, MOSFETs, PD trigger, BME280)**

```python
    # --- Electronics bay (dry zone, right side) ---
    # ESP32 pocket — rear of dry zone
    esp_x = DIVIDER_X + WALL_INNER / 2 + 10 + ESP32_W / 2
    esp_y = BASE_D / 4  # toward rear
    esp_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(esp_x, esp_y)
        .rect(ESP32_W + TOL * 2, ESP32_D + TOL * 2)
        .extrude(ESP32_H + 3)
    )
    base = base.cut(esp_pocket)
    
    # 5x MOSFET module pockets — in a row below ESP32
    mosfet_start_y = esp_y - ESP32_D / 2 - 8 - MOSFET_D / 2
    for i in range(5):
        mx = esp_x - ESP32_W / 2 + 5 + i * (MOSFET_W + 3)
        mosfet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(mx, mosfet_start_y)
            .rect(MOSFET_W + TOL * 2, MOSFET_D + TOL * 2)
            .extrude(MOSFET_H + 2)
        )
        base = base.cut(mosfet_pocket)
    
    # USB-C PD trigger pocket — near rear wall
    pd_x = esp_x
    pd_y = esp_y + ESP32_D / 2 + 5 + PD_TRIGGER_D / 2
    pd_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(pd_x, pd_y)
        .rect(PD_TRIGGER_W + TOL * 2, PD_TRIGGER_D + TOL * 2)
        .extrude(PD_TRIGGER_H + 2)
    )
    base = base.cut(pd_pocket)
```

- [ ] **Step 4: Add USB-C port cutout in rear wall**

```python
    # --- USB-C port cutout (rear wall) ---
    usbc_cutout = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 5)
        .center(pd_x, BASE_D / 2)
        .rect(USBC_PORT_W, USBC_PORT_H)
        .extrude(WALL + 2)
    )
    base = base.cut(usbc_cutout)
```

- [ ] **Step 5: Add rubber feet pockets**

```python
    # --- Rubber feet (4 corners) ---
    for fx, fy in [
        (-BASE_W / 2 + FOOT_INSET, -BASE_D / 2 + FOOT_INSET),
        ( BASE_W / 2 - FOOT_INSET, -BASE_D / 2 + FOOT_INSET),
        (-BASE_W / 2 + FOOT_INSET,  BASE_D / 2 - FOOT_INSET),
        ( BASE_W / 2 - FOOT_INSET,  BASE_D / 2 - FOOT_INSET),
    ]:
        foot = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(fx, fy)
            .circle(FOOT_DIA / 2)
            .extrude(FOOT_DEPTH + 0.5)
        )
        base = base.cut(foot)
```

- [ ] **Step 6: Add LED strip channel inside base (behind hex mesh area)**

```python
    # --- LED strip channel (runs along the left and front walls) ---
    # Horizontal channel inside the base wall for WS2812B strip
    led_channel = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H - 15)  # near top of base
        .center(-BASE_W / 4, -BASE_D / 2 + WALL + LED_CHANNEL_D / 2)
        .rect(BASE_W / 2, LED_CHANNEL_D)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_channel)
```

- [ ] **Step 7: Sync to CadQuery server and verify**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

Expected: base interior shows atomizer hole, pump pockets along divider, ESP32/MOSFET/PD pockets in electronics bay, USB-C cutout on rear, rubber feet on bottom.

- [ ] **Step 8: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): base internals — reservoir, atomizer, pumps, electronics bay

Atomizer mount, 5 pump pockets on divider, ESP32/MOSFET/PD trigger
pockets, USB-C port cutout, rubber feet, LED strip channel.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Base Hex Mesh Panels and Magnet/Pin Mounts

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

Cut hex mesh ventilation into the base side walls (dry zone side) and add magnet pockets + alignment pin posts on the base rim.

- [ ] **Step 1: Cut hex mesh into two base side panels**

The hex mesh goes on the two walls flanking the electronics/dry zone — the right wall and the rear wall. The hex pattern needs to be rotated and positioned to align with each wall face.

```python
    # --- Hex mesh panels (electronics bay ventilation + LED glow) ---
    # Right side wall — hex mesh for dry zone ventilation
    right_hex = hex_mesh_cutout(
        width=BASE_D * 0.6,   # span ~60% of the side
        height=BASE_H * 0.5,  # upper half of the wall
        cell_size=HEX_CELL_SIZE,
        wall_thickness=HEX_WALL,
        margin=HEX_MARGIN
    )
    # Rotate to face the right wall (YZ plane) and position
    right_hex = (
        right_hex
        .rotate((0, 0, 0), (0, 0, 1), 90)   # align with Y axis
        .rotate((0, 0, 0), (0, 1, 0), 90)    # lay flat on YZ
        .translate((BASE_W / 2 - WALL / 2, 10, BASE_H * 0.55))
    )
    base = base.cut(right_hex)
    
    # Front wall — hex mesh panel
    front_hex = hex_mesh_cutout(
        width=BASE_W * 0.4,
        height=BASE_H * 0.5,
        cell_size=HEX_CELL_SIZE,
        wall_thickness=HEX_WALL,
        margin=HEX_MARGIN
    )
    front_hex = (
        front_hex
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .rotate((0, 0, 0), (0, 0, 1), 90)
        .translate((0, -BASE_D / 2 + WALL / 2, BASE_H * 0.55))
    )
    base = base.cut(front_hex)
```

- [ ] **Step 2: Add magnet pockets on the base rim**

```python
    # --- Magnet pockets (top rim of base) ---
    # 4 magnets, one centered on each side edge of the rim
    rim_z = BASE_H - MAGNET_H  # magnet sits flush with top of base
    magnet_positions = [
        (0, -MEETING_D / 2 + MAGNET_INSET),    # front
        (0,  MEETING_D / 2 - MAGNET_INSET),     # rear
        (-MEETING_W / 2 + MAGNET_INSET, 0),     # left
        ( MEETING_W / 2 - MAGNET_INSET, 0),     # right
    ]
    for mx, my in magnet_positions:
        mag_pocket = (
            cq.Workplane("XY")
            .workplane(offset=rim_z)
            .center(mx, my)
            .circle(MAGNET_DIA / 2 + TOL)
            .extrude(MAGNET_H + 0.5)
        )
        base = base.cut(mag_pocket)
```

- [ ] **Step 3: Add alignment pin posts on the base rim**

```python
    # --- Alignment pins (protrude from base rim) ---
    # 4 pins at the corners (offset from magnet positions)
    pin_positions = [
        (-MEETING_W / 2 + 15, -MEETING_D / 2 + 15),
        ( MEETING_W / 2 - 15, -MEETING_D / 2 + 15),
        (-MEETING_W / 2 + 15,  MEETING_D / 2 - 15),
        ( MEETING_W / 2 - 15,  MEETING_D / 2 - 15),
    ]
    for px, py in pin_positions:
        pin = (
            cq.Workplane("XY")
            .workplane(offset=BASE_H)
            .center(px, py)
            .circle(PIN_DIA / 2)
            .extrude(PIN_H)
        )
        base = base.union(pin)
```

- [ ] **Step 4: Sync and verify**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

Expected: hex mesh visible on right and front walls. 4 magnet pockets on rim. 4 alignment pins sticking up from corners.

- [ ] **Step 5: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): hex mesh panels, magnet pockets, alignment pins on base

Cyberpunk hex ventilation on right and front walls. 4 magnet pockets
and 4 alignment pins on the base rim for top shell connection.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: Top Shell Internal Features — Bottles, Mist Channel, Fill Port

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

Cut the bottle wells, mist chimney channel, water fill port, and tube pass-throughs into the top shell.

- [ ] **Step 1: Add bottle wells to build_top_shell()**

```python
    # --- Oil bottle wells (5 upright bottles in a row) ---
    bottle_start_x = -(BOTTLE_COUNT - 1) * BOTTLE_SPACING / 2
    for i in range(BOTTLE_COUNT):
        bx = bottle_start_x + i * BOTTLE_SPACING
        by = BOTTLE_ROW_Y
        
        # Cylindrical well from top surface down
        well = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - BOTTLE_WELL_DEPTH)
            .center(bx, by)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(BOTTLE_WELL_DEPTH + 1)  # +1 to cut through top surface
        )
        shell = shell.cut(well)
        
        # Tube pass-through hole at bottom of each well
        tube_hole = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(bx, by)
            .circle(TUBE_HOLE_DIA / 2)
            .extrude(TOP_H - BOTTLE_WELL_DEPTH + 2)
        )
        shell = shell.cut(tube_hole)
```

- [ ] **Step 2: Add mist channel (internal chimney)**

```python
    # --- Mist channel (internal chimney from bottom to exhaust port) ---
    # Vertical tube from shell floor to just below the exhaust port
    mist_outer = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(MIST_POS_X, MIST_POS_Y)
        .circle(MIST_CHANNEL_DIA / 2 + MIST_CHANNEL_WALL)
        .extrude(TOP_H - WALL)
    )
    mist_bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.5)
        .center(MIST_POS_X, MIST_POS_Y)
        .circle(MIST_CHANNEL_DIA / 2)
        .extrude(TOP_H + 1)
    )
    shell = shell.union(mist_outer)
    shell = shell.cut(mist_bore)
```

- [ ] **Step 3: Add water fill port**

```python
    # --- Water fill port (silicone plug hole on top surface) ---
    fill_port = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - WALL - 0.5)
        .center(FILL_PORT_POS_X, FILL_PORT_POS_Y)
        .circle(FILL_PORT_DIA / 2)
        .extrude(WALL + 1)
    )
    shell = shell.cut(fill_port)
    
    # Slight lip/chamfer around the fill port for the plug to seat against
    fill_lip = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - 1.5)
        .center(FILL_PORT_POS_X, FILL_PORT_POS_Y)
        .circle(FILL_PORT_DIA / 2 + 2)
        .circle(FILL_PORT_DIA / 2)
        .extrude(1.5)
    )
    shell = shell.union(fill_lip)
```

- [ ] **Step 4: Add matching magnet pockets and pin holes in the top shell floor**

```python
    # --- Magnet pockets (matching base) ---
    for mx, my in magnet_positions:
        mag_pocket = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(mx, my)
            .circle(MAGNET_DIA / 2 + TOL)
            .extrude(MAGNET_H + 0.5)
        )
        shell = shell.cut(mag_pocket)
    
    # --- Alignment pin holes (matching base pins) ---
    for px, py in pin_positions:
        pin_hole = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(px, py)
            .circle(PIN_DIA / 2 + TOL)
            .extrude(PIN_H + 1)
        )
        shell = shell.cut(pin_hole)
```

**Note:** `magnet_positions` and `pin_positions` must be moved to module-level constants (out of `build_base()`) so both functions can reference them. The implementer should extract them during this task.

- [ ] **Step 5: Sync and verify**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

Expected: top shell shows 5 bottle wells visible from above, mist chimney tube in the interior, fill port hole on top, magnet pockets and pin holes on the bottom face.

- [ ] **Step 6: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): top shell internals — bottle wells, mist channel, fill port

5 bottle wells, mist chimney, water fill port with lip, matching
magnet pockets and alignment pin holes.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: Exhaust Port and Bottle Access Hatch

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

The two hero design features: the angular chevron exhaust vent on top and the hinged bottle access hatch opening on the side.

- [ ] **Step 1: Add chevron exhaust port to build_top_shell()**

```python
    # --- Exhaust port (chevron/diamond shape on top surface) ---
    # Angular diamond opening centered above the mist channel
    ehw = EXHAUST_W / 2
    ehd = EXHAUST_D / 2
    chevron_pts = [
        (EXHAUST_POS_X, EXHAUST_POS_Y - ehd),          # bottom point
        (EXHAUST_POS_X + ehw, EXHAUST_POS_Y),           # right point
        (EXHAUST_POS_X, EXHAUST_POS_Y + ehd),           # top point
        (EXHAUST_POS_X - ehw, EXHAUST_POS_Y),           # left point
        (EXHAUST_POS_X, EXHAUST_POS_Y - ehd),           # close
    ]
    exhaust_cut = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - WALL - 0.5)
        .polyline(chevron_pts)
        .close()
        .extrude(WALL + 1)
    )
    shell = shell.cut(exhaust_cut)
    
    # Internal vanes (2-3 thin angled fins inside the exhaust to direct mist)
    vane_count = 3
    vane_spacing = EXHAUST_W / (vane_count + 1)
    for i in range(vane_count):
        vx = EXHAUST_POS_X - EXHAUST_W / 2 + (i + 1) * vane_spacing
        vane = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL - 8)
            .center(vx, EXHAUST_POS_Y)
            .rect(1.2, EXHAUST_D * 0.6)
            .extrude(8)
        )
        shell = shell.union(vane)
```

- [ ] **Step 2: Add bottle access hatch cutout**

The hatch is a rectangular opening on the front face of the top shell, allowing access to the bottle wells. The actual hinge mechanism would be a separate printed piece, but the opening in the shell needs to be defined.

```python
    # --- Bottle access hatch (front face of top shell) ---
    # Rectangular opening on the front wall aligned with the bottle row
    # Interpolate wall position at hatch center height for the taper
    hatch_z_center = TOP_H * 0.55
    t = hatch_z_center / TOP_H
    wall_y_at_hatch = -(MEETING_D / 2 + t * (TOP_D / 2 - MEETING_D / 2))
    
    hatch_cut = (
        cq.Workplane("XY")
        .workplane(offset=(TOP_H - HATCH_H) / 2)
        .center(0, -MEETING_D / 2)
        .rect(HATCH_W, WALL + 2)
        .extrude(HATCH_H)
    )
    shell = shell.cut(hatch_cut)
    
    # Thin lip around the hatch opening (the hatch door sits against this)
    hatch_lip_depth = 1.5
    hatch_lip = (
        cq.Workplane("XY")
        .workplane(offset=(TOP_H - HATCH_H) / 2 - hatch_lip_depth)
        .center(0, -MEETING_D / 2 + WALL)
        .rect(HATCH_W + 4, hatch_lip_depth)
        .extrude(HATCH_H + hatch_lip_depth * 2)
    )
    # Only keep the frame, not the fill
    hatch_lip_inner = (
        cq.Workplane("XY")
        .workplane(offset=(TOP_H - HATCH_H) / 2 - hatch_lip_depth - 0.1)
        .center(0, -MEETING_D / 2 + WALL)
        .rect(HATCH_W - 2, hatch_lip_depth + 0.2)
        .extrude(HATCH_H + hatch_lip_depth * 2 + 0.2)
    )
    hatch_frame = hatch_lip.cut(hatch_lip_inner)
    shell = shell.union(hatch_frame)
```

- [ ] **Step 3: Add panel line to top shell**

```python
    # --- Panel line on top shell ---
    shell = panel_line_cut(
        shell, PANEL_LINE_Z_TOP, TOP_H,
        MEETING_W, MEETING_D, TOP_W, TOP_D,
        PANEL_LINE_WIDTH, PANEL_LINE_DEPTH
    )
```

- [ ] **Step 4: Sync and verify**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

Expected: diamond/chevron exhaust opening on top with internal vanes. Rectangular hatch opening on the front face with a seating lip. Panel line groove on the top shell.

- [ ] **Step 5: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): exhaust port and bottle access hatch

Chevron exhaust with internal directional vanes. Bottle access hatch
on front face with seating lip. Panel line on top shell.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: SOMNI Branding and Final Assembly Polish

**Files:**
- Modify: `designs/v2-oil-diffuser.py`

Add the debossed SOMNI branding on the rear panel, finalize the assembly summary printout, and ensure both parts display correctly.

- [ ] **Step 1: Add SOMNI deboss to build_base()**

```python
    # --- SOMNI branding (debossed on rear panel) ---
    # Simple rectangular deboss area — actual text would need STL import
    # or CadQuery text() if available. For now, a shallow rectangular
    # recess marks where the branding goes.
    brand_w = 35
    brand_h = 8
    brand = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H * 0.3)
        .center(0, BASE_D / 2 - BRAND_DEPTH / 2)
        .rect(brand_w, WALL)
        .extrude(brand_h)
    )
    # Only cut BRAND_DEPTH into the wall
    brand_inner = (
        cq.Workplane("XY")
        .workplane(offset=BASE_H * 0.3)
        .center(0, BASE_D / 2 - BRAND_DEPTH)
        .rect(brand_w, WALL)
        .extrude(brand_h)
    )
    brand_cut = brand.cut(brand_inner)
    base = base.cut(brand_cut)
```

Alternatively, if CadQuery `text()` is available on the server:

```python
    # SOMNI text deboss (if CadQuery text() works on the server)
    try:
        brand_text = (
            cq.Workplane("XZ")
            .workplane(offset=BASE_D / 2)
            .center(0, BASE_H * 0.35)
            .text("SOMNI", 8, -BRAND_DEPTH, font="sans-serif")
        )
        base = base.cut(brand_text)
    except Exception:
        pass  # Fall back to rectangular recess if text() unavailable
```

The implementer should try the `text()` approach first and fall back to the rectangle.

- [ ] **Step 2: Update assembly summary print block**

```python
# =============================================================================
# ASSEMBLY SUMMARY
# =============================================================================
print("=" * 60)
print("Somni Oil Diffuser V2 — Night City")
print("=" * 60)
print()
print(f"Base:       {BASE_W}×{BASE_D}×{BASE_H}mm")
print(f"Top shell:  {MEETING_W:.1f}×{MEETING_D:.1f}×{TOP_H}mm")
print(f"Total:      {TOTAL_H}mm tall")
print(f"Taper:      {TAPER_ANGLE}° per side")
print()
print("Base features:")
print(f"  Reservoir:    wet zone left of X={DIVIDER_X}mm divider")
print(f"  Atomizer:     ø{ATOMIZER_MOUNT_DIA}mm at ({ATOMIZER_POS_X}, {ATOMIZER_POS_Y})")
print(f"  Pumps:        {PUMP_COUNT}x along divider, {PUMP_SPACING}mm spacing")
print(f"  Electronics:  ESP32 + {5}x MOSFET + PD trigger in dry zone")
print(f"  Hex mesh:     {HEX_CELL_SIZE}mm cells on right + front walls")
print(f"  Magnets:      {MAGNET_COUNT}x ø{MAGNET_DIA}×{MAGNET_H}mm on rim")
print()
print("Top shell features:")
print(f"  Bottles:      {BOTTLE_COUNT}x ø{BOTTLE_WELL_DIA}mm wells, {BOTTLE_SPACING}mm spacing")
print(f"  Mist channel: ø{MIST_CHANNEL_DIA}mm chimney")
print(f"  Fill port:    ø{FILL_PORT_DIA}mm at ({FILL_PORT_POS_X}, {FILL_PORT_POS_Y})")
print(f"  Exhaust:      {EXHAUST_W}×{EXHAUST_D}mm chevron with {3} vanes")
print(f"  Hatch:        {HATCH_W}×{HATCH_H}mm on front face")
print()
print(f"Print bed: {BASE_W}mm fits QIDI Q2 (245mm)")
```

- [ ] **Step 3: Final sync to CadQuery server**

```bash
cat designs/v2-oil-diffuser.py | kubectl exec -i cadquery-server-77c8579495-qpll8 \
  -n utilities -c cadquery-server -- tee /projects/somni-humidifier/designs/v2-oil-diffuser.py > /dev/null
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc
```

- [ ] **Step 4: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit --author="Gerardo Palacios <gerardo.palacios@somni-labs.io>" \
  -m "feat(v2): SOMNI branding and assembly summary

Debossed branding on rear panel. Complete assembly summary output
with all dimensions and feature positions.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

- [ ] **Step 5: Push to main**

```bash
git push origin main
```

---

## Task 9: Sync to CadQuery Server and Verify Full Assembly

**Files:** None (verification only)

- [ ] **Step 1: Pull latest on CadQuery server**

```bash
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  git -C /projects/somni-humidifier pull --ff-only origin main
```

- [ ] **Step 2: Clear cache and verify symlink**

```bash
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  rm -f /projects/__pycache__/v2-oil-diffuser.cpython-310.pyc

kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  ls -la /projects/v2-oil-diffuser.py

# If symlink doesn't exist, create it:
kubectl exec cadquery-server-77c8579495-qpll8 -n utilities -- \
  ln -sf somni-humidifier/designs/v2-oil-diffuser.py /projects/v2-oil-diffuser.py
```

- [ ] **Step 3: Verify render loads without errors**

Open cadquery-server and load `v2-oil-diffuser.py`. Verify:
- Both parts render (base in dark gray, top shell in lighter gray)
- Top shell positioned above the base
- Hex mesh visible on base side walls
- Chevron exhaust visible on top
- Bottle wells visible from above
- Panel lines visible on both parts
- No geometry errors in the console

---

## Implementation Notes for the Executing Agent

1. **CadQuery loft() behavior:** The `tapered_box()` helper uses `loft()` between two rectangular profiles. If this produces errors (CadQuery can be finicky with loft), use the polyline-based fallback: build the 4 trapezoidal side faces individually and create a solid from the shell. Test early.

2. **Hex mesh performance:** Unioning hundreds of small hex cells can be slow. If performance is bad, consider using a single `compound()` instead of sequential `union()` calls, or reduce the hex mesh area.

3. **Module-level constants:** The `magnet_positions` and `pin_positions` lists are needed by both `build_base()` and `build_top_shell()`. Define them as module-level constants near the other parametric values.

4. **Taper math:** All internal features that reference wall positions need to account for the taper. At any Z height, the wall position is interpolated between the bottom and top footprint. The `panel_line_cut()` helper shows the pattern.

5. **CadQuery server sync:** After each task, copy the file to the server using `tee` (not `kubectl cp`, which has ownership issues). Always clear the `__pycache__` pyc file.

6. **Commit author:** Always use `--author="Gerardo Palacios <gerardo.palacios@somni-labs.io>"`.
