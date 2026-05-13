"""Test Print — Single Receiver with Mini Plate.

Quick-print file for validating thread engagement, o-ring fit, and drip
basin geometry with an actual 5ml essential oil bottle before committing
to the full 5-position carousel plate.

Print this piece, try screwing a bottle in, and check:
  1. Thread engagement — does the bottle bite and hold?
  2. O-ring groove — does the 18x2mm o-ring seat properly?
  3. Drip basin — is the recess visible and correctly sized?
  4. Oil bore — can you see through the center bore?
  5. Tube stub barb — does 3mm silicone tubing press on securely?

If threads are too coarse or don't engage, the next iteration will
switch to a bayonet-lock (quarter-turn with lugs).

Print settings:
  - Layer height: 0.16mm (fine detail for threads)
  - Infill: 30%
  - Supports: YES (for receiver hanging below plate)
  - Orientation: plate-side DOWN (tube stub faces up on build plate)
  - Material: PETG preferred (oil-resistant), PLA okay for fit test
  - Time estimate: ~25 min
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# DIMENSIONS — duplicated from v1-oil-carousel.py for standalone use.
# If you change the main design, update these to match.
# =============================================================================

TOL = 0.3
WALL = 2.5

# Bottle
BOTTLE_BODY_DIA = 22.0
BOTTLE_HEIGHT = 55.0
BOTTLE_NECK_OD = 18.0
BOTTLE_NECK_ID = 15.0
BOTTLE_NECK_LENGTH = 10.0

# Threads
THREAD_PITCH = 1.59
THREAD_DEPTH = 0.8

# Plate
PLATE_THICKNESS = 5.0

# Receiver
RECEIVER_OD = BOTTLE_NECK_OD + 2 * WALL
RECEIVER_THREAD_ID = BOTTLE_NECK_OD + 2 * TOL
RECEIVER_LENGTH = BOTTLE_NECK_LENGTH + 3.0
RECEIVER_CHAMFER = 1.0

# Tube stub
TUBE_OD = 3.0
TUBE_ID = 1.5
TUBE_STUB_OD = TUBE_OD + 1.0
TUBE_BORE = TUBE_ID + 0.2
TUBE_STUB_HEIGHT = 6.0

# O-ring
ORING_ID = 18.0
ORING_CS = 2.0
ORING_GROOVE_DEPTH = 1.5
ORING_GROOVE_WIDTH = ORING_CS + 0.3

# Drip basin
DRIP_BASIN_ID = RECEIVER_OD + 1.0
DRIP_BASIN_OD = RECEIVER_OD + 10.0
DRIP_BASIN_DEPTH = 2.0
DRIP_WEEP_DIA = 1.5


# =============================================================================
# RECEIVER BUILDER (same logic as main design)
# =============================================================================

def create_single_receiver(x, y):
    """One threaded receiver socket at (x, y), hanging below Z=0."""

    # Receiver body (below plate)
    body = (cq.Workplane("XY", origin=(x, y, 0))
            .circle(RECEIVER_OD / 2)
            .extrude(-RECEIVER_LENGTH))

    # Thread bore
    thread_bore = (cq.Workplane("XY", origin=(x, y, 0))
                   .circle(RECEIVER_THREAD_ID / 2)
                   .extrude(-RECEIVER_LENGTH - 1))
    body = body.cut(thread_bore)

    # Lead-in chamfer
    try:
        body = body.faces("<Z").chamfer(RECEIVER_CHAMFER)
    except Exception:
        pass

    # Thread ridges
    thread_ridges = None
    num_ridges = int(RECEIVER_LENGTH / THREAD_PITCH)
    for r in range(num_ridges):
        z_pos = -(r * THREAD_PITCH + THREAD_PITCH / 2)
        ridge = (cq.Workplane("XY", origin=(x, y, z_pos))
                 .circle(RECEIVER_THREAD_ID / 2 + THREAD_DEPTH)
                 .circle(RECEIVER_THREAD_ID / 2)
                 .extrude(THREAD_PITCH * 0.4))
        if thread_ridges is None:
            thread_ridges = ridge
        else:
            thread_ridges = thread_ridges.union(ridge)
    if thread_ridges is not None:
        body = body.union(thread_ridges)

    # O-ring groove
    oring_groove_r = ORING_ID / 2 + ORING_CS / 2
    oring_groove = (cq.Workplane("XY", origin=(x, y, 0))
                    .circle(oring_groove_r + ORING_GROOVE_WIDTH / 2)
                    .circle(oring_groove_r - ORING_GROOVE_WIDTH / 2)
                    .extrude(-ORING_GROOVE_DEPTH))
    body = body.cut(oring_groove)

    # Drip-catch basin
    drip_basin = (cq.Workplane("XY", origin=(x, y, 0))
                  .circle(DRIP_BASIN_OD / 2)
                  .circle(DRIP_BASIN_ID / 2)
                  .extrude(-DRIP_BASIN_DEPTH))
    body = body.cut(drip_basin)

    # Weep hole
    weep_offset_r = (DRIP_BASIN_ID + DRIP_BASIN_OD) / 4
    weep_hole = (cq.Workplane("XY", origin=(x + weep_offset_r, y, -DRIP_BASIN_DEPTH - 1))
                 .circle(DRIP_WEEP_DIA / 2)
                 .extrude(DRIP_BASIN_DEPTH + PLATE_THICKNESS + 2))
    body = body.cut(weep_hole)

    # Oil bore (through plate)
    bore = (cq.Workplane("XY", origin=(x, y, -1))
            .circle(TUBE_BORE / 2)
            .extrude(PLATE_THICKNESS + TUBE_STUB_HEIGHT + 2))
    body = body.cut(bore)

    # Tube stub with barb
    stub = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS))
            .circle(TUBE_STUB_OD / 2)
            .extrude(TUBE_STUB_HEIGHT))
    barb = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS + TUBE_STUB_HEIGHT * 0.65))
            .circle(TUBE_STUB_OD / 2 + 0.4)
            .circle(TUBE_STUB_OD / 2)
            .extrude(1.0))
    stub = stub.union(barb)
    stub_bore = (cq.Workplane("XY", origin=(x, y, PLATE_THICKNESS - 1))
                 .circle(TUBE_BORE / 2)
                 .extrude(TUBE_STUB_HEIGHT + 2))
    stub = stub.cut(stub_bore)

    body = body.union(stub)
    return body


# =============================================================================
# TEST PIECE
# =============================================================================

MINI_PLATE_SIZE = DRIP_BASIN_OD + 10.0

# Mini plate
mini_plate = (cq.Workplane("XY")
              .rect(MINI_PLATE_SIZE, MINI_PLATE_SIZE)
              .extrude(PLATE_THICKNESS))

# Receiver at center
receiver = create_single_receiver(0, 0)
test_piece = mini_plate.union(receiver)

# Round corners
try:
    test_piece = test_piece.edges("|Z").fillet(3.0)
except Exception:
    pass

show_object(test_piece, name="test_single_receiver")

# Ghost bottle for reference
neck_h = BOTTLE_NECK_LENGTH
body_h = BOTTLE_HEIGHT - neck_h

neck = (cq.Workplane("XY", origin=(0, 0, -RECEIVER_LENGTH))
        .circle(BOTTLE_NECK_OD / 2)
        .extrude(-neck_h))
shoulder = (cq.Workplane("XY", origin=(0, 0, -RECEIVER_LENGTH - neck_h))
            .circle(BOTTLE_NECK_OD / 2)
            .workplane(offset=-3)
            .circle(BOTTLE_BODY_DIA / 2)
            .loft())
body = (cq.Workplane("XY", origin=(0, 0, -RECEIVER_LENGTH - neck_h - 3))
        .circle(BOTTLE_BODY_DIA / 2)
        .extrude(-(body_h - 3)))
ghost_bottle = neck.union(shoulder).union(body)

show_object(ghost_bottle, name="ghost_bottle",
           options={"alpha": 0.35, "color": (1.0, 0.55, 0.0)})


print("=" * 50)
print("TEST PRINT — Single Receiver")
print("=" * 50)
print(f"  Piece size: {MINI_PLATE_SIZE:.0f} x {MINI_PLATE_SIZE:.0f} x "
      f"{PLATE_THICKNESS:.0f} mm plate")
print(f"  Height above plate: {TUBE_STUB_HEIGHT:.0f} mm (tube stub)")
print(f"  Height below plate: {RECEIVER_LENGTH:.0f} mm (receiver)")
print()
print("Checklist after printing:")
print("  [ ] Bottle threads engage and hold")
print("  [ ] O-ring groove visible and correctly sized")
print("  [ ] Drip basin recess is clean")
print("  [ ] Can see through oil bore")
print("  [ ] 3mm silicone tube fits on barb stub")
print("  [ ] Bottle hangs securely inverted")
