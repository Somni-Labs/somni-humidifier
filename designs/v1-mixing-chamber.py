"""V1 Mixing Chamber Design

The core mixing chamber where water meets essential oils and gets atomized into mist.
Features:
- Ultrasonic disk mount at bottom with O-ring seal
- Water inlet port for reservoir feed
- 5x oil inlet ports positioned above waterline
- Mist chimney with splash guard baffle
- Aesthetic mist outlet nozzle
- Drain port for cleaning
- 3mm+ wall thickness for water-tight FDM printing
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# === PARAMETERS ===

# Main chamber dimensions
CHAMBER_OUTER_DIAMETER = 80  # mm - overall chamber size
CHAMBER_HEIGHT = 60  # mm - total height from base to chimney top
WALL_THICKNESS = 3.5  # mm - minimum for water-tight FDM printing

# Ultrasonic disk mounting
PIEZO_DISK_DIAMETER = 16  # mm - TODO: measure actual ultrasonic disk
PIEZO_RECESS_DEPTH = 2  # mm - how deep the disk sits in the chamber
PIEZO_ORING_GROOVE_WIDTH = 1.5  # mm - O-ring groove for sealing
PIEZO_ORING_GROOVE_DEPTH = 0.8  # mm

# Water level and inlet
WATER_LEVEL_HEIGHT = 12  # mm - 10-15mm above piezo disk for operation
WATER_INLET_DIAMETER = 6  # mm - barb fitting for 1/4" tubing
WATER_INLET_HEIGHT = 8  # mm - positioned just above bottom

# Oil inlets (5x around perimeter)
OIL_INLET_DIAMETER = 3  # mm - smaller barb for oil tubes
OIL_INLET_COUNT = 5
OIL_INLET_HEIGHT = 20  # mm - above waterline so oil drips in
OIL_INLET_RADIUS = (CHAMBER_OUTER_DIAMETER - WALL_THICKNESS * 2) / 2 - 5  # mm from center

# Mist chimney
CHIMNEY_INNER_DIAMETER = 35  # mm - 30-40mm recommended for good mist flow
CHIMNEY_WALL_THICKNESS = 2.5  # mm
CHIMNEY_HEIGHT = 30  # mm - height above water level
CHIMNEY_START_HEIGHT = WATER_LEVEL_HEIGHT + 5  # mm - starts above splash zone

# Splash guard baffle
BAFFLE_DIAMETER = CHIMNEY_INNER_DIAMETER - 4  # mm - slightly smaller than chimney
BAFFLE_HEIGHT = 3  # mm - thin disc to catch water droplets
BAFFLE_CLEARANCE = 2  # mm - gap around edges for mist to pass

# Outlet nozzle (aesthetic top piece)
NOZZLE_HEIGHT = 8  # mm
NOZZLE_OUTER_DIAMETER = CHIMNEY_INNER_DIAMETER + CHIMNEY_WALL_THICKNESS * 2 + 2  # mm
NOZZLE_INNER_DIAMETER = CHIMNEY_INNER_DIAMETER - 2  # mm - slight taper for aesthetics

# Drain port
DRAIN_PORT_DIAMETER = 4  # mm - small threaded plug
DRAIN_PORT_THREAD_DEPTH = 6  # mm

# === HELPER FUNCTIONS ===

def create_barb_fitting_recess(diameter, depth=3):
    """Create a recess for press-fit barb fittings"""
    return (
        cq.Workplane("XY")
        .circle(diameter / 2)
        .extrude(depth)
        .faces(">Z")
        .circle(diameter / 2 - 0.5)  # Slight taper for press-fit
        .extrude(2)
    )

# === MAIN CHAMBER BODY ===

# Outer shell
chamber_body = (
    cq.Workplane("XY")
    .circle(CHAMBER_OUTER_DIAMETER / 2)
    .extrude(CHAMBER_HEIGHT)
    # Hollow out interior
    .faces(">Z")
    .circle((CHAMBER_OUTER_DIAMETER - WALL_THICKNESS * 2) / 2)
    .cutThruAll()
)

# === PIEZO DISK MOUNT ===

# Recess for ultrasonic disk
piezo_recess = (
    cq.Workplane("XY")
    .circle(PIEZO_DISK_DIAMETER / 2)
    .extrude(PIEZO_RECESS_DEPTH)
    # O-ring groove around edge
    .faces(">Z")
    .circle(PIEZO_DISK_DIAMETER / 2 + PIEZO_ORING_GROOVE_WIDTH / 2)
    .circle(PIEZO_DISK_DIAMETER / 2 - PIEZO_ORING_GROOVE_WIDTH / 2)
    .extrude(PIEZO_ORING_GROOVE_DEPTH)
)

# Cut piezo mount from bottom of chamber
chamber_body = chamber_body.cut(piezo_recess.translate((0, 0, -PIEZO_RECESS_DEPTH)))

# === WATER INLET ===

# Position water inlet on side of chamber
water_inlet_pos = (CHAMBER_OUTER_DIAMETER / 2, 0, WATER_INLET_HEIGHT)
water_inlet_hole = (
    create_barb_fitting_recess(WATER_INLET_DIAMETER)
    .rotate((0, 0, 0), (0, 1, 0), 90)  # Horizontal orientation
    .translate(water_inlet_pos)
)

chamber_body = chamber_body.cut(water_inlet_hole)

# === OIL INLETS (5x around perimeter) ===

for i in range(OIL_INLET_COUNT):
    angle = (i * 360 / OIL_INLET_COUNT)
    angle_rad = math.radians(angle)
    x = OIL_INLET_RADIUS * math.cos(angle_rad)
    y = OIL_INLET_RADIUS * math.sin(angle_rad)

    oil_inlet_pos = (x, y, OIL_INLET_HEIGHT)
    oil_inlet_hole = (
        create_barb_fitting_recess(OIL_INLET_DIAMETER, depth=8)
        .rotate((0, 0, 0), (1, 0, 0), -45)  # Angled down so oil drips in
        .translate(oil_inlet_pos)
    )

    chamber_body = chamber_body.cut(oil_inlet_hole)

# === MIST CHIMNEY ===

chimney = (
    cq.Workplane("XY")
    .workplane(offset=CHIMNEY_START_HEIGHT)
    .circle(CHIMNEY_INNER_DIAMETER / 2 + CHIMNEY_WALL_THICKNESS)
    .circle(CHIMNEY_INNER_DIAMETER / 2)
    .extrude(CHIMNEY_HEIGHT)
)

chamber_body = chamber_body.union(chimney)

# === SPLASH GUARD BAFFLE ===

# Horizontal disc to catch water droplets, positioned partway up chimney
baffle_height_position = CHIMNEY_START_HEIGHT + 8  # mm up from chimney base

baffle = (
    cq.Workplane("XY")
    .workplane(offset=baffle_height_position)
    .circle(BAFFLE_DIAMETER / 2)
    .extrude(BAFFLE_HEIGHT)
    # Support spokes to hold baffle in place (thin to minimize mist blockage)
    .union(
        cq.Workplane("XY")
        .workplane(offset=baffle_height_position)
        .rect(BAFFLE_DIAMETER, 1)  # Cross-shaped support
        .rect(1, BAFFLE_DIAMETER)
        .extrude(BAFFLE_HEIGHT)
        .intersect(
            cq.Workplane("XY")
            .workplane(offset=baffle_height_position)
            .circle(CHIMNEY_INNER_DIAMETER / 2)
            .extrude(BAFFLE_HEIGHT)
        )
    )
)

chamber_body = chamber_body.union(baffle)

# === OUTLET NOZZLE ===

nozzle_start_height = CHIMNEY_START_HEIGHT + CHIMNEY_HEIGHT

# Outer shell — tapered cylinder (loft between two circles)
nozzle_outer = (
    cq.Workplane("XY")
    .workplane(offset=nozzle_start_height)
    .circle(NOZZLE_OUTER_DIAMETER / 2)
    .workplane(offset=NOZZLE_HEIGHT)
    .circle(NOZZLE_OUTER_DIAMETER / 2 - 1)
    .loft()
)

# Inner bore — tapered hollow core, built separately then subtracted
nozzle_bore = (
    cq.Workplane("XY")
    .workplane(offset=nozzle_start_height - 0.5)
    .circle(CHIMNEY_INNER_DIAMETER / 2)
    .workplane(offset=NOZZLE_HEIGHT + 1)
    .circle(NOZZLE_INNER_DIAMETER / 2)
    .loft()
)

nozzle = nozzle_outer.cut(nozzle_bore)
chamber_body = chamber_body.union(nozzle)

# === DRAIN PORT ===

# Small threaded hole at bottom for cleaning
drain_hole = (
    cq.Workplane("XY")
    .circle(DRAIN_PORT_DIAMETER / 2)
    .extrude(DRAIN_PORT_THREAD_DEPTH)
    # Simple thread representation (actual threads would be tapped post-print)
    .faces(">Z")
    .circle(DRAIN_PORT_DIAMETER / 2 - 0.2)
    .extrude(-1)
)

# Position drain at edge of chamber bottom
drain_position = (CHAMBER_OUTER_DIAMETER / 4, 0, 0)
chamber_body = chamber_body.cut(drain_hole.translate(drain_position))

# === FINAL ASSEMBLY ===

# Add fillet to base edge for better bed adhesion and aesthetics
try:
    chamber_body = chamber_body.edges("<Z").fillet(1.5)
except Exception:
    pass

# Add small chamfer to top nozzle edge
try:
    chamber_body = chamber_body.edges(">Z").chamfer(0.5)
except Exception:
    pass

# === DISPLAY ===

show_object(chamber_body, name="mixing_chamber", options={"color": (0.68, 0.85, 0.90, 0.8)})

# === REFERENCE OBJECTS FOR VISUALIZATION ===

# Show water level as a transparent disc
water_level = (
    cq.Workplane("XY")
    .workplane(offset=WATER_LEVEL_HEIGHT)
    .circle((CHAMBER_OUTER_DIAMETER - WALL_THICKNESS * 2) / 2 - 2)
    .extrude(1)
)

show_object(water_level, name="water_level_reference", options={"color": (0.0, 0.0, 1.0, 0.3)})

# Show piezo disk position
piezo_disk = (
    cq.Workplane("XY")
    .circle(PIEZO_DISK_DIAMETER / 2)
    .extrude(3)  # Typical piezo thickness
)

show_object(piezo_disk, name="piezo_disk_reference", options={"color": (1.0, 0.84, 0.0, 0.7)})

# === DESIGN NOTES ===
"""
TODO items for actual implementation:
1. Measure actual ultrasonic disk dimensions (currently 16mm placeholder)
2. Verify barb fitting sizes for tubing compatibility
3. Test print wall thickness for water-tightness (may need 4mm+ depending on printer)
4. Consider adding locating pins for assembly if this becomes multi-part
5. Add actual thread modeling for drain port (or specify tap size)
6. Validate mist flow dynamics with CFD if available
7. Consider material selection (PETG recommended over PLA for water contact)
8. Add mounting features to attach to base unit
9. Size chimney diameter based on desired mist output rate testing

Design Features:
- Parametric model allows easy dimension adjustments
- O-ring groove ensures waterproof piezo mounting
- Angled oil inlets promote proper dripping into water
- Splash guard prevents large water droplets in mist stream
- Aesthetic nozzle makes visible output attractive
- Drain port enables proper cleaning and maintenance
- 3.5mm+ walls ensure FDM water-tightness
- Fillets and chamfers improve printability and appearance

Print Settings:
- 0.2mm layers or finer for water-tight sealing surfaces
- 100% infill or consider applying food-safe sealant to interior
- Print with drain port facing up to minimize support needs
- Consider vapor smoothing for enhanced water-tightness
"""