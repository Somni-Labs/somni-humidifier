"""
Somni Oil Diffuser — V3.0 "Night City"

Cyberpunk-styled essential oil diffuser with automated scent blending.
200x160mm rectangular footprint (fits QIDI Q2 245x255mm bed).

REAL-WORLD BOM — all component dimensions verified from sourcing research:
  Pumps:     5× JIHPUMP WX3 micro peristaltic (23×35×25mm, 3.7-6V)
  Atomizer:  20mm/113KHz piezo + 35×25mm driver board (5V, 250-400mA)
  MCU:       ESP32 DevKit (55×28mm) — WiFi, 6× GPIO for MOSFETs
  MOSFETs:   8-ch MOSFET driver board (50×26mm, 3.3V logic-level, using 6 ch)
  Power:     USB-C → CH224K PD trigger (24×18mm) → 12V → MP1584EN buck (22×17mm) → 5V
  LEDs:      WS2812B strip (12mm wide, 5V), continuous perimeter loop
  Buttons:   2× TTP223 capacitive touch (11×15mm) — power + mist intensity
  Sensor:    Capacitive water level sensor on divider wall

Two-part enclosure connected via magnets:
  BASE  — holds everything: reservoir, atomizer, pumps, bottles, electronics
  SHELL — three-zone functional lid: fill chute + mist chimney, transit, storage

Bottles sit upright in the base. Lift the top shell off for full access.

Base layout (three zones, left to right):
  WET ZONE  (left)    — water reservoir + atomizer mount
  PUMP ROW  (center)  — 5× WX3 micro pumps (narrower than V2.3)
  DRY ZONE  (right)   — 5 bottle wells + electronics bay

Top shell layout (three zones, matching base dividers):
  MIST+FILL  (left)   — mist chimney + chevron exhaust + water fill chute
  TRANSIT    (center) — structural / cable routing gap above pump row
  STORAGE    (right)  — compartment for accessories/spare bottles

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
BASE_W = 200             # base footprint width (X) at Z=0
BASE_D = 160             # base footprint depth (Y) at Z=0
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

# --- Zone dividers ---
# Two divider walls run parallel to Y axis, creating three zones.
# Wet zone: X < DIVIDER_WET_X
# Pump row: DIVIDER_WET_X < X < DIVIDER_DRY_X (width = pump body + clearance)
# Dry zone: X > DIVIDER_DRY_X (bottles + electronics)
# V3.0: WX3 pumps oriented 35mm along X, need 39mm pump row (35 + 4mm clearance)
DIVIDER_WET_X = -17      # left divider (wet/pump boundary)
DIVIDER_DRY_X = 22       # right divider (pump/dry boundary)
# Pump row width: 39mm — fits 35mm WX3 body (oriented lengthwise) + clearance

# --- Water reservoir (wet zone) ---
RESERVOIR_DEPTH = BASE_H - FLOOR_H - WALL

# --- Ultrasonic atomizer ---
ATOMIZER_DIA = 20
ATOMIZER_DRIVER_W = 35
ATOMIZER_DRIVER_D = 25
ATOMIZER_MOUNT_DIA = 26
ATOMIZER_POS_X = -55         # well into wet zone (left side)
ATOMIZER_POS_Y = 0           # centered front-to-back

# --- Peristaltic pumps (5x JIHPUMP WX3 micro, in pump row) ---
# WX3: 23mm wide × 35mm long × 25mm tall, 3.7-6V, up to 10ml/min
# Oriented with 35mm (length) along X (across pump row) and 23mm (width) along Y.
# At 26mm Y-spacing: 3mm clearance between 23mm bodies.
# Pump row needs ~39mm in X (35mm body + 2mm clearance each side).
PUMP_BODY_W = 35             # WX3 length oriented along X (across pump row)
PUMP_BODY_D = 23             # WX3 width oriented along Y (along the row)
PUMP_BODY_H = 25             # WX3 height
PUMP_COUNT = 5
PUMP_SPACING = 26            # center-to-center along Y axis
# Pumps sit centered between the two dividers
PUMP_CENTER_X = (DIVIDER_WET_X + DIVIDER_DRY_X) / 2

# --- Oil bottles (5x, in dry zone) ---
# 15ml essential oil bottles (industry standard): body ~22mm dia, cap ~18mm dia
# Total height ~55mm with cap (fits in 67mm usable height).
# NOTE: 50ml bottles (33mm × 95mm) are too tall for the 70mm base.
# Parametric — change BOTTLE_DIA/HEIGHT to accommodate other sizes.
BOTTLE_DIA = 22              # 15ml bottle body diameter
BOTTLE_CAP_DIA = 18          # dropper/screw cap diameter (narrower than body)
BOTTLE_HEIGHT = 55           # total height with cap (must fit in base)
BOTTLE_COUNT = 5
BOTTLE_WELL_DEPTH = 6        # deeper ring for secure seating
BOTTLE_WELL_DIA = BOTTLE_DIA + 2 * TOL + 2  # ~24.8mm
BOTTLE_SPACING = 26          # center-to-center along Y axis
# Bottles sit in the dry zone, centered front-to-back
BOTTLE_ROW_X = DIVIDER_DRY_X + WALL_INNER / 2 + BOTTLE_WELL_DIA / 2 + 3
BOTTLE_ROW_Y_CENTER = 0

# Bottle Y positions (row of 5)
bottle_y_positions = [-(BOTTLE_COUNT - 1) / 2 * BOTTLE_SPACING + i * BOTTLE_SPACING
                       for i in range(BOTTLE_COUNT)]

# --- Bottle retention clips (swing-latch over bottle neck) ---
# Printed hinged clips that swing over the bottle neck to lock it in place.
# Each clip pivots on a small pin at the base of the retaining wall and
# snaps over the cap/neck area. The clip arm spans across the bottle top.
CLIP_ARM_W = 4               # width of the clip arm
CLIP_ARM_H = 3               # thickness of the clip arm
CLIP_PIN_DIA = 2.0           # hinge pin diameter
CLIP_PIN_H = 5               # hinge post height (above retainer ring)
CLIP_CATCH_H = 8             # height of the catch hook on the opposite side
# Clip pivots on the "left" side of each well (toward divider),
# swings over the bottle, and catches on the "right" side.

# --- Tube clips (printed guide rings on the base floor) ---
TUBE_CLIP_DIA = 6            # outer diameter of tube guide
TUBE_CLIP_H = 5              # height of guide post

# --- Electronics bay (dry zone, RIGHT column beside bottles) ---
# Bottles occupy X ≈ 24–53. Electronics go in a column at X ≈ 56–84.
# All boards stacked along Y (front→rear) in that ~28mm-wide column.
ESP32_W = 55                 # ESP32 DevKit V1 long dimension
ESP32_D = 28                 # ESP32 DevKit V1 short dimension
ESP32_H = 13
# Single 8-channel MOSFET board replaces 6 individual 25×20mm modules.
# Common "8CH 3.3V/5V logic-level MOSFET driver" from AliExpress/Amazon.
MOSFET_BOARD_W = 50          # board long dimension (placed along Y)
MOSFET_BOARD_D = 26          # board short dimension (across X, fits in 28mm col)
MOSFET_BOARD_H = 12
MOSFET_COUNT = 6             # using 6 of 8 channels
PD_TRIGGER_W = 24            # CH224K module (verified)
PD_TRIGGER_D = 18
PD_TRIGGER_H = 8
BUCK_CONV_W = 22             # MP1584EN buck converter (verified)
BUCK_CONV_D = 17
BUCK_CONV_H = 5
BME280_W = 15
BME280_D = 12
BME280_H = 5

# --- PCB retention features ---
# Rail slots (ESP32, MOSFET board, PD trigger) — board slides in from top
RAIL_GROOVE_W = 1.2          # groove width in pocket wall
RAIL_GROOVE_D = 1.5          # groove depth into pocket wall
RAIL_CLEARANCE = 0.3         # clearance per side
RAIL_LIFT = 2.0              # board sits this far above pocket floor
RAIL_CHAMFER = 0.5           # entry chamfer at top of rail

# Snap tabs (buck converter, atomizer driver) — press-fit nubs
SNAP_NUB_W = 1.5             # nub width along pocket wall
SNAP_NUB_H = 1.0             # nub protrusion from wall
SNAP_NUB_ANGLE = 45          # entry ramp angle (degrees)

# Pump shelf ledges — anti-vibration lips inside pump pockets
PUMP_LEDGE_LIP = 1.0         # ledge protrusion into pocket
PUMP_LEDGE_H = 1.5           # ledge thickness (Z)

# --- Wire channel network ---
CHANNEL_W = 3.0              # channel width (open-top groove)
CHANNEL_D = 3.0              # channel depth into floor
CHANNEL_NOTCH_W = 3.0        # notch width where channel meets pocket wall
CHANNEL_NOTCH_H = 3.0        # notch height in pocket wall

# Cross-divider wire ports
WIRE_PORT_W = 5.0            # port width
WIRE_PORT_H = 4.0            # port height
WIRE_PORT_Z = FLOOR_H + 1   # port bottom Z position

# --- Capacitive touch buttons (top shell surface) ---
TOUCH_BTN_W = 15             # TTP223 module width (verified)
TOUCH_BTN_D = 11             # TTP223 module depth (verified)
TOUCH_BTN_H = 2              # module thickness (glued to underside)
TOUCH_ZONE_DIA = 20          # touch-sensitive area on top surface
TOUCH_BTN_COUNT = 2          # power + mist intensity
TOUCH_BTN_SPACING = 35       # center-to-center between buttons
# Buttons centered on the front edge of the top shell, Y offset toward front
TOUCH_BTN_Y = -40            # front half of top shell

# --- USB-C port (rear panel) ---
USBC_PORT_W = 12
USBC_PORT_H = 7

# --- Rubber feet ---
FOOT_DIA = 12
FOOT_DEPTH = 1.8
FOOT_INSET = 20

# --- Magnet pockets ---
MAGNET_DIA = 6
MAGNET_H = 3
MAGNET_INSET = 30

# --- Alignment pins ---
PIN_DIA = 4
PIN_H = 6

# --- Mist channel (top shell) ---
MIST_CHANNEL_DIA = 30
MIST_CHANNEL_WALL = 2.5
MIST_POS_X = ATOMIZER_POS_X
MIST_POS_Y = ATOMIZER_POS_Y

# --- Water fill chute (top shell, left zone) ---
# Funnel on top surface that channels water down through the top shell
# directly into the wet zone reservoir below. Offset to rear of wet zone
# to avoid the mist chimney (which is centered at ATOMIZER_POS_X, 0).
FILL_CHUTE_TOP_W = 35           # opening at top surface (wide funnel mouth)
FILL_CHUTE_TOP_D = 40
FILL_CHUTE_BOT_W = 18           # narrower at bottom (drip into reservoir)
FILL_CHUTE_BOT_D = 25
FILL_CHUTE_POS_X = ATOMIZER_POS_X  # same X as atomizer (wet zone center)
FILL_CHUTE_POS_Y = 45              # rear half of wet zone, away from chimney
FILL_CHUTE_LIP_H = 3               # raised lip to prevent spills

# --- Top shell zone dividers ---
# Mirror the base dividers but in the top shell coordinate space
TOP_DIVIDER_WET_X = DIVIDER_WET_X    # left divider (mist+fill | transit)
TOP_DIVIDER_DRY_X = DIVIDER_DRY_X    # right divider (transit | storage)

# --- Storage compartment (top shell, right zone) ---
STORAGE_LID_RECESS = 2.0       # recessed edge for a snap-fit lid
STORAGE_WALL = 2.0             # inner walls of storage compartment

# --- Exhaust port (top surface, chevron) ---
EXHAUST_W = 40
EXHAUST_D = 25
EXHAUST_POS_X = MIST_POS_X
EXHAUST_POS_Y = MIST_POS_Y

# --- Hex mesh ---
HEX_CELL_SIZE = 9
HEX_WALL = 1.5
HEX_MARGIN = 5

# --- LED strip channel (continuous perimeter loop) ---
LED_CHANNEL_W = 12           # WS2812B strip width
LED_CHANNEL_D = 5            # strip + adhesive depth (slightly deeper for routing)
# The strip runs a full loop around the inside of the base, behind all
# hex mesh panels. A single entry/exit point near the ESP32 for wiring.

# --- SOMNI branding ---
BRAND_DEPTH = 0.8            # deboss depth (slightly deeper for visibility)
BRAND_FONT_SIZE = 12         # "SOMNI" text size (mm)
BRAND_SUB_SIZE = 6           # "LABS" subtitle size (mm)


# =============================================================================
# SHARED POSITIONS
# =============================================================================

# Magnet positions — 6 total
magnet_positions = [
    (0, -MEETING_D / 2 + MAGNET_INSET),
    (0,  MEETING_D / 2 - MAGNET_INSET),
    (-MEETING_W / 2 + MAGNET_INSET, -MEETING_D / 4),
    (-MEETING_W / 2 + MAGNET_INSET,  MEETING_D / 4),
    ( MEETING_W / 2 - MAGNET_INSET, -MEETING_D / 4),
    ( MEETING_W / 2 - MAGNET_INSET,  MEETING_D / 4),
]

# Alignment pins — 4 corners
pin_positions = [
    (-MEETING_W / 2 + 15, -MEETING_D / 2 + 15),
    ( MEETING_W / 2 - 15, -MEETING_D / 2 + 15),
    (-MEETING_W / 2 + 15,  MEETING_D / 2 - 15),
    ( MEETING_W / 2 - 15,  MEETING_D / 2 - 15),
]

# Pump Y positions (row of 5 centered along Y)
pump_y_positions = [-(PUMP_COUNT - 1) / 2 * PUMP_SPACING + i * PUMP_SPACING
                     for i in range(PUMP_COUNT)]


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
    """Honeycomb hex pattern, pointy-top orientation. Extruded 100mm along Z."""
    pitch = cell_size + wall_thickness
    row_height = pitch * math.sqrt(3) / 2
    hex_radius = cell_size / 2
    usable_w = width - 2 * margin
    usable_h = height - 2 * margin
    cols = int(usable_w / pitch) + 1
    rows = int(usable_h / row_height) + 1
    cells = None
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
            cells = cell if cells is None else cells.union(cell)
    return cells if cells is not None else cq.Workplane("XY").box(0.1, 0.1, 0.1)


# =============================================================================
# BUILD BASE
# =============================================================================

def build_base():
    """Three-zone base: wet (left) | pumps (center) | dry+bottles (right).

    Bottles sit upright in the dry zone. Top shell lifts off for full access.
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

    # --- Divider walls (two, creating three zones) ---
    divider_h = BASE_H - FLOOR_H - WALL - 2

    # Left divider (wet zone | pump row)
    divider_left = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_WET_X, 0)
        .rect(WALL_INNER, BASE_D - WALL * 2 - 2)
        .extrude(divider_h)
    )
    base = base.union(divider_left)

    # Right divider (pump row | dry zone)
    divider_right = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_DRY_X, 0)
        .rect(WALL_INNER, BASE_D - WALL * 2 - 2)
        .extrude(divider_h)
    )
    base = base.union(divider_right)

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
    # Just a flat area — sensor adheres to the outside of the divider
    # (no physical geometry needed, but we mark it with a shallow recess)
    sensor_pad = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 15)
        .center(DIVIDER_WET_X - WALL_INNER / 2 - 0.5, 0)
        .rect(1, 20)
        .extrude(25)
    )
    base = base.cut(sensor_pad)

    # --- PUMP ROW (between dividers) ---

    # 5 pump pockets centered between dividers
    for py in pump_y_positions:
        pump_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(PUMP_CENTER_X, py)
            .rect(PUMP_BODY_W, PUMP_BODY_D)
            .extrude(PUMP_BODY_H + 2)
        )
        base = base.cut(pump_pocket)

    # Tube pass-through holes in LEFT divider (pump output → reservoir)
    # One per pump, at the top of the divider
    for py in pump_y_positions:
        tube_out = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + divider_h - 8)
            .center(DIVIDER_WET_X, py)
            .circle(3)
            .extrude(10)
        )
        base = base.cut(tube_out)

    # Tube pass-through holes in RIGHT divider (bottle → pump intake)
    # One per pump, matched to bottle positions
    for py in pump_y_positions:
        tube_in = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + divider_h - 8)
            .center(DIVIDER_DRY_X, py)
            .circle(3)
            .extrude(10)
        )
        base = base.cut(tube_in)

    # --- DRY ZONE (right of DIVIDER_DRY_X) ---
    # Front: 5 bottle wells in a row along Y
    # Rear: electronics (ESP32, MOSFETs, PD trigger, BME280, atomizer driver)

    # Bottle wells — deeper pockets with tall retaining walls + swing latch
    retainer_h = 18  # tall enough to grip ~1/3 of the bottle body
    for by in bottle_y_positions:
        # Well pocket (deeper for secure seating)
        well = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(BOTTLE_ROW_X, by)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(BOTTLE_WELL_DEPTH)
        )
        base = base.cut(well)

        # Tall retaining wall around each well — grips the bottle body
        retainer = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(BOTTLE_ROW_X, by)
            .circle(BOTTLE_WELL_DIA / 2 + 2)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(retainer_h)
        )
        base = base.union(retainer)

        # --- Swing latch (hinge + arm + catch) ---
        # Hinge post on the left side (toward divider) of the retainer ring.
        # The latch arm will be a separate printed piece that pivots on
        # this pin and snaps into the catch hook on the opposite side.
        hinge_x = BOTTLE_ROW_X - BOTTLE_WELL_DIA / 2 - 2
        hinge_z = FLOOR_H + retainer_h

        # Hinge post (vertical pin the latch arm rotates on)
        hinge_post = (
            cq.Workplane("XY")
            .workplane(offset=hinge_z)
            .center(hinge_x, by)
            .circle(CLIP_PIN_DIA / 2)
            .extrude(CLIP_PIN_H)
        )
        base = base.union(hinge_post)

        # Catch hook on the right side (opposite the hinge)
        # Small nub that the swing arm snaps behind when closed
        catch_x = BOTTLE_ROW_X + BOTTLE_WELL_DIA / 2 + 2
        catch_post = (
            cq.Workplane("XY")
            .workplane(offset=hinge_z)
            .center(catch_x, by)
            .rect(CLIP_ARM_W, CLIP_ARM_W)
            .extrude(CLIP_CATCH_H)
        )
        base = base.union(catch_post)

        # Catch undercut notch (the arm hooks behind this)
        catch_notch = (
            cq.Workplane("XY")
            .workplane(offset=hinge_z + CLIP_CATCH_H - 3)
            .center(catch_x - CLIP_ARM_W / 2, by)
            .rect(CLIP_ARM_W, CLIP_ARM_W + 1)
            .extrude(1.5)
        )
        base = base.cut(catch_notch)

    # Tube clip posts — guide tubes from bottle wells to pump intake holes
    # One clip per bottle, positioned between the bottle and the right divider
    clip_x = (BOTTLE_ROW_X + DIVIDER_DRY_X) / 2
    for by in bottle_y_positions:
        clip = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(clip_x, by)
            .circle(TUBE_CLIP_DIA / 2)
            .extrude(TUBE_CLIP_H)
        )
        # Hollow center for tube to pass through
        clip_bore = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H - 0.1)
            .center(clip_x, by)
            .circle(2)
            .extrude(TUBE_CLIP_H + 0.2)
        )
        base = base.union(clip)
        base = base.cut(clip_bore)

    # === ELECTRONICS COLUMN (right side of dry zone, X ≈ 55–90) ===
    # 34.6mm-wide column to the right of bottles, stacked along Y.
    # Compact layout: PD+Buck Z-stacked (front), MOSFET board (mid), ESP32 (rear).
    # Atomizer driver relocated to wet zone (near atomizer).
    # BME280 mounted on right divider wall (tiny sensor, doesn't need floor space).
    dry_left = DIVIDER_DRY_X + WALL_INNER / 2
    dry_right = MEETING_W / 2 - WALL
    _bottle_right = BOTTLE_ROW_X + BOTTLE_WELL_DIA / 2 + 4  # bottle + retainer + catch
    elec_col_x = (_bottle_right + dry_right) / 2
    interior_y_min = -(MEETING_D / 2 - WALL - 2)
    y_cursor = interior_y_min  # start from front wall

    # PD trigger + Buck converter Z-STACKED (buck on floor, PD on top)
    # Combined pocket: 24mm X (PD is wider) × 18mm Y (PD is deeper) × 15mm Z
    _pd_buck_w = max(PD_TRIGGER_W, BUCK_CONV_W)   # 24mm
    _pd_buck_d = max(PD_TRIGGER_D, BUCK_CONV_D)   # 18mm
    _pd_buck_h = BUCK_CONV_H + PD_TRIGGER_H + 2   # 5+8+2 = 15mm
    pd_buck_y = y_cursor + _pd_buck_d / 2
    pd_buck_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(elec_col_x, pd_buck_y)
        .rect(_pd_buck_w + 2, _pd_buck_d + 2)
        .extrude(_pd_buck_h)
    )
    base = base.cut(pd_buck_pocket)

    # Rail slots for PD trigger board (slides in from top)
    _pdb_pocket_hw = (_pd_buck_w + 2) / 2  # half-width of pocket in X
    for _rail_side in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + RAIL_LIFT)
            .center(elec_col_x + _rail_side * (_pdb_pocket_hw - RAIL_GROOVE_D / 2),
                    pd_buck_y)
            .rect(RAIL_GROOVE_D, _pd_buck_d)
            .extrude(_pd_buck_h - RAIL_LIFT)
        )
        base = base.union(rail)

    y_cursor += _pd_buck_d + 3

    # 8-channel MOSFET board (50×26mm, long dim along Y, short dim across X)
    mosfet_y = y_cursor + MOSFET_BOARD_W / 2  # 50mm along Y
    mosfet_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(elec_col_x, mosfet_y)
        .rect(MOSFET_BOARD_D + 2, MOSFET_BOARD_W + 2)  # 28mm X, 52mm Y
        .extrude(MOSFET_BOARD_H + 2)
    )
    base = base.cut(mosfet_pocket)

    # Rail slots for MOSFET board (slides in from top)
    _mos_pocket_hw = (MOSFET_BOARD_D + 2) / 2  # half-width in X
    for _rail_side in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + RAIL_LIFT)
            .center(elec_col_x + _rail_side * (_mos_pocket_hw - RAIL_GROOVE_D / 2),
                    mosfet_y)
            .rect(RAIL_GROOVE_D, MOSFET_BOARD_W)
            .extrude(MOSFET_BOARD_H + 2 - RAIL_LIFT)
        )
        base = base.union(rail)

    y_cursor += MOSFET_BOARD_W + 3

    # ESP32 DevKit (55×28mm, long dim along Y, short dim across X)
    esp32_y = y_cursor + ESP32_W / 2  # 55mm along Y
    esp32_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(elec_col_x, esp32_y)
        .rect(ESP32_D + 2, ESP32_W + 2)  # 30mm X, 57mm Y
        .extrude(ESP32_H + 2)
    )
    base = base.cut(esp32_pocket)

    # Rail slots for ESP32 (slides in from top)
    _esp_pocket_hw = (ESP32_D + 2) / 2  # half-width in X
    for _rail_side in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + RAIL_LIFT)
            .center(elec_col_x + _rail_side * (_esp_pocket_hw - RAIL_GROOVE_D / 2),
                    esp32_y)
            .rect(RAIL_GROOVE_D, ESP32_W)
            .extrude(ESP32_H + 2 - RAIL_LIFT)
        )
        base = base.union(rail)

    # BME280 sensor — sits on top of MOSFET board (Z-stacked in electronics column).
    # Tiny board (15×12×5mm) rests above the MOSFET (Z=FLOOR_H+MOSFET_BOARD_H+2).
    # No separate pocket needed — it just sits on the MOSFET board surface.
    # The combined height (MOSFET 12mm + gap 2mm + BME280 5mm = 19mm) is well
    # within the 64mm usable height.

    # Atomizer driver pocket — wet zone floor, rear area (near atomizer)
    # Driver board (35×25mm) placed flat on floor behind the atomizer.
    _atm_drv_x = ATOMIZER_POS_X
    _atm_drv_y = ATOMIZER_POS_Y + ATOMIZER_MOUNT_DIA / 2 + 5 + ATOMIZER_DRIVER_D / 2
    atm_driver_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(_atm_drv_x, _atm_drv_y)
        .rect(ATOMIZER_DRIVER_W, ATOMIZER_DRIVER_D)
        .extrude(8)
    )
    base = base.cut(atm_driver_pocket)

    # --- USB-C port cutout (rear wall, aligned with electronics column) ---
    usbc_cutout = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + ESP32_H / 2)
        .center(elec_col_x, BASE_D / 2)
        .rect(USBC_PORT_W, WALL + 2)
        .extrude(USBC_PORT_H)
    )
    base = base.cut(usbc_cutout)

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
    # The WS2812B strip runs a full loop inside the base walls, behind the
    # hex mesh panels. Channel sits near the top of the base for max glow.
    led_z = BASE_H - WALL - LED_CHANNEL_D - 2
    # Interpolate wall positions at LED channel height for taper
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
    hex_front = hex_mesh_cutout(BASE_W * 0.7, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_front_pos = (hex_front
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((0, -(BASE_D / 2 - _taper_shrink_base * 0.5), hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_front_pos)

    # Left wall hex mesh (wet zone glow)
    hex_left = hex_mesh_cutout(BASE_D * 0.5, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_left_pos = (hex_left
        .rotateAboutCenter((0, 0, 1), 90)
        .rotateAboutCenter((0, 1, 0), 90)
        .translate((-(BASE_W / 2 - _taper_shrink_base * 0.5), 0, hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_left_pos)

    # Rear wall hex mesh
    hex_rear = hex_mesh_cutout(BASE_W * 0.5, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_rear_pos = (hex_rear
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((0, (BASE_D / 2 - _taper_shrink_base * 0.5), hex_panel_z + hex_panel_h / 2)))
    base = base.cut(hex_rear_pos)

    # Right wall hex mesh (dry zone, LED glow through)
    hex_right = hex_mesh_cutout(BASE_D * 0.5, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
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
    # Full logo: S-curve wave icon (from somni-icon.svg) + wordmark.
    # The SVG has 8 bezier S-curves; we render 4 (every other) as debossed
    # grooves traced by overlapping cylinder cuts along the path.
    # Each groove is 1.2mm wide, 0.8mm deep — visible and printable.
    #
    # Layout: [wave icon ~25mm] [gap] [SOMNI / LABS text]
    brand_z = BASE_H * 0.30    # vertical center of branding on rear wall
    logo_cx = -22              # icon center X (left of text)
    groove_r = 0.6             # groove half-width (1.2mm diameter cuts)
    groove_d = BRAND_DEPTH     # groove depth into wall

    # S-curve waypoints — sampled from SVG bezier paths, scaled to 25mm.
    # Coordinates are (X_on_wall, Z_on_wall) relative to icon center.
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

    # Cut each S-curve by placing small box cuts at each waypoint, translated
    # to the rear wall (+Y face). CadQuery's XZ workplane extrude doesn't
    # reliably cut at large Y offsets, so we use box().translate() instead.
    groove_size = groove_r * 2  # 1.2mm square cross-section per cut
    for curve_pts in s_curves:
        for cx_pt, cz_pt in curve_pts:
            px = logo_cx + cx_pt
            pz = brand_z + cz_pt
            cut = (
                cq.Workplane("XY")
                .box(groove_size, groove_d + 1, groove_size)
                .translate((px, BASE_D / 2 - groove_d / 2 + 0.5, pz))
            )
            base = base.cut(cut)

    # Center circle — approximate with ring of small box cuts
    center_ring_r = 2.0
    center_dot_r = 1.0
    num_ring_pts = 16
    for i in range(num_ring_pts):
        angle = 2 * math.pi * i / num_ring_pts
        rx = logo_cx + center_ring_r * math.cos(angle)
        rz = brand_z + center_ring_r * math.sin(angle)
        ring_cut = (
            cq.Workplane("XY")
            .box(groove_size, groove_d + 1, groove_size)
            .translate((rx, BASE_D / 2 - groove_d / 2 + 0.5, rz))
        )
        base = base.cut(ring_cut)

    # Center dot
    dot_cut = (
        cq.Workplane("XY")
        .box(center_dot_r * 2, groove_d + 1, center_dot_r * 2)
        .translate((logo_cx, BASE_D / 2 - groove_d / 2 + 0.5, brand_z))
    )
    base = base.cut(dot_cut)

    # Wordmark: "SOMNI" + "LABS" to the right of the icon
    try:
        brand_main = (
            cq.Workplane("XZ")
            .workplane(offset=BASE_D / 2)
            .center(4, brand_z + 4)
            .text("SOMNI", BRAND_FONT_SIZE, -BRAND_DEPTH, font="sans-serif")
        )
        base = base.cut(brand_main)
        brand_sub = (
            cq.Workplane("XZ")
            .workplane(offset=BASE_D / 2)
            .center(4, brand_z - 6)
            .text("LABS", BRAND_SUB_SIZE, -BRAND_DEPTH, font="sans-serif")
        )
        base = base.cut(brand_sub)
    except Exception:
        brand_recess = (
            cq.Workplane("XY")
            .workplane(offset=brand_z)
            .center(4, BASE_D / 2)
            .rect(45, 16)
            .extrude(-BRAND_DEPTH)
        )
        base = base.cut(brand_recess)

    return base


# =============================================================================
# BUILD TOP SHELL
# =============================================================================

def build_top_shell():
    """Three-zone functional lid matching base divider layout.

    MIST+FILL (left)   — mist chimney + chevron exhaust + water fill chute
    TRANSIT   (center) — structural gap above pump row, cable routing
    STORAGE   (right)  — compartment for accessories, spare bottles, etc.

    Lifts off for full access to everything in the base.
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

    # --- Internal divider walls (creating three zones) ---
    # These mirror the base dividers so each top zone aligns with its base zone.
    top_divider_h = TOP_H - WALL * 2 - 1  # slightly shorter than cavity

    # Left divider (fill zone | mist zone)
    top_div_left = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(TOP_DIVIDER_WET_X, 0)
        .rect(WALL_INNER, MEETING_D - WALL * 2 - 2)
        .extrude(top_divider_h)
    )
    shell = shell.union(top_div_left)

    # Right divider (mist zone | storage)
    top_div_right = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(TOP_DIVIDER_DRY_X, 0)
        .rect(WALL_INNER, MEETING_D - WALL * 2 - 2)
        .extrude(top_divider_h)
    )
    shell = shell.union(top_div_right)

    # =============================================
    # MIST+FILL ZONE (left) — chimney, exhaust, fill chute
    # =============================================

    # --- Water fill chute (rear of left zone) ---
    # Tapered funnel: wide opening at top, narrow channel at bottom.
    # Water pours in from the top and drains into the wet zone reservoir
    # when the shell sits on the base. The bottom of the chute is open
    # (shell bottom is open at Z=0) so water falls straight through.

    # Top opening (funnel mouth) — cut through the top ceiling
    fill_top_cut = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - WALL - 0.1)
        .center(FILL_CHUTE_POS_X, FILL_CHUTE_POS_Y)
        .rect(FILL_CHUTE_TOP_W, FILL_CHUTE_TOP_D)
        .extrude(WALL + 0.2)
    )
    shell = shell.cut(fill_top_cut)

    # Raised lip around the fill opening to prevent spills
    fill_lip = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H)
        .center(FILL_CHUTE_POS_X, FILL_CHUTE_POS_Y)
        .rect(FILL_CHUTE_TOP_W + 4, FILL_CHUTE_TOP_D + 4)
        .rect(FILL_CHUTE_TOP_W, FILL_CHUTE_TOP_D)
        .extrude(FILL_CHUTE_LIP_H)
    )
    shell = shell.union(fill_lip)

    # Internal funnel walls — tapered from top opening down to narrower bottom.
    # Build the funnel centered at origin, then translate to position.
    # (CadQuery loft with off-center workplanes can double-offset — avoid it.)
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

    # Cut the inner bore of the funnel to ensure it's clear
    shell = shell.cut(_funnel_inner)

    # --- Mist chimney + exhaust (also in left zone, above atomizer) ---
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

    # Chevron exhaust port (on top surface, above the chimney)
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
    # TRANSIT ZONE (center) — structural gap above pump row
    # =============================================
    # This zone provides structural rigidity and a cable routing path
    # between the left (mist+fill) and right (storage) zones.
    # The divider walls already define the boundaries. No additional
    # features needed — it acts as an air gap / structural member.

    # =============================================
    # STORAGE ZONE (right) — accessory compartment
    # =============================================
    # Open-top compartment accessed by lifting the whole top shell off.
    # Has a recessed lip around the top for a snap-fit dust lid (separate print).

    # Calculate storage compartment bounds (inside the right zone)
    # Taper at top surface
    _t_top = 1.0  # at the very top
    _w_at_top = MEETING_W + _t_top * (TOP_W - MEETING_W)
    _stor_left = TOP_DIVIDER_DRY_X + WALL_INNER / 2 + STORAGE_WALL
    _stor_right = _w_at_top / 2 - WALL - STORAGE_WALL
    _stor_front = -(MEETING_D / 2 - WALL * 2 - STORAGE_WALL)
    _stor_back = MEETING_D / 2 - WALL * 2 - STORAGE_WALL
    _stor_w = _stor_right - _stor_left
    _stor_d = _stor_back - _stor_front
    _stor_cx = (_stor_left + _stor_right) / 2
    _stor_cy = (_stor_front + _stor_back) / 2

    if _stor_w > 5 and _stor_d > 5:
        # Storage cavity (hollowed interior of right zone)
        stor_cavity = (
            cq.Workplane("XY")
            .workplane(offset=WALL + 1)
            .center(_stor_cx, _stor_cy)
            .rect(_stor_w, _stor_d)
            .extrude(TOP_H - WALL * 2 - 2)
        )
        shell = shell.cut(stor_cavity)

        # Storage access opening on top surface
        stor_top_cut = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL - 0.1)
            .center(_stor_cx, _stor_cy)
            .rect(_stor_w - 2, _stor_d - 2)
            .extrude(WALL + 0.2)
        )
        shell = shell.cut(stor_top_cut)

        # Lid recess lip — stepped edge around the opening for a dust cover
        lid_recess = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - STORAGE_LID_RECESS)
            .center(_stor_cx, _stor_cy)
            .rect(_stor_w + 2, _stor_d + 2)
            .rect(_stor_w - 2, _stor_d - 2)
            .extrude(STORAGE_LID_RECESS + 0.1)
        )
        # Only cut this if it doesn't go outside the shell
        shell = shell.cut(lid_recess)

    # =============================================
    # CAPACITIVE TOUCH BUTTONS (top surface, front edge)
    # =============================================
    # Two TTP223 modules glued to the underside of the top shell ceiling.
    # Touch zones are indicated by shallow circular deboss marks on the
    # outer top surface (cosmetic only — the capacitive sensing works
    # through the 1.5mm PETG wall). Thin the ceiling locally to 1.5mm
    # for reliable touch sensing through the plastic.

    # Button positions: centered left-right on the front half of the top
    btn_x_center = 0  # centered on X axis
    for btn_i in range(TOUCH_BTN_COUNT):
        bx = btn_x_center + (btn_i - (TOUCH_BTN_COUNT - 1) / 2) * TOUCH_BTN_SPACING
        by = TOUCH_BTN_Y

        # Cosmetic circle deboss on outer surface (0.5mm deep indicator ring)
        indicator = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - 0.5)
            .center(bx, by)
            .circle(TOUCH_ZONE_DIA / 2)
            .circle(TOUCH_ZONE_DIA / 2 - 1.5)
            .extrude(0.6)
        )
        shell = shell.cut(indicator)

        # Thin the ceiling above the touch zone to 1.5mm for sensing
        # (remove material from the underside to create a thinner ceiling)
        thin_zone = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL)
            .center(bx, by)
            .circle(TOUCH_ZONE_DIA / 2 + 2)
            .extrude(WALL - 1.5)  # thin from WALL (3mm) to 1.5mm
        )
        shell = shell.cut(thin_zone)

        # TTP223 module pocket (recessed into the ceiling underside)
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
# These are NOT 3D-printed parts. They represent the real electronic and
# mechanical components placed in their pockets so you can verify clearance.
# Each is rendered with a distinct color to identify it in the viewer.

def build_components():
    """Build simplified solid models of all internal components at their
    installed positions. Returns a dict of {name: (solid, color)}.

    Layout matches build_base() pockets:
      Electronics column (X≈72, ~35mm wide):
        Front: PD trigger + buck converter Z-stacked
        Mid:   8-channel MOSFET board (50mm along Y)
        Rear:  ESP32 DevKit (55mm along Y)
      Relocated:
        Atomizer driver → wet zone floor (behind atomizer)
        BME280 → right divider wall (mid-height)
    """

    parts = {}

    # --- Recompute layout positions (must match build_base exactly) ---
    dry_right = MEETING_W / 2 - WALL
    _bottle_right = BOTTLE_ROW_X + BOTTLE_WELL_DIA / 2 + 4
    elec_col_x = (_bottle_right + dry_right) / 2
    interior_y_min = -(MEETING_D / 2 - WALL - 2)

    # Y-cursor positions (same math as build_base)
    _pd_buck_d = max(PD_TRIGGER_D, BUCK_CONV_D)  # 18mm
    y_cursor = interior_y_min
    pd_buck_y = y_cursor + _pd_buck_d / 2
    y_cursor += _pd_buck_d + 3
    mosfet_y = y_cursor + MOSFET_BOARD_W / 2
    y_cursor += MOSFET_BOARD_W + 3
    esp32_y = y_cursor + ESP32_W / 2

    # Atomizer driver position (wet zone, behind atomizer)
    _atm_drv_x = ATOMIZER_POS_X
    _atm_drv_y = ATOMIZER_POS_Y + ATOMIZER_MOUNT_DIA / 2 + 5 + ATOMIZER_DRIVER_D / 2

    # =============================================
    # WET ZONE components
    # =============================================

    # Atomizer piezo disk (20mm dia × 3mm, mounted flush in floor)
    atomizer_disk = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H - 1)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_DIA / 2)
        .extrude(3)
    )
    parts["atomizer_disk"] = (atomizer_disk, (0.75, 0.75, 0.15, 0.95))  # gold

    # Atomizer driver board (35×25mm, on wet zone floor behind atomizer)
    atomizer_driver = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(_atm_drv_x, _atm_drv_y)
        .rect(ATOMIZER_DRIVER_W, ATOMIZER_DRIVER_D)
        .extrude(6)
    )
    parts["atomizer_driver"] = (atomizer_driver, (0.2, 0.6, 0.2, 0.95))  # green PCB

    # Water (simplified as a transparent blue block filling wet zone)
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
    # PUMP ROW components
    # =============================================

    # 5× WX3 micro peristaltic pumps
    for i, py in enumerate(pump_y_positions):
        pump = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + 0.5)
            .center(PUMP_CENTER_X, py)
            .rect(PUMP_BODY_W, PUMP_BODY_D)
            .extrude(PUMP_BODY_H)
        )
        parts[f"pump_{i}"] = (pump, (0.85, 0.45, 0.1, 0.9))  # orange

    # =============================================
    # DRY ZONE — Bottles
    # =============================================

    # 5× 15ml essential oil bottles (cylinder body + smaller cap)
    for i, by in enumerate(bottle_y_positions):
        bottle_body_h = BOTTLE_HEIGHT - 15
        body = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + BOTTLE_WELL_DEPTH)
            .center(BOTTLE_ROW_X, by)
            .circle(BOTTLE_DIA / 2)
            .extrude(bottle_body_h)
        )
        cap_h = 15
        cap = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + BOTTLE_WELL_DEPTH + bottle_body_h)
            .center(BOTTLE_ROW_X, by)
            .circle(BOTTLE_CAP_DIA / 2)
            .extrude(cap_h)
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
    # DRY ZONE — Electronics Column
    # =============================================

    # Buck converter (22×17mm, on floor, front of column)
    buck_conv = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(elec_col_x, pd_buck_y)
        .rect(BUCK_CONV_W, BUCK_CONV_D)
        .extrude(BUCK_CONV_H)
    )
    parts["buck_converter"] = (buck_conv, (0.5, 0.1, 0.5, 0.95))  # purple PCB

    # CH224K PD trigger (24×18mm, stacked on top of buck converter)
    pd_trigger = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5 + BUCK_CONV_H + 1)
        .center(elec_col_x, pd_buck_y)
        .rect(PD_TRIGGER_W, PD_TRIGGER_D)
        .extrude(PD_TRIGGER_H)
    )
    parts["pd_trigger"] = (pd_trigger, (0.7, 0.1, 0.1, 0.95))  # red PCB

    # 8-channel MOSFET board (26mm X × 50mm Y × 12mm Z)
    mosfet_board = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(elec_col_x, mosfet_y)
        .rect(MOSFET_BOARD_D, MOSFET_BOARD_W)  # 26mm X, 50mm Y
        .extrude(MOSFET_BOARD_H)
    )
    parts["mosfet_board"] = (mosfet_board, (0.15, 0.55, 0.15, 0.9))  # green

    # ESP32 DevKit (28mm X × 55mm Y × 13mm Z)
    esp32 = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(elec_col_x, esp32_y)
        .rect(ESP32_D, ESP32_W)  # 28mm X, 55mm Y
        .extrude(ESP32_H)
    )
    parts["esp32"] = (esp32, (0.1, 0.35, 0.7, 0.95))  # blue PCB

    # BME280 sensor (15×12mm, on top of MOSFET board, Z-stacked)
    _bme_z = FLOOR_H + 0.5 + MOSFET_BOARD_H + 2  # sits above MOSFET board
    bme280 = (
        cq.Workplane("XY")
        .workplane(offset=_bme_z)
        .center(elec_col_x, mosfet_y)
        .rect(BME280_W, BME280_D)
        .extrude(BME280_H)
    )
    parts["bme280"] = (bme280, (0.3, 0.3, 0.8, 0.95))  # light blue

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

    return parts


# =============================================================================
# ASSEMBLY — color-coded per zone for visibility
# =============================================================================
#
# Color legend:
#   Base:  teal (wet zone), amber (pump row), purple (dry zone)
#   Top:   blue (mist+fill zone), teal (transit zone), orange (storage)
#
# We split each part into zone-colored sub-bodies by cutting with bounding boxes.

base = build_base()
top_shell = build_top_shell()
top_shell = top_shell.translate((0, 0, BASE_H))

# --- Zone splitter boxes (oversized, for boolean intersection) ---
# Base zones — cut at Z=0..BASE_H
_big_h = BASE_H + 20
_big_d = BASE_D + 20

# Wet zone: X from far-left to DIVIDER_WET_X
base_wet_box = (
    cq.Workplane("XY").box(BASE_W, _big_d, _big_h)
    .translate((-(BASE_W / 2 + DIVIDER_WET_X) / 2 + DIVIDER_WET_X, 0, _big_h / 2 - 5))
)
# Pump row: X from DIVIDER_WET_X to DIVIDER_DRY_X
pump_row_w = DIVIDER_DRY_X - DIVIDER_WET_X
base_pump_box = (
    cq.Workplane("XY").box(pump_row_w, _big_d, _big_h)
    .translate(((DIVIDER_WET_X + DIVIDER_DRY_X) / 2, 0, _big_h / 2 - 5))
)
# Dry zone: X from DIVIDER_DRY_X to far-right
base_dry_box = (
    cq.Workplane("XY").box(BASE_W, _big_d, _big_h)
    .translate(((BASE_W / 2 + DIVIDER_DRY_X) / 2 + DIVIDER_DRY_X, 0, _big_h / 2 - 5))
)

# Show the complete base in a neutral dark color, and overlay zone highlights
# Using the full base for structural integrity view, zone colors for identification.
show_object(base, name="base",
            options={"color": (0.12, 0.12, 0.15, 0.55)})

# Top shell zones — offset by BASE_H
_top_big_h = TOP_H + 20

# Fill zone (left, above wet zone)
top_fill_box = (
    cq.Workplane("XY").box(BASE_W, _big_d, _top_big_h)
    .translate((-(BASE_W / 2 + TOP_DIVIDER_WET_X) / 2 + TOP_DIVIDER_WET_X, 0,
                BASE_H + _top_big_h / 2 - 5))
)
# Mist zone (center)
top_mist_box = (
    cq.Workplane("XY").box(pump_row_w, _big_d, _top_big_h)
    .translate(((TOP_DIVIDER_WET_X + TOP_DIVIDER_DRY_X) / 2, 0,
                BASE_H + _top_big_h / 2 - 5))
)
# Storage zone (right)
top_stor_box = (
    cq.Workplane("XY").box(BASE_W, _big_d, _top_big_h)
    .translate(((BASE_W / 2 + TOP_DIVIDER_DRY_X) / 2 + TOP_DIVIDER_DRY_X, 0,
                BASE_H + _top_big_h / 2 - 5))
)

# Show top shell with distinct color
show_object(top_shell, name="top_shell",
            options={"color": (0.18, 0.18, 0.22, 0.55)})

# --- Zone indicator markers (thin colored slabs on the floor of each zone) ---
# These provide clear visual color coding without splitting the geometry.
marker_h = 1.5  # thin slab

# Base wet zone marker (teal)
wet_marker_w = abs(DIVIDER_WET_X - (-(MEETING_W / 2 - WALL)))
wet_marker = (
    cq.Workplane("XY")
    .box(wet_marker_w - 4, MEETING_D - WALL * 2 - 8, marker_h)
    .translate(((-(MEETING_W / 2 - WALL) + DIVIDER_WET_X) / 2, 0, FLOOR_H + marker_h / 2))
)
show_object(wet_marker, name="zone_wet",
            options={"color": (0.08, 0.72, 0.65, 0.85)})  # teal

# Base pump row marker (amber)
pump_marker_w = DIVIDER_DRY_X - DIVIDER_WET_X - WALL_INNER
pump_marker = (
    cq.Workplane("XY")
    .box(pump_marker_w - 2, MEETING_D - WALL * 2 - 8, marker_h)
    .translate((PUMP_CENTER_X, 0, FLOOR_H + marker_h / 2))
)
show_object(pump_marker, name="zone_pumps",
            options={"color": (0.92, 0.69, 0.13, 0.85)})  # amber

# Base dry zone marker (purple)
dry_marker_w = abs((MEETING_W / 2 - WALL) - DIVIDER_DRY_X) - WALL_INNER / 2
dry_marker = (
    cq.Workplane("XY")
    .box(dry_marker_w - 4, MEETING_D - WALL * 2 - 8, marker_h)
    .translate(((DIVIDER_DRY_X + MEETING_W / 2 - WALL) / 2 + WALL_INNER / 4, 0,
                FLOOR_H + marker_h / 2))
)
show_object(dry_marker, name="zone_dry",
            options={"color": (0.58, 0.27, 0.88, 0.85)})  # purple

# Top mist+fill zone marker (blue) — on the ceiling inside
mist_fill_marker_w = abs(TOP_DIVIDER_WET_X - (-(MEETING_W / 2 - WALL)))
mist_fill_marker = (
    cq.Workplane("XY")
    .box(mist_fill_marker_w - 4, MEETING_D - WALL * 2 - 8, marker_h)
    .translate(((-(MEETING_W / 2 - WALL) + TOP_DIVIDER_WET_X) / 2, 0,
                BASE_H + TOP_H - WALL - marker_h / 2 - 1))
)
show_object(mist_fill_marker, name="zone_mist_fill",
            options={"color": (0.15, 0.56, 0.94, 0.85)})  # blue

# Top transit zone marker (teal)
transit_marker_w = TOP_DIVIDER_DRY_X - TOP_DIVIDER_WET_X - WALL_INNER
transit_marker = (
    cq.Workplane("XY")
    .box(transit_marker_w - 2, MEETING_D - WALL * 2 - 8, marker_h)
    .translate(((TOP_DIVIDER_WET_X + TOP_DIVIDER_DRY_X) / 2, 0,
                BASE_H + TOP_H - WALL - marker_h / 2 - 1))
)
show_object(transit_marker, name="zone_transit",
            options={"color": (0.08, 0.72, 0.65, 0.85)})  # teal

# Top storage zone marker (orange)
stor_marker_w = abs((MEETING_W / 2 - WALL) - TOP_DIVIDER_DRY_X) - WALL_INNER / 2
stor_marker = (
    cq.Workplane("XY")
    .box(stor_marker_w - 4, MEETING_D - WALL * 2 - 8, marker_h)
    .translate(((TOP_DIVIDER_DRY_X + MEETING_W / 2 - WALL) / 2 + WALL_INNER / 4, 0,
                BASE_H + TOP_H - WALL - marker_h / 2 - 1))
)
show_object(stor_marker, name="zone_storage",
            options={"color": (0.96, 0.49, 0.13, 0.85)})  # orange

# --- Button color indicators (colored discs on top shell surface) ---
# Power button — RED disc
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

# Mist intensity button — CYAN disc
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
_pump_left = DIVIDER_WET_X
_pump_right = DIVIDER_DRY_X
_dry_left = DIVIDER_DRY_X + WALL_INNER / 2
_dry_right = MEETING_W / 2 - WALL

print("=" * 60)
print("Somni Oil Diffuser V3.0 — Night City")
print("=" * 60)
print()
print("--- BOM (verified dimensions) ---")
print(f"Pumps:       {PUMP_COUNT}x JIHPUMP WX3 ({PUMP_BODY_W}x{PUMP_BODY_D}x{PUMP_BODY_H}mm, 5V)")
print(f"Atomizer:    20mm/113KHz piezo + {ATOMIZER_DRIVER_W}x{ATOMIZER_DRIVER_D}mm driver (5V)")
print(f"MCU:         ESP32 DevKit ({ESP32_W}x{ESP32_D}mm)")
print(f"MOSFETs:     8-ch board ({MOSFET_BOARD_W}x{MOSFET_BOARD_D}x{MOSFET_BOARD_H}mm, using {MOSFET_COUNT} ch)")
print(f"PD trigger:  CH224K ({PD_TRIGGER_W}x{PD_TRIGGER_D}mm)")
print(f"Buck conv:   MP1584EN ({BUCK_CONV_W}x{BUCK_CONV_D}mm, 12V→5V)")
print(f"Buttons:     {TOUCH_BTN_COUNT}x TTP223 capacitive ({TOUCH_BTN_W}x{TOUCH_BTN_D}mm)")
print(f"LEDs:        WS2812B strip ({LED_CHANNEL_W}mm wide)")
print()
print("--- Enclosure ---")
print(f"Base:        {BASE_W}x{BASE_D}x{BASE_H}mm (bottom)")
print(f"             {MEETING_W:.1f}x{MEETING_D:.1f}mm (meeting line)")
print(f"Top shell:   {TOP_W:.1f}x{TOP_D:.1f}mm (top)")
print(f"Total:       {TOTAL_H}mm tall")
print()
print("--- Base Zones (left to right) ---")
print(f"WET ZONE:    X={_wet_left:.1f} to {_wet_right}mm ({_wet_right - _wet_left:.0f}mm wide)  [TEAL]")
print(f"  Reservoir: depth={RESERVOIR_DEPTH:.1f}mm")
print(f"  Atomizer:  {ATOMIZER_MOUNT_DIA}mm at ({ATOMIZER_POS_X}, {ATOMIZER_POS_Y})")
print()
print(f"PUMP ROW:    X={_pump_left} to {_pump_right}mm ({_pump_right - _pump_left}mm wide)  [AMBER]")
print(f"  Pumps:     {PUMP_COUNT}x WX3 at Y={[f'{y:.0f}' for y in pump_y_positions]}")
print(f"  Body:      {PUMP_BODY_W}x{PUMP_BODY_D}x{PUMP_BODY_H}mm each (oriented 35mm across row)")
print()
print(f"DRY ZONE:    X={_dry_left:.1f} to {_dry_right:.1f}mm ({_dry_right - _dry_left:.0f}mm wide)  [PURPLE]")
print(f"  Bottles:   {BOTTLE_COUNT}x {BOTTLE_DIA}mm dia wells at X={BOTTLE_ROW_X:.1f}")
print(f"             Y={[f'{y:.0f}' for y in bottle_y_positions]}")
print(f"  Elec col:  X≈{(_dry_right + BOTTLE_ROW_X + BOTTLE_WELL_DIA/2 + 4) / 2:.0f}, 3 boards stacked along Y:")
print(f"    PD+Buck: Z-stacked ({PD_TRIGGER_W}x{PD_TRIGGER_D} + {BUCK_CONV_W}x{BUCK_CONV_D}mm)")
print(f"    MOSFET:  8-ch board ({MOSFET_BOARD_D}x{MOSFET_BOARD_W}mm, 50mm along Y)")
print(f"    ESP32:   {ESP32_D}x{ESP32_W}mm (55mm along Y)")
print(f"  BME280:    {BME280_W}x{BME280_D}mm (on top of MOSFET board)")
print(f"  Atm driver:{ATOMIZER_DRIVER_W}x{ATOMIZER_DRIVER_D}mm (relocated to wet zone)")
print(f"  USB-C:     {USBC_PORT_W}x{USBC_PORT_H}mm (rear wall)")
print()
print("--- Top Shell Zones (left to right) ---")
print(f"MIST+FILL:   above wet zone  [BLUE]")
print(f"  Chimney:    {MIST_CHANNEL_DIA}mm bore at ({MIST_POS_X}, {MIST_POS_Y})")
print(f"  Exhaust:    {EXHAUST_W}x{EXHAUST_D}mm chevron, 3 vanes")
print(f"  Fill chute: {FILL_CHUTE_TOP_W}x{FILL_CHUTE_TOP_D}mm top → {FILL_CHUTE_BOT_W}x{FILL_CHUTE_BOT_D}mm bottom")
print(f"  Fill pos:   ({FILL_CHUTE_POS_X}, {FILL_CHUTE_POS_Y}), lip {FILL_CHUTE_LIP_H}mm")
print()
print(f"TRANSIT:     above pump row  [TEAL]")
print(f"  Structural gap, cable routing")
print()
print(f"STORAGE:     above dry zone  [ORANGE]")
print(f"  Compartment for spare bottles, accessories, etc.")
print(f"  Lid recess: {STORAGE_LID_RECESS}mm step for snap-fit dust cover")
print()
print(f"BUTTONS:     {TOUCH_BTN_COUNT}x TTP223 capacitive touch on top surface")
print(f"  Power + Mist Intensity, {TOUCH_BTN_SPACING}mm apart")
print(f"  Sensing through 1.5mm PETG ceiling")
print()
print(f"ACCESS:      LIFT TOP SHELL OFF — full access to everything")
print()
print("--- Connections ---")
print(f"Magnets:     {len(magnet_positions)}x {MAGNET_DIA}mm dia x {MAGNET_H}mm")
print(f"Pins:        {len(pin_positions)}x {PIN_DIA}mm dia x {PIN_H}mm")
print(f"Hex mesh:    all 4 walls (front + rear + left + right)")
print(f"LED strip:   continuous perimeter loop, {LED_CHANNEL_W}x{LED_CHANNEL_D}mm channel")
print(f"Branding:    'SOMNI LABS' debossed on rear panel ({BRAND_FONT_SIZE}pt + {BRAND_SUB_SIZE}pt)")
print()
print("--- Power Architecture ---")
print(f"USB-C PD → CH224K (12V) → MP1584EN → 5V rail")
print(f"  5V rail: pumps + atomizer + ESP32 + LEDs")
print(f"  Alt: USB-C 5V/3A direct (no PD needed)")
print()
print(f"Print bed:   {BASE_W}x{BASE_D}mm fits QIDI Q2 (245x255mm)")
