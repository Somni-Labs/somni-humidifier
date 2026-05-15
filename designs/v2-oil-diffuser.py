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
_taper_shrink_base = BASE_H * math.tan(math.radians(TAPER_ANGLE))
MEETING_W = BASE_W - 2 * _taper_shrink_base  # ~145.3mm
MEETING_D = BASE_D - 2 * _taper_shrink_base

# Derived: top-of-shell footprint (smallest cross-section)
_taper_shrink_top = TOP_H * math.tan(math.radians(TAPER_ANGLE))
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


# =============================================================================
# MODULE-LEVEL SHARED POSITIONS
# =============================================================================

# Magnet positions on the rim — one centered on each side edge.
# Coordinates are at the MEETING footprint (top of base / bottom of top shell).
magnet_positions = [
    (0, -MEETING_D / 2 + MAGNET_INSET),    # front
    (0,  MEETING_D / 2 - MAGNET_INSET),     # rear
    (-MEETING_W / 2 + MAGNET_INSET, 0),     # left
    ( MEETING_W / 2 - MAGNET_INSET, 0),     # right
]

# Alignment pin positions — one near each corner of the meeting footprint.
pin_positions = [
    (-MEETING_W / 2 + 15, -MEETING_D / 2 + 15),
    ( MEETING_W / 2 - 15, -MEETING_D / 2 + 15),
    (-MEETING_W / 2 + 15,  MEETING_D / 2 - 15),
    ( MEETING_W / 2 - 15,  MEETING_D / 2 - 15),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def tapered_box(width_bottom, depth_bottom, width_top, depth_top, height):
    """Create an angular tapered box — larger at bottom, smaller at top.

    All four sides taper inward linearly. No fillets — sharp cyberpunk edges.
    Returns a solid centered on XY at Z=0..height.
    """
    # Build via CadQuery loft between two rectangular profiles
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
    Returns a solid block of hex cells extruded 100mm along Z (deep enough
    to cut through any wall).

    Parameters:
        width:          panel width (X extent)
        height:         panel height (Y extent)
        cell_size:      flat-to-flat distance of each hex cell
        wall_thickness: wall between adjacent hex cells
        margin:         inset from panel edges before hex pattern starts
    """
    pitch = cell_size + wall_thickness
    row_height = pitch * math.sqrt(3) / 2
    hex_radius = cell_size / 2

    usable_w = width - 2 * margin
    usable_h = height - 2 * margin

    cols = int(usable_w / pitch) + 1
    rows = int(usable_h / row_height) + 1

    cells = None
    cell_count = 0

    for row in range(rows):
        for col in range(cols):
            cx = -usable_w / 2 + col * pitch + (pitch / 2 if row % 2 else 0)
            cy = -usable_h / 2 + row * row_height

            # Skip cells outside the usable area
            if abs(cx) > usable_w / 2 - hex_radius or abs(cy) > usable_h / 2 - hex_radius:
                continue

            # Build a pointy-top hexagon from 6 vertices
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
            cell_count += 1

    # If no cells fit, return a tiny box to avoid empty solid errors
    if cells is None:
        cells = cq.Workplane("XY").box(0.1, 0.1, 0.1)

    return cells


# =============================================================================
# BUILD FUNCTIONS
# =============================================================================

def build_base():
    """Build the base unit — outer tapered shell, hollowed out.

    160mm square at Z=0, tapering inward at 6 deg per side up to
    MEETING_W x MEETING_D at Z=BASE_H (70mm).
    Shell is WALL (3mm) thick with a solid FLOOR_H (3mm) floor.
    """

    # Outer tapered shell
    base = tapered_box(BASE_W, BASE_D, MEETING_W, MEETING_D, BASE_H)

    # Hollow interior — same taper but offset inward by WALL on each side.
    # Cavity starts at FLOOR_H and goes up to BASE_H (top is open for the
    # shell to sit on, the rim created by the wall difference seals it).
    cavity = tapered_box(
        BASE_W - WALL * 2, BASE_D - WALL * 2,
        MEETING_W - WALL * 2, MEETING_D - WALL * 2,
        BASE_H - FLOOR_H
    ).translate((0, 0, FLOOR_H))

    base = base.cut(cavity)

    # --- Panel line ---
    base = panel_line_cut(base, PANEL_LINE_Z_BASE, BASE_H, BASE_W, BASE_D, MEETING_W, MEETING_D, PANEL_LINE_WIDTH, PANEL_LINE_DEPTH)

    # --- Wet/dry divider wall ---
    divider = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_X, 0)
        .rect(WALL_INNER, BASE_D - WALL * 2 - 2)
        .extrude(BASE_H - FLOOR_H - WALL - 2)
    )
    base = base.union(divider)

    # --- Atomizer mount (wet zone) ---
    # Circular pocket through the reservoir floor for the piezo disk + wiring
    atomizer_pocket = (
        cq.Workplane("XY")
        .workplane(offset=-0.1)
        .center(ATOMIZER_POS_X, ATOMIZER_POS_Y)
        .circle(ATOMIZER_MOUNT_DIA / 2)
        .extrude(FLOOR_H + 0.2)
    )
    base = base.cut(atomizer_pocket)

    # Atomizer driver board pocket (dry zone, near divider)
    driver_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(DIVIDER_X + WALL_INNER / 2 + 5 + ATOMIZER_DRIVER_W / 2, ATOMIZER_POS_Y)
        .rect(ATOMIZER_DRIVER_W, ATOMIZER_DRIVER_D)
        .extrude(8)
    )
    base = base.cut(driver_pocket)

    # --- Peristaltic pump pockets (5x along divider wall) ---
    pump_y_start = -(PUMP_COUNT - 1) / 2 * PUMP_SPACING
    for i in range(PUMP_COUNT):
        py = pump_y_start + i * PUMP_SPACING
        pump_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(DIVIDER_X - WALL_INNER / 2 - PUMP_BODY_W / 2 - 1, py)
            .rect(PUMP_BODY_W, PUMP_BODY_D)
            .extrude(PUMP_BODY_H + 2)
        )
        base = base.cut(pump_pocket)

    # --- Electronics bay pockets (dry zone, right of divider) ---
    # Dry zone center X: midpoint between divider right edge and right inner wall
    dry_center_x = DIVIDER_X + WALL_INNER / 2 + (MEETING_W / 2 - WALL - DIVIDER_X - WALL_INNER / 2) / 2

    # ESP32 pocket (toward rear of dry zone)
    esp32_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(dry_center_x, 30)
        .rect(ESP32_W, ESP32_D)
        .extrude(ESP32_H + 2)
    )
    base = base.cut(esp32_pocket)

    # 5 MOSFET module pockets in a row (below ESP32)
    mosfet_row_y = 0
    mosfet_start_x = dry_center_x - (4 * (MOSFET_W + 2)) / 2
    for i in range(5):
        mx = mosfet_start_x + i * (MOSFET_W + 2)
        mosfet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H)
            .center(mx, mosfet_row_y)
            .rect(MOSFET_W, MOSFET_D)
            .extrude(MOSFET_H + 2)
        )
        base = base.cut(mosfet_pocket)

    # PD trigger pocket (near rear wall in dry zone)
    pd_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(dry_center_x, BASE_D / 2 - WALL - PD_TRIGGER_D / 2 - 5)
        .rect(PD_TRIGGER_W, PD_TRIGGER_D)
        .extrude(PD_TRIGGER_H + 2)
    )
    base = base.cut(pd_pocket)

    # --- USB-C port cutout (rear wall, near PD trigger) ---
    usbc_cutout = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + PD_TRIGGER_H / 2)
        .center(dry_center_x, BASE_D / 2)
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

    # --- LED strip channel (shallow channel inside base wall near top) ---
    # Runs along the right and front inner walls behind where hex mesh will go
    led_z = BASE_H - WALL - LED_CHANNEL_D - 2
    # Right wall channel
    led_right = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(MEETING_W / 2 - WALL - LED_CHANNEL_D / 2, 0)
        .rect(LED_CHANNEL_D, BASE_D - WALL * 2 - 10)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_right)
    # Front wall channel
    led_front = (
        cq.Workplane("XY")
        .workplane(offset=led_z)
        .center(0, -(MEETING_D / 2 - WALL - LED_CHANNEL_D / 2))
        .rect(BASE_W - WALL * 2 - 10, LED_CHANNEL_D)
        .extrude(LED_CHANNEL_W)
    )
    base = base.cut(led_front)

    # --- Hex mesh cutouts (right wall + front wall, upper half) ---
    # Hex mesh height covers roughly the upper half of the base wall
    hex_panel_h = BASE_H * 0.45
    hex_panel_z = BASE_H - hex_panel_h - WALL - 2  # leave rim at top

    # Right wall hex mesh
    hex_right = hex_mesh_cutout(BASE_D * 0.7, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    # Rotate: XY plane -> align with right wall (YZ plane)
    # rotate 90° around Z to swap X/Y, then 90° around X to get into YZ
    hex_right_positioned = (
        hex_right
        .rotateAboutCenter((0, 0, 1), 90)
        .rotateAboutCenter((0, 1, 0), 90)
        .translate((BASE_W / 2 - _taper_shrink_base * 0.5, 0, hex_panel_z + hex_panel_h / 2))
    )
    base = base.cut(hex_right_positioned)

    # Front wall hex mesh
    hex_front = hex_mesh_cutout(BASE_W * 0.7, hex_panel_h, HEX_CELL_SIZE, HEX_WALL, HEX_MARGIN)
    # Rotate: XY plane -> align with front wall (XZ plane)
    hex_front_positioned = (
        hex_front
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((0, -(BASE_D / 2 - _taper_shrink_base * 0.5), hex_panel_z + hex_panel_h / 2))
    )
    base = base.cut(hex_front_positioned)

    # --- Magnet pockets on base rim (4x) ---
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

    return base


def build_top_shell():
    """Build the top shell — outer tapered shell, hollowed out.

    Continues the taper from where the base left off:
    MEETING_W x MEETING_D at Z=0 (local), tapering to TOP_W x TOP_D
    at Z=TOP_H (60mm). Shell is WALL (3mm) thick with a solid top cap.
    """

    # Outer tapered shell
    shell = tapered_box(MEETING_W, MEETING_D, TOP_W, TOP_D, TOP_H)

    # Hollow interior — inset by WALL, starting above a WALL-thick floor
    # and stopping below the WALL-thick ceiling (solid top surface).
    cavity = tapered_box(
        MEETING_W - WALL * 2, MEETING_D - WALL * 2,
        TOP_W - WALL * 2, TOP_D - WALL * 2,
        TOP_H - WALL * 2
    ).translate((0, 0, WALL))

    shell = shell.cut(cavity)

    # --- Bottle wells (5x, cut from top surface) ---
    bottle_y_start = -(BOTTLE_COUNT - 1) / 2 * BOTTLE_SPACING
    for i in range(BOTTLE_COUNT):
        bx = bottle_y_start + i * BOTTLE_SPACING  # spread along X axis
        by = BOTTLE_ROW_Y

        # Main well — cylindrical pocket from top surface downward
        well = (
            cq.Workplane("XY")
            .workplane(offset=TOP_H - BOTTLE_WELL_DEPTH)
            .center(bx, by)
            .circle(BOTTLE_WELL_DIA / 2)
            .extrude(BOTTLE_WELL_DEPTH + 0.1)
        )
        shell = shell.cut(well)

        # Tube pass-through hole at the bottom of each well
        tube_hole = (
            cq.Workplane("XY")
            .workplane(offset=-0.1)
            .center(bx, by)
            .circle(TUBE_HOLE_DIA / 2)
            .extrude(TOP_H - BOTTLE_WELL_DEPTH + 1)
        )
        shell = shell.cut(tube_hole)

    # --- Mist channel (internal chimney) ---
    # Outer chimney wall
    chimney_outer = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(MIST_POS_X, MIST_POS_Y)
        .circle(MIST_CHANNEL_DIA / 2 + MIST_CHANNEL_WALL)
        .extrude(TOP_H - WALL * 2)
    )
    shell = shell.union(chimney_outer)

    # Bore through the chimney (all the way through)
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

    # Fill port lip/rim (2mm wider ring, 1.5mm tall)
    fill_lip = (
        cq.Workplane("XY")
        .workplane(offset=TOP_H)
        .center(FILL_PORT_POS_X, FILL_PORT_POS_Y)
        .circle(FILL_PORT_DIA / 2 + 2)
        .circle(FILL_PORT_DIA / 2)
        .extrude(1.5)
    )
    shell = shell.union(fill_lip)

    # --- Matching magnet pockets (bottom of top shell floor) ---
    for mx, my in magnet_positions:
        magnet_pocket = (
            cq.Workplane("XY")
            .workplane(offset=-0.1)
            .center(mx, my)
            .circle((MAGNET_DIA + TOL * 2) / 2)
            .extrude(MAGNET_H + 0.1)
        )
        shell = shell.cut(magnet_pocket)

    # --- Matching pin holes (bottom of top shell) ---
    for px, py in pin_positions:
        pin_hole = (
            cq.Workplane("XY")
            .workplane(offset=-0.1)
            .center(px, py)
            .circle((PIN_DIA + TOL * 2) / 2)
            .extrude(PIN_H + WALL + 0.1)
        )
        shell = shell.cut(pin_hole)

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
print("=" * 60)
print("Somni Oil Diffuser V2 — Night City")
print("=" * 60)
print()
print(f"Base:      {BASE_W}x{BASE_D}x{BASE_H}mm (bottom footprint)")
print(f"           {MEETING_W:.1f}x{MEETING_D:.1f}mm (top of base)")
print(f"Top shell: {MEETING_W:.1f}x{MEETING_D:.1f}x{TOP_H}mm (bottom)")
print(f"           {TOP_W:.1f}x{TOP_D:.1f}mm (top)")
print(f"Total:     {TOTAL_H}mm tall")
print(f"Taper:     {TAPER_ANGLE} deg per side")
print(f"Wall:      {WALL}mm outer, {FLOOR_H}mm floor")
print()
print(f"Taper shrink base: {_taper_shrink_base:.1f}mm per side")
print(f"Taper shrink top:  {_taper_shrink_top:.1f}mm per side")
print(f"Meeting dims:      {MEETING_W:.1f} x {MEETING_D:.1f}mm")
print(f"Top dims:          {TOP_W:.1f} x {TOP_D:.1f}mm")
print()
print(f"Magnets:   {MAGNET_COUNT}x at {magnet_positions}")
print(f"Pins:      {PIN_COUNT}x at {pin_positions}")
print()
print(f"Print bed: {BASE_W}mm fits QIDI Q2 (245mm)")
