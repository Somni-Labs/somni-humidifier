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
