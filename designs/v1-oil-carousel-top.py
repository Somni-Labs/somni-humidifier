"""Essential Oil Bottle Carousel Design v1 - TOP-MOUNTED VERSION.

Top-mounted carousel for the smart humidifier. Bottles screw DOWN into
threaded receivers in a top plate and hang cap-side-down from above. Gravity
feeds oil down through tubes that route to dedicated peristaltic pumps in the base.

This design fixes the V1 issue where bottles hung below the base, making the
unit unstable on tables. Now the bottles are accessible from above and the
base sits flat.

User experience:
  1. Lift the top carousel assembly (or open a hinged lid).
  2. Grab a standard 5ml essential oil bottle (cap already removed).
  3. Screw its neck threads into one of the 5 printed receivers on the
     top surface of the carousel plate.
  4. Done — gravity feeds oil down through tubes to pumps below.
  To swap: lift carousel, unscrew, screw in a new bottle.

Architecture (top to bottom):
  1. CAROUSEL PLATE — flat structural plate that mounts above the base enclosure.
     Bottom surface has tube routing and connection points to base.
  2. THREADED RECEIVERS — 5 printed sockets on the top surface of the plate.
     Each has internal threads matching the bottle neck (18-415 / 18-400).
     A drip-catch basin surrounds the bore to contain leaks during bottle
     swaps. A tube stub protrudes downward through the plate.
  3. BOTTLES — hang inverted from above the plate. The bottle body and label
     face downward and remain fully visible.
  4. TUBE ROUTING — silicone tubes connect each receiver stub (bottom of plate)
     down to the corresponding peristaltic pump in the base below.

Why top-mounted:
  - Base sits flat on table surface — no bottles hanging below.
  - Bottles still gravity-fed downward to pumps.
  - Easy user access — lift lid or remove carousel assembly.
  - Labels face outward and are completely unobstructed.
  - Maintains all benefits of inverted design while fixing stability issue.

Mounting options:
  - Removable: Carousel lifts off entirely for bottle swaps.
  - Hinged: Carousel hinges open like a lid.
  - Sliding: Carousel slides out like a drawer.
  This design supports removable mounting with locating pins.
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Tolerances ---
TOL = 0.3                  # print tolerance per side
WALL = 2.5                 # general wall thickness

# --- Bottle specs (standard 5 ml essential oil) ---
BOTTLE_BODY_DIA = 22.0     # body outer diameter
BOTTLE_HEIGHT = 55.0       # total height including cap
BOTTLE_NECK_OD = 18.0      # neck outer diameter (thread crest)
BOTTLE_NECK_ID = 15.0      # neck inner diameter (bore)
BOTTLE_NECK_LENGTH = 10.0  # threaded portion of neck

# Thread profile — 18-415 (GPI/SPI finish)
THREAD_PITCH = 1.59        # mm per revolution (18-415 standard)
THREAD_DEPTH = 0.8         # mm radial depth of thread
THREAD_STARTS = 1          # single-start thread

# --- Carousel layout ---
BOTTLE_COUNT = 5
# Arc arrangement — bottles fan out in a 180° arc
ARC_RADIUS = 40.0          # mm — center of plate to center of each receiver
ARC_SPAN_DEG = 160.0       # degrees — total arc the 5 positions span

# --- Carousel plate ---
PLATE_THICKNESS = 8.0      # mm — structural plate (thicker for top mounting)
PLATE_MARGIN = 15.0        # mm — extra material beyond outermost receiver

# --- Threaded receiver (protrudes above plate) ---
RECEIVER_OD = BOTTLE_NECK_OD + 2 * WALL  # outer diameter of printed socket
RECEIVER_THREAD_ID = BOTTLE_NECK_OD + 2 * TOL  # internal thread major dia
RECEIVER_LENGTH = BOTTLE_NECK_LENGTH + 3.0  # mm — enough thread engagement + clearance
RECEIVER_HEIGHT = 8.0      # how far receivers protrude above plate surface

# --- Tube stub (hangs down through plate) ---
TUBE_OD = 3.0              # silicone tubing outer diameter
TUBE_ID = 1.5              # silicone tubing inner diameter
TUBE_STUB_OD = TUBE_OD + 1.0  # printed stub outer diameter (press-fit)
TUBE_BORE = TUBE_ID + 0.2  # bore through stub and plate for oil flow
TUBE_STUB_HEIGHT = 6.0     # mm below plate surface — barb for silicone tube

# --- Mounting to base ---
MOUNT_PIN_DIA = 6.0        # locating pins that insert into base receptacles
MOUNT_PIN_HEIGHT = 8.0     # how far pins protrude below plate
MOUNT_PIN_COUNT = 3        # triangular mounting pattern
MOUNT_PIN_RADIUS = ARC_RADIUS + PLATE_MARGIN - 8.0  # near plate edge

# --- O-ring seal (sits at bottom of receiver bore) ---
ORING_ID = 18.0            # matches bottle neck OD
ORING_CS = 2.0             # cross-section diameter
ORING_GROOVE_DEPTH = 1.5   # mm — ~75% of CS for proper compression
ORING_GROOVE_WIDTH = ORING_CS + 0.3  # slightly wider than CS for fit

# --- Drip-catch basin (top surface of plate, around each receiver) ---
DRIP_BASIN_ID = RECEIVER_OD + 1.0   # just outside receiver body
DRIP_BASIN_OD = RECEIVER_OD + 10.0  # outer rim of catch basin
DRIP_BASIN_DEPTH = 2.0              # mm recess into top surface of plate
DRIP_WEEP_DIA = 1.5                 # mm — small hole to drain basin back to bore

# --- Position labels ---
LABEL_FONT_SIZE = 6.0      # mm — height of embossed number
LABEL_DEPTH = 0.6          # mm — extrusion depth (raised text on surface)
LABEL_OFFSET = RECEIVER_OD / 2 + 6.0  # mm — distance from receiver center

# --- Cosmetic ---
FILLET_R = 1.5


# =============================================================================
# GEOMETRY HELPERS
# =============================================================================

def receiver_positions():
    """Return list of (x, y, angle_deg) for each bottle receiver."""
    positions = []
    start = -ARC_SPAN_DEG / 2
    step = ARC_SPAN_DEG / (BOTTLE_COUNT - 1)
    for i in range(BOTTLE_COUNT):
        angle_deg = start + i * step
        angle_rad = math.radians(angle_deg)
        x = ARC_RADIUS * math.sin(angle_rad)   # sin so arc opens toward +Y
        y = ARC_RADIUS * math.cos(angle_rad)
        positions.append((x, y, angle_deg))
    return positions


def mount_pin_positions():
    """Return list of (x, y) for mounting pins in triangular pattern."""
    positions = []
    for i in range(MOUNT_PIN_COUNT):
        angle = i * 2 * math.pi / MOUNT_PIN_COUNT + math.pi / 6  # offset 30°
        px = MOUNT_PIN_RADIUS * math.cos(angle)
        py = MOUNT_PIN_RADIUS * math.sin(angle)
        positions.append((px, py))
    return positions


# =============================================================================
# COMPONENT BUILDERS
# =============================================================================

def create_plate():
    """Structural carousel plate — circular plate that spans all receiver positions."""
    plate_radius = ARC_RADIUS + RECEIVER_OD / 2 + PLATE_MARGIN

    plate = (cq.Workplane("XY")
             .circle(plate_radius)
             .extrude(PLATE_THICKNESS))

    return plate


def create_single_receiver(x, y):
    """One threaded receiver socket, positioned at (x, y) protruding above the
    plate (positive Z). Includes the oil bore down through the plate and the
    tube stub underneath."""

    # --- Receiver body (above plate) ---
    # Solid cylinder protruding above Z=PLATE_THICKNESS
    body = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS))
            .circle(RECEIVER_OD / 2)
            .extrude(RECEIVER_HEIGHT))

    # Hollow out the thread bore
    thread_bore = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS - 1))
                   .circle(RECEIVER_THREAD_ID / 2)
                   .extrude(RECEIVER_HEIGHT + 2))  # through-cut
    body = body.cut(thread_bore)

    # Lead-in chamfer at the top (entry point for bottle)
    try:
        body = body.faces(">Z").chamfer(1.0)
    except Exception:
        pass

    # --- Thread ridges (simplified helical bumps) ---
    thread_ridges = None
    num_ridges = int(RECEIVER_HEIGHT / THREAD_PITCH)
    for r in range(num_ridges):
        z_pos = PLATE_THICKNESS + (r * THREAD_PITCH + THREAD_PITCH / 2)
        ridge = (cq.Workplane("XY", origin=(x, y, z_pos))
                 .circle(RECEIVER_THREAD_ID / 2 + THREAD_DEPTH)
                 .circle(RECEIVER_THREAD_ID / 2)
                 .extrude(THREAD_PITCH * 0.4))  # ridge is 40% of pitch
        if thread_ridges is None:
            thread_ridges = ridge
        else:
            thread_ridges = thread_ridges.union(ridge)

    if thread_ridges is not None:
        body = body.union(thread_ridges)

    # --- O-ring groove (at base of receiver, where bottle shoulder seats) ---
    oring_groove_r = ORING_ID / 2 + ORING_CS / 2  # groove centerline radius
    oring_groove = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS))
                    .circle(oring_groove_r + ORING_GROOVE_WIDTH / 2)
                    .circle(oring_groove_r - ORING_GROOVE_WIDTH / 2)
                    .extrude(ORING_GROOVE_DEPTH))
    body = body.cut(oring_groove)

    # --- Drip-catch basin (top surface of plate around receiver) ---
    drip_basin = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS))
                  .circle(DRIP_BASIN_OD / 2)
                  .circle(DRIP_BASIN_ID / 2)
                  .extrude(DRIP_BASIN_DEPTH))
    body = body.cut(drip_basin)

    # Weep hole — lets captured oil drain back into the bore
    weep_offset_r = (DRIP_BASIN_ID + DRIP_BASIN_OD) / 4  # midway in basin
    weep_hole = (cq.Workplane("XY", origin=(x + weep_offset_r, y, PLATE_THICKNESS + DRIP_BASIN_DEPTH + 1))
                 .circle(DRIP_WEEP_DIA / 2)
                 .extrude(-DRIP_BASIN_DEPTH - PLATE_THICKNESS - TUBE_STUB_HEIGHT - 2))
    body = body.cut(weep_hole)

    # --- Oil bore (through the plate) ---
    bore = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS + 1))
            .circle(TUBE_BORE / 2)
            .extrude(-PLATE_THICKNESS - TUBE_STUB_HEIGHT - 2))
    body = body.cut(bore)

    # --- Tube stub (below plate, barb for silicone tube) ---
    stub = (cq.Workplane("XY", origin=(x, y, 0))
            .circle(TUBE_STUB_OD / 2)
            .extrude(-TUBE_STUB_HEIGHT))

    # Barb ring near bottom of stub for tube retention
    barb = (cq.Workplane("XY", origin=(x, y, -TUBE_STUB_HEIGHT * 0.65))
            .circle(TUBE_STUB_OD / 2 + 0.4)
            .circle(TUBE_STUB_OD / 2)
            .extrude(-1.0))
    stub = stub.union(barb)

    # Bore through the stub
    stub_bore = (cq.Workplane("XY", origin=(x, y, 1))
                 .circle(TUBE_BORE / 2)
                 .extrude(-TUBE_STUB_HEIGHT - 2))
    stub = stub.cut(stub_bore)

    body = body.union(stub)

    return body


def create_all_receivers():
    """Create all 5 threaded receivers and merge them."""
    receivers = None
    for x, y, _angle in receiver_positions():
        r = create_single_receiver(x, y)
        if receivers is None:
            receivers = r
        else:
            receivers = receivers.union(r)
    return receivers


def create_mounting_pins():
    """Locating pins that insert into receptacles in the base."""
    pins = None
    for px, py in mount_pin_positions():
        pin = (cq.Workplane("XY", origin=(px, py, 0))
               .circle(MOUNT_PIN_DIA / 2)
               .extrude(-MOUNT_PIN_HEIGHT))

        # Chamfer pin tips for easier insertion
        try:
            pin = pin.faces("<Z").chamfer(0.8)
        except Exception:
            pass

        if pins is None:
            pins = pin
        else:
            pins = pins.union(pin)
    return pins


def create_position_labels():
    """Create raised position numbers (1-5) on the plate top surface near
    each receiver using simple dot patterns."""
    labels = None
    positions = receiver_positions()

    for i, (rx, ry, angle_deg) in enumerate(positions):
        count = i + 1  # positions 1-5
        # Place dots in a radial line outward from the receiver center
        angle_rad = math.radians(angle_deg)
        base_x = rx + LABEL_OFFSET * math.sin(angle_rad)
        base_y = ry + LABEL_OFFSET * math.cos(angle_rad)

        for d in range(count):
            # Stack dots along the tangent direction
            tangent_x = math.cos(angle_rad)
            tangent_y = -math.sin(angle_rad)
            offset = (d - (count - 1) / 2) * 3.0  # 3mm between dots

            dot_x = base_x + offset * tangent_x
            dot_y = base_y + offset * tangent_y

            dot = (cq.Workplane("XY", origin=(dot_x, dot_y, PLATE_THICKNESS))
                   .circle(1.2)
                   .extrude(LABEL_DEPTH))

            if labels is None:
                labels = dot
            else:
                labels = labels.union(dot)

    return labels


def create_reference_bottle(x, y):
    """Ghost bottle hanging below a receiver for visualisation."""
    # Bottle body (inverted — neck at top, base at bottom)
    neck_h = BOTTLE_NECK_LENGTH
    body_h = BOTTLE_HEIGHT - neck_h

    # Neck (threads into receiver, starts at plate surface)
    neck = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS + RECEIVER_HEIGHT))
            .circle(BOTTLE_NECK_OD / 2)
            .extrude(neck_h))

    # Shoulder taper
    shoulder = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS + RECEIVER_HEIGHT + neck_h))
                .circle(BOTTLE_NECK_OD / 2)
                .workplane(offset=3)
                .circle(BOTTLE_BODY_DIA / 2)
                .loft())

    # Main body
    body = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS + RECEIVER_HEIGHT + neck_h + 3))
            .circle(BOTTLE_BODY_DIA / 2)
            .extrude(body_h - 3))

    bottle = neck.union(shoulder).union(body)
    return bottle


# =============================================================================
# ASSEMBLY
# =============================================================================

def assemble_oil_carousel_top():
    """Full top-mounted carousel: plate + receivers + mounting pins + labels."""
    plate = create_plate()
    receivers = create_all_receivers()
    pins = create_mounting_pins()
    labels = create_position_labels()

    assembly = plate.union(receivers)

    if pins:
        assembly = assembly.union(pins)

    if labels:
        assembly = assembly.union(labels)

    # Cosmetic fillets on plate rim
    try:
        assembly = assembly.faces("|Z").edges().fillet(FILLET_R)
    except Exception:
        pass

    return assembly


# =============================================================================
# RENDER
# =============================================================================

oil_carousel_top = assemble_oil_carousel_top()
show_object(oil_carousel_top, name="oil_carousel_top_complete")

# Show ghost bottles in all positions for scale
positions = receiver_positions()
for i, (x, y, _a) in enumerate(positions):
    bottle = create_reference_bottle(x, y)
    show_object(bottle, name=f"bottle_top_{i+1}",
               options={"color": (1.0, 0.55, 0.0, 0.45)})

# Exploded single receiver for detail review
single_receiver = create_single_receiver(0, 0)
show_object(single_receiver.translate((120, 0, 0)), name="single_receiver_top_detail",
           options={"color": (0.56, 0.93, 0.56, 0.8)})

# Plate only (for print orientation reference)
show_object(create_plate().translate((-120, 0, 0)), name="plate_top_only",
           options={"color": (0.68, 0.85, 0.90, 0.5)})

# Print summary
print("=" * 60)
print("Essential Oil Bottle Carousel v1 — TOP-MOUNTED DESIGN")
print("=" * 60)
print(f"  Bottles: {BOTTLE_COUNT} × standard 5 ml (hanging from above)")
print(f"  Arrangement: {ARC_SPAN_DEG:.0f}° arc, R={ARC_RADIUS:.0f} mm")
print(f"  Plate diameter: ~{2 * (ARC_RADIUS + RECEIVER_OD/2 + PLATE_MARGIN):.0f} mm")
print(f"  Plate thickness: {PLATE_THICKNESS:.1f} mm")
print(f"  Receiver OD: {RECEIVER_OD:.1f} mm, height: {RECEIVER_HEIGHT:.1f} mm")
print(f"  Thread: {BOTTLE_NECK_OD:.0f}-415, pitch {THREAD_PITCH:.2f} mm")
print(f"  Mounting: {MOUNT_PIN_COUNT} × ø{MOUNT_PIN_DIA:.0f} mm locating pins")
print(f"  Tube stubs: {TUBE_STUB_OD:.1f} mm OD, {TUBE_STUB_HEIGHT:.0f} mm below plate")
print()
print("Benefits of top mounting:")
print("  ✓ Base sits flat on table (no bottles hanging below)")
print("  ✓ Bottles still gravity-fed downward")
print("  ✓ Easy user access from above")
print("  ✓ Labels fully visible")
print("  ✓ Removable for maintenance")
print()
print("User workflow:")
print("  1. Lift carousel assembly")
print("  2. Remove bottle cap")
print("  3. Screw bottle neck down into receiver (o-ring seals)")
print("  4. Lower carousel back onto base")
print("  5. Oil gravity-feeds down through tubes to pumps")