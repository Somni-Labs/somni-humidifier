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
WIRE_PORT_Z = FLOOR_H + 1

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

    # === WIRE CHANNEL NETWORK (base floor only) ===
    # Atomizer spur: wires route through divider port, then through air gap
    # between left-column pumps (tight but sufficient for thin wires)
    _atm_spur_y = 0  # wire corridor runs at Y=0

    # Wet zone channel: from left divider to atomizer X position
    _atm_seg2_x_start = ATOMIZER_POS_X
    _atm_seg2_x_end = DIVIDER_WET_X - WALL_INNER / 2 - 1
    atm_seg2 = (
        cq.Workplane("XY")
        .box(abs(_atm_seg2_x_end - _atm_seg2_x_start), CHANNEL_W, CHANNEL_D)
        .translate(((_atm_seg2_x_start + _atm_seg2_x_end) / 2, _atm_spur_y,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_seg2)

    # === CROSS-DIVIDER WIRE PORTS ===

    # Left divider: atomizer spur port
    atm_port_left = (
        cq.Workplane("XY")
        .workplane(offset=WIRE_PORT_Z)
        .center(DIVIDER_WET_X, _atm_spur_y)
        .rect(WALL_INNER + 2, WIRE_PORT_W)
        .extrude(WIRE_PORT_H)
    )
    base = base.cut(atm_port_left)

    # Left divider: tray wire pass-through
    tray_wire_port = (
        cq.Workplane("XY")
        .workplane(offset=TRAY_Z + TRAY_FLOOR)
        .center(DIVIDER_WET_X, 0)
        .rect(WALL_INNER + 2, 8)
        .extrude(6)
    )
    base = base.cut(tray_wire_port)

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
    # WIRE CHANNEL VISUALIZATION (base floor only)
    # =============================================
    _ch_z = FLOOR_H + CHANNEL_D / 2
    _atm_spur_y = 0

    # Atomizer spur: wet zone horizontal (divider to atomizer)
    _as2_xs = ATOMIZER_POS_X
    _as2_xe = DIVIDER_WET_X - WALL_INNER / 2 - 1
    atm_s2_vis = (
        cq.Workplane("XY")
        .box(abs(_as2_xe - _as2_xs), CHANNEL_W - 0.5, CHANNEL_D - 0.5)
        .translate(((_as2_xs + _as2_xe) / 2, _atm_spur_y, _ch_z))
    )
    parts["wire_atm_spur"] = (atm_s2_vis, (0.85, 0.15, 0.85, 0.85))

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
# DIMENSION ANNOTATIONS
# =============================================================================
# Thin colored lines with endpoint dots showing key measurements.
# Convention: Red = X (width), Green = Y (depth), Blue = Z (height)
# Lines are 0.8mm thick, endpoint dots are 2.5mm cubes.

_dim_line_t = 0.8    # line thickness
_dim_dot_s = 2.5     # endpoint dot size
_dim_offset = 8      # how far outside the enclosure to place lines

# --- Helper: dimension line with endpoint dots ---
def _dim_line(x1, y1, z1, x2, y2, z2, color, name):
    """Create a dimension line from (x1,y1,z1) to (x2,y2,z2) with endpoint cubes."""
    dx = x2 - x1; dy = y2 - y1; dz = z2 - z1
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    cx = (x1 + x2) / 2; cy = (y1 + y2) / 2; cz = (z1 + z2) / 2

    # Line body (thin box along the dominant axis)
    if abs(dx) >= abs(dy) and abs(dx) >= abs(dz):
        line = cq.Workplane("XY").box(length, _dim_line_t, _dim_line_t).translate((cx, cy, cz))
    elif abs(dy) >= abs(dx) and abs(dy) >= abs(dz):
        line = cq.Workplane("XY").box(_dim_line_t, length, _dim_line_t).translate((cx, cy, cz))
    else:
        line = cq.Workplane("XY").box(_dim_line_t, _dim_line_t, length).translate((cx, cy, cz))

    # Endpoint dots
    dot1 = cq.Workplane("XY").box(_dim_dot_s, _dim_dot_s, _dim_dot_s).translate((x1, y1, z1))
    dot2 = cq.Workplane("XY").box(_dim_dot_s, _dim_dot_s, _dim_dot_s).translate((x2, y2, z2))

    result = line.union(dot1).union(dot2)
    show_object(result, name=f"dim_{name}", options={"color": color})


# --- Overall envelope at base (Z=0) ---
_env_z = -_dim_offset / 2   # slightly below base
_red   = (1.0, 0.15, 0.15, 0.95)   # X dimensions
_green = (0.15, 0.85, 0.15, 0.95)  # Y dimensions
_blue  = (0.15, 0.15, 1.0, 0.95)   # Z dimensions
_white = (0.95, 0.95, 0.95, 0.9)   # zone widths

# Base width (X) — along front edge
_dim_line(-BASE_W/2, -BASE_D/2 - _dim_offset, 0,
           BASE_W/2, -BASE_D/2 - _dim_offset, 0,
          _red, f"base_W_{BASE_W}mm")

# Base depth (Y) — along left edge
_dim_line(-BASE_W/2 - _dim_offset, -BASE_D/2, 0,
          -BASE_W/2 - _dim_offset,  BASE_D/2, 0,
          _green, f"base_D_{BASE_D}mm")

# Total height (Z) — along front-left corner
_dim_line(-BASE_W/2 - _dim_offset, -BASE_D/2 - _dim_offset, 0,
          -BASE_W/2 - _dim_offset, -BASE_D/2 - _dim_offset, TOTAL_H,
          _blue, f"total_H_{TOTAL_H}mm")

# Meeting line width (X) — at Z=BASE_H, front edge
_dim_line(-MEETING_W/2, -MEETING_D/2 - _dim_offset + 3, BASE_H,
           MEETING_W/2, -MEETING_D/2 - _dim_offset + 3, BASE_H,
          _red, f"meeting_W_{MEETING_W:.0f}mm")

# Meeting line depth (Y) — at Z=BASE_H, left edge
_dim_line(-MEETING_W/2 - _dim_offset + 3, -MEETING_D/2, BASE_H,
          -MEETING_W/2 - _dim_offset + 3,  MEETING_D/2, BASE_H,
          _green, f"meeting_D_{MEETING_D:.0f}mm")

# Crown width and depth (X, Y at top)
_dim_line(-TOP_W/2, -TOP_D/2 - _dim_offset + 5, TOTAL_H,
           TOP_W/2, -TOP_D/2 - _dim_offset + 5, TOTAL_H,
          _red, f"crown_W_{TOP_W:.0f}mm")

_dim_line(-TOP_W/2 - _dim_offset + 5, -TOP_D/2, TOTAL_H,
          -TOP_W/2 - _dim_offset + 5,  TOP_D/2, TOTAL_H,
          _green, f"crown_D_{TOP_D:.0f}mm")

# --- Base height / Top shell height (Z split) ---
_corner_x = BASE_W/2 + _dim_offset
_corner_y = -BASE_D/2 - _dim_offset

# Base height
_dim_line(_corner_x, _corner_y, 0,
          _corner_x, _corner_y, BASE_H,
          _blue, f"base_H_{BASE_H}mm")

# Top shell height
_dim_line(_corner_x, _corner_y, BASE_H,
          _corner_x, _corner_y, TOTAL_H,
          _blue, f"top_H_{TOP_H}mm")

# --- Zone widths on base floor (Z = FLOOR_H + 1) ---
_zone_z = FLOOR_H + 2
_zone_y = -MEETING_D/2 + WALL + 3  # near front inner wall

_wet_inner_left = -(MEETING_W/2 - WALL)
_wet_inner_right = DIVIDER_WET_X - WALL_INNER/2
_center_inner_left_x = DIVIDER_WET_X + WALL_INNER/2
_center_inner_right_x = MEETING_W/2 - WALL

# Wet zone width
_dim_line(_wet_inner_left, _zone_y, _zone_z,
          _wet_inner_right, _zone_y, _zone_z,
          _white, f"wet_zone_{abs(_wet_inner_right - _wet_inner_left):.0f}mm")

# Center zone width
_dim_line(_center_inner_left_x, _zone_y, _zone_z,
          _center_inner_right_x, _zone_y, _zone_z,
          _white, f"center_zone_{abs(_center_inner_right_x - _center_inner_left_x):.0f}mm")

# --- Tray dimensions ---
_tray_inner_left = DIVIDER_WET_X + WALL_INNER/2 + TRAY_CLEARANCE
_tray_inner_right = MEETING_W/2 - WALL - TRAY_CLEARANCE
_tray_z_mid = TRAY_Z + TRAY_H / 2

# Tray width
_dim_line(_tray_inner_left, -MEETING_D/2 + WALL + 2, _tray_z_mid,
          _tray_inner_right, -MEETING_D/2 + WALL + 2, _tray_z_mid,
          _white, f"tray_W_{_tray_inner_right - _tray_inner_left:.0f}mm")

# --- Key clearance: atomizer to wet zone walls ---
_atm_clearance_z = FLOOR_H + 5
_dim_line(ATOMIZER_POS_X - ATOMIZER_MOUNT_DIA/2, ATOMIZER_POS_Y, _atm_clearance_z,
          _wet_inner_left, ATOMIZER_POS_Y, _atm_clearance_z,
          (1.0, 0.8, 0.0, 0.9),
          f"atm_wall_gap_{abs(ATOMIZER_POS_X - ATOMIZER_MOUNT_DIA/2 - _wet_inner_left):.1f}mm")

_dim_line(ATOMIZER_POS_X + ATOMIZER_MOUNT_DIA/2, ATOMIZER_POS_Y, _atm_clearance_z,
          _wet_inner_right, ATOMIZER_POS_Y, _atm_clearance_z,
          (1.0, 0.8, 0.0, 0.9),
          f"atm_div_gap_{abs(_wet_inner_right - (ATOMIZER_POS_X + ATOMIZER_MOUNT_DIA/2)):.1f}mm")


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
