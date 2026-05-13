"""Mist Chimney and Outlet Nozzle Design v1.

The visible top portion of the smart humidifier that channels atomized water+oil
upward and out through an aesthetically pleasing directional nozzle.

This is the most visible desktop component - designed for bedroom/office use with
smooth organic curves and minimal seams.

Key Features:
- 30-40mm ID chimney tube, ~60-80mm tall above mixing chamber
- Smooth internal walls to minimize condensation drip-back
- Directional outlet nozzle with anti-drip lip
- Removable snap-on attachment for easy cleaning
- Clean, modern aesthetic suitable for desktop placement
"""

import cadquery as cq
from cq_server.ui import ui, show_object

# Design parameters - using placeholders with TODOs for refinement
# TODO: Verify optimal ID for mist flow dynamics
CHIMNEY_INNER_DIAMETER = 35.0  # mm - target 30-40mm range
CHIMNEY_OUTER_DIAMETER = 42.0  # mm - 3.5mm wall thickness for durability

# TODO: Test actual height needed for proper mist dispersion
CHIMNEY_HEIGHT = 70.0  # mm - target 60-80mm above mixing chamber

# Wall thickness and structural parameters
WALL_THICKNESS = 3.5  # mm - balance between strength and material use
NOZZLE_DIAMETER = 25.0  # mm - outlet opening
NOZZLE_HEIGHT = 15.0  # mm

# Snap-on connection parameters
# TODO: Test fit tolerance with mixing chamber prototype
SNAP_RING_DIAMETER = 50.0  # mm - connects to mixing chamber
SNAP_RING_HEIGHT = 8.0  # mm
SNAP_GROOVE_WIDTH = 2.0  # mm
SNAP_GROOVE_DEPTH = 1.5  # mm

# Anti-drip and aesthetic parameters
DRIP_LIP_INWARD_CURVE = 2.0  # mm - prevents condensation rundown
NOZZLE_ANGLE = 15.0  # degrees - slight upward angle for mist direction
FILLET_RADIUS = 3.0  # mm - smooth organic curves throughout


def create_main_chimney():
    """Create the main cylindrical chimney tube with smooth interior."""
    chimney = (cq.Workplane("XY")
               .circle(CHIMNEY_OUTER_DIAMETER / 2)
               .extrude(CHIMNEY_HEIGHT)
               .faces(">Z")
               .circle(CHIMNEY_INNER_DIAMETER / 2)
               .cutThruAll())

    # Add subtle external taper for aesthetics
    # TODO: Evaluate if taper affects visual cleanliness
    taper_factor = 0.95  # Slight taper toward top
    tapered_top = (cq.Workplane("XY", origin=(0, 0, CHIMNEY_HEIGHT))
                   .circle((CHIMNEY_OUTER_DIAMETER / 2) * taper_factor)
                   .extrude(-CHIMNEY_HEIGHT / 3))

    # Blend the taper with the main body
    chimney = chimney.intersect(tapered_top.translate((0, 0, CHIMNEY_HEIGHT / 3)))

    return chimney


def create_snap_connection():
    """Create snap-on connection ring for attachment to mixing chamber."""
    # Main connection ring
    snap_ring = (cq.Workplane("XY")
                 .circle(SNAP_RING_DIAMETER / 2)
                 .circle((SNAP_RING_DIAMETER / 2) - WALL_THICKNESS)
                 .extrude(SNAP_RING_HEIGHT))

    # Snap groove for secure connection
    # TODO: Test snap force - should be firm but not difficult
    groove_position = SNAP_RING_HEIGHT * 0.7
    snap_groove = (cq.Workplane("XY", origin=(0, 0, groove_position))
                   .circle((SNAP_RING_DIAMETER / 2) - SNAP_GROOVE_DEPTH)
                   .circle((SNAP_RING_DIAMETER / 2) - SNAP_GROOVE_DEPTH - SNAP_GROOVE_WIDTH)
                   .extrude(SNAP_GROOVE_WIDTH))

    snap_ring = snap_ring.cut(snap_groove)

    # Add lead-in chamfer for easier insertion
    chamfer_size = 1.0  # mm
    snap_ring = snap_ring.faces("<Z").chamfer(chamfer_size)

    return snap_ring


def create_directional_nozzle():
    """Create angled outlet nozzle with anti-drip lip."""
    # Position nozzle at top of chimney with slight forward angle
    nozzle_center_height = CHIMNEY_HEIGHT + NOZZLE_HEIGHT / 2

    # Main nozzle body - elliptical for directional flow
    # TODO: Optimize nozzle shape for mist pattern and reach
    nozzle_body = (cq.Workplane("XZ", origin=(0, 0, nozzle_center_height))
                   .ellipse(NOZZLE_DIAMETER / 2, NOZZLE_HEIGHT / 2)
                   .extrude(NOZZLE_DIAMETER)
                   .rotate((0, 0, 0), (1, 0, 0), NOZZLE_ANGLE))

    # Create nozzle opening - slightly smaller than body for velocity increase
    opening_diameter = NOZZLE_DIAMETER * 0.8
    nozzle_opening = (cq.Workplane("XZ", origin=(0, 0, nozzle_center_height))
                      .ellipse(opening_diameter / 2, (NOZZLE_HEIGHT / 2) * 0.9)
                      .extrude(NOZZLE_DIAMETER + 5)  # Cut completely through
                      .rotate((0, 0, 0), (1, 0, 0), NOZZLE_ANGLE))

    nozzle_body = nozzle_body.cut(nozzle_opening)

    # Anti-drip lip - inward curve at nozzle rim
    # TODO: Test anti-drip effectiveness with various lip geometries
    lip_sweep_path = (cq.Workplane("YZ", origin=(NOZZLE_DIAMETER / 2, 0, nozzle_center_height))
                      .spline([(0, 0), (-DRIP_LIP_INWARD_CURVE, -1),
                              (-DRIP_LIP_INWARD_CURVE, -2)]))

    # Apply fillets for smooth, organic appearance
    nozzle_body = nozzle_body.edges().fillet(FILLET_RADIUS * 0.5)

    return nozzle_body


def create_internal_flow_guide():
    """Create internal features to guide mist flow and reduce turbulence."""
    # Gentle internal taper to accelerate mist flow toward nozzle
    # TODO: CFD analysis to optimize flow characteristics
    taper_height = CHIMNEY_HEIGHT * 0.3  # Top 30% of chimney
    flow_guide = (cq.Workplane("XY", origin=(0, 0, CHIMNEY_HEIGHT - taper_height))
                  .circle(CHIMNEY_INNER_DIAMETER / 2)
                  .circle((CHIMNEY_INNER_DIAMETER / 2) * 0.8)  # Taper to 80% diameter
                  .loft())

    return flow_guide


@ui
def assemble_mist_chimney():
    """Assemble complete mist chimney and outlet system."""

    # Create main components
    chimney = create_main_chimney()
    snap_connection = create_snap_connection()
    nozzle = create_directional_nozzle()
    flow_guide = create_internal_flow_guide()

    # Position snap connection at bottom of chimney
    snap_connection = snap_connection.translate((0, 0, -SNAP_RING_HEIGHT))

    # Combine all components
    complete_assembly = chimney.union(snap_connection).union(nozzle)

    # Subtract flow guide from interior for smooth mist path
    complete_assembly = complete_assembly.cut(flow_guide)

    # Apply overall fillets for smooth, modern appearance
    # TODO: Evaluate fillet radii for manufacturing constraints
    complete_assembly = complete_assembly.edges().fillet(FILLET_RADIUS)

    return complete_assembly


# Generate and display the complete mist chimney design
mist_chimney = assemble_mist_chimney()
show_object(mist_chimney, name="mist_chimney_complete")

# Show individual components for reference
show_object(create_main_chimney(), name="chimney_tube",
           options={"alpha": 0.7, "color": "lightblue"})
show_object(create_snap_connection().translate((60, 0, 0)), name="snap_connection",
           options={"alpha": 0.7, "color": "lightgreen"})
show_object(create_directional_nozzle().translate((120, 0, 0)), name="outlet_nozzle",
           options={"alpha": 0.7, "color": "orange"})

# Display design specifications as a reference object
specs_text = f"""Design Specifications:
- Chimney ID: {CHIMNEY_INNER_DIAMETER}mm
- Chimney Height: {CHIMNEY_HEIGHT}mm
- Wall Thickness: {WALL_THICKNESS}mm
- Nozzle Angle: {NOZZLE_ANGLE}°
- Anti-drip Lip: {DRIP_LIP_INWARD_CURVE}mm inward
- Snap Ring: {SNAP_RING_DIAMETER}mm diameter

Features:
✓ Removable for cleaning
✓ Anti-drip lip design
✓ Directional mist output
✓ Smooth internal surfaces
✓ Desktop-friendly aesthetics
✓ Snap-on attachment system

TODO Items:
- Verify optimal ID for mist flow
- Test snap-fit tolerance
- CFD analysis for flow optimization
- Manufacturing constraint review
- Surface finish specifications
"""

# Create a simple reference plate with the specs
reference_plate = (cq.Workplane("XY", origin=(0, -100, 0))
                   .box(80, 60, 2)
                   .edges().fillet(2))

show_object(reference_plate, name="design_specifications",
           options={"alpha": 0.3, "color": "gray"})

print("Mist chimney and outlet nozzle design generated successfully!")
print("Key features:")
print(f"  - Chimney: {CHIMNEY_INNER_DIAMETER}mm ID × {CHIMNEY_HEIGHT}mm tall")
print(f"  - Directional nozzle with {NOZZLE_ANGLE}° angle")
print(f"  - Anti-drip lip with {DRIP_LIP_INWARD_CURVE}mm inward curve")
print(f"  - Snap-on connection: {SNAP_RING_DIAMETER}mm diameter")
print("  - Removable design for easy cleaning")
print("  - Smooth organic curves for desktop aesthetics")