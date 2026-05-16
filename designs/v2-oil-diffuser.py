"""
Somni Oil Diffuser — V3.3 "Compact Grid"

Cyberpunk-styled essential oil diffuser with automated scent blending.
130x104mm rectangular footprint (fits QIDI Q2 245x255mm bed).

REAL-WORLD BOM — all component dimensions verified from sourcing research:
  Pumps:     5× JIHPUMP WX3 micro peristaltic (23×35×25mm, 3.7-6V) in 2+3 pump grid
  Atomizer:  20mm/113KHz piezo + 35×25mm driver board (5V, 250-400mA)
  MCU:       ESP32 DevKit (55×28mm) — WiFi, 6× GPIO for MOSFETs
  MOSFETs:   8-ch MOSFET driver board (50×26mm, 3.3V logic-level, using 6 ch)
  Power:     USB-C → CH224K PD trigger (24×18mm) → 12V → MP1584EN buck (22×17mm) → 5V
  LEDs:      WS2812B strip (12mm wide, 5V), continuous perimeter loop
  Buttons:   2× TTP223 capacitive touch (11×15mm) — power + mist intensity
  Sensor:    Capacitive water level sensor on divider wall

Three-part enclosure connected via magnets:
  BASE  — holds reservoir, atomizer, pumps (two zones)
  TRAY  — lift-out electronics shelf, sits above pumps in center zone
  SHELL — two-zone functional lid: fill chute + mist chimney, bottles + storage

Bottles hang cap-down from the top shell ceiling in a 3+2 bottle grid. Lift top shell off for access.
Electronics tray lifts out for pump access (building Legos assembly).

Base layout (two zones, left to right):
  WET ZONE    (left)    — water reservoir + atomizer mount
  CENTER ZONE (right)   — two levels: 2+3 pump grid (bottom) + electronics tray (top)

Top shell layout (two zones, matching base divider):
  MIST+FILL        (left)   — mist chimney + chevron exhaust + water fill chute
  BOTTLES+STORAGE  (right)  — 5 bottle wells in 3+2 bottle grid (ceiling) + open storage below

Power architecture: 5V single-rail (all loads are 5V)
  USB-C PD (12V) → buck converter → 5V rail
  Alt: USB-C 5V/3A direct (no PD needed for light use)

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
FILLET_R = 1.5            # small edge breaks

# --- Overall form factor ---
BASE_W = 130             # base footprint width (X) at Z=0 — rectangular
BASE_D = 104             # base footprint depth (Y) at Z=0
BASE_H = 70              # base height (Z)
TOP_H = 60               # top shell height (Z)
TOTAL_H = BASE_H + TOP_H # 130mm assembled
TAPER_ANGLE = 6          # degrees inward per side

# Derived taper dimensions
_taper_shrink_base = BASE_H * math.tan(math.radians(TAPER_ANGLE))
MEETING_W = BASE_W - 2 * _taper_shrink_base
MEETING_D = BASE_D - 2 * _taper_shrink_base

_taper_shrink_top = TOP_H * math.tan(math.radians(TAPER_ANGLE))
TOP_W = MEETING_W - 2 * _taper_shrink_top
TOP_D = MEETING_D - 2 * _taper_shrink_top

# --- Panel lines ---
PANEL_LINE_Z_BASE = 45
PANEL_LINE_Z_TOP = 30
PANEL_LINE_WIDTH = 1.5
PANEL_LINE_DEPTH = 1.0

# --- Base floor ---
FLOOR_H = 3.0

# --- Zone divider ---
# One divider wall runs parallel to Y axis, creating two zones.
# Wet zone: X < DIVIDER_WET_X — water reservoir + atomizer
# Center zone: X > DIVIDER_WET_X — two-level: pumps + electronics tray
DIVIDER_WET_X = -21.8    # left divider (wet/center boundary)

# --- Water reservoir (wet zone) ---
RESERVOIR_DEPTH = BASE_H - FLOOR_H - WALL

# --- Ultrasonic atomizer ---
ATOMIZER_DIA = 20
ATOMIZER_DRIVER_W = 35
ATOMIZER_DRIVER_D = 25
ATOMIZER_MOUNT_DIA = 24  # 20mm piezo + 2mm rim each side
ATOMIZER_POS_X = -38.1       # centered in narrower wet zone
ATOMIZER_POS_Y = 0           # centered front-to-back

# --- Peristaltic pumps (5x JIHPUMP WX3 micro, 2+3 grid in center zone) ---
PUMP_BODY_W = 35             # WX3 length oriented along X
PUMP_BODY_D = 23             # WX3 width oriented along Y
PUMP_BODY_H = 25             # WX3 height
PUMP_LEFT_COL_COUNT = 2      # near divider
PUMP_RIGHT_COL_COUNT = 3     # near outer wall
PUMP_TOTAL = PUMP_LEFT_COL_COUNT + PUMP_RIGHT_COL_COUNT
PUMP_COL_GAP = 3             # gap between columns (X)
PUMP_ROW_GAP = 3             # gap between pumps in same column (Y)

# --- Bottle wells (top shell, 3+2 grid) ---
# Bottles hang cap-down from the top shell ceiling in the right zone.
# Wells are recessed 3mm into the ceiling with retaining rings.
BOTTLE_DIA = 22
BOTTLE_CAP_DIA = 18
BOTTLE_HEIGHT = 55
BOTTLE_LEFT_ROW_COUNT = 3    # near divider (row 1)
BOTTLE_RIGHT_ROW_COUNT = 2   # near outer wall (row 2)
BOTTLE_TOTAL = BOTTLE_LEFT_ROW_COUNT + BOTTLE_RIGHT_ROW_COUNT
BOTTLE_WELL_DEPTH = 3        # recess into ceiling
BOTTLE_WELL_DIA = 22 + 2 * 0.4 + 2  # 24.8mm
BOTTLE_ROW_GAP = 2           # gap between rows (X)
BOTTLE_Y_SPACING = BOTTLE_WELL_DIA + 2.5  # center-to-center in Y within a row

# --- Electronics (on lift-out tray in center zone upper level) ---
ESP32_W = 55                 # ESP32 DevKit V1 long dimension (along Y on tray)
ESP32_D = 28                 # ESP32 DevKit V1 short dimension (across X on tray)
ESP32_H = 13
MOSFET_BOARD_W = 50          # board long dimension (placed along Y on tray)
MOSFET_BOARD_D = 26          # board short dimension (across X on tray)
MOSFET_BOARD_H = 12
MOSFET_COUNT = 6             # using 6 of 8 channels
PD_TRIGGER_W = 24            # CH224K module
PD_TRIGGER_D = 18
PD_TRIGGER_H = 8
BUCK_CONV_W = 22             # MP1584EN buck converter
BUCK_CONV_D = 17
BUCK_CONV_H = 5
ATOMIZER_DRIVER_H = 6
BME280_W = 15
BME280_D = 12
BME280_H = 5

# --- Electronics tray ---
TRAY_WALL = 2.0
TRAY_FLOOR = 2.0
TRAY_LEG_W = 5.0
TRAY_LEG_INSET = 8.0
TRAY_CLEARANCE = 0.5
TRAY_Z = FLOOR_H + PUMP_BODY_H + 4  # tray floor Z = 32mm
TRAY_H = 20
TRAY_TAB_W = 8.0
TRAY_TAB_D = 2.0
TRAY_TAB_H = 4.0

# --- PCB retention features ---
RAIL_GROOVE_W = 1.2
RAIL_GROOVE_D = 1.5
RAIL_CLEARANCE = 0.3
RAIL_LIFT = 2.0
RAIL_CHAMFER = 0.5

SNAP_NUB_W = 1.5
SNAP_NUB_H = 1.0
SNAP_NUB_ANGLE = 45

# Pump shelf ledges
PUMP_LEDGE_LIP = 1.0
PUMP_LEDGE_H = 1.5

# --- Wire channel network ---
CHANNEL_W = 3.0
CHANNEL_D = 3.0
CHANNEL_NOTCH_W = 3.0
CHANNEL_NOTCH_H = 3.0

# Cross-divider wire ports
WIRE_PORT_W = 5.0
WIRE_PORT_H = 4.0
WIRE_PORT_Z_ABOVE_WATER = FLOOR_H + 45  # above max water level (43mm) + margin

# --- Assembly channels (V3.3) ---
# Tube troughs (divider wall side)
TUBE_TROUGH_W = 10.0         # combined divider-face trough internal width (5 tubes)
TUBE_TROUGH_D = 4.0          # depth (cut INTO divider wall face)
TUBE_TROUGH_WALL = 1.5       # trough wall thickness
TUBE_TROUGH_Z_TOP = 29.0     # top of trough (1mm above pump tops)
TUBE_TROUGH_Z_BOT = 20.0     # bottom of trough (below lowest holes)
TUBE_TROUGH_Y_SPAN = 60.0    # Y=-30 to Y=+30
TUBE_BRIDGE_Z = 29.0         # horizontal bridge height (above pump tops)
TUBE_BRIDGE_DEPTH = 2.0      # shallow groove depth (tray acts as lid)
TUBE_BRIDGE_WALL = 1.0       # low walls for bridge

# Wire bus (outer wall side)
WIRE_BUS_W = 6.0             # main bus channel internal width
WIRE_BUS_D = 4.0             # main bus channel depth
WIRE_BUS_WALL = 1.5          # bus wall thickness
WIRE_SPUR_W = 4.0            # pump power spur width
WIRE_SPUR_D = 3.0            # pump power spur depth
WIRE_RISER_W = 6.0           # vertical riser width
WIRE_RISER_D = 4.0           # vertical riser depth

# Clip guides (top shell)
CLIP_GUIDE_ID = 5.0          # internal diameter
CLIP_GUIDE_WALL = 1.5        # clip wall thickness
CLIP_GUIDE_COUNT = 3         # number of clip guides on inlet run

# --- Tubing channels (base floor) ---
TUBE_CHANNEL_W = 4           # collector channel width
TUBE_CHANNEL_D = 3           # collector channel depth
TUBE_SPUR_W = 3              # spur from pump to collector
TUBE_HOLE_DIA = 6            # pass-through hole in divider

# --- Capacitive touch buttons ---
TOUCH_BTN_W = 15
TOUCH_BTN_D = 11
TOUCH_BTN_H = 2
TOUCH_ZONE_DIA = 20
TOUCH_BTN_COUNT = 2
TOUCH_BTN_SPACING = 35
TOUCH_BTN_Y = -25            # was -40, moved inward to fit 130x104 footprint

# --- USB-C port ---
USBC_PORT_W = 12
USBC_PORT_H = 7

# --- Rubber feet ---
FOOT_DIA = 12
FOOT_DEPTH = 1.8
FOOT_INSET = 15

# --- Magnet pockets ---
MAGNET_DIA = 6
MAGNET_H = 3
MAGNET_INSET = 20

# --- Alignment pins ---
PIN_DIA = 4
PIN_H = 6

# --- Mist channel (top shell) ---
MIST_CHANNEL_DIA = 25
MIST_CHANNEL_WALL = 2.5
MIST_POS_X = ATOMIZER_POS_X
MIST_POS_Y = ATOMIZER_POS_Y

# --- Water fill chute (top shell, left zone) ---
FILL_CHUTE_TOP_W = 25
FILL_CHUTE_TOP_D = 30
FILL_CHUTE_BOT_W = 14
FILL_CHUTE_BOT_D = 20
FILL_CHUTE_POS_X = ATOMIZER_POS_X
FILL_CHUTE_POS_Y = 18        # was 30, moved inward to fit 130x104 footprint
FILL_CHUTE_LIP_H = 3

# --- Top shell zone divider ---
TOP_DIVIDER_WET_X = DIVIDER_WET_X

# --- Storage compartment (top shell, right zone) ---
STORAGE_LID_RECESS = 2.0
STORAGE_WALL = 2.0

# --- Exhaust port ---
EXHAUST_W = 30
EXHAUST_D = 20
EXHAUST_POS_X = MIST_POS_X
EXHAUST_POS_Y = MIST_POS_Y

# --- Hex mesh ---
HEX_CELL_SIZE = 9
HEX_WALL = 1.5
HEX_MARGIN = 5

# --- LED strip channel ---
LED_CHANNEL_W = 12
LED_CHANNEL_D = 5

# --- SOMNI branding ---
BRAND_DEPTH = 0.8
BRAND_FONT_SIZE = 12
BRAND_SUB_SIZE = 6


# =============================================================================
# SHARED POSITIONS
# =============================================================================

# Magnet positions — 4 total (one per side)
magnet_positions = [
    (0, -MEETING_D / 2 + MAGNET_INSET),     # front
    (0,  MEETING_D / 2 - MAGNET_INSET),      # back
    (-MEETING_W / 2 + MAGNET_INSET, 0),      # left
    ( MEETING_W / 2 - MAGNET_INSET, 0),      # right
]

# Alignment pins — 2 diagonal (for keying)
pin_positions = [
    (-MEETING_W / 2 + 15, -MEETING_D / 2 + 15),   # front-left
    ( MEETING_W / 2 - 15,  MEETING_D / 2 - 15),    # rear-right
]

# Pump grid positions (2+3 layout)
# Center zone boundaries at meeting line
_center_inner_left = DIVIDER_WET_X + WALL_INNER / 2
_center_inner_right = MEETING_W / 2 - WALL

# Column X positions
_pump_left_col_cx = _center_inner_left + 1 + PUMP_BODY_W / 2
_pump_right_col_cx = _pump_left_col_cx + PUMP_BODY_W / 2 + PUMP_COL_GAP + PUMP_BODY_W / 2

# Per-column Y positions (centered at Y=0)
_pump_left_col_ys = [
    -(PUMP_LEFT_COL_COUNT - 1) / 2 * (PUMP_BODY_D + PUMP_ROW_GAP) + i * (PUMP_BODY_D + PUMP_ROW_GAP)
    for i in range(PUMP_LEFT_COL_COUNT)
]
_pump_right_col_ys = [
    -(PUMP_RIGHT_COL_COUNT - 1) / 2 * (PUMP_BODY_D + PUMP_ROW_GAP) + i * (PUMP_BODY_D + PUMP_ROW_GAP)
    for i in range(PUMP_RIGHT_COL_COUNT)
]

# Flat list of all pump positions: (x, y) for iteration
pump_grid_positions = (
    [(_pump_left_col_cx, y) for y in _pump_left_col_ys] +
    [(_pump_right_col_cx, y) for y in _pump_right_col_ys]
)

# All pump Y positions (union of both columns, for tube pass-throughs)
_all_pump_ys = sorted(set(_pump_left_col_ys + _pump_right_col_ys))

# Bottle grid positions (3+2 layout in top shell)
_top_center_left = DIVIDER_WET_X + WALL_INNER / 2
_top_center_right = MEETING_W / 2 - WALL
_bottle_row1_cx = _top_center_left + 4 + BOTTLE_WELL_DIA / 2   # row 1 near divider
_bottle_row2_cx = _bottle_row1_cx + BOTTLE_WELL_DIA / 2 + BOTTLE_ROW_GAP + BOTTLE_WELL_DIA / 2

_bottle_row1_ys = [
    -(BOTTLE_LEFT_ROW_COUNT - 1) / 2 * BOTTLE_Y_SPACING + i * BOTTLE_Y_SPACING
    for i in range(BOTTLE_LEFT_ROW_COUNT)
]
# Row 2 bottles nest between row 1: at Y positions matching row 1 extremes
_bottle_row2_ys = [_bottle_row1_ys[0], _bottle_row1_ys[-1]]  # Y=-26, Y=+26

# Flat list of all bottle positions: (x, y) for iteration
bottle_grid_positions = (
    [(_bottle_row1_cx, y) for y in _bottle_row1_ys] +
    [(_bottle_row2_cx, y) for y in _bottle_row2_ys]
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def tapered_box(width_bottom, depth_bottom, width_top, depth_top, height):
    """Angular tapered box via loft. Z=0..height, centered on XY."""
    return (
        cq.Workplane("XY")
        .rect(width_bottom, depth_bottom)
        .workplane(offset=height)
        .rect(width_top, depth_top)
        .loft()
    )


def panel_line_cut(body, z_height, total_height, w_bottom, d_bottom, w_top, d_top, width, depth):
    """Horizontal groove around perimeter — 'armor seam' panel line."""
    t = z_height / total_height
    w_at_z = w_bottom + t * (w_top - w_bottom)
    d_at_z = d_bottom + t * (d_top - d_bottom)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=z_height - width / 2)
        .rect(w_at_z + 1, d_at_z + 1)
        .extrude(width)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=z_height - width / 2 - 0.1)
        .rect(w_at_z - depth * 2, d_at_z - depth * 2)
        .extrude(width + 0.2)
    )
    return body.cut(outer.cut(inner))


def hex_mesh_cutout(width, height, cell_size, wall_thickness, margin):
    """Honeycomb hex pattern, pointy-top orientation. Extruded 100mm along Z.

    Uses CadQuery Compound to batch all hex cells into a single solid in one
    boolean pass instead of iterative union (which is O(n²) slow).
    """
    pitch = cell_size + wall_thickness
    row_height = pitch * math.sqrt(3) / 2
    hex_radius = cell_size / 2
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin
    cols = int(usable_w / pitch) + 1
    rows = int(usable_h / row_height) + 1

    # Collect all hex cell solids into a list, then combine once
    cell_solids = []
    for row in range(rows):
        for col in range(cols):
            cx = -usable_w / 2 + col * pitch + (pitch / 2 if row % 2 else 0)
            cy = -usable_h / 2 + row * row_height
            if abs(cx) > usable_w / 2 - hex_radius or abs(cy) > usable_h / 2 - hex_radius:
                continue
            pts = [(cx + hex_radius * math.cos(math.radians(60 * i + 30)),
                     cy + hex_radius * math.sin(math.radians(60 * i + 30)))
                    for i in range(6)]
            cell = (cq.Workplane("XY").moveTo(pts[0][0], pts[0][1])
                    .polyline(pts[1:]).close().extrude(100))
            cell_solids.append(cell)

    if not cell_solids:
        return cq.Workplane("XY").box(0.1, 0.1, 0.1)

    # Batch combine: union the first with a compound of the rest
    result = cell_solids[0]
    if len(cell_solids) > 1:
        from cadquery import Compound
        compound = Compound.makeCompound(
            [s.val() for s in cell_solids[1:]]
        )
        result = result.union(cq.Workplane("XY").newObject([compound]))
    return result


# =============================================================================
# BUILD BASE
# =============================================================================

def build_base():
    """Two-zone base: wet (left) | center two-level (right).

    Center zone lower level: 2+3 pump grid.
    Center zone upper level: lift-out electronics tray (separate part).
    """

    # --- Outer tapered shell ---
    base = tapered_box(BASE_W, BASE_D, MEETING_W, MEETING_D, BASE_H)

    # Hollow interior
    cavity = tapered_box(
        BASE_W - WALL * 2, BASE_D - WALL * 2,
        MEETING_W - WALL * 2, MEETING_D - WALL * 2,
        BASE_H - FLOOR_H
    ).translate((0, 0, FLOOR_H))
    base = base.cut(cavity)

    # --- Panel line ---
    base = panel_line_cut(
        base, PANEL_LINE_Z_BASE, BASE_H,
        BASE_W, BASE_D, MEETING_W, MEETING_D,
        PANEL_LINE_WIDTH, PANEL_LINE_DEPTH
    )

    # --- Divider wall (one, creating two zones) ---
    divider_h = BASE_H - FLOOR_H - WALL - 2

    divider_left = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_WET_X, 0)
        .rect(WALL_INNER, BASE_D - WALL * 2 - 2)
        .extrude(divider_h)
    )
    base = base.union(divider_left)

    # --- WET ZONE (left of DIVIDER_WET_X) ---

    # Atomizer mount — through-hole in floor for piezo disk
    atomizer_pocket = (
        cq.Workplane("XY")
        .workplane(offset=-0.1)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_MOUNT_DIA / 2)
        .extrude(FLOOR_H + 0.2)
    )
    base = base.cut(atomizer_pocket)

    # Atomizer seal ring (raised rim around the mount)
    seal_ring = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_MOUNT_DIA / 2 + 2)
        .circle(ATOMIZER_MOUNT_DIA / 2)
        .extrude(2)
    )
    base = base.union(seal_ring)

    # Water level sensor mounting pad (on outside of left divider wall)
    sensor_pad = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 15)
        .center(DIVIDER_WET_X - WALL_INNER / 2 - 0.5, 0)
        .rect(1, 20)
        .extrude(25)
    )
    base = base.cut(sensor_pad)

    # --- CENTER ZONE (right of DIVIDER_WET_X) ---

    # 2+3 pump grid pockets
    for px, py in pump_grid_positions:
        pump_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(px, py)
            .rect(PUMP_BODY_W, PUMP_BODY_D)
            .extrude(PUMP_BODY_H + 2)
        )
        base = base.cut(pump_pocket)

        # Shelf ledges on +/-Y walls of pump pocket
        for _ledge_side in [-1, 1]:
            ledge = (
                cq.Workplane("XY")
                .workplane(offset=FLOOR_H)
                .center(px,
                        py + _ledge_side * (PUMP_BODY_D / 2 - PUMP_LEDGE_LIP / 2))
                .rect(PUMP_BODY_W - 4, PUMP_LEDGE_LIP)
                .extrude(PUMP_LEDGE_H)
            )
            base = base.union(ledge)

    # Tube pass-through holes in divider (pump output -> reservoir)
    # One hole per unique pump Y position
    for tube_y in _all_pump_ys:
        tube_out = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + divider_h - 8)
            .center(DIVIDER_WET_X, tube_y)
            .circle(TUBE_HOLE_DIA / 2)
            .extrude(10)
        )
        base = base.cut(tube_out)

    # === CENTER ZONE UPPER LEVEL — tray support ledges ===
    interior_y_min = -(MEETING_D / 2 - WALL - 2)
    interior_y_max = (MEETING_D / 2 - WALL - 2)
    _center_y_span = interior_y_max - interior_y_min
    _tray_ledge_w = 4.0
    _tray_ledge_h = 3.0

    # Left divider ledge (wet side of center zone)
    tray_ledge_left = (
        cq.Workplane("XY")
        .workplane(offset=TRAY_Z - _tray_ledge_h)
        .center(DIVIDER_WET_X + WALL_INNER / 2 + _tray_ledge_w / 2, 0)
        .rect(_tray_ledge_w, _center_y_span - 4)
        .extrude(_tray_ledge_h)
    )
    base = base.union(tray_ledge_left)

    # Right outer wall ledge (inner face of right wall)
    tray_ledge_right = (
        cq.Workplane("XY")
        .workplane(offset=TRAY_Z - _tray_ledge_h)
        .center(MEETING_W / 2 - WALL - _tray_ledge_w / 2, 0)
        .rect(_tray_ledge_w, _center_y_span - 4)
        .extrude(_tray_ledge_h)
    )
    base = base.union(tray_ledge_right)

    # Registration tab slots (2 on left divider, 2 on right outer wall)
    _tab_y_positions = [interior_y_min + 15, interior_y_max - 15]
    for tab_y in _tab_y_positions:
        # Left divider tab slot
        tab_slot_left = (
            cq.Workplane("XY")
            .workplane(offset=TRAY_Z - 1)
            .center(DIVIDER_WET_X + WALL_INNER / 2 + TRAY_TAB_D / 2, tab_y)
            .rect(TRAY_TAB_D + 0.5, TRAY_TAB_W + 0.5)
            .extrude(TRAY_TAB_H + 1)
        )
        base = base.cut(tab_slot_left)

        # Right outer wall tab slot
        tab_slot_right = (
            cq.Workplane("XY")
            .workplane(offset=TRAY_Z - 1)
            .center(MEETING_W / 2 - WALL - TRAY_TAB_D / 2, tab_y)
            .rect(TRAY_TAB_D + 0.5, TRAY_TAB_W + 0.5)
            .extrude(TRAY_TAB_H + 1)
        )
        base = base.cut(tab_slot_right)

    # --- USB-C port cutout (rear wall of center zone) ---
    _usbc_x = (_pump_left_col_cx + _pump_right_col_cx) / 2
    _usbc_z = TRAY_Z + TRAY_FLOOR + 3
    _t_usbc = _usbc_z / BASE_H
    _d_at_usbc = BASE_D + _t_usbc * (MEETING_D - BASE_D)
    usbc_cutout = (
        cq.Workplane("XY")
        .workplane(offset=_usbc_z)
        .center(_usbc_x, _d_at_usbc / 2)
        .rect(USBC_PORT_W, WALL + 2)
        .extrude(USBC_PORT_H)
    )
    base = base.cut(usbc_cutout)

    # === WIRE ROUTING ===
    # Atomizer wires must stay DRY. Water level reaches Z ≈ FLOOR_H + 40 = 43mm.
    # Route: atomizer → UP divider wall (sealed vertical channel on wet side)
    #        → cross divider ABOVE water line at Z=48 → center zone → tray
    #
    # Other wires (pump power, LED, buttons) stay in the center zone / tray
    # and never contact water.

    # --- Atomizer vertical wire chase (wet side of divider wall) ---
    # Sealed channel running up the wet face of the divider from floor to above water
    _atm_chase_z_bot = FLOOR_H
    _atm_chase_z_top = FLOOR_H + 45  # 48mm — above max water level (43mm) + margin
    _atm_chase_x = DIVIDER_WET_X - WALL_INNER / 2 - CHANNEL_W / 2  # wet side of divider
    atm_vertical_chase = (
        cq.Workplane("XY")
        .box(CHANNEL_W, CHANNEL_W, _atm_chase_z_top - _atm_chase_z_bot)
        .translate((_atm_chase_x, 0,
                    (_atm_chase_z_bot + _atm_chase_z_top) / 2))
    )
    base = base.cut(atm_vertical_chase)

    # --- Atomizer horizontal run (wet zone floor, from atomizer to divider) ---
    # This short run is on the floor and WILL be submerged — wires are waterproof
    # silicone-jacketed. The channel just keeps them tidy.
    _atm_floor_x_start = ATOMIZER_POS_X
    _atm_floor_x_end = _atm_chase_x
    atm_floor_run = (
        cq.Workplane("XY")
        .box(abs(_atm_floor_x_end - _atm_floor_x_start), CHANNEL_W, CHANNEL_D)
        .translate(((_atm_floor_x_start + _atm_floor_x_end) / 2, 0,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_floor_run)

    # --- Cross-divider wire port (ABOVE water line) ---
    _wire_port_z_above_water = FLOOR_H + 45  # Z=48, above water level
    atm_cross_port = (
        cq.Workplane("XY")
        .workplane(offset=_wire_port_z_above_water)
        .center(DIVIDER_WET_X, 0)
        .rect(WALL_INNER + 2, WIRE_PORT_W)
        .extrude(WIRE_PORT_H)
    )
    base = base.cut(atm_cross_port)

    # --- Pump power wire drop (tray floor → pump level) ---
    # Wires drop from tray through a slot in the tray floor area
    # to reach pumps below. Runs along the gap between left-column pumps at Y≈0.
    _pump_wire_drop_z_top = TRAY_Z
    _pump_wire_drop_z_bot = FLOOR_H + PUMP_BODY_H + 1  # just above pump tops
    pump_wire_drop = (
        cq.Workplane("XY")
        .box(CHANNEL_W, 6, _pump_wire_drop_z_top - _pump_wire_drop_z_bot)
        .translate((_pump_left_col_cx, 0,
                    (_pump_wire_drop_z_top + _pump_wire_drop_z_bot) / 2))
    )
    base = base.cut(pump_wire_drop)

    # === ASSEMBLY CHANNELS — TUBE ROUTING (divider wall side) ===

    # --- Combined divider-face tube trough ---
    # All 5 outlet tubes converge here before entering their respective pass-through holes.
    # Cut INTO the center-zone face of the divider wall (does not protrude into center zone).
    # Open face points +X (toward center zone for press-fit assembly).
    _divider_cz_face_x = DIVIDER_WET_X + WALL_INNER / 2
    _trough_cx = _divider_cz_face_x + TUBE_TROUGH_D / 2  # center of cut in X
    _trough_height = TUBE_TROUGH_Z_TOP - TUBE_TROUGH_Z_BOT
    tube_trough = (
        cq.Workplane("XY")
        .box(TUBE_TROUGH_D, TUBE_TROUGH_Y_SPAN, _trough_height)
        .translate((_trough_cx, 0,
                    (TUBE_TROUGH_Z_TOP + TUBE_TROUGH_Z_BOT) / 2))
    )
    base = base.cut(tube_trough)

    # Trough side walls (left and right in Y, to keep tubes contained)
    for _tw_side in [-1, 1]:
        _tw_y = _tw_side * (TUBE_TROUGH_Y_SPAN / 2 + TUBE_TROUGH_WALL / 2)
        trough_wall = (
            cq.Workplane("XY")
            .box(TUBE_TROUGH_D + TUBE_TROUGH_WALL * 2, TUBE_TROUGH_WALL, _trough_height)
            .translate((_trough_cx, _tw_y,
                        (TUBE_TROUGH_Z_TOP + TUBE_TROUGH_Z_BOT) / 2))
        )
        base = base.union(trough_wall)

    # --- Horizontal tube bridge (right-column pumps → divider) ---
    # Runs at Z=29 (1mm above pump tops) from right-column pump edge to divider.
    # Shallow open groove — tray bottom above (Z=32) acts as the "lid".
    # 3 right-column pump outlet tubes drop into this bridge and run to divider trough.
    _bridge_x_start = _pump_right_col_cx + PUMP_BODY_W / 2 + 2  # just past right pump edge
    _bridge_x_end = _divider_cz_face_x + TUBE_TROUGH_D  # meets the trough
    _bridge_length = abs(_bridge_x_start - _bridge_x_end)
    _bridge_cx = (_bridge_x_start + _bridge_x_end) / 2
    _bridge_w_internal = 10.0  # holds 3× 3mm tubes

    tube_bridge = (
        cq.Workplane("XY")
        .box(_bridge_length, _bridge_w_internal, TUBE_BRIDGE_DEPTH)
        .translate((_bridge_cx, 0, TUBE_BRIDGE_Z + TUBE_BRIDGE_DEPTH / 2))
    )
    base = base.cut(tube_bridge)

    # Bridge side walls (low, since tray is the lid)
    for _bw_side in [-1, 1]:
        _bw_y = _bw_side * (_bridge_w_internal / 2 + TUBE_BRIDGE_WALL / 2)
        bridge_wall = (
            cq.Workplane("XY")
            .box(_bridge_length, TUBE_BRIDGE_WALL, TUBE_BRIDGE_WALL + TUBE_BRIDGE_DEPTH)
            .translate((_bridge_cx, _bw_y,
                        TUBE_BRIDGE_Z + (TUBE_BRIDGE_WALL + TUBE_BRIDGE_DEPTH) / 2))
        )
        base = base.union(bridge_wall)

    # === ASSEMBLY CHANNELS — WIRE ROUTING (outer wall side) ===

    # --- Main wire bus (inner face of outer wall, floor level) ---
    # Carries: 5× pump power pairs + LED strip feed + USB-C power
    # Sits on the floor, open-top U-channel, open face points -X (toward interior).
    _outer_wall_inner_x = MEETING_W / 2 - WALL
    _wire_bus_y_span = 70.0  # Y=-35 to Y=+35, covers all pump positions
    _wire_bus_cx = _outer_wall_inner_x - WIRE_BUS_D / 2  # recessed into wall face

    wire_bus = (
        cq.Workplane("XY")
        .box(WIRE_BUS_D, _wire_bus_y_span, WIRE_BUS_W)
        .translate((_wire_bus_cx, 0, FLOOR_H + WIRE_BUS_W / 2))
    )
    base = base.cut(wire_bus)

    # --- Pump power spur channels (floor level, from bus to each pump) ---
    # Right-column pumps: 1-2mm stubs (pumps are near outer wall)
    # Left-column pumps: ~55mm runs along floor, recessed below FLOOR_H
    # Spurs run at Y positions between pump rows to avoid pump pocket conflicts.

    for pi, (px, py) in enumerate(pump_grid_positions):
        _spur_x_end = px - PUMP_BODY_W / 2  # pump pocket left edge
        _spur_x_start = _wire_bus_cx - WIRE_BUS_D / 2  # bus left edge
        _spur_length = abs(_spur_x_end - _spur_x_start)

        if _spur_length < 2:
            # Right-column pump stub — barely any length needed
            continue

        # Floor-level spur: cut into floor (Z=0 to FLOOR_H) so it passes UNDER pump pockets
        _spur_z = FLOOR_H / 2  # centered in floor thickness
        pump_spur = (
            cq.Workplane("XY")
            .box(_spur_length, WIRE_SPUR_W, WIRE_SPUR_D)
            .translate(((_spur_x_start + _spur_x_end) / 2, py, _spur_z))
        )
        base = base.cut(pump_spur)

    # --- Vertical wire riser (outer wall face, Z=FLOOR_H to TRAY_Z) ---
    # Wires rise from floor bus up to tray level.
    # Position: Y=0 (centered between pump rows), on outer wall inner face.
    _riser_height = TRAY_Z - FLOOR_H
    _riser_z_center = (FLOOR_H + TRAY_Z) / 2

    wire_riser = (
        cq.Workplane("XY")
        .box(WIRE_RISER_D, WIRE_RISER_W, _riser_height)
        .translate((_wire_bus_cx, 0, _riser_z_center))
    )
    base = base.cut(wire_riser)

    # --- Tray ledge gap for wire riser pass-through ---
    # The tray ledge on the right outer wall runs at Z=29-32.
    # Cut a gap at Y=0 to let wires pass from riser into tray area.
    _ledge_gap_w = WIRE_RISER_W + 4  # slightly wider than riser for clearance
    ledge_gap = (
        cq.Workplane("XY")
        .box(_tray_ledge_w + 2, _ledge_gap_w, _tray_ledge_h + 1)
        .translate((MEETING_W / 2 - WALL - _tray_ledge_w / 2, 0,
                    TRAY_Z - _tray_ledge_h / 2))
    )
    base = base.cut(ledge_gap)

    # --- LED wire branch (from riser at Z≈60 to LED channel) ---
    # Short horizontal spur at LED strip height connecting riser to LED channel.
    _led_branch_z = BASE_H - WALL - LED_CHANNEL_D - 2 + LED_CHANNEL_W / 2
    _led_branch_length = 8  # short run to reach LED channel
    led_branch = (
        cq.Workplane("XY")
        .box(_led_branch_length, WIRE_SPUR_W, WIRE_SPUR_D)
        .translate((_wire_bus_cx - _led_branch_length / 2, 0, _led_branch_z))
    )
    base = base.cut(led_branch)

    # --- Rubber feet ---
    foot_coords = [
        (-BASE_W / 2 + FOOT_INSET, -BASE_D / 2 + FOOT_INSET),
        ( BASE_W / 2 - FOOT_INSET, -BASE_D / 2 + FOOT_INSET),
        (-BASE_W / 2 + FOOT_INSET,  BASE_D / 2 - FOOT_INSET),
        ( BASE_W / 2 - FOOT_INSET,  BASE_D / 2 - FOOT_INSET),
    ]
    for fx, fy in foot_coords:
        foot_pocket = (
            cq.Workplane("XY")
            .workplane(offset=-0.1)
            .center(fx, fy)
            .circle(FOOT_DIA / 2)
            .extrude(FOOT_DEPTH + 0.1)
        )
        base = base.cut(foot_pocket)

    # --- LED strip channel (continuous perimeter loop, all 4 walls) ---
    led_z = BASE_H - WALL - LED_CHANNEL_D - 2
    _t_led = (led_z + LED_CHANNEL_W / 2) / BASE_H
    _w_at_led = BASE_W + _t_led * (MEETING_W - BASE_W)
    _d_at_led = BASE_D + _t_led * (MEETING_D - BASE_D)

    # Front wall (-Y)
    led_front = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(0, -(_d_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1))
        .rect(_w_at_led - WALL * 2 - 6, LED_CHANNEL_D)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_front)

    # Rear wall (+Y)
    led_rear = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(0, _d_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1)
        .rect(_w_at_led - WALL * 2 - 6, LED_CHANNEL_D)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_rear)

    # Left wall (-X)
    led_left = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(-(_w_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1), 0)
        .rect(LED_CHANNEL_D, _d_at_led - WALL * 2 - 6)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_left)

    # Right wall (+X)
    led_right = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(_w_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1, 0)
        .rect(LED_CHANNEL_D, _d_at_led - WALL * 2 - 6)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_right)

    # --- Hex mesh cutouts ---
    hex_panel_h = BASE_H * 0.45
    hex_panel_z = BASE_H - hex_panel_h - WALL - 2

    # Front wall hex mesh
    hex_front = hex_mesh_cutout(BASE_W * 0.6, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_front_pos = (hex_front
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((0, -(BASE_D / 2 - _taper_shrink_base * 0.5), hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_front_pos)

    # Left wall hex mesh
    hex_left = hex_mesh_cutout(BASE_D * 0.5, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_left_pos = (hex_left
        .rotateAboutCenter((0, 0, 1), 90)
        .rotateAboutCenter((0, 1, 0), 90)
        .translate((-(BASE_W / 2 - _taper_shrink_base * 0.5), 0, hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_left_pos)

    # Rear wall hex mesh
    hex_rear = hex_mesh_cutout(BASE_W * 0.4, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_rear_pos = (hex_rear
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((0, (BASE_D / 2 - _taper_shrink_base * 0.5), hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_rear_pos)

    # Right wall hex mesh
    hex_right = hex_mesh_cutout(BASE_D * 0.4, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_right_pos = (hex_right
        .rotateAboutCenter((0, 0, 1), 90)
        .rotateAboutCenter((0, 1, 0), 90)
        .translate((BASE_W / 2 - _taper_shrink_base * 0.5, 0, hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_right_pos)

    # --- Magnet pockets on base rim ---
    for mx, my in magnet_positions:
        mp = (cq.Workplane("XY").workplane(offset=BASE_H - MAGNET_H)
              .center(mx, my).circle((MAGNET_DIA + TOL * 2) / 2)
              .extrude(MAGNET_H + 0.1))
        base = base.cut(mp)

    # --- Alignment pins ---
    for px, py in pin_positions:
        pin = (cq.Workplane("XY").workplane(offset=BASE_H)
               .center(px, py).circle(PIN_DIA / 2).extrude(PIN_H))
        base = base.union(pin)

    # --- SOMNI LABS branding (rear panel, +Y wall) ---
    brand_z = BASE_H * 0.30
    logo_cx = -15       # adjusted for narrower rear panel
    groove_r = 0.6
    groove_d = BRAND_DEPTH

    # S-curve waypoints — sampled from SVG bezier paths, scaled to 25mm.
    s_curves = [
        # Curve 0 (outermost)
        [(7.0,10.0),(8.23,9.74),(9.27,9.14),(10.14,7.95),
         (10.5,6.0),(8.32,4.02),(3.11,2.61),(-3.11,1.39),(-8.32,-0.02),
         (-10.5,-2.0),(-9.27,-6.9),(-7.36,-10.45),(-7.0,-11.0)],
        # Curve 2
        [(5.5,8.0),(6.56,7.78),(7.44,7.24),(8.19,6.21),
         (8.5,4.5),(6.73,2.76),(2.52,1.53),(-2.52,0.47),(-6.73,-0.76),
         (-8.5,-2.5),(-7.44,-6.3),(-5.81,-8.66),(-5.5,-9.0)],
        # Curve 4
        [(4.0,6.0),(4.88,5.81),(5.62,5.35),(6.24,4.46),
         (6.5,3.0),(5.15,1.51),(1.92,0.46),(-1.92,-0.46),(-5.15,-1.51),
         (-6.5,-3.0),(-5.62,-5.7),(-4.26,-6.87),(-4.0,-7.0)],
        # Curve 6 (innermost)
        [(2.5,4.0),(3.2,3.84),(3.8,3.46),(4.29,2.72),
         (4.5,1.5),(3.56,0.26),(1.33,-0.62),(-1.33,-1.38),(-3.56,-2.26),
         (-4.5,-3.5),(-3.8,-4.89),(-2.71,-5.04),(-2.5,-5.0)],
    ]

    # Cut all S-curve waypoints + center ring as a single batched boolean.
    groove_size = groove_r * 2
    _brand_cuts = []

    for curve_pts in s_curves:
        for cx_pt, cz_pt in curve_pts:
            px = logo_cx + cx_pt
            pz = brand_z + cz_pt
            _brand_cuts.append(
                cq.Workplane("XY")
                .box(groove_size, groove_d + 1, groove_size)
                .translate((px, BASE_D / 2 - groove_d / 2 + 0.5, pz))
            )

    # Center circle — ring of small box cuts
    center_ring_r = 2.0
    center_dot_r = 1.0
    num_ring_pts = 16
    for i in range(num_ring_pts):
        angle = 2 * math.pi * i / num_ring_pts
        rx = logo_cx + center_ring_r * math.cos(angle)
        rz = brand_z + center_ring_r * math.sin(angle)
        _brand_cuts.append(
            cq.Workplane("XY")
            .box(groove_size, groove_d + 1, groove_size)
            .translate((rx, BASE_D / 2 - groove_d / 2 + 0.5, rz))
        )

    # Center dot
    _brand_cuts.append(
        cq.Workplane("XY")
        .box(center_dot_r * 2, groove_d + 1, center_dot_r * 2)
        .translate((logo_cx, BASE_D / 2 - groove_d / 2 + 0.5, brand_z))
    )

    # Batch all branding cuts into a single boolean operation
    if _brand_cuts:
        from cadquery import Compound
        _brand_compound = Compound.makeCompound(
            [s.val() for s in _brand_cuts]
        )
        base = base.cut(cq.Workplane("XY").newObject([_brand_compound]))

    # Wordmark: "SOMNI" + "LABS" to the right of the icon
    try:
        brand_main = (
            cq.Workplane("XZ")
            .workplane(offset=BASE_D / 2)
            .center(10, brand_z + 4)
            .text("SOMNI", BRAND_FONT_SIZE, -BRAND_DEPTH, font="sans-serif")
        )
        base = base.cut(brand_main)
        brand_sub = (
            cq.Workplane("XZ")
            .workplane(offset=BASE_D / 2)
            .center(10, brand_z - 6)
            .text("LABS", BRAND_SUB_SIZE, -BRAND_DEPTH, font="sans-serif")
        )
        base = base.cut(brand_sub)
    except Exception:
        brand_recess = (
            cq.Workplane("XY")
            .workplane(offset=brand_z)
            .center(10, BASE_D / 2)
            .rect(45, 16)
            .extrude(-BRAND_DEPTH)
        )
        base = base.cut(brand_recess)

    return base



# =============================================================================
# BUILD ELECTRONICS TRAY (lift-out shelf for center zone upper level)
# =============================================================================

def build_electronics_tray():
    """Removable tray that sits above pumps in the center zone.

    Lifts straight out for pump access. Left legs rest on divider wall
    ledge, right legs rest on the outer wall ledge.

    Board layout (two columns side-by-side in X):
      Left col:  ESP32 (28mm X x 55mm Y) + BME280 (15mm X x 12mm Y)
      Right col: MOSFET (26mm X x 50mm Y) + atomizer driver (25mm x 35mm, Z-stacked on MOSFET)
                 + PD+Buck (24mm x 18mm, Z-stacked)
    """

    # Tray outer dimensions (fits inside center zone with clearance)
    _center_inner_left = DIVIDER_WET_X + WALL_INNER / 2 + TRAY_CLEARANCE
    _center_inner_right = MEETING_W / 2 - WALL - TRAY_CLEARANCE
    tray_w = _center_inner_right - _center_inner_left
    interior_y_min = -(MEETING_D / 2 - WALL - 2)
    interior_y_max = (MEETING_D / 2 - WALL - 2)
    tray_d = (interior_y_max - interior_y_min) - 2 * TRAY_CLEARANCE
    tray_cx = (_center_inner_left + _center_inner_right) / 2
    tray_cy = 0

    # Tray base plate
    tray = (
        cq.Workplane("XY")
        .box(tray_w, tray_d, TRAY_FLOOR)
        .translate((tray_cx, tray_cy, TRAY_Z + TRAY_FLOOR / 2))
    )

    # Perimeter walls
    _wall_inner_w = tray_w - 2 * TRAY_WALL
    _wall_inner_d = tray_d - 2 * TRAY_WALL
    _wall_h = TRAY_H - TRAY_FLOOR
    perimeter_outer = (
        cq.Workplane("XY")
        .box(tray_w, tray_d, _wall_h)
        .translate((tray_cx, tray_cy, TRAY_Z + TRAY_FLOOR + _wall_h / 2))
    )
    perimeter_inner = (
        cq.Workplane("XY")
        .box(_wall_inner_w, _wall_inner_d, _wall_h + 1)
        .translate((tray_cx, tray_cy, TRAY_Z + TRAY_FLOOR + _wall_h / 2))
    )
    perimeter_walls = perimeter_outer.cut(perimeter_inner)
    tray = tray.union(perimeter_walls)

    # Support legs (4 corners)
    _leg_h = TRAY_Z - FLOOR_H - PUMP_BODY_H - 2
    _leg_left_x = _center_inner_left + TRAY_LEG_INSET
    _leg_right_x = _center_inner_right - TRAY_LEG_INSET
    _leg_front_y = interior_y_min + TRAY_CLEARANCE + TRAY_LEG_INSET
    _leg_rear_y = interior_y_max - TRAY_CLEARANCE - TRAY_LEG_INSET
    leg_positions = [
        (_leg_left_x, _leg_front_y),
        (_leg_left_x, _leg_rear_y),
        (_leg_right_x, _leg_front_y),
        (_leg_right_x, _leg_rear_y),
    ]
    for lx, ly in leg_positions:
        leg = (
            cq.Workplane("XY")
            .box(TRAY_LEG_W, TRAY_LEG_W, _leg_h)
            .translate((lx, ly, TRAY_Z - _leg_h / 2))
        )
        tray = tray.union(leg)

    # Registration tabs (left side into divider wall, right side into outer wall)
    _tab_y_positions = [interior_y_min + 15, interior_y_max - 15]
    for tab_y in _tab_y_positions:
        # Left side tab
        left_tab = (
            cq.Workplane("XY")
            .box(TRAY_TAB_D, TRAY_TAB_W, TRAY_TAB_H)
            .translate((_center_inner_left - TRAY_TAB_D / 2, tab_y,
                        TRAY_Z + TRAY_TAB_H / 2))
        )
        tray = tray.union(left_tab)

        # Right side tab (into outer wall)
        right_tab = (
            cq.Workplane("XY")
            .box(TRAY_TAB_D, TRAY_TAB_W, TRAY_TAB_H)
            .translate((_center_inner_right + TRAY_TAB_D / 2, tab_y,
                        TRAY_Z + TRAY_TAB_H / 2))
        )
        tray = tray.union(right_tab)

    # === BOARD POCKETS on tray floor ===
    # V3.3 compact layout: boards redistributed across two columns to fit
    # 78mm tray depth. Atomizer driver Z-stacks on MOSFET, BME280 moves
    # to left column below ESP32.
    #   Left col:  ESP32 (55mm) + 2mm gap + BME280 (12mm) = 69mm
    #   Right col: MOSFET (50mm) + atm_drv Z-stacked + 2mm gap + PD/Buck (18mm) = 70mm
    _tray_y_min = tray_cy - tray_d / 2 + TRAY_WALL + 2
    _tray_y_max = tray_cy + tray_d / 2 - TRAY_WALL - 2

    # Two columns
    _gap = 3
    _left_col_w = ESP32_D + 2   # 30mm
    _right_col_w = MOSFET_BOARD_D + 2  # 28mm
    _total_col_w = _left_col_w + _gap + _right_col_w
    _col_offset = (tray_w - _total_col_w) / 2
    _left_col_x = tray_cx - tray_w / 2 + _col_offset + _left_col_w / 2
    _right_col_x = _left_col_x + _left_col_w / 2 + _gap + _right_col_w / 2

    _tray_floor_z = TRAY_Z + TRAY_FLOOR

    # --- Left column: ESP32 pocket ---
    y_cur_l = _tray_y_min
    esp32_tray_y = y_cur_l + ESP32_W / 2
    esp32_pocket = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z)
        .center(_left_col_x, esp32_tray_y)
        .rect(ESP32_D + 2, ESP32_W + 2)
        .extrude(ESP32_H + 1)
    )
    tray = tray.cut(esp32_pocket)

    # Rail slots for ESP32
    _esp_hw = (ESP32_D + 2) / 2
    for _rs in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=_tray_floor_z + RAIL_LIFT)
            .center(_left_col_x + _rs * (_esp_hw - RAIL_GROOVE_D / 2),
                    esp32_tray_y)
            .rect(RAIL_GROOVE_D, ESP32_W)
            .extrude(ESP32_H + 1 - RAIL_LIFT)
        )
        tray = tray.union(rail)

    y_cur_l += ESP32_W + 2

    # --- Left column: BME280 pocket ---
    bme_tray_y = y_cur_l + BME280_D / 2
    bme_pocket = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z)
        .center(_left_col_x, bme_tray_y)
        .rect(BME280_W + 2, BME280_D + 2)
        .extrude(BME280_H + 1)
    )
    tray = tray.cut(bme_pocket)

    # --- Right column: MOSFET pocket (atomizer driver Z-stacked on top) ---
    y_cur_r = _tray_y_min
    mosfet_tray_y = y_cur_r + MOSFET_BOARD_W / 2
    # Pocket deep enough for MOSFET + atomizer driver stacked on top
    _mosfet_stack_h = MOSFET_BOARD_H + ATOMIZER_DRIVER_H + 1
    mosfet_pocket = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z)
        .center(_right_col_x, mosfet_tray_y)
        .rect(MOSFET_BOARD_D + 2, MOSFET_BOARD_W + 2)
        .extrude(_mosfet_stack_h)
    )
    tray = tray.cut(mosfet_pocket)

    # Rail slots for MOSFET
    _mos_hw = (MOSFET_BOARD_D + 2) / 2
    for _rs in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=_tray_floor_z + RAIL_LIFT)
            .center(_right_col_x + _rs * (_mos_hw - RAIL_GROOVE_D / 2),
                    mosfet_tray_y)
            .rect(RAIL_GROOVE_D, MOSFET_BOARD_W)
            .extrude(MOSFET_BOARD_H + 1 - RAIL_LIFT)
        )
        tray = tray.union(rail)

    # Atomizer driver sits on top of MOSFET (Z-stacked, centered on MOSFET Y)
    atm_drv_tray_y = mosfet_tray_y  # same Y center as MOSFET

    y_cur_r += MOSFET_BOARD_W + 2

    # --- Right column: PD trigger + Buck converter Z-stacked pocket ---
    _pd_buck_w = max(PD_TRIGGER_W, BUCK_CONV_W)
    _pd_buck_d = max(PD_TRIGGER_D, BUCK_CONV_D)
    _pd_buck_h = BUCK_CONV_H + PD_TRIGGER_H + 2
    pd_buck_tray_y = y_cur_r + _pd_buck_d / 2
    pd_buck_pocket = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z)
        .center(_right_col_x, pd_buck_tray_y)
        .rect(_pd_buck_w + 2, _pd_buck_d + 2)
        .extrude(_pd_buck_h)
    )
    tray = tray.cut(pd_buck_pocket)

    # Snap tabs for buck converter
    _pdb_hw = (_pd_buck_w + 2) / 2
    _buck_mid_z = _tray_floor_z + BUCK_CONV_H / 2
    for _ss in [-1, 1]:
        snap = (
            cq.Workplane("XY")
            .workplane(offset=_buck_mid_z - SNAP_NUB_W / 2)
            .center(_right_col_x + _ss * (_pdb_hw - SNAP_NUB_H / 2),
                    pd_buck_tray_y)
            .rect(SNAP_NUB_H, SNAP_NUB_W)
            .extrude(SNAP_NUB_W)
        )
        tray = tray.union(snap)

    # === Tray wire channels ===
    _tch_z = _tray_floor_z + CHANNEL_D / 2

    # Power bus along right column
    _pwr_y_start = pd_buck_tray_y
    _pwr_y_end = mosfet_tray_y
    pwr_bus = (
        cq.Workplane("XY")
        .box(CHANNEL_W, abs(_pwr_y_end - _pwr_y_start), CHANNEL_D)
        .translate((_right_col_x + MOSFET_BOARD_D / 2 + 2, (_pwr_y_start + _pwr_y_end) / 2, _tch_z))
    )
    tray = tray.cut(pwr_bus)

    # Signal bus: ESP32 -> MOSFET
    _sig_y_mid = (esp32_tray_y + mosfet_tray_y) / 2
    sig_bridge = (
        cq.Workplane("XY")
        .box(abs(_right_col_x - _left_col_x), CHANNEL_W, CHANNEL_D)
        .translate(((_left_col_x + _right_col_x) / 2, _sig_y_mid, _tch_z))
    )
    tray = tray.cut(sig_bridge)

    # Wire drop hole: atomizer wire drops from tray to base floor
    _drop_hole_y = _tray_y_min + 3
    wire_drop = (
        cq.Workplane("XY")
        .workplane(offset=TRAY_Z)
        .center(tray_cx - tray_w / 4, _drop_hole_y)
        .rect(5, 5)
        .extrude(TRAY_FLOOR + 1)
    )
    tray = tray.cut(wire_drop)

    return tray


# =============================================================================
# BUILD TOP SHELL
# =============================================================================

def build_top_shell():
    """Two-zone functional lid matching base divider layout.

    MIST+FILL        (left)  — mist chimney + chevron exhaust + water fill chute
    BOTTLES+STORAGE  (right) — 5 bottle wells (ceiling) + open storage below

    Lifts off for full access to everything in the base.
    Bottles pre-loaded into ceiling wells before placing shell.
    """

    # --- Outer shell ---
    shell = tapered_box(MEETING_W, MEETING_D, TOP_W, TOP_D, TOP_H)

    # Hollow interior
    cavity = tapered_box(
        MEETING_W - WALL * 2, MEETING_D - WALL * 2,
        TOP_W - WALL * 2, TOP_D - WALL * 2,
        TOP_H - WALL * 2
    ).translate((0, 0, WALL))
    shell = shell.cut(cavity)

    # --- Internal divider wall (one, creating two zones) ---
    top_divider_h = TOP_H - WALL * 2 - 1

    # Left divider (mist+fill | bottles+storage)
    top_div_left = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(TOP_DIVIDER_WET_X, 0)
        .rect(WALL_INNER, MEETING_D - WALL * 2 - 2)
        .extrude(top_divider_h)
    )
    shell = shell.union(top_div_left)

    # =============================================
    # MIST+FILL ZONE (left) — chimney, exhaust, fill chute
    # =============================================

    # --- Water fill chute (rear of left zone) ---
    fill_top_cut = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - WALL - 0.1)
        .center(FILL_CHUTE_POS_X, FILL_CHUTE_POS_Y)
        .rect(FILL_CHUTE_TOP_W, FILL_CHUTE_TOP_D)
        .extrude(WALL + 0.2)
    )
    shell = shell.cut(fill_top_cut)

    # Raised lip around the fill opening
    fill_lip = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H)
        .center(FILL_CHUTE_POS_X, FILL_CHUTE_POS_Y)
        .rect(FILL_CHUTE_TOP_W + 4, FILL_CHUTE_TOP_D + 4)
        .rect(FILL_CHUTE_TOP_W, FILL_CHUTE_TOP_D)
        .extrude(FILL_CHUTE_LIP_H)
    )
    shell = shell.union(fill_lip)

    # Internal funnel walls
    _funnel_outer = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .rect(FILL_CHUTE_BOT_W + WALL_INNER * 2, FILL_CHUTE_BOT_D + WALL_INNER * 2)
        .workplane(offset=TOP_H - WALL * 2)
        .rect(FILL_CHUTE_TOP_W + WALL_INNER * 2, FILL_CHUTE_TOP_D + WALL_INNER * 2)
        .loft()
    ).translate((FILL_CHUTE_POS_X, FILL_CHUTE_POS_Y, 0))

    _funnel_inner = (
        cq.Workplane("XY")
        .workplane(offset=WALL - 0.1)
        .rect(FILL_CHUTE_BOT_W, FILL_CHUTE_BOT_D)
        .workplane(offset=TOP_H - WALL * 2 + 0.2)
        .rect(FILL_CHUTE_TOP_W, FILL_CHUTE_TOP_D)
        .loft()
    ).translate((FILL_CHUTE_POS_X, FILL_CHUTE_POS_Y, 0))

    funnel_walls = _funnel_outer.cut(_funnel_inner)
    shell = shell.union(funnel_walls)
    shell = shell.cut(_funnel_inner)

    # --- Mist chimney + exhaust ---
    chimney_outer = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(MIST_POS_X, MIST_POS_Y)
        .circle(MIST_CHANNEL_DIA / 2 + MIST_CHANNEL_WALL)
        .extrude(TOP_H - WALL * 2)
    )
    shell = shell.union(chimney_outer)

    chimney_bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.1)
        .center(MIST_POS_X, MIST_POS_Y)
        .circle(MIST_CHANNEL_DIA / 2)
        .extrude(TOP_H + 0.2)
    )
    shell = shell.cut(chimney_bore)

    # Chevron exhaust port
    exhaust_pts = [
        (EXHAUST_POS_X, EXHAUST_POS_Y + EXHAUST_D / 2),
        (EXHAUST_POS_X + EXHAUST_W / 2, EXHAUST_POS_Y),
        (EXHAUST_POS_X, EXHAUST_POS_Y - EXHAUST_D / 2),
        (EXHAUST_POS_X - EXHAUST_W / 2, EXHAUST_POS_Y),
    ]
    exhaust_cut = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - WALL - 0.1)
        .moveTo(exhaust_pts[0][0], exhaust_pts[0][1])
        .lineTo(exhaust_pts[1][0], exhaust_pts[1][1])
        .lineTo(exhaust_pts[2][0], exhaust_pts[2][1])
        .lineTo(exhaust_pts[3][0], exhaust_pts[3][1])
        .close()
        .extrude(WALL + 0.2)
    )
    shell = shell.cut(exhaust_cut)

    # Internal vanes for directed airflow
    vane_thickness = 1.2
    for v in range(3):
        vane_offset = -EXHAUST_D / 4 + v * (EXHAUST_D / 4)
        vy = EXHAUST_POS_Y + vane_offset
        t_v = 1.0 - abs(vane_offset) / (EXHAUST_D / 2)
        vane_hw = (EXHAUST_W / 2) * t_v
        if vane_hw < 2:
            continue
        vane = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL)
            .center(EXHAUST_POS_X, vy)
            .rect(vane_hw * 2, vane_thickness)
            .extrude(WALL)
        )
        shell = shell.union(vane)

    # =============================================
    # BOTTLES+STORAGE ZONE (right) — bottle wells + open storage
    # =============================================

    # 3+2 bottle grid recessed 3mm into ceiling with retaining rings
    _ceiling_z = TOP_H - WALL  # inner ceiling surface
    _retainer_ring_h = 15      # ring hangs down from ceiling
    _retainer_ring_wall = 2    # ring wall thickness

    for bx, by in bottle_grid_positions:
        # Well recess into ceiling (3mm deep)
        well_recess = (
            cq.Workplane("XY")
            .workplane(offset=_ceiling_z - BOTTLE_WELL_DEPTH)
            .center(bx, by)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(BOTTLE_WELL_DEPTH + 0.1)
        )
        shell = shell.cut(well_recess)

        # Retaining ring (hangs down from ceiling)
        ring_outer = (
            cq.Workplane("XY")
            .workplane(offset=_ceiling_z - BOTTLE_WELL_DEPTH - _retainer_ring_h)
            .center(bx, by)
            .circle(BOTTLE_WELL_DIA / 2 + _retainer_ring_wall)
            .extrude(_retainer_ring_h)
        )
        ring_inner = (
            cq.Workplane("XY")
            .workplane(offset=_ceiling_z - BOTTLE_WELL_DEPTH - _retainer_ring_h - 0.1)
            .center(bx, by)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(_retainer_ring_h + 0.2)
        )
        retainer = ring_outer.cut(ring_inner)
        shell = shell.union(retainer)

    # =============================================
    # CAPACITIVE TOUCH BUTTONS (top surface, front edge)
    # =============================================
    btn_x_center = 0
    for btn_i in range(TOUCH_BTN_COUNT):
        bx = btn_x_center + (btn_i - (TOUCH_BTN_COUNT - 1) / 2) * TOUCH_BTN_SPACING
        by = TOUCH_BTN_Y

        # Cosmetic circle deboss
        indicator = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - 0.5)
            .center(bx, by)
            .circle(TOUCH_ZONE_DIA / 2)
            .circle(TOUCH_ZONE_DIA / 2 - 1.5)
            .extrude(0.6)
        )
        shell = shell.cut(indicator)

        # Thin the ceiling above the touch zone to 1.5mm
        thin_zone = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL)
            .center(bx, by)
            .circle(TOUCH_ZONE_DIA / 2 + 2)
            .extrude(WALL - 1.5)
        )
        shell = shell.cut(thin_zone)

        # TTP223 module pocket
        module_pocket = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL - TOUCH_BTN_H - 0.5)
            .center(bx, by)
            .rect(TOUCH_BTN_W + 1, TOUCH_BTN_D + 1)
            .extrude(TOUCH_BTN_H + 0.5)
        )
        shell = shell.cut(module_pocket)

    # =============================================
    # SHARED FEATURES
    # =============================================

    # --- Matching magnet pockets ---
    for mx, my in magnet_positions:
        mp = (cq.Workplane("XY").workplane(offset=-0.1)
              .center(mx, my).circle((MAGNET_DIA + TOL * 2) / 2)
              .extrude(MAGNET_H + 0.1))
        shell = shell.cut(mp)

    # --- Matching pin holes ---
    for px, py in pin_positions:
        ph = (cq.Workplane("XY").workplane(offset=-0.1)
              .center(px, py).circle((PIN_DIA + TOL * 2) / 2)
              .extrude(PIN_H + WALL + 0.1))
        shell = shell.cut(ph)

    # --- Panel line ---
    shell = panel_line_cut(
        shell, PANEL_LINE_Z_TOP, TOP_H,
        MEETING_W, MEETING_D, TOP_W, TOP_D,
        PANEL_LINE_WIDTH, PANEL_LINE_DEPTH
    )

    return shell


# =============================================================================
# FITMENT COMPONENTS — simplified solid models for visual fit check
# =============================================================================

def build_components():
    """Build simplified solid models of all internal components at their
    installed positions. Returns a dict of {name: (solid, color)}.

    V3.3 Layout (2+3 pump grid, 3+2 bottle grid):
      Wet zone: atomizer piezo disk, water
      Center zone (lower): 5x pumps in 2+3 grid
      Center zone (upper / tray): ESP32, MOSFET, PD+Buck, atomizer driver, BME280
      Top shell: 5x bottles hanging from ceiling wells in 3+2 grid
    """

    parts = {}

    # --- Recompute tray board positions (must match build_electronics_tray) ---
    # V3.3 compact layout: BME280 in left col, atomizer driver Z-stacked on MOSFET
    _center_inner_left = DIVIDER_WET_X + WALL_INNER / 2 + TRAY_CLEARANCE
    _center_inner_right = MEETING_W / 2 - WALL - TRAY_CLEARANCE
    tray_w = _center_inner_right - _center_inner_left
    tray_cx = (_center_inner_left + _center_inner_right) / 2
    interior_y_min = -(MEETING_D / 2 - WALL - 2)
    interior_y_max = (MEETING_D / 2 - WALL - 2)
    tray_d = (interior_y_max - interior_y_min) - 2 * TRAY_CLEARANCE
    _tray_y_min = -tray_d / 2 + TRAY_WALL + 2
    _tray_floor_z = TRAY_Z + TRAY_FLOOR

    # Two columns on tray
    _gap = 3
    _left_col_w = ESP32_D + 2
    _right_col_w = MOSFET_BOARD_D + 2
    _total_col_w = _left_col_w + _gap + _right_col_w
    _col_offset = (tray_w - _total_col_w) / 2
    _left_col_x = tray_cx - tray_w / 2 + _col_offset + _left_col_w / 2
    _right_col_x = _left_col_x + _left_col_w / 2 + _gap + _right_col_w / 2

    # Left column: ESP32 + BME280
    esp32_tray_y = _tray_y_min + ESP32_W / 2
    bme_tray_y = _tray_y_min + ESP32_W + 2 + BME280_D / 2

    # Right column: MOSFET (+ atm_drv Z-stacked) + PD/Buck
    _pd_buck_d = max(PD_TRIGGER_D, BUCK_CONV_D)
    y_cur_r = _tray_y_min
    mosfet_tray_y = y_cur_r + MOSFET_BOARD_W / 2
    atm_drv_tray_y = mosfet_tray_y  # Z-stacked on MOSFET, same Y center
    y_cur_r += MOSFET_BOARD_W + 2
    pd_buck_tray_y = y_cur_r + _pd_buck_d / 2

    # =============================================
    # WET ZONE components
    # =============================================

    # Atomizer piezo disk
    atomizer_disk = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H - 1)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_DIA / 2)
        .extrude(3)
    )
    parts["atomizer_disk"] = (atomizer_disk, (0.75, 0.75, 0.15, 0.95))  # gold

    # Water (transparent blue block filling wet zone)
    water_level = 40
    _wet_left_x = -(MEETING_W / 2 - WALL)
    _wet_width = abs(DIVIDER_WET_X - _wet_left_x) - WALL_INNER
    _wet_depth = MEETING_D - WALL * 2 - 4
    water = (
        cq.Workplane("XY")
        .box(_wet_width - 4, _wet_depth - 4, water_level)
        .translate(((_wet_left_x + DIVIDER_WET_X) / 2, 0, FLOOR_H + water_level / 2))
    )
    parts["water"] = (water, (0.15, 0.4, 0.85, 0.25))  # translucent blue

    # =============================================
    # CENTER ZONE — Lower level (pumps, 2+3 grid)
    # =============================================

    for i, (px, py) in enumerate(pump_grid_positions):
        pump = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + 0.5)
            .center(px, py)
            .rect(PUMP_BODY_W, PUMP_BODY_D)
            .extrude(PUMP_BODY_H)
        )
        parts[f"pump_{i}"] = (pump, (0.85, 0.45, 0.1, 0.9))  # orange

    # =============================================
    # CENTER ZONE — Upper level (tray electronics)
    # =============================================

    # ESP32 DevKit
    esp32 = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z + 0.5)
        .center(_left_col_x, esp32_tray_y)
        .rect(ESP32_D, ESP32_W)
        .extrude(ESP32_H)
    )
    parts["esp32"] = (esp32, (0.1, 0.35, 0.7, 0.95))  # blue PCB

    # 8-channel MOSFET board
    mosfet_board = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z + 0.5)
        .center(_right_col_x, mosfet_tray_y)
        .rect(MOSFET_BOARD_D, MOSFET_BOARD_W)
        .extrude(MOSFET_BOARD_H)
    )
    parts["mosfet_board"] = (mosfet_board, (0.15, 0.55, 0.15, 0.9))  # green

    # Buck converter
    buck_conv = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z + 0.5)
        .center(_right_col_x, pd_buck_tray_y)
        .rect(BUCK_CONV_W, BUCK_CONV_D)
        .extrude(BUCK_CONV_H)
    )
    parts["buck_converter"] = (buck_conv, (0.5, 0.1, 0.5, 0.95))  # purple PCB

    # CH224K PD trigger (stacked on buck)
    pd_trigger = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z + 0.5 + BUCK_CONV_H + 1)
        .center(_right_col_x, pd_buck_tray_y)
        .rect(PD_TRIGGER_W, PD_TRIGGER_D)
        .extrude(PD_TRIGGER_H)
    )
    parts["pd_trigger"] = (pd_trigger, (0.7, 0.1, 0.1, 0.95))  # red PCB

    # Atomizer driver board (Z-stacked on top of MOSFET)
    atomizer_driver = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z + 0.5 + MOSFET_BOARD_H)
        .center(_right_col_x, atm_drv_tray_y)
        .rect(ATOMIZER_DRIVER_D, ATOMIZER_DRIVER_W)
        .extrude(ATOMIZER_DRIVER_H)
    )
    parts["atomizer_driver"] = (atomizer_driver, (0.2, 0.6, 0.2, 0.95))  # green PCB

    # BME280 sensor (left column, below ESP32)
    bme280 = (
        cq.Workplane("XY")
        .workplane(offset=_tray_floor_z + 0.5)
        .center(_left_col_x, bme_tray_y)
        .rect(BME280_W, BME280_D)
        .extrude(BME280_H)
    )
    parts["bme280"] = (bme280, (0.3, 0.3, 0.8, 0.95))  # light blue

    # =============================================
    # TOP SHELL — Bottles (hanging from ceiling wells, 3+2 grid)
    # =============================================

    _ceiling_z_top = BASE_H + TOP_H - WALL  # top shell ceiling in assembly coords
    for i, (bx, by) in enumerate(bottle_grid_positions):
        bottle_body_h = BOTTLE_HEIGHT - 15
        cap_h = 15
        # Bottle hangs cap-down: cap at top (near ceiling), body below
        cap_top_z = _ceiling_z_top - BOTTLE_WELL_DEPTH
        cap_bot_z = cap_top_z - cap_h
        body_bot_z = cap_bot_z - bottle_body_h

        cap = (
            cq.Workplane("XY")
            .workplane(offset=cap_bot_z)
            .center(bx, by)
            .circle(BOTTLE_CAP_DIA / 2)
            .extrude(cap_h)
        )
        body = (
            cq.Workplane("XY")
            .workplane(offset=body_bot_z)
            .center(bx, by)
            .circle(BOTTLE_DIA / 2)
            .extrude(bottle_body_h)
        )
        bottle = body.union(cap)
        colors = [
            (0.6, 0.35, 0.05, 0.8),   # amber
            (0.45, 0.25, 0.1, 0.8),    # dark brown
            (0.55, 0.4, 0.15, 0.8),    # light amber
            (0.4, 0.2, 0.05, 0.8),     # deep brown
            (0.65, 0.45, 0.1, 0.8),    # golden
        ]
        parts[f"bottle_{i}"] = (bottle, colors[i % len(colors)])

    # =============================================
    # LED strip (simplified as thin colored ring)
    # =============================================
    led_z = BASE_H - WALL - LED_CHANNEL_D - 2
    _t_led = (led_z + LED_CHANNEL_W / 2) / BASE_H
    _w_at_led = BASE_W + _t_led * (MEETING_W - BASE_W)
    _d_at_led = BASE_D + _t_led * (MEETING_D - BASE_D)

    led_f = (
        cq.Workplane("XY")
        .box(_w_at_led - WALL * 2 - 8, 3, LED_CHANNEL_W - 1)
        .translate((0, -(_d_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1),
                    led_z + LED_CHANNEL_W / 2))
    )
    led_r = (
        cq.Workplane("XY")
        .box(_w_at_led - WALL * 2 - 8, 3, LED_CHANNEL_W - 1)
        .translate((0, _d_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1,
                    led_z + LED_CHANNEL_W / 2))
    )
    led_l = (
        cq.Workplane("XY")
        .box(3, _d_at_led - WALL * 2 - 8, LED_CHANNEL_W - 1)
        .translate((-(_w_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1), 0,
                    led_z + LED_CHANNEL_W / 2))
    )
    led_ri = (
        cq.Workplane("XY")
        .box(3, _d_at_led - WALL * 2 - 8, LED_CHANNEL_W - 1)
        .translate((_w_at_led / 2 - WALL - LED_CHANNEL_D / 2 + 1, 0,
                    led_z + LED_CHANNEL_W / 2))
    )
    led_strip = led_f.union(led_r).union(led_l).union(led_ri)
    parts["led_strip"] = (led_strip, (0.2, 1.0, 0.3, 0.8))  # bright green

    # =============================================
    # WIRING VISUALIZATION (all routes)
    # =============================================
    # Color coding:
    #   Magenta  = atomizer wires (power to piezo, through wet zone)
    #   Yellow   = pump power wires (MOSFET → pumps)
    #   Cyan     = signal/data wires (ESP32 ↔ peripherals)
    #   Orange   = power bus (USB-C → PD/Buck → 5V rail)

    _wire_t = 1.5   # wire visualization thickness
    _magenta = (0.85, 0.15, 0.85, 0.85)
    _yellow  = (0.9, 0.85, 0.1, 0.85)
    _cyan    = (0.1, 0.85, 0.85, 0.85)
    _orange_w = (1.0, 0.55, 0.1, 0.85)

    # --- Atomizer wires (magenta): atomizer → floor → up divider → across → tray ---
    _atm_chase_x = DIVIDER_WET_X - WALL_INNER / 2 - CHANNEL_W / 2

    # Segment 1: floor run (atomizer to divider base)
    atm_w1 = (
        cq.Workplane("XY")
        .box(abs(_atm_chase_x - ATOMIZER_POS_X), _wire_t, _wire_t)
        .translate(((ATOMIZER_POS_X + _atm_chase_x) / 2, 0, FLOOR_H + CHANNEL_D / 2))
    )
    parts["wire_atm_floor"] = (atm_w1, _magenta)

    # Segment 2: vertical chase up divider wall (wet side)
    _atm_chase_z_bot = FLOOR_H
    _atm_chase_z_top = FLOOR_H + 45
    atm_w2 = (
        cq.Workplane("XY")
        .box(_wire_t, _wire_t, _atm_chase_z_top - _atm_chase_z_bot)
        .translate((_atm_chase_x, 0, (_atm_chase_z_bot + _atm_chase_z_top) / 2))
    )
    parts["wire_atm_vertical"] = (atm_w2, _magenta)

    # Segment 3: cross divider (above water line, Z=48)
    atm_w3 = (
        cq.Workplane("XY")
        .box(WALL_INNER + 2, _wire_t, _wire_t)
        .translate((DIVIDER_WET_X, 0, _atm_chase_z_top + WIRE_PORT_H / 2))
    )
    parts["wire_atm_cross"] = (atm_w3, _magenta)

    # Segment 4: center zone side, drop DOWN from cross port (Z=48) to tray (Z=34)
    _atm_center_x = DIVIDER_WET_X + WALL_INNER / 2 + 1
    _atm_seg4_height = abs(_atm_chase_z_top - _tray_floor_z)
    if _atm_seg4_height > 0.5:
        atm_w4 = (
            cq.Workplane("XY")
            .box(_wire_t, _wire_t, _atm_seg4_height)
            .translate((_atm_center_x, 0,
                        (min(_atm_chase_z_top, _tray_floor_z) + max(_atm_chase_z_top, _tray_floor_z)) / 2))
        )
        parts["wire_atm_to_tray"] = (atm_w4, _magenta)

    # --- Pump power wires (yellow): MOSFET on tray → drop down → each pump ---
    # Vertical drop from tray to pump level
    _pump_wire_z_top = _tray_floor_z
    _pump_wire_z_bot = FLOOR_H + PUMP_BODY_H + 1
    pump_drop = (
        cq.Workplane("XY")
        .box(_wire_t, 4, _pump_wire_z_top - _pump_wire_z_bot)
        .translate((_pump_left_col_cx, 0,
                    (_pump_wire_z_top + _pump_wire_z_bot) / 2))
    )
    parts["wire_pump_drop"] = (pump_drop, _yellow)

    # Horizontal runs from wire drop to each pump (at pump top Z)
    _pump_wire_z = FLOOR_H + PUMP_BODY_H + 0.5
    for pi, (px, py) in enumerate(pump_grid_positions):
        _horiz_dist = abs(px - _pump_left_col_cx)
        if _horiz_dist < 1:
            # Left-column pump: just a short Y jog from the wire drop
            if abs(py) > 1:
                pw = (
                    cq.Workplane("XY")
                    .box(_wire_t, abs(py) + 1, _wire_t)
                    .translate((_pump_left_col_cx, py / 2, _pump_wire_z))
                )
                parts[f"wire_pump_{pi}"] = (pw, _yellow)
        else:
            # Right-column pump: horizontal run from drop to pump X, then Y jog
            pw_x = (
                cq.Workplane("XY")
                .box(_horiz_dist, _wire_t, _wire_t)
                .translate(((px + _pump_left_col_cx) / 2, 0, _pump_wire_z))
            )
            if abs(py) > 1:
                pw_y = (
                    cq.Workplane("XY")
                    .box(_wire_t, abs(py) + 1, _wire_t)
                    .translate((px, py / 2, _pump_wire_z))
                )
                pw_x = pw_x.union(pw_y)
            parts[f"wire_pump_{pi}"] = (pw_x, _yellow)

    # --- USB-C → Power bus (orange): USB-C rear → PD/Buck → 5V rail on tray ---
    _usbc_x = (_pump_left_col_cx + _pump_right_col_cx) / 2
    _usbc_z = TRAY_Z + TRAY_FLOOR + 3 + USBC_PORT_H / 2
    # Short run from USB-C port inward to tray
    usbc_wire = (
        cq.Workplane("XY")
        .box(_wire_t, 8, _wire_t)
        .translate((_usbc_x, interior_y_max - 4, _usbc_z))
    )
    parts["wire_usbc_in"] = (usbc_wire, _orange_w)

    # =============================================
    # TUBING VISUALIZATION (bottle → pump → reservoir)
    # =============================================
    # Color: soft blue for inlet tubes (bottle→pump), red for outlet (pump→reservoir)
    _tube_t = 2.0   # tube visualization thickness (3mm OD silicone)
    _tube_in_color = (0.3, 0.5, 0.9, 0.7)    # soft blue (inlet)
    _tube_out_color = (0.9, 0.3, 0.3, 0.7)    # soft red (outlet)

    # Inlet tubes: from TOP of bottle cap → up → over → down outside bottle → pump
    #
    # Bottles hang cap-up (cap nearest ceiling). Tube is threaded through the cap
    # center. Outside the cap, the tube exits UPWARD from the cap top, bends over
    # to clear the bottle, then runs down the outside of the bottle body to the pump.
    #
    # Path:
    #   1. Up from cap top center (short vertical stub, ~5mm)
    #   2. Horizontal jog to clear bottle radius
    #   3. Down outside the bottle body
    #   4. Continue dropping below bottle to pump level
    #   5. Horizontal jog to pump position

    for i, ((bx, by), (px, py)) in enumerate(zip(bottle_grid_positions, pump_grid_positions)):
        _cap_top_z = BASE_H + TOP_H - WALL - BOTTLE_WELL_DEPTH  # ~124mm
        _cap_bot_z = _cap_top_z - 15  # cap is 15mm tall → ~109mm
        _bottle_bot_z = _cap_bot_z - (BOTTLE_HEIGHT - 15)  # body is 40mm → ~69mm
        _pump_top_z = FLOOR_H + PUMP_BODY_H  # ~28mm

        # Tube exits cap top, goes up 5mm, then bends over to the side
        _stub_h = 5
        _bend_top_z = _cap_top_z + _stub_h  # top of the stub (~129mm)

        # Offset direction: toward the pump X
        _tube_offset_x = BOTTLE_DIA / 2 + 2  # just outside bottle body
        if px > bx:
            _ext_x = bx + _tube_offset_x
        else:
            _ext_x = bx - _tube_offset_x

        tube_parts = []

        # Seg 1: vertical stub UP from cap top center
        seg1 = (
            cq.Workplane("XY")
            .box(_tube_t, _tube_t, _stub_h)
            .translate((bx, by, _cap_top_z + _stub_h / 2))
        )
        tube_parts.append(seg1)

        # Seg 2: horizontal jog at top of stub to clear bottle (to ext_x)
        _jog_to_ext = abs(_ext_x - bx)
        if _jog_to_ext > 0.5:
            seg2 = (
                cq.Workplane("XY")
                .box(_jog_to_ext, _tube_t, _tube_t)
                .translate(((bx + _ext_x) / 2, by, _bend_top_z))
            )
            tube_parts.append(seg2)

        # Seg 3: vertical run DOWN outside bottle (from bend top to bottle bottom)
        _down_h = _bend_top_z - _bottle_bot_z
        if _down_h > 1:
            seg3 = (
                cq.Workplane("XY")
                .box(_tube_t, _tube_t, _down_h)
                .translate((_ext_x, by, (_bend_top_z + _bottle_bot_z) / 2))
            )
            tube_parts.append(seg3)

        # Seg 4: continue dropping from bottle bottom to pump level
        _drop_h = _bottle_bot_z - _pump_top_z
        if _drop_h > 1:
            seg4 = (
                cq.Workplane("XY")
                .box(_tube_t, _tube_t, _drop_h)
                .translate((_ext_x, by, (_bottle_bot_z + _pump_top_z) / 2))
            )
            tube_parts.append(seg4)

        # Seg 5: horizontal jog at pump level (X) from ext_x to pump X
        _jog_x = abs(px - _ext_x)
        if _jog_x > 1:
            seg5x = (
                cq.Workplane("XY")
                .box(_jog_x, _tube_t, _tube_t)
                .translate(((px + _ext_x) / 2, by, _pump_top_z))
            )
            tube_parts.append(seg5x)

        # Seg 6: horizontal jog at pump level (Y) from bottle Y to pump Y
        _jog_y = abs(py - by)
        if _jog_y > 1:
            seg5y = (
                cq.Workplane("XY")
                .box(_tube_t, _jog_y, _tube_t)
                .translate((px, (by + py) / 2, _pump_top_z))
            )
            tube_parts.append(seg5y)

        # Union all segments
        tube_solid = tube_parts[0]
        for tp in tube_parts[1:]:
            tube_solid = tube_solid.union(tp)

        parts[f"tube_inlet_{i}"] = (tube_solid, _tube_in_color)

    # Outlet tubes: pump → through divider → drip down into reservoir water
    #
    # Path:
    #   1. From pump top, horizontal run to divider pass-through hole
    #   2. Through the divider hole into wet zone
    #   3. Drop down into the water (to just above floor level)
    _divider_hole_z = FLOOR_H + (TRAY_Z - FLOOR_H) - 8  # ~24mm
    _water_drip_z = FLOOR_H + 5  # drip endpoint (just above floor in reservoir)
    _wet_drip_x = DIVIDER_WET_X - WALL_INNER / 2 - 5  # 5mm into wet zone

    for i, (px, py) in enumerate(pump_grid_positions):
        _pump_out_z = FLOOR_H + PUMP_BODY_H  # pump output at top

        out_parts = []

        # Seg 1: vertical from pump top down to divider hole Z
        if abs(_pump_out_z - _divider_hole_z) > 1:
            seg_v = (
                cq.Workplane("XY")
                .box(_tube_t, _tube_t, abs(_pump_out_z - _divider_hole_z))
                .translate((px, py, (_pump_out_z + _divider_hole_z) / 2))
            )
            out_parts.append(seg_v)

        # Seg 2: horizontal run from pump X to divider at hole Z
        _horiz_len = abs(px - DIVIDER_WET_X)
        if _horiz_len > 1:
            seg_h = (
                cq.Workplane("XY")
                .box(_horiz_len, _tube_t, _tube_t)
                .translate(((px + DIVIDER_WET_X) / 2, py, _divider_hole_z))
            )
            out_parts.append(seg_h)

        # Seg 3: through divider into wet zone (short horizontal)
        seg_thru = (
            cq.Workplane("XY")
            .box(abs(_wet_drip_x - DIVIDER_WET_X), _tube_t, _tube_t)
            .translate(((DIVIDER_WET_X + _wet_drip_x) / 2, py, _divider_hole_z))
        )
        out_parts.append(seg_thru)

        # Seg 4: drip down into reservoir water
        _drip_h = _divider_hole_z - _water_drip_z
        if _drip_h > 1:
            seg_drip = (
                cq.Workplane("XY")
                .box(_tube_t, _tube_t, _drip_h)
                .translate((_wet_drip_x, py, (_divider_hole_z + _water_drip_z) / 2))
            )
            out_parts.append(seg_drip)

        # Union all segments
        out_solid = out_parts[0]
        for op in out_parts[1:]:
            out_solid = out_solid.union(op)

        parts[f"tube_outlet_{i}"] = (out_solid, _tube_out_color)

    return parts


# =============================================================================
# ASSEMBLY — color-coded per zone for visibility
# =============================================================================

base = build_base()
electronics_tray = build_electronics_tray()
top_shell = build_top_shell()
top_shell = top_shell.translate((0, 0, BASE_H))

# Show the three main parts
show_object(base, name="base",
            options={"color": (0.12, 0.12, 0.15, 0.55)})
show_object(electronics_tray, name="electronics_tray",
            options={"color": (0.6, 0.6, 0.65, 0.7)})  # silver
show_object(top_shell, name="top_shell",
            options={"color": (0.18, 0.18, 0.22, 0.55)})

# --- Zone indicator markers ---
marker_h = 1.5

# Base wet zone marker (teal)
wet_marker_w = abs(DIVIDER_WET_X - (-(MEETING_W / 2 - WALL)))
wet_marker = (
    cq.Workplane("XY")
    .box(wet_marker_w - 4, MEETING_D - WALL * 2 - 8, marker_h)
    .translate(((-(MEETING_W / 2 - WALL) + DIVIDER_WET_X) / 2, 0, FLOOR_H + marker_h / 2))
)
show_object(wet_marker, name="zone_wet",
            options={"color": (0.08, 0.72, 0.65, 0.85)})  # teal

# Base center zone marker (amber)
center_marker_w = (MEETING_W / 2 - WALL) - DIVIDER_WET_X - WALL_INNER / 2
_center_cx = (DIVIDER_WET_X + WALL_INNER / 2 + MEETING_W / 2 - WALL) / 2
center_marker = (
    cq.Workplane("XY")
    .box(center_marker_w - 2, MEETING_D - WALL * 2 - 8, marker_h)
    .translate((_center_cx, 0, FLOOR_H + marker_h / 2))
)
show_object(center_marker, name="zone_center",
            options={"color": (0.92, 0.69, 0.13, 0.85)})  # amber

# Top shell markers — compute tapered dimensions at marker Z
_top_marker_z = BASE_H + TOP_H - WALL - marker_h / 2 - 1  # Z ≈ 125.25
_top_marker_t = (TOP_H - WALL - marker_h / 2 - 1) / TOP_H  # fraction into top shell
_top_marker_w = MEETING_W + _top_marker_t * (TOP_W - MEETING_W)
_top_marker_d = MEETING_D + _top_marker_t * (TOP_D - MEETING_D)

# Top mist+fill zone marker (blue)
mist_fill_marker_w = abs(TOP_DIVIDER_WET_X - (-(_top_marker_w / 2 - WALL)))
mist_fill_marker = (
    cq.Workplane("XY")
    .box(mist_fill_marker_w - 4, _top_marker_d - WALL * 2 - 8, marker_h)
    .translate(((-(_top_marker_w / 2 - WALL) + TOP_DIVIDER_WET_X) / 2, 0,
                _top_marker_z))
)
show_object(mist_fill_marker, name="zone_mist_fill",
            options={"color": (0.15, 0.56, 0.94, 0.85)})  # blue

# Top bottles+storage zone marker (orange)
bottles_marker_w = (_top_marker_w / 2 - WALL) - TOP_DIVIDER_WET_X - WALL_INNER / 2
bottles_marker = (
    cq.Workplane("XY")
    .box(bottles_marker_w - 4, _top_marker_d - WALL * 2 - 8, marker_h)
    .translate(((TOP_DIVIDER_WET_X + WALL_INNER / 2 + _top_marker_w / 2 - WALL) / 2, 0,
                _top_marker_z))
)
show_object(bottles_marker, name="zone_bottles_storage",
            options={"color": (0.96, 0.49, 0.13, 0.85)})  # orange

# --- Button color indicators ---
btn_x_center = 0
power_btn_x = btn_x_center + (0 - (TOUCH_BTN_COUNT - 1) / 2) * TOUCH_BTN_SPACING
mist_btn_x = btn_x_center + (1 - (TOUCH_BTN_COUNT - 1) / 2) * TOUCH_BTN_SPACING

power_btn_marker = (
    cq.Workplane("XY")
    .workplane(offset=BASE_H + TOP_H + 0.1)
    .center(power_btn_x, TOUCH_BTN_Y)
    .circle(TOUCH_ZONE_DIA / 2 - 2)
    .extrude(0.5)
)
show_object(power_btn_marker, name="btn_power",
            options={"color": (0.9, 0.15, 0.15, 0.95)})  # red

mist_btn_marker = (
    cq.Workplane("XY")
    .workplane(offset=BASE_H + TOP_H + 0.1)
    .center(mist_btn_x, TOUCH_BTN_Y)
    .circle(TOUCH_ZONE_DIA / 2 - 2)
    .extrude(0.5)
)
show_object(mist_btn_marker, name="btn_mist",
            options={"color": (0.08, 0.82, 0.82, 0.95)})  # cyan/teal

# --- Internal components (fitment check) ---
components = build_components()
for comp_name, (comp_solid, comp_color) in components.items():
    show_object(comp_solid, name=f"comp_{comp_name}",
                options={"color": comp_color})


# =============================================================================
# ASSEMBLY SUMMARY
# =============================================================================

_wet_left = -(MEETING_W / 2 - WALL)
_wet_right = DIVIDER_WET_X
_center_left = DIVIDER_WET_X + WALL_INNER / 2
_center_right = MEETING_W / 2 - WALL

print("=" * 60)
print("Somni Oil Diffuser V3.3 — Compact Grid")
print("=" * 60)
print()
print(f"Three-part: base ({BASE_W}x{BASE_D}mm) + electronics tray + top shell")
print("Zones: wet | center (2-level: 2+3 pump grid + electronics tray)")
print("Top shell: mist+fill | bottles+storage (3+2 grid)")
print("Assembly: 1) pumps -> 2) tray -> 3) boards -> 4) top shell (bottles pre-loaded)")
print()
print("--- BOM (verified dimensions) ---")
print(f"Pumps:       {PUMP_TOTAL}x JIHPUMP WX3 ({PUMP_BODY_W}x{PUMP_BODY_D}x{PUMP_BODY_H}mm, 5V)")
print(f"Atomizer:    20mm/113KHz piezo + {ATOMIZER_DRIVER_W}x{ATOMIZER_DRIVER_D}mm driver (5V)")
print(f"MCU:         ESP32 DevKit ({ESP32_W}x{ESP32_D}mm)")
print(f"MOSFETs:     8-ch board ({MOSFET_BOARD_W}x{MOSFET_BOARD_D}x{MOSFET_BOARD_H}mm, using {MOSFET_COUNT} ch)")
print(f"PD trigger:  CH224K ({PD_TRIGGER_W}x{PD_TRIGGER_D}mm)")
print(f"Buck conv:   MP1584EN ({BUCK_CONV_W}x{BUCK_CONV_D}mm, 12V->5V)")
print(f"Buttons:     {TOUCH_BTN_COUNT}x TTP223 capacitive ({TOUCH_BTN_W}x{TOUCH_BTN_D}mm)")
print(f"LEDs:        WS2812B strip ({LED_CHANNEL_W}mm wide)")
print()
print("--- Enclosure (3 parts) ---")
print(f"Base:        {BASE_W}x{BASE_D}x{BASE_H}mm (bottom)")
print(f"             {MEETING_W:.1f}x{MEETING_D:.1f}mm (meeting line)")
print(f"Elec tray:   lift-out shelf in center zone (Z={TRAY_Z}mm)")
print(f"Top shell:   {TOP_W:.1f}x{TOP_D:.1f}mm (top)")
print(f"Total:       {TOTAL_H}mm tall")
print()
print("--- Base Zones (left to right) ---")
print(f"WET ZONE:    X={_wet_left:.1f} to {_wet_right}mm ({_wet_right - _wet_left:.0f}mm wide)  [TEAL]")
print(f"  Reservoir: depth={RESERVOIR_DEPTH:.1f}mm")
print(f"  Atomizer:  {ATOMIZER_MOUNT_DIA}mm at ({ATOMIZER_POS_X}, {ATOMIZER_POS_Y})")
print()
print(f"CENTER ZONE: X={_center_left:.1f} to {_center_right:.1f}mm ({_center_right - _center_left:.0f}mm wide)  [AMBER]")
print(f"  Lower:     {PUMP_TOTAL}x WX3 pumps in 2+3 grid")
print(f"  Left col:  {PUMP_LEFT_COL_COUNT} pumps at X={_pump_left_col_cx:.1f}")
print(f"  Right col: {PUMP_RIGHT_COL_COUNT} pumps at X={_pump_right_col_cx:.1f}")
print(f"  Upper:     Electronics tray (lift-out, Z={TRAY_Z}mm)")
print(f"  Tray ledges on left divider + right outer wall, 4 registration tab slots")
print()
print("--- Electronics Tray (lift-out shelf) ---")
print(f"  Left col:  ESP32 ({ESP32_D}x{ESP32_W}mm) + BME280 ({BME280_W}x{BME280_D}mm)")
print(f"  Right col: MOSFET ({MOSFET_BOARD_D}x{MOSFET_BOARD_W}mm)")
print(f"             Atm driver ({ATOMIZER_DRIVER_D}x{ATOMIZER_DRIVER_W}mm, Z-stacked on MOSFET)")
print(f"             PD+Buck Z-stacked ({PD_TRIGGER_W}x{PD_TRIGGER_D} + {BUCK_CONV_W}x{BUCK_CONV_D}mm)")
print(f"  USB-C:     {USBC_PORT_W}x{USBC_PORT_H}mm (rear wall, center zone)")
print()
print("--- Top Shell Zones (left to right) ---")
print(f"MIST+FILL:   above wet zone  [BLUE]")
print(f"  Chimney:    {MIST_CHANNEL_DIA}mm bore at ({MIST_POS_X}, {MIST_POS_Y})")
print(f"  Exhaust:    {EXHAUST_W}x{EXHAUST_D}mm chevron, 3 vanes")
print(f"  Fill chute: {FILL_CHUTE_TOP_W}x{FILL_CHUTE_TOP_D}mm top -> {FILL_CHUTE_BOT_W}x{FILL_CHUTE_BOT_D}mm bottom")
print()
print(f"BOTTLES+STORAGE: above center zone  [ORANGE]")
print(f"  Bottles:   {BOTTLE_TOTAL}x {BOTTLE_DIA}mm dia wells in 3+2 grid")
print(f"  Row 1 (3): X={_bottle_row1_cx:.1f}, Y={[f'{y:.0f}' for y in _bottle_row1_ys]}")
print(f"  Row 2 (2): X={_bottle_row2_cx:.1f}, Y={[f'{y:.0f}' for y in _bottle_row2_ys]}")
print(f"  Bottles hang cap-down from ceiling (3mm recess + 15mm retaining rings)")
print()
print(f"--- Assembly (building Legos) ---")
print(f"1. Drop pumps into center zone pockets (2+3 grid, shelf ledges hold them)")
print(f"2. Set electronics tray on ledges (left divider + right wall, tabs locate it)")
print(f"3. Drop boards into tray pockets (rail slots + snap tabs)")
print(f"4. Load bottles cap-down into top shell ceiling wells (3+2 grid)")
print(f"5. Place top shell (magnets + pins align it)")
print()
print(f"Print bed:   {BASE_W}x{BASE_D}mm fits QIDI Q2 (245x255mm)")
