"""Smart Humidifier — Full Assembly View (V1).

Unified rendering of all four humidifier components in their correct
spatial positions so you can see how they fit together:

  1. Base enclosure         — dark gray, semi-transparent
  2. Mixing chamber         — light blue, sits on the bund inside the base
  3. Mist chimney           — light green, stacks on top of the mixing chamber
  4. Oil carousel + bottles — tan plate with amber ghost bottles, hangs below

KNOWN DIMENSIONAL CONFLICTS (visible in the assembly):
  - Mixing chamber OD (80mm) overflows the base's reserved footprint (70mm)
    by 5mm per side. The next revision needs to reconcile these.
  - Chimney snap ring (50mm) is wider than the mixing chamber's chimney
    stub (~40mm OD). Interface redesign needed.
  - These mismatches are LEFT VISIBLE so you can see what needs fixing.

Each component is built with simplified geometry (no internal cable
channels, tube routing, or small cosmetic features) to keep render time
reasonable. For full detail, open the individual component files.

Loadable by cadquery-server via show_object().
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object


# =============================================================================
# CONSTANTS — FROM v1-humidifier-base.py
# =============================================================================

# Tolerances & shell
TOL = 0.4
WALL = 3.0
WALL_THIN = 1.8
FILLET_R = 4.0

# Overall base
BASE_W = 230
BASE_D = 210
BASE_H = 55
FLOOR_H = 3.0

# Bund
BUND_H = 28
BUND_WALL = 4
BUND_LIP = 2
DRIP_SLOT_W = 14
DRIP_SLOT_H = 4

# Electronics bay
ELEC_BAY_D = 70

# Derived layout
BUND_TOP_Z = FLOOR_H + BUND_H
BUND_INNER_W = BASE_W - WALL * 2
BUND_INNER_D = BASE_D - WALL * 2 - ELEC_BAY_D - WALL_THIN
REAR_Y = BASE_D / 2
FRONT_Y = -BASE_D / 2
ELEC_BAY_CENTER_Y = REAR_Y - WALL - ELEC_BAY_D / 2

# Apollo dock
APOLLO_W = 95
APOLLO_D = 95
APOLLO_CRADLE_DEPTH = 35
APOLLO_NOTCH_W = 25
APOLLO_NOTCH_H = 18
APOLLO_HOSE_DIA = 14
APOLLO_CENTER_X = -BASE_W / 2 + WALL + APOLLO_W / 2 + TOL + 4
APOLLO_CENTER_Y = -BASE_D / 2 + WALL + APOLLO_D / 2 + TOL + 4

# Mixing chamber footprint on bund
MIX_CHAMBER_DIA = 70      # base's reserved size (NOTE: actual chamber is 80mm)
MIX_OUTLET_DIA = 22
MIX_CENTER_X = (APOLLO_CENTER_X + APOLLO_W / 2 + MIX_CHAMBER_DIA / 2 + 18)
MIX_CENTER_Y = APOLLO_CENTER_Y + 8

# Pumps
PUMP_COUNT = 5
PUMP_ARC_R = 40
PUMP_ARC_SWEEP_DEG = 80
PUMP_BODY_DIA = 32
PUMP_MOUNT_DEPTH = 18

# Rubber feet
FOOT_DIA = 12
FOOT_DEPTH = 1.8
FOOT_INSET = 16


# =============================================================================
# CONSTANTS — FROM v1-mixing-chamber.py
# =============================================================================

CHAMBER_OUTER_DIAMETER = 80   # NOTE: 10mm wider than base's reserved 70mm
CHAMBER_HEIGHT = 60
CHAMBER_WALL_THICKNESS = 3.5

# Oil inlets
OIL_INLET_COUNT = 5
OIL_INLET_DIAMETER = 3
OIL_INLET_HEIGHT = 20
OIL_INLET_RADIUS = (CHAMBER_OUTER_DIAMETER - CHAMBER_WALL_THICKNESS * 2) / 2 - 5

# Internal chimney stub (part of mixing chamber)
MC_CHIMNEY_ID = 35
MC_CHIMNEY_WALL = 2.5
MC_CHIMNEY_HEIGHT = 30
MC_CHIMNEY_START = 17    # WATER_LEVEL_HEIGHT + 5

# Drain
DRAIN_PORT_DIAMETER = 4
DRAIN_PORT_THREAD_DEPTH = 6

# Nozzle (top of mixing chamber's internal chimney)
MC_NOZZLE_OUTER_DIA = MC_CHIMNEY_ID + MC_CHIMNEY_WALL * 2 + 2
MC_NOZZLE_INNER_DIA = MC_CHIMNEY_ID - 2
MC_NOZZLE_HEIGHT = 8


# =============================================================================
# CONSTANTS — FROM v1-mist-chimney.py
# =============================================================================

CHIMNEY_INNER_DIAMETER = 35.0
CHIMNEY_OUTER_DIAMETER = 42.0
CHIMNEY_HEIGHT = 70.0
CHIMNEY_WALL_THICKNESS = 3.5
NOZZLE_DIAMETER = 25.0
NOZZLE_HEIGHT = 15.0
SNAP_RING_DIAMETER = 50.0
SNAP_RING_HEIGHT = 8.0
SNAP_GROOVE_WIDTH = 2.0
SNAP_GROOVE_DEPTH = 1.5
DRIP_LIP_INWARD_CURVE = 2.0
CHIMNEY_FILLET_RADIUS = 3.0


# =============================================================================
# CONSTANTS — FROM v1-oil-carousel.py
# =============================================================================

CAROUSEL_TOL = 0.3
CAROUSEL_WALL = 2.5

BOTTLE_BODY_DIA = 22.0
BOTTLE_HEIGHT = 55.0
BOTTLE_NECK_OD = 18.0
BOTTLE_NECK_LENGTH = 10.0

THREAD_PITCH = 1.59
THREAD_DEPTH = 0.8

BOTTLE_COUNT = 5
ARC_RADIUS = 40.0
ARC_SPAN_DEG = 160.0

PLATE_THICKNESS = 5.0
PLATE_MARGIN = 15.0

RECEIVER_OD = BOTTLE_NECK_OD + 2 * CAROUSEL_WALL
RECEIVER_THREAD_ID = BOTTLE_NECK_OD + 2 * CAROUSEL_TOL
RECEIVER_LENGTH = BOTTLE_NECK_LENGTH + 3.0

TUBE_OD = 3.0
TUBE_ID = 1.5
TUBE_STUB_OD = TUBE_OD + 1.0
TUBE_BORE = TUBE_ID + 0.2
TUBE_STUB_HEIGHT = 6.0

ORING_ID = 18.0
ORING_CS = 2.0
ORING_GROOVE_DEPTH = 1.5
ORING_GROOVE_WIDTH = ORING_CS + 0.3

DRIP_BASIN_ID = RECEIVER_OD + 1.0
DRIP_BASIN_OD = RECEIVER_OD + 10.0
DRIP_BASIN_DEPTH = 2.0
DRIP_WEEP_DIA = 1.5


# =============================================================================
# HELPERS
# =============================================================================

def pump_positions():
    """5 pump positions on an arc in front of the mixing chamber."""
    cx, cy = MIX_CENTER_X, MIX_CENTER_Y
    sweep = math.radians(PUMP_ARC_SWEEP_DEG)
    base_angle = -math.pi / 2
    out = []
    for i in range(PUMP_COUNT):
        t = (i / (PUMP_COUNT - 1)) - 0.5
        a = base_angle + t * sweep
        px = cx + PUMP_ARC_R * math.cos(a)
        py = cy + PUMP_ARC_R * math.sin(a)
        out.append((px, py))
    return out


def carousel_receiver_positions():
    """5 bottle receiver positions on the carousel arc."""
    positions = []
    start = -ARC_SPAN_DEG / 2
    step = ARC_SPAN_DEG / (BOTTLE_COUNT - 1)
    for i in range(BOTTLE_COUNT):
        angle_deg = start + i * step
        angle_rad = math.radians(angle_deg)
        x = ARC_RADIUS * math.sin(angle_rad)
        y = ARC_RADIUS * math.cos(angle_rad)
        positions.append((x, y, angle_deg))
    return positions


# =============================================================================
# BUILD: BASE (simplified — outer shell + bund + key features)
# =============================================================================

def build_base_simplified():
    """Simplified base: outer shell, bund, Apollo dock, pump pockets, feet.
    Omits cable channels, vent slots, ESP32/MOSFET pockets, BME280 mount."""

    # Outer shell
    base = (
        cq.Workplane("XY")
        .box(BASE_W, BASE_D, BASE_H, centered=[True, True, False])
    )
    base = base.edges("|Z").fillet(FILLET_R)

    # Hollow interior
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .box(BASE_W - WALL * 2, BASE_D - WALL * 2, BASE_H - FLOOR_H + 1,
             centered=[True, True, False])
    )
    base = base.cut(cavity)

    # Bund (raised platform)
    bund_y_center = -BASE_D / 2 + WALL + BUND_INNER_D / 2
    bund = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(0, bund_y_center)
        .box(BUND_INNER_W, BUND_INNER_D, BUND_H,
             centered=[True, True, False])
    )
    base = base.union(bund)

    # Bund spill lip
    bund_lip_outer = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z)
        .center(0, bund_y_center)
        .box(BUND_INNER_W, BUND_INNER_D, BUND_LIP,
             centered=[True, True, False])
    )
    bund_lip_inner = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - 0.1)
        .center(0, bund_y_center)
        .box(BUND_INNER_W - BUND_WALL * 2, BUND_INNER_D - BUND_WALL * 2,
             BUND_LIP + 0.2, centered=[True, True, False])
    )
    base = base.union(bund_lip_outer).cut(bund_lip_inner)

    # Drip slot
    drip_slot = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - DRIP_SLOT_H)
        .center(0, -BASE_D / 2)
        .box(DRIP_SLOT_W, WALL * 4, DRIP_SLOT_H,
             centered=[True, True, False])
    )
    base = base.cut(drip_slot)

    # Electronics bay divider rib
    bay_rear_y = bund_y_center + BUND_INNER_D / 2
    rib = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(0, bay_rear_y + WALL_THIN / 2)
        .box(BUND_INNER_W, WALL_THIN, BASE_H - FLOOR_H - WALL - 6,
             centered=[True, True, False])
    )
    base = base.union(rib)

    # Apollo dock pocket
    apollo_pocket = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - APOLLO_CRADLE_DEPTH)
        .center(APOLLO_CENTER_X, APOLLO_CENTER_Y)
        .rect(APOLLO_W + TOL * 2, APOLLO_D + TOL * 2)
        .extrude(APOLLO_CRADLE_DEPTH + BUND_LIP + 1)
    )
    base = base.cut(apollo_pocket)

    # Mixing chamber riser hole
    mix_riser = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - 2)
        .center(MIX_CENTER_X, MIX_CENTER_Y)
        .circle(MIX_OUTLET_DIA / 2)
        .extrude(BUND_LIP + 4)
    )
    base = base.cut(mix_riser)

    # Pump pockets (simplified — just the circular bores)
    for px, py in pump_positions():
        body_pocket = (
            cq.Workplane("XY")
            .workplane(offset=BUND_TOP_Z - PUMP_MOUNT_DEPTH)
            .center(px, py)
            .circle(PUMP_BODY_DIA / 2 + TOL)
            .extrude(PUMP_MOUNT_DEPTH + 1)
        )
        base = base.cut(body_pocket)

    # Rubber feet
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

    return base


# =============================================================================
# BUILD: MIXING CHAMBER (simplified — outer shell + chimney stub + inlets)
# =============================================================================

def build_mixing_chamber_simplified():
    """Simplified mixing chamber: outer shell, oil inlet holes, chimney stub.
    Omits piezo mount, baffle, nozzle, drain port."""

    # Outer shell — hollow cylinder
    chamber = (
        cq.Workplane("XY")
        .circle(CHAMBER_OUTER_DIAMETER / 2)
        .extrude(CHAMBER_HEIGHT)
        .faces(">Z")
        .circle((CHAMBER_OUTER_DIAMETER - CHAMBER_WALL_THICKNESS * 2) / 2)
        .cutThruAll()
    )

    # Oil inlet holes (5x around perimeter)
    for i in range(OIL_INLET_COUNT):
        angle_rad = math.radians(i * 360 / OIL_INLET_COUNT)
        ix = OIL_INLET_RADIUS * math.cos(angle_rad)
        iy = OIL_INLET_RADIUS * math.sin(angle_rad)
        inlet = (
            cq.Workplane("XY")
            .workplane(offset=OIL_INLET_HEIGHT)
            .center(ix, iy)
            .circle(OIL_INLET_DIAMETER / 2)
            .extrude(CHAMBER_WALL_THICKNESS + 2)
        )
        chamber = chamber.cut(inlet)

    # Internal chimney stub
    chimney_stub = (
        cq.Workplane("XY")
        .workplane(offset=MC_CHIMNEY_START)
        .circle(MC_CHIMNEY_ID / 2 + MC_CHIMNEY_WALL)
        .circle(MC_CHIMNEY_ID / 2)
        .extrude(MC_CHIMNEY_HEIGHT)
    )
    chamber = chamber.union(chimney_stub)

    # Nozzle at top of chimney stub
    nozzle_z = MC_CHIMNEY_START + MC_CHIMNEY_HEIGHT
    nozzle = (
        cq.Workplane("XY")
        .workplane(offset=nozzle_z)
        .circle(MC_NOZZLE_OUTER_DIA / 2)
        .extrude(MC_NOZZLE_HEIGHT)
    )
    nozzle_bore = (
        cq.Workplane("XY")
        .workplane(offset=nozzle_z - 0.5)
        .circle(MC_NOZZLE_INNER_DIA / 2)
        .extrude(MC_NOZZLE_HEIGHT + 1)
    )
    nozzle = nozzle.cut(nozzle_bore)
    chamber = chamber.union(nozzle)

    return chamber


# =============================================================================
# BUILD: MIST CHIMNEY (full — it's already simple)
# =============================================================================

def build_mist_chimney():
    """Standalone mist chimney with snap ring, nozzle, and flow guide."""

    # Main chimney tube
    chimney = (
        cq.Workplane("XY")
        .circle(CHIMNEY_OUTER_DIAMETER / 2)
        .circle(CHIMNEY_INNER_DIAMETER / 2)
        .extrude(CHIMNEY_HEIGHT)
    )

    # Snap connection ring (below chimney)
    snap_ring = (
        cq.Workplane("XY")
        .circle(SNAP_RING_DIAMETER / 2)
        .circle(SNAP_RING_DIAMETER / 2 - CHIMNEY_WALL_THICKNESS)
        .extrude(SNAP_RING_HEIGHT)
    )
    groove_pos = SNAP_RING_HEIGHT * 0.7
    snap_groove = (
        cq.Workplane("XY", origin=(0, 0, groove_pos))
        .circle(SNAP_RING_DIAMETER / 2 - SNAP_GROOVE_DEPTH)
        .circle(SNAP_RING_DIAMETER / 2 - SNAP_GROOVE_DEPTH - SNAP_GROOVE_WIDTH)
        .extrude(SNAP_GROOVE_WIDTH)
    )
    snap_ring = snap_ring.cut(snap_groove)
    try:
        snap_ring = snap_ring.faces("<Z").chamfer(1.0)
    except Exception:
        pass
    snap_ring = snap_ring.translate((0, 0, -SNAP_RING_HEIGHT))

    # Directional nozzle
    nozzle_z = CHIMNEY_HEIGHT
    nozzle_body = (
        cq.Workplane("XY", origin=(0, 0, nozzle_z))
        .circle(NOZZLE_DIAMETER / 2)
        .extrude(NOZZLE_HEIGHT)
    )
    nozzle_opening = (
        cq.Workplane("XY", origin=(0, 0, nozzle_z))
        .circle(NOZZLE_DIAMETER * 0.4)
        .extrude(NOZZLE_HEIGHT + 2)
    )
    nozzle_body = nozzle_body.cut(nozzle_opening)
    try:
        nozzle_body = nozzle_body.faces(">Z").chamfer(DRIP_LIP_INWARD_CURVE)
    except Exception:
        pass

    # Combine
    assembly = chimney.union(snap_ring).union(nozzle_body)

    try:
        assembly = assembly.edges("|Z").fillet(CHIMNEY_FILLET_RADIUS * 0.5)
    except Exception:
        pass

    return assembly


# =============================================================================
# BUILD: OIL CAROUSEL (simplified — plate + receivers, no routing channels)
# =============================================================================

def build_oil_carousel_simplified():
    """Carousel plate with threaded receivers. Omits tube routing channels,
    mounting holes, and position labels."""

    plate_radius = ARC_RADIUS + RECEIVER_OD / 2 + PLATE_MARGIN
    plate = (
        cq.Workplane("XY")
        .circle(plate_radius)
        .extrude(PLATE_THICKNESS)
    )

    # Build all receivers
    for x, y, _angle in carousel_receiver_positions():
        # Receiver body (hangs below plate in -Z)
        body = (
            cq.Workplane("XY", origin=(x, y, 0))
            .circle(RECEIVER_OD / 2)
            .extrude(-RECEIVER_LENGTH)
        )
        # Thread bore
        bore = (
            cq.Workplane("XY", origin=(x, y, 0))
            .circle(RECEIVER_THREAD_ID / 2)
            .extrude(-RECEIVER_LENGTH - 1)
        )
        body = body.cut(bore)

        # O-ring groove
        oring_r = ORING_ID / 2 + ORING_CS / 2
        oring = (
            cq.Workplane("XY", origin=(x, y, 0))
            .circle(oring_r + ORING_GROOVE_WIDTH / 2)
            .circle(oring_r - ORING_GROOVE_WIDTH / 2)
            .extrude(-ORING_GROOVE_DEPTH)
        )
        body = body.cut(oring)

        # Oil bore through plate
        oil_bore = (
            cq.Workplane("XY", origin=(x, y, -1))
            .circle(TUBE_BORE / 2)
            .extrude(PLATE_THICKNESS + TUBE_STUB_HEIGHT + 2)
        )
        body = body.cut(oil_bore)

        # Tube stub above plate
        stub = (
            cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS))
            .circle(TUBE_STUB_OD / 2)
            .extrude(TUBE_STUB_HEIGHT)
        )
        stub_bore = (
            cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS - 1))
            .circle(TUBE_BORE / 2)
            .extrude(TUBE_STUB_HEIGHT + 2)
        )
        stub = stub.cut(stub_bore)

        plate = plate.union(body).union(stub)

    return plate


def build_ghost_bottles():
    """Reference bottles hanging below the carousel for visualization."""
    bottles = None
    for x, y, _angle in carousel_receiver_positions():
        neck_h = BOTTLE_NECK_LENGTH
        body_h = BOTTLE_HEIGHT - neck_h

        neck = (
            cq.Workplane("XY", origin=(x, y, -RECEIVER_LENGTH))
            .circle(BOTTLE_NECK_OD / 2)
            .extrude(-neck_h)
        )
        shoulder = (
            cq.Workplane("XY", origin=(x, y, -RECEIVER_LENGTH - neck_h))
            .circle(BOTTLE_NECK_OD / 2)
            .workplane(offset=-3)
            .circle(BOTTLE_BODY_DIA / 2)
            .loft()
        )
        body = (
            cq.Workplane("XY", origin=(x, y, -RECEIVER_LENGTH - neck_h - 3))
            .circle(BOTTLE_BODY_DIA / 2)
            .extrude(-(body_h - 3))
        )
        bottle = neck.union(shoulder).union(body)

        if bottles is None:
            bottles = bottle
        else:
            bottles = bottles.union(bottle)

    return bottles


# =============================================================================
# ASSEMBLY — position each component in the base's coordinate system
# =============================================================================

# Build all components at their local origins
base = build_base_simplified()
mixing_chamber = build_mixing_chamber_simplified()
mist_chimney = build_mist_chimney()
oil_carousel = build_oil_carousel_simplified()
ghost_bottles = build_ghost_bottles()

# Position the mixing chamber on the bund
# Chamber is built at origin (Z=0..CHAMBER_HEIGHT)
# Move it so Z=0 aligns with the bund top surface
mixing_chamber = mixing_chamber.translate((
    MIX_CENTER_X,
    MIX_CENTER_Y,
    BUND_TOP_Z
))

# Position the chimney on top of the mixing chamber
# The chimney's snap ring extends below Z=0 by SNAP_RING_HEIGHT.
# The chimney body starts at Z=0.
# Place it so the snap ring sits at the top of the mixing chamber.
chimney_z = BUND_TOP_Z + CHAMBER_HEIGHT
mist_chimney = mist_chimney.translate((
    MIX_CENTER_X,
    MIX_CENTER_Y,
    chimney_z
))

# Position the oil carousel under the base
# The carousel plate top surface should be roughly at the base floor (Z=0).
# The receivers and bottles hang below. Center it under the mixing chamber
# area where the pump tube drops are.
carousel_z = 0  # plate top at base floor level
oil_carousel = oil_carousel.translate((
    MIX_CENTER_X,
    MIX_CENTER_Y,
    carousel_z - PLATE_THICKNESS
))
ghost_bottles = ghost_bottles.translate((
    MIX_CENTER_X,
    MIX_CENTER_Y,
    carousel_z - PLATE_THICKNESS
))


# =============================================================================
# DISPLAY — each component with a distinct color
# =============================================================================

show_object(base, name="base_enclosure",
            options={"color": (0.2, 0.22, 0.25, 0.55)})

show_object(mixing_chamber, name="mixing_chamber",
            options={"color": (0.68, 0.85, 0.90, 0.6)})

show_object(mist_chimney, name="mist_chimney",
            options={"color": (0.56, 0.93, 0.56, 0.55)})

show_object(oil_carousel, name="oil_carousel_plate",
            options={"color": (0.85, 0.82, 0.78, 0.6)})

show_object(ghost_bottles, name="oil_bottles",
            options={"color": (1.0, 0.55, 0.0, 0.35)})


# =============================================================================
# ASSEMBLY SUMMARY
# =============================================================================

print("=" * 60)
print("Smart Humidifier — Full Assembly V1")
print("=" * 60)
print()
print("Component positions (X, Y, Z bottom):")
print(f"  Base:            (0, 0, 0)  — {BASE_W}×{BASE_D}×{BASE_H}mm")
print(f"  Mixing chamber:  ({MIX_CENTER_X:.1f}, {MIX_CENTER_Y:.1f}, {BUND_TOP_Z})"
      f"  — ø{CHAMBER_OUTER_DIAMETER}×{CHAMBER_HEIGHT}mm")
print(f"  Mist chimney:    ({MIX_CENTER_X:.1f}, {MIX_CENTER_Y:.1f}, {chimney_z})"
      f"  — ø{CHIMNEY_OUTER_DIAMETER}×{CHIMNEY_HEIGHT + NOZZLE_HEIGHT:.0f}mm")
print(f"  Oil carousel:    ({MIX_CENTER_X:.1f}, {MIX_CENTER_Y:.1f},"
      f" {carousel_z - PLATE_THICKNESS})"
      f"  — ø{2*(ARC_RADIUS + RECEIVER_OD/2 + PLATE_MARGIN):.0f}×{PLATE_THICKNESS}mm plate")
print()
print("KNOWN CONFLICTS:")
print(f"  ⚠ Chamber OD ({CHAMBER_OUTER_DIAMETER}mm) > base footprint"
      f" ({MIX_CHAMBER_DIA}mm) — overflows by"
      f" {(CHAMBER_OUTER_DIAMETER - MIX_CHAMBER_DIA)/2:.0f}mm/side")
print(f"  ⚠ Chimney snap ring ({SNAP_RING_DIAMETER}mm) > chamber chimney stub"
      f" (~{MC_CHIMNEY_ID + MC_CHIMNEY_WALL*2}mm OD)")
total_height = chimney_z + CHIMNEY_HEIGHT + NOZZLE_HEIGHT
total_depth = PLATE_THICKNESS + RECEIVER_LENGTH + BOTTLE_HEIGHT
print()
print(f"Total height above floor:  {total_height:.0f}mm"
      f" (base {BASE_H} + chamber {CHAMBER_HEIGHT} + chimney"
      f" {CHIMNEY_HEIGHT + NOZZLE_HEIGHT:.0f})")
print(f"Total depth below floor:   {total_depth:.0f}mm"
      f" (plate {PLATE_THICKNESS} + receiver {RECEIVER_LENGTH:.0f}"
      f" + bottle {BOTTLE_HEIGHT:.0f})")
