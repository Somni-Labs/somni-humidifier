"""
Somni Oil Diffuser — V2.2 "Night City"

Cyberpunk-styled essential oil diffuser with automated scent blending.
200x160mm rectangular footprint (fits QIDI Q2 245x255mm bed).

Two-part enclosure connected via magnets:
  BASE  — holds everything: reservoir, atomizer, pumps, bottles, electronics
  SHELL — purely aesthetic lid: mist chimney, exhaust port, fill port, hex mesh

Bottles sit upright in the base. Lift the top shell off for full access
to bottles, pumps, electronics, and reservoir. No hatch, no hinges.

Base layout (three zones, left to right):
  WET ZONE  (left,   ~55%)  — water reservoir + atomizer mount
  PUMP ROW  (center strip)  — 5 peristaltic pumps on a divider wall
  DRY ZONE  (right,  ~45%)  — 5 bottle wells (front) + electronics (rear)

Tube path: bottle → short tube → pump intake (same zone, ~30mm) →
           pump output → into reservoir (through divider)

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
DIVIDER_WET_X = -20      # left divider (wet/pump boundary)
DIVIDER_DRY_X = 25       # right divider (pump/dry boundary)
# Pump row width: 45mm — fits 38mm pump body + clearance

# --- Water reservoir (wet zone) ---
RESERVOIR_DEPTH = BASE_H - FLOOR_H - WALL

# --- Ultrasonic atomizer ---
ATOMIZER_DIA = 20
ATOMIZER_DRIVER_W = 35
ATOMIZER_DRIVER_D = 25
ATOMIZER_MOUNT_DIA = 26
ATOMIZER_POS_X = -55         # well into wet zone (left side)
ATOMIZER_POS_Y = 0           # centered front-to-back

# --- Peristaltic pumps (5x, in pump row) ---
PUMP_BODY_W = 38
PUMP_BODY_D = 28             # depth along Y (verify — some pumps are ~28mm)
PUMP_BODY_H = 27
PUMP_COUNT = 5
PUMP_SPACING = 28            # center-to-center along Y axis
# Pumps sit centered between the two dividers
PUMP_CENTER_X = (DIVIDER_WET_X + DIVIDER_DRY_X) / 2  # = 2.5

# --- Oil bottles (5x, in dry zone, front row) ---
BOTTLE_DIA = 22              # 5ml essential oil bottle body diameter
BOTTLE_HEIGHT = 55           # bottle total height (must fit in base height)
BOTTLE_COUNT = 5
BOTTLE_WELL_DEPTH = 4        # shallow ring to keep bottle from sliding
BOTTLE_WELL_DIA = BOTTLE_DIA + 2 * TOL + 2  # ~23.8mm
BOTTLE_SPACING = 26          # center-to-center along Y axis
# Bottles sit in the dry zone, front half (negative Y area)
BOTTLE_ROW_X = DIVIDER_DRY_X + WALL_INNER / 2 + BOTTLE_WELL_DIA / 2 + 3
BOTTLE_ROW_Y_CENTER = 0      # centered front-to-back

# Bottle Y positions (row of 5)
bottle_y_positions = [-(BOTTLE_COUNT - 1) / 2 * BOTTLE_SPACING + i * BOTTLE_SPACING
                       for i in range(BOTTLE_COUNT)]

# --- Tube clips (printed guide rings on the base floor) ---
TUBE_CLIP_DIA = 6            # outer diameter of tube guide
TUBE_CLIP_H = 5              # height of guide post

# --- Electronics bay (dry zone, behind bottles) ---
ESP32_W = 55
ESP32_D = 28
ESP32_H = 13
MOSFET_W = 25
MOSFET_D = 20
MOSFET_H = 15
PD_TRIGGER_W = 30
PD_TRIGGER_D = 18
PD_TRIGGER_H = 10
BME280_W = 15
BME280_D = 12
BME280_H = 5
# Electronics sit behind the bottle row (positive Y area of dry zone)
ELECTRONICS_ROW_X = BOTTLE_ROW_X + 20  # offset right from bottles

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

# --- Water fill port (top surface) ---
FILL_PORT_DIA = 30
FILL_PORT_POS_X = -60
FILL_PORT_POS_Y = 35

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

    # Bottle wells — shallow circular pockets to locate each bottle
    for by in bottle_y_positions:
        # Well pocket
        well = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(BOTTLE_ROW_X, by)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(BOTTLE_WELL_DEPTH)
        )
        base = base.cut(well)

        # Low retaining wall around each well (3mm tall ring)
        retainer = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(BOTTLE_ROW_X, by)
            .circle(BOTTLE_WELL_DIA / 2 + 1.5)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(BOTTLE_WELL_DEPTH + 3)
        )
        base = base.union(retainer)

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

    # Electronics layout in the dry zone (rear/right area)
    dry_left = DIVIDER_DRY_X + WALL_INNER / 2
    dry_right = MEETING_W / 2 - WALL
    dry_center_x = (dry_left + dry_right) / 2

    # ESP32 pocket (rear of dry zone)
    esp32_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(dry_center_x, 45)
        .rect(ESP32_D, ESP32_W)  # rotated to fit width
        .extrude(ESP32_H + 2)
    )
    base = base.cut(esp32_pocket)

    # 5 MOSFET pockets in a row along Y, between bottles and ESP32
    mosfet_x = dry_center_x - 8
    mosfet_y_start = pump_y_positions[0]
    for i in range(5):
        my = mosfet_y_start + i * PUMP_SPACING
        mosfet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(mosfet_x, my)
            .rect(MOSFET_W, MOSFET_D)
            .extrude(MOSFET_H + 2)
        )
        base = base.cut(mosfet_pocket)

    # PD trigger pocket (rear corner)
    pd_x = dry_center_x + 15
    pd_y = MEETING_D / 2 - WALL - PD_TRIGGER_D / 2 - 5
    pd_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(pd_x, pd_y)
        .rect(PD_TRIGGER_W, PD_TRIGGER_D)
        .extrude(PD_TRIGGER_H + 2)
    )
    base = base.cut(pd_pocket)

    # Atomizer driver pocket (near left divider in dry zone)
    driver_x = DIVIDER_DRY_X + WALL_INNER / 2 + 5 + ATOMIZER_DRIVER_W / 2
    driver_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(driver_x, -45)
        .rect(ATOMIZER_DRIVER_W, ATOMIZER_DRIVER_D)
        .extrude(8)
    )
    base = base.cut(driver_pocket)

    # BME280 pocket (front-right corner, away from mist)
    bme_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(dry_center_x + 15, -(MEETING_D / 2 - WALL - BME280_D / 2 - 5))
        .rect(BME280_W, BME280_D)
        .extrude(BME280_H + 2)
    )
    base = base.cut(bme_pocket)

    # --- USB-C port cutout (rear wall) ---
    usbc_cutout = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + PD_TRIGGER_H / 2)
        .center(pd_x, BASE_D / 2)
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
    """Simple aesthetic lid — no bottles, no tubes, no hatch.

    Just: mist chimney, chevron exhaust, fill port, panel lines, hex mesh.
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

    # --- Mist channel (internal chimney) ---
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

    # --- Water fill port (top surface) ---
    fill_hole = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H - WALL - 0.1)
        .center(FILL_PORT_POS_X, FILL_PORT_POS_Y)
        .circle(FILL_PORT_DIA / 2)
        .extrude(WALL + 0.2)
    )
    shell = shell.cut(fill_hole)

    fill_lip = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H)
        .center(FILL_PORT_POS_X, FILL_PORT_POS_Y)
        .circle(FILL_PORT_DIA / 2 + 2)
        .circle(FILL_PORT_DIA / 2)
        .extrude(1.5)
    )
    shell = shell.union(fill_lip)

    # --- Chevron exhaust port ---
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

    # Internal vanes
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
# ASSEMBLY
# =============================================================================

base = build_base()
top_shell = build_top_shell()
top_shell = top_shell.translate((0, 0, BASE_H))

show_object(base, name="base",
            options={"color": (0.15, 0.15, 0.18, 0.85)})
show_object(top_shell, name="top_shell",
            options={"color": (0.2, 0.2, 0.25, 0.7)})


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
print("Somni Oil Diffuser V2.2 — Night City")
print("=" * 60)
print()
print("--- Enclosure ---")
print(f"Base:        {BASE_W}x{BASE_D}x{BASE_H}mm (bottom)")
print(f"             {MEETING_W:.1f}x{MEETING_D:.1f}mm (meeting line)")
print(f"Top shell:   {TOP_W:.1f}x{TOP_D:.1f}mm (top)")
print(f"Total:       {TOTAL_H}mm tall")
print()
print("--- Base Zones (left to right) ---")
print(f"WET ZONE:    X={_wet_left:.1f} to {_wet_right}mm ({_wet_right - _wet_left:.0f}mm wide)")
print(f"  Reservoir: depth={RESERVOIR_DEPTH:.1f}mm")
print(f"  Atomizer:  {ATOMIZER_MOUNT_DIA}mm at ({ATOMIZER_POS_X}, {ATOMIZER_POS_Y})")
print()
print(f"PUMP ROW:    X={_pump_left} to {_pump_right}mm ({_pump_right - _pump_left}mm wide)")
print(f"  Pumps:     {PUMP_COUNT}x at Y={[f'{y:.0f}' for y in pump_y_positions]}")
print(f"  Body:      {PUMP_BODY_W}x{PUMP_BODY_D}x{PUMP_BODY_H}mm each")
print()
print(f"DRY ZONE:    X={_dry_left:.1f} to {_dry_right:.1f}mm ({_dry_right - _dry_left:.0f}mm wide)")
print(f"  Bottles:   {BOTTLE_COUNT}x {BOTTLE_DIA}mm dia wells at X={BOTTLE_ROW_X:.1f}")
print(f"             Y={[f'{y:.0f}' for y in bottle_y_positions]}")
print(f"  ESP32:     {ESP32_W}x{ESP32_D}mm (rotated)")
print(f"  MOSFETs:   {PUMP_COUNT}x {MOSFET_W}x{MOSFET_D}mm")
print(f"  PD trigger:{PD_TRIGGER_W}x{PD_TRIGGER_D}mm")
print(f"  BME280:    {BME280_W}x{BME280_D}mm")
print(f"  USB-C:     {USBC_PORT_W}x{USBC_PORT_H}mm (rear wall)")
print()
print("--- Top Shell (aesthetic lid) ---")
print(f"Mist channel:{MIST_CHANNEL_DIA}mm bore at ({MIST_POS_X}, {MIST_POS_Y})")
print(f"Fill port:   {FILL_PORT_DIA}mm dia at ({FILL_PORT_POS_X}, {FILL_PORT_POS_Y})")
print(f"Exhaust:     {EXHAUST_W}x{EXHAUST_D}mm chevron, 3 vanes")
print(f"Access:      LIFT TOP SHELL OFF — full access to everything")
print()
print("--- Connections ---")
print(f"Magnets:     {len(magnet_positions)}x {MAGNET_DIA}mm dia x {MAGNET_H}mm")
print(f"Pins:        {len(pin_positions)}x {PIN_DIA}mm dia x {PIN_H}mm")
print(f"Hex mesh:    all 4 walls (front + rear + left + right)")
print(f"LED strip:   continuous perimeter loop, {LED_CHANNEL_W}x{LED_CHANNEL_D}mm channel")
print(f"Branding:    'SOMNI LABS' debossed on rear panel ({BRAND_FONT_SIZE}pt + {BRAND_SUB_SIZE}pt)")
print()
print(f"Print bed:   {BASE_W}x{BASE_D}mm fits QIDI Q2 (245x255mm)")
