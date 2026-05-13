"""Essential Oil Bottle Carousel Design v1.

Inverted-bottle carousel for the smart humidifier. Bottles screw UP into
threaded receivers in a base plate and hang cap-side-up beneath it. Gravity
feeds oil down through a short tube stub in each receiver, into silicone
tubing that routes to a dedicated peristaltic pump.

User experience:
  1. Grab a standard 5ml essential oil bottle (cap already removed).
  2. Screw its neck threads into one of the 5 printed receivers on the
     underside of the carousel plate.
  3. Done — gravity feeds oil, the pump meters it.
  To swap: unscrew, screw in a new bottle.

Architecture (top to bottom):
  1. CAROUSEL PLATE — flat structural plate that mounts inside the enclosure.
     Top surface has tube routing channels leading to pump headers.
  2. THREADED RECEIVERS — 5 printed sockets on the underside of the plate.
     Each has internal threads matching the bottle neck (18-415 / 18-400).
     A short tube stub protrudes upward through the plate into a routing
     channel on the top surface.
  3. BOTTLES — hang inverted beneath the plate. The bottle body and label
     face downward and remain fully visible.
  4. TUBE ROUTING — silicone tubes connect each receiver stub (top of plate)
     to the corresponding peristaltic pump elsewhere in the enclosure.

Why inverted:
  - Gravity feeds oil to the pump — no dip tube reaching the bottle bottom.
  - Screw-in mounting = secure, vibration-proof, one-handed swap.
  - Labels face outward and are completely unobstructed.
  - No wells, collars, or windows needed — simpler to print.

Standard 5ml Essential Oil Bottle Specifications:
  - Body diameter: ~22 mm
  - Total height:  ~55 mm (with cap)
  - Neck OD:       ~18 mm
  - Neck thread:   18-415 (1 start, 1.59 mm pitch) — verify with calipers
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
# TODO: Measure actual bottles with calipers and update
BOTTLE_BODY_DIA = 22.0     # body outer diameter
BOTTLE_HEIGHT = 55.0       # total height including cap
BOTTLE_NECK_OD = 18.0      # neck outer diameter (thread crest)
BOTTLE_NECK_ID = 15.0      # neck inner diameter (bore)
BOTTLE_NECK_LENGTH = 10.0  # threaded portion of neck

# Thread profile — 18-415 (GPI/SPI finish)
# "18" = 18 mm closure diameter, "415" = 4 turns, 15° bevel
# TODO: Verify thread pitch with actual bottles
THREAD_PITCH = 1.59        # mm per revolution (18-415 standard)
THREAD_DEPTH = 0.8         # mm radial depth of thread
THREAD_STARTS = 1          # single-start thread

# --- Carousel layout ---
BOTTLE_COUNT = 5
# Arc arrangement — bottles fan out in a 180° arc
ARC_RADIUS = 40.0          # mm — center of plate to center of each receiver
ARC_SPAN_DEG = 160.0       # degrees — total arc the 5 positions span

# --- Carousel plate ---
PLATE_THICKNESS = 5.0      # mm — structural plate
PLATE_MARGIN = 15.0        # mm — extra material beyond outermost receiver

# --- Threaded receiver (hangs below plate) ---
RECEIVER_OD = BOTTLE_NECK_OD + 2 * WALL  # outer diameter of printed socket
RECEIVER_THREAD_ID = BOTTLE_NECK_OD + 2 * TOL  # internal thread major dia
RECEIVER_LENGTH = BOTTLE_NECK_LENGTH + 3.0  # mm — enough thread engagement + clearance
RECEIVER_CHAMFER = 1.0     # lead-in chamfer so the bottle starts easily

# --- Tube stub (pokes up through plate) ---
TUBE_OD = 3.0              # silicone tubing outer diameter
TUBE_ID = 1.5              # silicone tubing inner diameter
TUBE_STUB_OD = TUBE_OD + 1.0  # printed stub outer diameter (press-fit)
TUBE_BORE = TUBE_ID + 0.2  # bore through stub and plate for oil flow
TUBE_STUB_HEIGHT = 6.0     # mm above plate surface — barb for silicone tube

# --- Tube routing (top surface of plate) ---
ROUTE_CHANNEL_WIDTH = TUBE_OD + 1.5   # channel wide enough for tube + clearance
ROUTE_CHANNEL_DEPTH = 2.5             # mm — recessed into plate top
ROUTE_EXIT_Y = -(ARC_RADIUS + PLATE_MARGIN + 5.0)  # where tubes exit toward pumps

# --- Mounting ---
MOUNT_HOLE_DIA = 3.2       # M3 clearance
MOUNT_HOLE_COUNT = 4
MOUNT_HOLE_RADIUS = ARC_RADIUS + PLATE_MARGIN - 5.0  # near plate edge

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


# =============================================================================
# COMPONENT BUILDERS
# =============================================================================

def create_plate():
    """Structural carousel plate — a rounded rectangle or circle that spans
    all receiver positions with margin."""
    # Use a circle large enough to contain all receivers
    plate_radius = ARC_RADIUS + RECEIVER_OD / 2 + PLATE_MARGIN

    plate = (cq.Workplane("XY")
             .circle(plate_radius)
             .extrude(PLATE_THICKNESS))

    return plate


def create_single_receiver(x, y):
    """One threaded receiver socket, positioned at (x, y) hanging below the
    plate (negative Z).  Includes the oil bore up through the plate and the
    tube stub on top."""

    # --- Receiver body (below plate) ---
    # Solid cylinder hanging below Z=0
    body = (cq.Workplane("XY", origin=(x, y, 0))
            .circle(RECEIVER_OD / 2)
            .extrude(-RECEIVER_LENGTH))

    # Hollow out the thread bore
    thread_bore = (cq.Workplane("XY", origin=(x, y, 0))
                   .circle(RECEIVER_THREAD_ID / 2)
                   .extrude(-RECEIVER_LENGTH - 1))  # through-cut
    body = body.cut(thread_bore)

    # Lead-in chamfer at the bottom (entry point for bottle)
    try:
        body = body.faces("<Z").chamfer(RECEIVER_CHAMFER)
    except Exception:
        pass

    # --- Thread ridges (simplified helical bumps) ---
    # True helical threads are hard to FDM-print at this scale.
    # Instead we create concentric ring ridges at thread pitch intervals
    # that a bottle neck can bite into. Works well enough for hand-tight
    # screw-in; refine after test prints.
    # TODO: Evaluate printed thread quality; consider switching to
    #       bayonet-lock or friction-fit if threads don't resolve well.
    thread_ridges = None
    num_ridges = int(RECEIVER_LENGTH / THREAD_PITCH)
    for r in range(num_ridges):
        z_pos = -(r * THREAD_PITCH + THREAD_PITCH / 2)
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

    # --- Oil bore (through the plate) ---
    bore = (cq.Workplane("XY", origin=(x, y, -1))
            .circle(TUBE_BORE / 2)
            .extrude(PLATE_THICKNESS + TUBE_STUB_HEIGHT + 2))
    body = body.cut(bore)

    # --- Tube stub (above plate, barb for silicone tube) ---
    stub = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS))
            .circle(TUBE_STUB_OD / 2)
            .extrude(TUBE_STUB_HEIGHT))

    # Barb ring near top of stub for tube retention
    barb = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS + TUBE_STUB_HEIGHT * 0.65))
            .circle(TUBE_STUB_OD / 2 + 0.4)
            .circle(TUBE_STUB_OD / 2)
            .extrude(1.0))
    stub = stub.union(barb)

    # Bore through the stub
    stub_bore = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS - 1))
                 .circle(TUBE_BORE / 2)
                 .extrude(TUBE_STUB_HEIGHT + 2))
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


def create_routing_channels():
    """Cut channels into the top surface of the plate to guide silicone
    tubing from each tube stub toward the pump exit edge."""
    channels = None

    positions = receiver_positions()
    for i, (rx, ry, _angle) in enumerate(positions):
        # Each channel runs from the tube stub position straight toward
        # the exit edge (negative Y).  Simple straight slot for v1.
        # TODO: Add gentle curves to avoid crossover for adjacent channels
        exit_x = (i - (BOTTLE_COUNT - 1) / 2) * (ROUTE_CHANNEL_WIDTH + 3.0)

        # Vertical slot from stub to exit — two-segment path:
        #   stub (rx, ry) → bend point (exit_x, ry - 5) → exit (exit_x, exit_y)

        # Segment 1: stub to bend
        seg1_dx = exit_x - rx
        seg1_dy = -5.0
        seg1_len = math.sqrt(seg1_dx**2 + seg1_dy**2)
        seg1_angle = math.degrees(math.atan2(seg1_dx, seg1_dy))

        ch1 = (cq.Workplane("XY", origin=(rx, ry, PLATE_THICKNESS - ROUTE_CHANNEL_DEPTH))
               .rect(ROUTE_CHANNEL_WIDTH, seg1_len + ROUTE_CHANNEL_WIDTH)
               .extrude(ROUTE_CHANNEL_DEPTH + 0.1))  # slight overcut to ensure clean subtraction
        ch1 = ch1.rotate((rx, ry, 0), (rx, ry, 1), -seg1_angle)

        # Segment 2: bend to exit edge (straight down in -Y)
        bend_y = ry - 5.0
        seg2_len = abs(bend_y - ROUTE_EXIT_Y)

        ch2 = (cq.Workplane("XY", origin=(exit_x, bend_y - seg2_len / 2,
                                          PLATE_THICKNESS - ROUTE_CHANNEL_DEPTH))
               .rect(ROUTE_CHANNEL_WIDTH, seg2_len)
               .extrude(ROUTE_CHANNEL_DEPTH + 0.1))

        seg = ch1.union(ch2)

        if channels is None:
            channels = seg
        else:
            channels = channels.union(seg)

    return channels


def create_mounting_holes():
    """M3 clearance holes near the plate perimeter."""
    holes = None
    for i in range(MOUNT_HOLE_COUNT):
        angle = i * 2 * math.pi / MOUNT_HOLE_COUNT + math.pi / 4  # offset 45°
        hx = MOUNT_HOLE_RADIUS * math.cos(angle)
        hy = MOUNT_HOLE_RADIUS * math.sin(angle)
        hole = (cq.Workplane("XY", origin=(hx, hy, -1))
                .circle(MOUNT_HOLE_DIA / 2)
                .extrude(PLATE_THICKNESS + 2))
        if holes is None:
            holes = hole
        else:
            holes = holes.union(hole)
    return holes


def create_reference_bottle(x, y):
    """Ghost bottle hanging below a receiver for visualisation."""
    # Bottle body (inverted — neck at top, base at bottom)
    neck_h = BOTTLE_NECK_LENGTH
    body_h = BOTTLE_HEIGHT - neck_h

    # Neck (threads into receiver, starts just below plate)
    neck = (cq.Workplane("XY", origin=(x, y, -RECEIVER_LENGTH))
            .circle(BOTTLE_NECK_OD / 2)
            .extrude(-neck_h))

    # Shoulder taper
    shoulder = (cq.Workplane("XY", origin=(x, y, -RECEIVER_LENGTH - neck_h))
                .circle(BOTTLE_NECK_OD / 2)
                .workplane(offset=-3)
                .circle(BOTTLE_BODY_DIA / 2)
                .loft())

    # Main body
    body = (cq.Workplane("XY", origin=(x, y, -RECEIVER_LENGTH - neck_h - 3))
            .circle(BOTTLE_BODY_DIA / 2)
            .extrude(-(body_h - 3)))

    bottle = neck.union(shoulder).union(body)
    return bottle


# =============================================================================
# ASSEMBLY
# =============================================================================

def assemble_oil_carousel():
    """Full carousel: plate + receivers + routing channels + mounting holes."""
    plate = create_plate()
    receivers = create_all_receivers()

    assembly = plate.union(receivers)

    # Cut routing channels into top surface
    channels = create_routing_channels()
    if channels:
        assembly = assembly.cut(channels)

    # Cut mounting holes
    holes = create_mounting_holes()
    if holes:
        assembly = assembly.cut(holes)

    # Cosmetic fillets
    try:
        assembly = assembly.faces(">Z").edges().fillet(FILLET_R)
    except Exception:
        pass

    return assembly


# =============================================================================
# RENDER
# =============================================================================

oil_carousel = assemble_oil_carousel()
show_object(oil_carousel, name="oil_carousel_complete")

# Show ghost bottles in all positions for scale
positions = receiver_positions()
for i, (x, y, _a) in enumerate(positions):
    bottle = create_reference_bottle(x, y)
    show_object(bottle, name=f"bottle_{i+1}",
               options={"alpha": 0.45, "color": "darkorange"})

# Exploded single receiver for detail review
single_receiver = create_single_receiver(0, 0)
show_object(single_receiver.translate((120, 0, 0)), name="single_receiver_detail",
           options={"alpha": 0.8, "color": "lightgreen"})

# Plate only (for print orientation reference)
show_object(create_plate().translate((-120, 0, 0)), name="plate_only",
           options={"alpha": 0.5, "color": "lightblue"})

# Print summary
print("=" * 60)
print("Essential Oil Bottle Carousel v1 — INVERTED DESIGN")
print("=" * 60)
print(f"  Bottles: {BOTTLE_COUNT} × standard 5 ml")
print(f"  Arrangement: {ARC_SPAN_DEG:.0f}° arc, R={ARC_RADIUS:.0f} mm")
print(f"  Plate diameter: ~{2 * (ARC_RADIUS + RECEIVER_OD/2 + PLATE_MARGIN):.0f} mm")
print(f"  Plate thickness: {PLATE_THICKNESS:.1f} mm")
print(f"  Receiver OD: {RECEIVER_OD:.1f} mm, length: {RECEIVER_LENGTH:.1f} mm")
print(f"  Thread: {BOTTLE_NECK_OD:.0f}-415, pitch {THREAD_PITCH:.2f} mm, "
      f"depth {THREAD_DEPTH:.1f} mm")
print(f"  Tube stub: {TUBE_STUB_OD:.1f} mm OD, {TUBE_STUB_HEIGHT:.0f} mm tall, "
      f"bore {TUBE_BORE:.1f} mm")
print(f"  Routing channels: {ROUTE_CHANNEL_WIDTH:.1f} × {ROUTE_CHANNEL_DEPTH:.1f} mm")
print()
print("User workflow:")
print("  1. Remove bottle cap")
print("  2. Screw bottle neck up into receiver")
print("  3. Oil gravity-feeds through bore → tube stub → silicone tube → pump")
print("  4. To swap: unscrew, replace, done")
print()
print("TODO:")
print("  - Measure actual bottle threads with calipers")
print("  - Test-print a single receiver for thread engagement")
print("  - Evaluate bayonet-lock if FDM threads are too coarse")
print("  - Add drip-catch lip around each receiver bore")
print("  - Add position numbers (1-5) embossed on plate edge")
