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
     A drip-catch basin surrounds the bore to contain leaks during bottle
     swaps. A short tube stub protrudes upward through the plate into a
     routing channel on the top surface.
  3. BOTTLES — hang inverted beneath the plate. The bottle body and label
     face downward and remain fully visible.
  4. TUBE ROUTING — silicone tubes connect each receiver stub (top of plate)
     to the corresponding peristaltic pump elsewhere in the enclosure.
     Channels fan out radially to avoid crossover.

Why inverted:
  - Gravity feeds oil to the pump — no dip tube reaching the bottle bottom.
  - Screw-in mounting = secure, vibration-proof, one-handed swap.
  - Labels face outward and are completely unobstructed.
  - No wells, collars, or windows needed — simpler to print.

O-ring seal:
  Each receiver has a groove at the top (plate junction) sized for an 18 mm ID
  o-ring. The bottle shoulder compresses it when fully screwed in, preventing
  slow oil seepage around the threads.

Drip-catch basin:
  A shallow annular basin is recessed into the underside of the plate around
  each receiver bore. If oil drips during a bottle swap, it pools here instead
  of running across the plate. A small weep hole lets captured oil drain back
  toward the bore once a new bottle is installed.

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

# --- O-ring seal (sits at top of receiver bore) ---
# Standard 18 mm ID o-ring (18 × 2 mm cross-section, Buna-N / nitrile)
# The bottle shoulder compresses it when fully screwed in.
ORING_ID = 18.0            # matches bottle neck OD
ORING_CS = 2.0             # cross-section diameter
ORING_GROOVE_DEPTH = 1.5   # mm — ~75% of CS for proper compression
ORING_GROOVE_WIDTH = ORING_CS + 0.3  # slightly wider than CS for fit

# --- Drip-catch basin (underside of plate, around each receiver) ---
# Catches oil that may drip when swapping bottles.
DRIP_BASIN_ID = RECEIVER_OD + 1.0   # just outside receiver body
DRIP_BASIN_OD = RECEIVER_OD + 10.0  # outer rim of catch basin
DRIP_BASIN_DEPTH = 2.0              # mm recess into underside of plate
DRIP_WEEP_DIA = 1.5                 # mm — small hole to drain basin back to bore

# --- Position labels ---
# Embossed numbers 1-5 on the plate top surface near each receiver.
LABEL_FONT_SIZE = 6.0      # mm — height of embossed number
LABEL_DEPTH = 0.6           # mm — extrusion depth (raised text on surface)
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

    # --- O-ring groove (at top of receiver, where bottle shoulder seats) ---
    # Annular groove cut into the top face of the receiver (Z=0 plane)
    # so the o-ring sits flush and gets compressed by the bottle shoulder.
    oring_groove_r = ORING_ID / 2 + ORING_CS / 2  # groove centerline radius
    oring_groove = (cq.Workplane("XY", origin=(x, y, 0))
                    .circle(oring_groove_r + ORING_GROOVE_WIDTH / 2)
                    .circle(oring_groove_r - ORING_GROOVE_WIDTH / 2)
                    .extrude(-ORING_GROOVE_DEPTH))
    body = body.cut(oring_groove)

    # --- Drip-catch basin (underside of plate around receiver) ---
    # Shallow annular recess to catch drips during bottle swaps.
    drip_basin = (cq.Workplane("XY", origin=(x, y, 0))
                  .circle(DRIP_BASIN_OD / 2)
                  .circle(DRIP_BASIN_ID / 2)
                  .extrude(-DRIP_BASIN_DEPTH))
    body = body.cut(drip_basin)

    # Weep hole — lets captured oil drain back into the bore once a
    # bottle is re-installed and the system is sealed again.
    weep_offset_r = (DRIP_BASIN_ID + DRIP_BASIN_OD) / 4  # midway in basin
    weep_hole = (cq.Workplane("XY", origin=(x + weep_offset_r, y, -DRIP_BASIN_DEPTH - 1))
                 .circle(DRIP_WEEP_DIA / 2)
                 .extrude(DRIP_BASIN_DEPTH + PLATE_THICKNESS + 2))
    body = body.cut(weep_hole)

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
    tubing from each tube stub toward the pump exit edge.

    Routing strategy — radial fan-out (no crossovers):
      Each channel runs radially inward from the receiver toward the plate
      center, then turns and runs straight toward the exit edge (-Y).
      Because receivers are already arranged in an arc, radial-inward paths
      naturally converge without crossing.  The final parallel run keeps
      tubes neatly spaced for pump connection.
    """
    channels = None
    z_bot = PLATE_THICKNESS - ROUTE_CHANNEL_DEPTH
    z_height = ROUTE_CHANNEL_DEPTH + 0.1  # slight overcut for clean boolean

    positions = receiver_positions()

    # Exit positions — evenly spaced along the exit edge
    exit_spacing = ROUTE_CHANNEL_WIDTH + 3.0
    exit_x_center = 0.0

    for i, (rx, ry, _angle) in enumerate(positions):
        exit_x = exit_x_center + (i - (BOTTLE_COUNT - 1) / 2) * exit_spacing

        # --- Segment 1: radial run from receiver toward center ---
        # Run from (rx, ry) toward the plate center, stopping partway
        # so we don't collide with other channels near the middle.
        radial_stop_r = ARC_RADIUS * 0.35  # how far inward to come
        angle_rad = math.atan2(rx, ry)  # angle from center to receiver
        mid_x = radial_stop_r * math.sin(angle_rad)
        mid_y = radial_stop_r * math.cos(angle_rad)

        seg1_dx = mid_x - rx
        seg1_dy = mid_y - ry
        seg1_len = math.sqrt(seg1_dx**2 + seg1_dy**2)
        seg1_angle = math.degrees(math.atan2(seg1_dx, seg1_dy))

        if seg1_len > 1.0:
            ch1 = (cq.Workplane("XY", origin=(
                       rx + seg1_dx / 2, ry + seg1_dy / 2, z_bot))
                   .rect(ROUTE_CHANNEL_WIDTH, seg1_len + ROUTE_CHANNEL_WIDTH)
                   .extrude(z_height))
            ch1 = ch1.rotate(
                (rx + seg1_dx / 2, ry + seg1_dy / 2, 0),
                (rx + seg1_dx / 2, ry + seg1_dy / 2, 1),
                -(seg1_angle - 90))
        else:
            ch1 = None

        # --- Segment 2: jog from radial end to the exit column ---
        jog_dx = exit_x - mid_x
        jog_dy = -5.0
        jog_len = math.sqrt(jog_dx**2 + jog_dy**2)
        jog_angle = math.degrees(math.atan2(jog_dx, jog_dy))

        ch2 = (cq.Workplane("XY", origin=(
                   mid_x + jog_dx / 2, mid_y + jog_dy / 2, z_bot))
               .rect(ROUTE_CHANNEL_WIDTH, jog_len + ROUTE_CHANNEL_WIDTH)
               .extrude(z_height))
        ch2 = ch2.rotate(
            (mid_x + jog_dx / 2, mid_y + jog_dy / 2, 0),
            (mid_x + jog_dx / 2, mid_y + jog_dy / 2, 1),
            -(jog_angle - 90))

        # --- Segment 3: straight run to exit edge (-Y) ---
        run_start_y = mid_y + jog_dy
        run_len = abs(run_start_y - ROUTE_EXIT_Y)

        ch3 = (cq.Workplane("XY", origin=(
                   exit_x, run_start_y - run_len / 2, z_bot))
               .rect(ROUTE_CHANNEL_WIDTH, run_len)
               .extrude(z_height))

        # Merge segments
        seg = ch2.union(ch3)
        if ch1 is not None:
            seg = ch1.union(seg)

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


def create_position_labels():
    """Create raised position numbers (1-5) on the plate top surface near
    each receiver so the user knows which oil goes where.

    Uses simple geometric digit shapes since CadQuery text support varies
    across environments.  Each number is a small raised dot pattern:
      1 = single dot, 2 = two dots, etc.  Braille-style — works on any
      printer, no font dependencies, tactile for low-light use.
    """
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
    """Full carousel: plate + receivers + routing channels + mounting holes
    + position labels."""
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

    # Add raised position labels (dot-count pattern)
    labels = create_position_labels()
    if labels:
        assembly = assembly.union(labels)

    # Cosmetic fillets on plate rim
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
print(f"  O-ring seal: {ORING_ID:.0f} × {ORING_CS:.0f} mm (groove depth "
      f"{ORING_GROOVE_DEPTH:.1f} mm)")
print(f"  Drip basin: {DRIP_BASIN_OD:.0f} mm OD × {DRIP_BASIN_DEPTH:.0f} mm deep, "
      f"weep hole {DRIP_WEEP_DIA:.1f} mm")
print(f"  Tube stub: {TUBE_STUB_OD:.1f} mm OD, {TUBE_STUB_HEIGHT:.0f} mm tall, "
      f"bore {TUBE_BORE:.1f} mm")
print(f"  Routing: radial fan-out, {ROUTE_CHANNEL_WIDTH:.1f} × "
      f"{ROUTE_CHANNEL_DEPTH:.1f} mm channels")
print(f"  Position labels: dot-count pattern (tactile, 1-5)")
print()
print("User workflow:")
print("  1. Remove bottle cap")
print("  2. Screw bottle neck up into receiver (o-ring seals)")
print("  3. Oil gravity-feeds through bore → tube stub → silicone tube → pump")
print("  4. To swap: unscrew (drip basin catches any drips), replace, done")
print()
print("TODO:")
print("  - Measure actual bottle threads with calipers")
print("  - Test-print a single receiver for thread engagement")
print("  - Evaluate bayonet-lock if FDM threads are too coarse")
print("  - Source 18 × 2 mm o-rings (nitrile, oil-resistant)")
print("  - Test drip basin capacity and weep hole flow")
print("  - Verify position dot legibility after printing")
