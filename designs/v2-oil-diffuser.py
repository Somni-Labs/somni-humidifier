"""
Somni Oil Diffuser — V2.1 "Night City"

Cyberpunk-styled essential oil diffuser with automated scent blending.
200x160mm rectangular footprint (fits QIDI Q2 245x255mm bed).

Two-part enclosure: base (reservoir + electronics + pumps) and top shell
(bottle receivers + tube routing + mist channel + exhaust), magnets.

Layout:
  Base left side  = wet zone (reservoir, atomizer, pump outputs)
  Base right side = dry zone (ESP32, 5x MOSFET, PD trigger, atomizer driver)
  Pumps straddle the divider wall between zones
  Top shell holds 5 bottle receivers (2+3 cluster) with individual tube
  channels routing each tube to its own exit grommet above its pump.

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
# Rectangular base: wider (X) than deep (Y). Tapers inward on all sides.
BASE_W = 200             # base footprint width (X) at Z=0
BASE_D = 160             # base footprint depth (Y) at Z=0
BASE_H = 70              # base height (Z)
TOP_H = 60               # top shell height (Z)
TOTAL_H = BASE_H + TOP_H # 130mm assembled
TAPER_ANGLE = 6          # degrees inward per side

# Derived: top-of-base footprint (where the two parts meet)
_taper_shrink_base = BASE_H * math.tan(math.radians(TAPER_ANGLE))
MEETING_W = BASE_W - 2 * _taper_shrink_base  # ~185.3mm
MEETING_D = BASE_D - 2 * _taper_shrink_base  # ~145.3mm

# Derived: top-of-shell footprint (smallest cross-section)
_taper_shrink_top = TOP_H * math.tan(math.radians(TAPER_ANGLE))
TOP_W = MEETING_W - 2 * _taper_shrink_top    # ~172.7mm
TOP_D = MEETING_D - 2 * _taper_shrink_top    # ~132.7mm

# --- Panel line (horizontal chamfer break) ---
PANEL_LINE_Z_BASE = 45       # Z height on base where the panel line sits
PANEL_LINE_Z_TOP = 30        # Z height on top shell (relative to shell bottom)
PANEL_LINE_WIDTH = 1.5       # groove width
PANEL_LINE_DEPTH = 1.0       # groove depth into the wall

# --- Base floor ---
FLOOR_H = 3.0               # solid floor thickness

# --- Wet/dry divider ---
# Divider runs parallel to Y axis. Positive X = right.
# Wet zone: left of divider (~60%). Dry zone: right (~40%).
# Moved from X=20 to X=30 — gives dry zone ~62mm usable width
# (enough for ESP32 55mm + clearance, and MOSFETs in 2 rows).
DIVIDER_X = 30

# --- Water reservoir (wet zone) ---
RESERVOIR_DEPTH = BASE_H - FLOOR_H - WALL  # usable depth inside basin
# Wet zone usable width: ~120mm (from left wall to divider)
# Wet zone usable depth: ~140mm (front to back minus walls)
# At 55mm depth: 120 * 140 * 55 = ~924ml max. Target 200-300ml is trivial.

# --- Ultrasonic atomizer ---
ATOMIZER_DIA = 20            # piezo disk diameter
ATOMIZER_DRIVER_W = 35       # driver PCB width (approximate, verify)
ATOMIZER_DRIVER_D = 25       # driver PCB depth
ATOMIZER_MOUNT_DIA = 26      # sealed mounting pad diameter (disk + o-ring)
ATOMIZER_POS_X = -40         # X position in wet zone (well left of divider)
ATOMIZER_POS_Y = -30         # Y position (toward front)

# --- Peristaltic pumps (5x, mounted on divider wall) ---
PUMP_BODY_W = 38             # pump body width (verify with Kamoer KFS)
PUMP_BODY_D = 58             # pump body depth/length
PUMP_BODY_H = 27             # pump body height
PUMP_COUNT = 5
PUMP_SPACING = 30            # center-to-center along Y axis (was 28, more room)
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
FOOT_INSET = 20              # distance from corner

# --- Magnet pockets (base rim + top shell) ---
MAGNET_DIA = 6               # neodymium disc magnet diameter
MAGNET_H = 3                 # magnet thickness
MAGNET_COUNT = 6             # 2 per long side, 1 per short side
MAGNET_INSET = 30            # distance from corners along each edge

# --- Alignment pins ---
PIN_DIA = 4                  # locating pin diameter
PIN_H = 6                    # pin protrusion height
PIN_COUNT = 4                # one per corner

# --- Oil bottle receivers (top shell) ---
# Bottles screw UP into threaded receivers (like screwing on a cap).
# Each receiver has a tube pre-routed through it that dips into the bottle.
# Arranged in a tight 2+3 cluster (2 rear, 3 front).
BOTTLE_DIA = 22              # 5ml essential oil bottle body diameter
BOTTLE_NECK_OD = 18          # bottle neck outer diameter (18-415 thread)
BOTTLE_HEIGHT = 55           # bottle total height
BOTTLE_COUNT = 5

# Threaded receiver dimensions
RECEIVER_OD = BOTTLE_NECK_OD + 2 * WALL_INNER
RECEIVER_THREAD_ID = BOTTLE_NECK_OD + 2 * TOL
RECEIVER_LENGTH = 13
TUBE_BORE_DIA = 3            # bore through receiver center for silicone tube

# Receiver positions — 2+3 quincunx cluster
_cluster_row_gap = BOTTLE_DIA + 4      # ~26mm front-to-back between row centers
_cluster_col_gap = BOTTLE_DIA + 4      # ~26mm side-to-side between centers
RECEIVER_POSITIONS = [
    # Back row (2 bottles)
    (-_cluster_col_gap / 2,  _cluster_row_gap / 2),
    ( _cluster_col_gap / 2,  _cluster_row_gap / 2),
    # Front row (3 bottles)
    (-_cluster_col_gap,     -_cluster_row_gap / 2),
    ( 0,                    -_cluster_row_gap / 2),
    ( _cluster_col_gap,     -_cluster_row_gap / 2),
]
# Cluster center: centered on the right half of the shell (bottle zone),
# vertically centered in Y to align tubes with pump row below.
CLUSTER_CENTER_X = 20        # slightly right of center (above pump divider area)
CLUSTER_CENTER_Y = 0         # centered front-to-back (aligns with pump row)

# --- Individual tube exit grommets (one per pump) ---
# Each tube gets its own 5mm exit hole through the shell floor,
# positioned directly above its corresponding pump in the base.
TUBE_HOLE_DIA = 5            # hole for silicone tube + grommet
TUBE_CHANNEL_W = 6           # individual channel width (one tube)
TUBE_CHANNEL_D = 6           # channel depth (cut into ceiling)

# --- Mist channel (top shell, internal chimney) ---
MIST_CHANNEL_DIA = 30        # internal chimney diameter
MIST_CHANNEL_WALL = 2.5      # chimney wall thickness
MIST_POS_X = ATOMIZER_POS_X
MIST_POS_Y = ATOMIZER_POS_Y

# --- Water fill port (top surface) ---
FILL_PORT_DIA = 30           # silicone plug hole
FILL_PORT_POS_X = -60        # far left of top, away from bottles and exhaust
FILL_PORT_POS_Y = 30         # toward rear

# --- Exhaust port (top surface, chevron shape) ---
EXHAUST_W = 40               # chevron width
EXHAUST_D = 25               # chevron depth
EXHAUST_POS_X = MIST_POS_X
EXHAUST_POS_Y = MIST_POS_Y

# --- Hex mesh panels ---
HEX_CELL_SIZE = 9            # flat-to-flat distance of each hex cell
HEX_WALL = 1.5              # wall between hex cells
HEX_MARGIN = 5               # margin from panel edges before hex pattern starts

# --- Bottle access hatch (right side panel, +X wall) ---
# Full side panel opening for hand access to all 5 bottles.
# 130mm wide x 50mm tall — almost the entire right wall of the top shell.
HATCH_W = 130                # hatch opening width (along Y axis on the side wall)
HATCH_H = 50                 # hatch opening height
HATCH_WALL = 2.0             # hatch panel thickness

# --- LED strip channel ---
LED_CHANNEL_W = 12           # WS2812B strip width
LED_CHANNEL_D = 4            # strip + adhesive depth

# --- SOMNI branding ---
BRAND_DEPTH = 0.6            # deboss depth


# =============================================================================
# MODULE-LEVEL SHARED POSITIONS
# =============================================================================

# Magnet positions — 6 total: 2 per long side (X), 1 per short side (Y).
magnet_positions = [
    # Front and rear (short sides, 1 each, centered)
    (0, -MEETING_D / 2 + MAGNET_INSET),
    (0,  MEETING_D / 2 - MAGNET_INSET),
    # Left side (long side, 2 magnets)
    (-MEETING_W / 2 + MAGNET_INSET, -MEETING_D / 4),
    (-MEETING_W / 2 + MAGNET_INSET,  MEETING_D / 4),
    # Right side (long side, 2 magnets)
    ( MEETING_W / 2 - MAGNET_INSET, -MEETING_D / 4),
    ( MEETING_W / 2 - MAGNET_INSET,  MEETING_D / 4),
]

# Alignment pin positions — one near each corner.
pin_positions = [
    (-MEETING_W / 2 + 15, -MEETING_D / 2 + 15),
    ( MEETING_W / 2 - 15, -MEETING_D / 2 + 15),
    (-MEETING_W / 2 + 15,  MEETING_D / 2 - 15),
    ( MEETING_W / 2 - 15,  MEETING_D / 2 - 15),
]

# Pump Y positions (centered row of 5 along divider)
pump_y_positions = [-(PUMP_COUNT - 1) / 2 * PUMP_SPACING + i * PUMP_SPACING
                     for i in range(PUMP_COUNT)]

# Tube exit positions — one per pump, on the shell floor above each pump.
# Each grommet sits at the divider X, at the same Y as its pump.
tube_exit_positions = [(DIVIDER_X, py) for py in pump_y_positions]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def tapered_box(width_bottom, depth_bottom, width_top, depth_top, height):
    """Create an angular tapered box — larger at bottom, smaller at top.

    All four sides taper inward linearly. No fillets — sharp cyberpunk edges.
    Returns a solid centered on XY at Z=0..height.
    """
    result = (
        cq.Workplane("XY")
        .rect(width_bottom, depth_bottom)
        .workplane(offset=height)
        .rect(width_top, depth_top)
        .loft()
    )
    return result


def panel_line_cut(body, z_height, total_height, w_bottom, d_bottom, w_top, d_top, width, depth):
    """Cut a horizontal groove around the perimeter at a given Z height.

    Interpolates the taper to find correct XY dimensions at that height,
    then cuts a shallow rectangular ring — the 'armor seam' panel line.
    """
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
    groove = outer.cut(inner)
    return body.cut(groove)


def hex_mesh_cutout(width, height, cell_size, wall_thickness, margin):
    """Generate a honeycomb pattern of hexagonal prisms as a single CadQuery solid.

    Pointy-top hex orientation (support-free vertical printing).
    Returns a solid block of hex cells extruded 100mm along Z.
    """
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

            pts = []
            for i in range(6):
                angle = math.radians(60 * i + 30)
                pts.append((
                    cx + hex_radius * math.cos(angle),
                    cy + hex_radius * math.sin(angle),
                ))

            hex_cell = (
                cq.Workplane("XY")
                .moveTo(pts[0][0], pts[0][1])
                .polyline(pts[1:])
                .close()
                .extrude(100)
            )

            if cells is None:
                cells = hex_cell
            else:
                cells = cells.union(hex_cell)

    if cells is None:
        cells = cq.Workplane("XY").box(0.1, 0.1, 0.1)

    return cells


# =============================================================================
# BUILD FUNCTIONS
# =============================================================================

def build_base():
    """Build the base unit — 200x160mm rectangular, tapered, hollowed.

    Wet zone (left): reservoir, atomizer mount, pump output tubes.
    Dry zone (right): ESP32, 5x MOSFET, PD trigger, atomizer driver, BME280.
    Pumps mount along the divider wall straddling both zones.
    """

    # --- Outer shell ---
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

    # --- Wet/dry divider wall ---
    # Full height internal wall from floor to rim
    divider_h = BASE_H - FLOOR_H - WALL - 2
    divider = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_X, 0)
        .rect(WALL_INNER, BASE_D - WALL * 2 - 2)
        .extrude(divider_h)
    )
    base = base.union(divider)

    # --- Atomizer mount (wet zone, floor) ---
    atomizer_pocket = (
        cq.Workplane("XY")
        .workplane(offset=-0.1)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_MOUNT_DIA / 2)
        .extrude(FLOOR_H + 0.2)
    )
    base = base.cut(atomizer_pocket)

    # Atomizer driver board pocket (dry zone, near divider, close to atomizer Y)
    driver_x = DIVIDER_X + WALL_INNER / 2 + 5 + ATOMIZER_DRIVER_W / 2
    driver_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(driver_x, ATOMIZER_POS_Y)
        .rect(ATOMIZER_DRIVER_W, ATOMIZER_DRIVER_D)
        .extrude(8)
    )
    base = base.cut(driver_pocket)

    # --- Peristaltic pump pockets (5x along divider wall, wet side) ---
    # Pumps sit on the wet side of the divider. Their intake tubes come from
    # above (top shell), output tubes discharge into the reservoir.
    for py in pump_y_positions:
        pump_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(DIVIDER_X - WALL_INNER / 2 - PUMP_BODY_W / 2 - 1, py)
            .rect(PUMP_BODY_W, PUMP_BODY_D)
            .extrude(PUMP_BODY_H + 2)
        )
        base = base.cut(pump_pocket)

    # --- Tube pass-through holes in divider wall (5x, one per pump) ---
    # Each pump needs a small hole through the divider for its intake tube
    # coming from the top shell. Hole is at the top of the divider.
    for py in pump_y_positions:
        tube_thru = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + divider_h - TUBE_HOLE_DIA - 2)
            .center(DIVIDER_X, py)
            .circle(TUBE_HOLE_DIA / 2)
            .extrude(TUBE_HOLE_DIA + 4)
        )
        base = base.cut(tube_thru)

    # --- Electronics bay (dry zone, right of divider) ---
    # Dry zone X range: from (DIVIDER_X + WALL_INNER/2) to (MEETING_W/2 - WALL)
    dry_left = DIVIDER_X + WALL_INNER / 2
    dry_right = MEETING_W / 2 - WALL
    dry_center_x = (dry_left + dry_right) / 2
    dry_usable_w = dry_right - dry_left  # ~62mm

    # ESP32 pocket (rear of dry zone, oriented lengthwise along Y)
    esp32_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(dry_center_x, 35)
        .rect(ESP32_D, ESP32_W)   # rotated: 28mm wide x 55mm deep
        .extrude(ESP32_H + 2)
    )
    base = base.cut(esp32_pocket)

    # 5 MOSFET module pockets — arranged in a column along Y (one per pump)
    # Each MOSFET is 25x20mm. Placed in a vertical column in the dry zone,
    # spaced to match pump spacing for clean wiring.
    mosfet_x = dry_center_x
    for i, py in enumerate(pump_y_positions):
        mosfet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(mosfet_x, py)
            .rect(MOSFET_W, MOSFET_D)
            .extrude(MOSFET_H + 2)
        )
        base = base.cut(mosfet_pocket)

    # PD trigger pocket (rear corner of dry zone, near USB-C port)
    pd_x = dry_center_x + 10
    pd_y = MEETING_D / 2 - WALL - PD_TRIGGER_D / 2 - 5
    pd_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(pd_x, pd_y)
        .rect(PD_TRIGGER_W, PD_TRIGGER_D)
        .extrude(PD_TRIGGER_H + 2)
    )
    base = base.cut(pd_pocket)

    # BME280 pocket (near front wall of dry zone, away from mist)
    bme_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(dry_center_x + 10, -(MEETING_D / 2 - WALL - BME280_D / 2 - 5))
        .rect(BME280_W, BME280_D)
        .extrude(BME280_H + 2)
    )
    base = base.cut(bme_pocket)

    # --- USB-C port cutout (rear wall, aligned with PD trigger) ---
    usbc_cutout = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + PD_TRIGGER_H / 2)
        .center(pd_x, BASE_D / 2)
        .rect(USBC_PORT_W, WALL + 2)
        .extrude(USBC_PORT_H)
    )
    base = base.cut(usbc_cutout)

    # --- Rubber feet (4 circular pockets on the bottom) ---
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

    # --- LED strip channel (inside base wall near top, behind hex mesh) ---
    led_z = BASE_H - WALL - LED_CHANNEL_D - 2
    # Right wall channel (long side)
    led_right = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(MEETING_W / 2 - WALL - LED_CHANNEL_D / 2, 0)
        .rect(LED_CHANNEL_D, BASE_D - WALL * 2 - 10)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_right)
    # Front wall channel (short side)
    led_front = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(0, -(MEETING_D / 2 - WALL - LED_CHANNEL_D / 2))
        .rect(BASE_W - WALL * 2 - 10, LED_CHANNEL_D)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_front)

    # --- Hex mesh cutouts (front wall + right wall, upper half) ---
    hex_panel_h = BASE_H * 0.45
    hex_panel_z = BASE_H - hex_panel_h - WALL - 2

    # Front wall hex mesh (long axis of the front face)
    hex_front = hex_mesh_cutout(BASE_W * 0.7, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_front_positioned = (
        hex_front
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((0, -(BASE_D / 2 - _taper_shrink_base * 0.5), hex_panel_z + hex_panel_h / 2))
    )
    base = base.cut(hex_front_positioned)

    # Right wall hex mesh (dry zone ventilation)
    hex_right = hex_mesh_cutout(BASE_D * 0.6, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_right_positioned = (
        hex_right
        .rotateAboutCenter((0, 0, 1), 90)
        .rotateAboutCenter((0, 1, 0), 90)
        .translate((BASE_W / 2 - _taper_shrink_base * 0.5, 0, hex_panel_z + hex_panel_h / 2))
    )
    base = base.cut(hex_right_positioned)

    # Left wall hex mesh (wet zone, LED glow)
    hex_left = hex_mesh_cutout(BASE_D * 0.5, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    hex_left_positioned = (
        hex_left
        .rotateAboutCenter((0, 0, 1), 90)
        .rotateAboutCenter((0, 1, 0), 90)
        .translate((-(BASE_W / 2 - _taper_shrink_base * 0.5), 0, hex_panel_z + hex_panel_h / 2))
    )
    base = base.cut(hex_left_positioned)

    # --- Magnet pockets on base rim (6x) ---
    for mx, my in magnet_positions:
        magnet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=BASE_H - MAGNET_H)
            .center(mx, my)
            .circle((MAGNET_DIA + TOL * 2) / 2)
            .extrude(MAGNET_H + 0.1)
        )
        base = base.cut(magnet_pocket)

    # --- Alignment pins (4x, protrude upward from base rim) ---
    for px, py in pin_positions:
        pin = (
            cq.Workplane("XY")
            .workplane(offset=BASE_H)
            .center(px, py)
            .circle(PIN_DIA / 2)
            .extrude(PIN_H)
        )
        base = base.union(pin)

    # --- SOMNI branding (rear panel, +Y wall) ---
    try:
        brand_text = (
            cq.Workplane("XZ")
            .workplane(offset=BASE_D / 2)
            .center(0, BASE_H * 0.35)
            .text("SOMNI", 8, -BRAND_DEPTH, font="sans-serif")
        )
        base = base.cut(brand_text)
    except Exception:
        brand_recess = (
            cq.Workplane("XY")
            .workplane(offset=BASE_H * 0.3)
            .center(0, BASE_D / 2)
            .rect(35, 8)
            .extrude(-BRAND_DEPTH)
        )
        base = base.cut(brand_recess)

    return base


def build_top_shell():
    """Build the top shell — continues taper, houses bottles + tube routing.

    Key features:
    - 5 threaded bottle receivers in 2+3 cluster
    - 5 individual tube channels from each receiver to its exit grommet
    - Large access hatch (130x50mm) on the right wall
    - Mist chimney, fill port, chevron exhaust
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

    # --- Bottle receivers (5x, 2+3 quincunx cluster) ---
    receiver_top_z = TOP_H - WALL - 3
    receiver_bottom_z = receiver_top_z - RECEIVER_LENGTH

    for idx, (rx, ry) in enumerate(RECEIVER_POSITIONS):
        bx = rx + CLUSTER_CENTER_X
        by = ry + CLUSTER_CENTER_Y

        # Receiver body
        receiver = (
            cq.Workplane("XY")
            .workplane(offset=receiver_bottom_z)
            .center(bx, by)
            .circle(RECEIVER_OD / 2)
            .extrude(RECEIVER_LENGTH)
        )
        shell = shell.union(receiver)

        # Thread bore
        thread_bore = (
            cq.Workplane("XY")
            .workplane(offset=receiver_bottom_z - 0.5)
            .center(bx, by)
            .circle(RECEIVER_THREAD_ID / 2)
            .extrude(RECEIVER_LENGTH + 1)
        )
        shell = shell.cut(thread_bore)

        # Tube bore through receiver + ceiling
        tube_bore = (
            cq.Workplane("XY")
            .workplane(offset=receiver_bottom_z - 0.5)
            .center(bx, by)
            .circle(TUBE_BORE_DIA / 2)
            .extrude(TOP_H - receiver_bottom_z + 1)
        )
        shell = shell.cut(tube_bore)

        # Bottle body clearance below receiver
        bottle_clearance = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(bx, by)
            .circle(BOTTLE_DIA / 2 + TOL)
            .extrude(receiver_bottom_z + 1)
        )
        shell = shell.cut(bottle_clearance)

    # --- Individual tube routing channels (5x) ---
    # Each receiver's tube needs to route from the receiver top, along the
    # shell ceiling, to an exit grommet above its corresponding pump.
    # Channels are cut into the ceiling as shallow troughs.
    channel_z = TOP_H - WALL - TUBE_CHANNEL_D

    for idx, (rx, ry) in enumerate(RECEIVER_POSITIONS):
        bx = rx + CLUSTER_CENTER_X
        by = ry + CLUSTER_CENTER_Y
        exit_x, exit_y = tube_exit_positions[idx]

        # Route: horizontal channel from receiver to exit point.
        # Two-segment L-shaped route: first move in X, then in Y.
        # Segment 1: horizontal (along X) from receiver to exit X
        seg1_start_x = bx
        seg1_end_x = exit_x
        seg1_y = by
        seg1_len = abs(seg1_end_x - seg1_start_x)
        seg1_cx = (seg1_start_x + seg1_end_x) / 2

        if seg1_len > 1:
            channel_seg1 = (
                cq.Workplane("XY")
                .workplane(offset=channel_z)
                .center(seg1_cx, seg1_y)
                .rect(seg1_len + TUBE_CHANNEL_W, TUBE_CHANNEL_W)
                .extrude(TUBE_CHANNEL_D + 0.5)
            )
            shell = shell.cut(channel_seg1)

        # Segment 2: vertical (along Y) from receiver Y to exit Y
        seg2_x = exit_x
        seg2_start_y = by
        seg2_end_y = exit_y
        seg2_len = abs(seg2_end_y - seg2_start_y)
        seg2_cy = (seg2_start_y + seg2_end_y) / 2

        if seg2_len > 1:
            channel_seg2 = (
                cq.Workplane("XY")
                .workplane(offset=channel_z)
                .center(seg2_x, seg2_cy)
                .rect(TUBE_CHANNEL_W, seg2_len + TUBE_CHANNEL_W)
                .extrude(TUBE_CHANNEL_D + 0.5)
            )
            shell = shell.cut(channel_seg2)

        # Exit grommet hole through the shell floor
        tube_exit = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(exit_x, exit_y)
            .circle(TUBE_HOLE_DIA / 2)
            .extrude(WALL + 1)
        )
        shell = shell.cut(tube_exit)

        # Vertical drop from ceiling channel to floor grommet
        tube_drop = (
            cq.Workplane("XY")
            .workplane(offset=-0.5)
            .center(exit_x, exit_y)
            .rect(TUBE_CHANNEL_W, TUBE_CHANNEL_W)
            .extrude(TOP_H - WALL + 1)
        )
        shell = shell.cut(tube_drop)

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

    # --- Matching magnet pockets (bottom of top shell) ---
    for mx, my in magnet_positions:
        magnet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=-0.1)
            .center(mx, my)
            .circle((MAGNET_DIA + TOL * 2) / 2)
            .extrude(MAGNET_H + 0.1)
        )
        shell = shell.cut(magnet_pocket)

    # --- Matching pin holes ---
    for px, py in pin_positions:
        pin_hole = (
            cq.Workplane("XY")
            .workplane(offset=-0.1)
            .center(px, py)
            .circle((PIN_DIA + TOL * 2) / 2)
            .extrude(PIN_H + WALL + 0.1)
        )
        shell = shell.cut(pin_hole)

    # --- Chevron exhaust port (top surface) ---
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

    # 3 internal vanes across exhaust diamond
    vane_thickness = 1.2
    for v in range(3):
        vane_offset = -EXHAUST_D / 4 + v * (EXHAUST_D / 4)
        vy = EXHAUST_POS_Y + vane_offset
        t_vane = 1.0 - abs(vane_offset) / (EXHAUST_D / 2)
        vane_half_w = (EXHAUST_W / 2) * t_vane
        if vane_half_w < 2:
            continue
        vane = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - WALL)
            .center(EXHAUST_POS_X, vy)
            .rect(vane_half_w * 2, vane_thickness)
            .extrude(WALL)
        )
        shell = shell.union(vane)

    # --- Bottle access hatch (right side, +X wall) ---
    # Large opening: 130mm wide x 50mm tall — nearly the full right wall.
    hatch_z_bottom = WALL + 2
    hatch_z_center = hatch_z_bottom + HATCH_H / 2
    t_hatch = hatch_z_center / TOP_H
    wall_x_at_hatch = (MEETING_W + t_hatch * (TOP_W - MEETING_W)) / 2

    hatch_cut = (
        cq.Workplane("XY")
        .workplane(offset=hatch_z_bottom)
        .center(wall_x_at_hatch, 0)
        .rect(WALL + 2, HATCH_W)
        .extrude(HATCH_H)
    )
    shell = shell.cut(hatch_cut)

    # Hatch lip/frame
    lip_thickness = 1.5
    lip_depth = 2.0
    hatch_lip_outer = (
        cq.Workplane("XY")
        .workplane(offset=hatch_z_bottom - lip_thickness)
        .center(wall_x_at_hatch - WALL, 0)
        .rect(lip_depth, HATCH_W + lip_thickness * 2)
        .extrude(HATCH_H + lip_thickness * 2)
    )
    hatch_lip_inner = (
        cq.Workplane("XY")
        .workplane(offset=hatch_z_bottom - 0.1)
        .center(wall_x_at_hatch - WALL, 0)
        .rect(lip_depth + 0.2, HATCH_W)
        .extrude(HATCH_H + 0.2)
    )
    hatch_lip = hatch_lip_outer.cut(hatch_lip_inner)
    shell = shell.union(hatch_lip)

    # --- Panel line on top shell ---
    shell = panel_line_cut(
        shell, PANEL_LINE_Z_TOP, TOP_H,
        MEETING_W, MEETING_D, TOP_W, TOP_D,
        PANEL_LINE_WIDTH, PANEL_LINE_DEPTH
    )

    return shell


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

# Compute dry zone dimensions for summary
_dry_left = DIVIDER_X + WALL_INNER / 2
_dry_right = MEETING_W / 2 - WALL
_dry_usable_w = _dry_right - _dry_left

print("=" * 60)
print("Somni Oil Diffuser V2.1 — Night City")
print("=" * 60)
print()
print("--- Enclosure ---")
print(f"Base:        {BASE_W}x{BASE_D}x{BASE_H}mm (bottom footprint)")
print(f"             {MEETING_W:.1f}x{MEETING_D:.1f}mm (meeting line)")
print(f"Top shell:   {MEETING_W:.1f}x{MEETING_D:.1f}x{TOP_H}mm (bottom)")
print(f"             {TOP_W:.1f}x{TOP_D:.1f}mm (top)")
print(f"Total:       {TOTAL_H}mm tall")
print(f"Taper:       {TAPER_ANGLE} deg per side")
print(f"Wall:        {WALL}mm outer, {WALL_INNER}mm inner, {FLOOR_H}mm floor")
print()
print("--- Base — Wet Zone (left of divider) ---")
print(f"Divider at:  X={DIVIDER_X}mm")
print(f"Reservoir:   ~{int(DIVIDER_X + BASE_W/2 - WALL*2)}mm wide, depth={RESERVOIR_DEPTH:.1f}mm")
print(f"Atomizer:    {ATOMIZER_MOUNT_DIA}mm mount at ({ATOMIZER_POS_X}, {ATOMIZER_POS_Y})")
print(f"Pumps:       {PUMP_COUNT}x peristaltic, {PUMP_SPACING}mm spacing along divider")
print(f"             Body: {PUMP_BODY_W}x{PUMP_BODY_D}x{PUMP_BODY_H}mm each")
print(f"             Y positions: {[f'{y:.0f}' for y in pump_y_positions]}")
print()
print("--- Base — Dry Zone (right of divider) ---")
print(f"Usable width:{_dry_usable_w:.1f}mm (X={_dry_left:.1f} to {_dry_right:.1f})")
print(f"ESP32:       {ESP32_W}x{ESP32_D}mm (rotated, fits in {_dry_usable_w:.0f}mm zone)")
print(f"MOSFETs:     {PUMP_COUNT}x {MOSFET_W}x{MOSFET_D}mm (column, aligned with pumps)")
print(f"PD trigger:  {PD_TRIGGER_W}x{PD_TRIGGER_D}mm (rear corner)")
print(f"BME280:      {BME280_W}x{BME280_D}mm (front corner)")
print(f"USB-C port:  {USBC_PORT_W}x{USBC_PORT_H}mm (rear wall)")
print()
print("--- Top Shell ---")
print(f"Bottles:     {BOTTLE_COUNT}x threaded receivers (2+3 cluster)")
print(f"             Cluster center: ({CLUSTER_CENTER_X}, {CLUSTER_CENTER_Y})")
print(f"             Receiver OD {RECEIVER_OD:.0f}mm, thread ID {RECEIVER_THREAD_ID:.1f}mm")
print(f"Tube routing:{PUMP_COUNT}x individual L-shaped channels in ceiling")
print(f"             {PUMP_COUNT}x {TUBE_HOLE_DIA}mm exit grommets (one per pump)")
print(f"Hatch:       {HATCH_W}x{HATCH_H}mm (+X wall, nearly full side)")
print(f"Mist channel:{MIST_CHANNEL_DIA}mm bore at ({MIST_POS_X}, {MIST_POS_Y})")
print(f"Fill port:   {FILL_PORT_DIA}mm dia at ({FILL_PORT_POS_X}, {FILL_PORT_POS_Y})")
print(f"Exhaust:     {EXHAUST_W}x{EXHAUST_D}mm chevron, 3 vanes")
print()
print("--- Connections ---")
print(f"Magnets:     {len(magnet_positions)}x {MAGNET_DIA}mm dia x {MAGNET_H}mm")
print(f"Pins:        {PIN_COUNT}x {PIN_DIA}mm dia x {PIN_H}mm")
print(f"Hex mesh:    front + right + left walls, {HEX_CELL_SIZE}mm cells")
print()
print(f"Print bed:   {BASE_W}x{BASE_D}mm fits QIDI Q2 (245x255mm)")
