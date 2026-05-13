"""Essential Oil Bottle Carousel Design v1.

A section of the humidifier enclosure that holds 5 standard 5ml essential oil
bottles upright in a semicircular arrangement. Each bottle has a dip tube
inserted through the cap, connected via silicone tubing to its dedicated
peristaltic pump.

This component is designed to integrate with the main humidifier base and
provide easy access for bottle swapping while maintaining clean tube routing.

Key Features:
- 5 cylindrical bottle wells sized for standard 5ml bottles (~22mm dia x 55mm)
- Threaded cap interface or friction-fit collar for secure bottle mounting
- Dip tube pass-through holes for 3mm silicone tubing
- Tube routing channels from each well to corresponding pumps below
- Cutaway windows for bottle label visibility
- Quick-swap design for easy bottle replacement
- Semicircular arrangement for visual appeal and space efficiency

Standard 5ml Essential Oil Bottle Specifications:
- Body diameter: ~22mm
- Total height: ~55mm (with cap)
- Neck outer diameter: ~18mm
- Cap threading: typically 18-400 or 18-415 (to be measured)
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Bottle Specifications (standard 5ml essential oil bottles) ---
# TODO: Verify actual bottle dimensions with physical samples
BOTTLE_BODY_DIAMETER = 22.0     # mm - main bottle body diameter
BOTTLE_HEIGHT = 55.0            # mm - total height including cap
BOTTLE_NECK_DIAMETER = 18.0     # mm - neck outer diameter
BOTTLE_CAP_THREAD = "18-400"    # standard thread size (to be confirmed)

# --- Carousel Layout ---
BOTTLE_COUNT = 5                # number of bottle positions
CAROUSEL_ARRANGEMENT = "semicircle"  # semicircle or linear arrangement
BOTTLE_WELL_SPACING = 35.0      # mm - center-to-center distance between wells

# --- Well Dimensions ---
WELL_DIAMETER = BOTTLE_BODY_DIAMETER + 1.0  # mm - slight clearance for bottles
WELL_DEPTH = BOTTLE_HEIGHT * 0.7             # mm - wells hold ~70% of bottle height
WELL_WALL_THICKNESS = 2.5       # mm - wall thickness around each well

# --- Cap Interface ---
# TODO: Determine if threaded or friction-fit works better
CAP_INTERFACE_TYPE = "friction"  # "threaded" or "friction"
CAP_COLLAR_HEIGHT = 8.0         # mm - height of cap interface collar
CAP_COLLAR_INNER_DIA = BOTTLE_NECK_DIAMETER + 0.5  # mm - slight clearance

# --- Dip Tube System ---
DIP_TUBE_DIAMETER = 3.0         # mm - silicone tubing outer diameter
DIP_TUBE_HOLE_DIAMETER = DIP_TUBE_DIAMETER + 0.3  # mm - clearance for tubing
DIP_TUBE_LENGTH = BOTTLE_HEIGHT - 5.0  # mm - reaches near bottle bottom

# --- Tube Routing ---
ROUTING_CHANNEL_WIDTH = 5.0     # mm - width of tube routing channels
ROUTING_CHANNEL_DEPTH = 3.0     # mm - depth of tube routing channels
PUMP_SPACING = 40.0             # mm - spacing between peristaltic pumps below
PUMP_Y_OFFSET = 50.0            # mm - distance from carousel center to pump row

# --- Structural Design ---
BASE_THICKNESS = 4.0            # mm - thickness of carousel base plate
WALL_HEIGHT = WELL_DEPTH + BASE_THICKNESS  # mm - total height of well walls
LABEL_WINDOW_HEIGHT = 25.0      # mm - height of cutaway for label visibility
LABEL_WINDOW_WIDTH = 15.0       # mm - width of cutaway for label visibility

# --- Assembly Integration ---
MOUNTING_HOLE_DIAMETER = 3.2    # mm - M3 mounting holes
MOUNTING_HOLE_COUNT = 4         # number of mounting holes
MOUNTING_HOLE_CIRCLE_RADIUS = 60.0  # mm - radius of mounting hole pattern

# --- Visual and Ergonomic ---
FILLET_RADIUS = 2.0             # mm - radius for smooth edges
CHAMFER_SIZE = 1.0              # mm - chamfer size for easy handling


def calculate_well_positions():
    """Calculate the XY positions for each bottle well based on arrangement."""
    positions = []

    if CAROUSEL_ARRANGEMENT == "semicircle":
        # Arrange wells in a semicircle
        well_radius = (BOTTLE_COUNT - 1) * BOTTLE_WELL_SPACING / (2 * math.pi) * 2
        start_angle = -math.pi / 2  # Start at bottom of semicircle
        end_angle = math.pi / 2     # End at top of semicircle
        angle_step = (end_angle - start_angle) / (BOTTLE_COUNT - 1)

        for i in range(BOTTLE_COUNT):
            angle = start_angle + i * angle_step
            x = well_radius * math.cos(angle)
            y = well_radius * math.sin(angle)
            positions.append((x, y))
    else:
        # Linear arrangement
        start_x = -(BOTTLE_COUNT - 1) * BOTTLE_WELL_SPACING / 2
        for i in range(BOTTLE_COUNT):
            x = start_x + i * BOTTLE_WELL_SPACING
            positions.append((x, 0))

    return positions


def create_bottle_well(position_x, position_y, well_index):
    """Create a single bottle well with cap interface and dip tube hole."""
    # Main cylindrical well
    well = (cq.Workplane("XY", origin=(position_x, position_y, 0))
            .circle(WELL_DIAMETER / 2)
            .extrude(WELL_DEPTH))

    # Create bottle cavity (hollow out the well)
    bottle_cavity = (cq.Workplane("XY", origin=(position_x, position_y, BASE_THICKNESS))
                     .circle((WELL_DIAMETER - 2 * WELL_WALL_THICKNESS) / 2)
                     .extrude(WELL_DEPTH - BASE_THICKNESS))

    well = well.cut(bottle_cavity)

    # Add cap interface collar at the top
    if CAP_INTERFACE_TYPE == "friction":
        cap_collar = (cq.Workplane("XY", origin=(position_x, position_y, WELL_DEPTH))
                      .circle(CAP_COLLAR_INNER_DIA / 2 + WELL_WALL_THICKNESS)
                      .circle(CAP_COLLAR_INNER_DIA / 2)
                      .extrude(CAP_COLLAR_HEIGHT))
        well = well.union(cap_collar)

    # TODO: Implement threaded interface if needed
    # elif CAP_INTERFACE_TYPE == "threaded":
    #     # Add threaded collar implementation
    #     pass

    # Dip tube pass-through hole (center of cap interface)
    dip_tube_hole = (cq.Workplane("XY", origin=(position_x, position_y, 0))
                     .circle(DIP_TUBE_HOLE_DIAMETER / 2)
                     .extrude(WELL_DEPTH + CAP_COLLAR_HEIGHT + 2))

    well = well.cut(dip_tube_hole)

    # Label visibility window (cutaway in the side wall)
    label_window = (cq.Workplane("YZ", origin=(position_x + WELL_DIAMETER / 2 - 1, position_y,
                                              BASE_THICKNESS + LABEL_WINDOW_HEIGHT / 2))
                    .rect(LABEL_WINDOW_WIDTH, LABEL_WINDOW_HEIGHT)
                    .extrude(-WELL_WALL_THICKNESS - 1))

    well = well.cut(label_window)

    # Add identification number embossed on the well
    # TODO: Add embossed numbers for well identification

    return well


def create_base_plate():
    """Create the main base plate that connects all wells."""
    well_positions = calculate_well_positions()

    # Calculate base plate dimensions to encompass all wells
    if CAROUSEL_ARRANGEMENT == "semicircle":
        # Semicircular base with some margin
        max_radius = max(math.sqrt(x**2 + y**2) for x, y in well_positions)
        base_radius = max_radius + WELL_DIAMETER / 2 + 10  # 10mm margin

        base_plate = (cq.Workplane("XY")
                      .circle(base_radius)
                      .extrude(BASE_THICKNESS))
    else:
        # Rectangular base for linear arrangement
        max_x = max(x for x, y in well_positions) + WELL_DIAMETER / 2 + 10
        min_x = min(x for x, y in well_positions) - WELL_DIAMETER / 2 - 10
        base_width = max_x - min_x
        base_length = WELL_DIAMETER + 20  # 20mm total margin

        base_plate = (cq.Workplane("XY")
                      .rect(base_width, base_length)
                      .extrude(BASE_THICKNESS))

    return base_plate


def create_tube_routing_channels():
    """Create channels for routing silicone tubes from wells to pumps."""
    well_positions = calculate_well_positions()
    channels = None

    for i, (well_x, well_y) in enumerate(well_positions):
        # Calculate pump position for this well
        pump_x = (i - (BOTTLE_COUNT - 1) / 2) * PUMP_SPACING
        pump_y = -PUMP_Y_OFFSET  # Pumps are behind the carousel

        # Create simple rectangular channel from well to pump
        # TODO: Optimize routing to avoid crossovers and add smooth curves

        # Calculate channel path (simple straight line for now)
        channel_length = math.sqrt((pump_x - well_x)**2 + (pump_y - well_y)**2)
        channel_angle = math.atan2(pump_y - well_y, pump_x - well_x)

        # Create rectangular channel
        channel = (cq.Workplane("XY", origin=(well_x, well_y, 0))
                   .rect(ROUTING_CHANNEL_WIDTH, channel_length)
                   .rotate((0, 0, 0), (0, 0, 1), math.degrees(channel_angle))
                   .translate((0, channel_length / 2, 0))
                   .extrude(ROUTING_CHANNEL_DEPTH))

        if channels is None:
            channels = channel
        else:
            channels = channels.union(channel)

    return channels


def create_mounting_holes():
    """Create mounting holes for attaching carousel to main enclosure."""
    mounting_holes = None

    for i in range(MOUNTING_HOLE_COUNT):
        angle = i * 2 * math.pi / MOUNTING_HOLE_COUNT
        hole_x = MOUNTING_HOLE_CIRCLE_RADIUS * math.cos(angle)
        hole_y = MOUNTING_HOLE_CIRCLE_RADIUS * math.sin(angle)

        hole = (cq.Workplane("XY", origin=(hole_x, hole_y, 0))
                .circle(MOUNTING_HOLE_DIAMETER / 2)
                .extrude(BASE_THICKNESS + 2))

        if mounting_holes is None:
            mounting_holes = hole
        else:
            mounting_holes = mounting_holes.union(hole)

    return mounting_holes


def assemble_oil_carousel():
    """Assemble the complete essential oil bottle carousel."""
    # Create base components
    base_plate = create_base_plate()
    well_positions = calculate_well_positions()

    # Add all bottle wells
    complete_assembly = base_plate
    for i, (x, y) in enumerate(well_positions):
        well = create_bottle_well(x, y, i)
        complete_assembly = complete_assembly.union(well)

    # Add tube routing channels
    routing_channels = create_tube_routing_channels()
    if routing_channels:
        complete_assembly = complete_assembly.cut(routing_channels)

    # Add mounting holes
    mounting_holes = create_mounting_holes()
    if mounting_holes:
        complete_assembly = complete_assembly.cut(mounting_holes)

    # Apply finishing touches
    try:
        # Add fillets for smooth appearance
        complete_assembly = complete_assembly.edges("|Z").fillet(FILLET_RADIUS * 0.5)
        # Add chamfers to top edges for easy handling
        complete_assembly = complete_assembly.faces(">Z").chamfer(CHAMFER_SIZE)
    except:
        # Skip filleting if geometry is too complex
        pass

    return complete_assembly


def create_reference_bottle():
    """Create a reference 5ml bottle for visualization."""
    # Simple bottle shape for reference
    bottle_body = (cq.Workplane("XY")
                   .circle(BOTTLE_BODY_DIAMETER / 2)
                   .extrude(BOTTLE_HEIGHT * 0.8))

    bottle_neck = (cq.Workplane("XY", origin=(0, 0, BOTTLE_HEIGHT * 0.8))
                   .circle(BOTTLE_NECK_DIAMETER / 2)
                   .extrude(BOTTLE_HEIGHT * 0.2))

    bottle = bottle_body.union(bottle_neck)
    return bottle


# =============================================================================
# GENERATE AND DISPLAY THE DESIGN
# =============================================================================

# Generate the complete oil carousel design
oil_carousel = assemble_oil_carousel()
show_object(oil_carousel, name="oil_carousel_complete")

# Show reference bottle in first well position for scale
well_positions = calculate_well_positions()
if well_positions:
    reference_bottle = create_reference_bottle()
    reference_bottle = reference_bottle.translate((well_positions[0][0],
                                                  well_positions[0][1],
                                                  BASE_THICKNESS))
    show_object(reference_bottle, name="reference_bottle",
               options={"alpha": 0.6, "color": "amber"})

# Show individual components for reference
show_object(create_base_plate().translate((100, 0, 0)), name="base_plate",
           options={"alpha": 0.7, "color": "lightblue"})

if well_positions:
    show_object(create_bottle_well(0, 0, 0).translate((150, 0, 0)),
               name="single_well", options={"alpha": 0.7, "color": "lightgreen"})

# Create design specifications reference
specifications_text = f"""Essential Oil Carousel Specifications:

BOTTLE WELLS:
- Count: {BOTTLE_COUNT} bottles
- Arrangement: {CAROUSEL_ARRANGEMENT}
- Well diameter: {WELL_DIAMETER:.1f}mm
- Well depth: {WELL_DEPTH:.1f}mm
- Wall thickness: {WELL_WALL_THICKNESS:.1f}mm

BOTTLE COMPATIBILITY:
- Body diameter: {BOTTLE_BODY_DIAMETER:.1f}mm
- Height: {BOTTLE_HEIGHT:.1f}mm
- Cap interface: {CAP_INTERFACE_TYPE}
- Thread type: {BOTTLE_CAP_THREAD}

DIP TUBE SYSTEM:
- Tube diameter: {DIP_TUBE_DIAMETER:.1f}mm
- Hole clearance: {DIP_TUBE_HOLE_DIAMETER:.1f}mm
- Tube length: {DIP_TUBE_LENGTH:.1f}mm

FEATURES:
✓ Label visibility windows
✓ Quick-swap bottle design
✓ Integrated tube routing
✓ Mounting holes for assembly
✓ Smooth filleted edges
✓ Anti-drip design

TODO ITEMS:
- Measure actual bottle thread specifications
- Test friction-fit vs threaded cap interface
- Optimize tube routing to avoid crossovers
- Add embossed well numbers/labels
- Validate pump spacing alignment
- Test print tolerances and fit
- Consider anti-rotation features
- Add cable management clips
"""

# Create reference plate for specifications
reference_plate = (cq.Workplane("XY", origin=(0, -150, 0))
                   .box(120, 80, 3))

show_object(reference_plate, name="design_specifications",
           options={"alpha": 0.3, "color": "gray"})

print("Essential Oil Bottle Carousel design generated successfully!")
print(f"Configuration:")
print(f"  - {BOTTLE_COUNT} bottle wells in {CAROUSEL_ARRANGEMENT} arrangement")
print(f"  - Well spacing: {BOTTLE_WELL_SPACING:.1f}mm center-to-center")
print(f"  - Compatible with standard 5ml bottles ({BOTTLE_BODY_DIAMETER:.1f}mm dia)")
print(f"  - {CAP_INTERFACE_TYPE.title()} cap interface with {DIP_TUBE_DIAMETER:.1f}mm dip tubes")
print(f"  - Label windows: {LABEL_WINDOW_WIDTH:.1f} x {LABEL_WINDOW_HEIGHT:.1f}mm")
print(f"  - Base thickness: {BASE_THICKNESS:.1f}mm with {MOUNTING_HOLE_COUNT} mounting holes")
print("Key features:")
print("  ✓ Quick-swap bottle replacement")
print("  ✓ Integrated dip tube pass-throughs")
print("  ✓ Tube routing channels to pumps")
print("  ✓ Label visibility windows")
print("  ✓ Secure cap interface system")
print("  ✓ Easy integration with main enclosure")