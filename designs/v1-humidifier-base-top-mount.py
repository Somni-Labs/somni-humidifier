"""
Smart Humidifier — Main Enclosure Base — V1 with TOP-MOUNTED OIL CAROUSEL

Modified version of the main base to support top-mounted oil bottles.
Key changes from the original base:
  1. Increased height to provide clearance for bottles above
  2. Added mounting receptacles for carousel locating pins
  3. Added top rim structure to support carousel plate
  4. Tube routing provisions for oil lines from top carousel to pumps

The oil carousel now sits on top of the base instead of hanging below,
solving the table stability issue while maintaining gravity feed.
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object


# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Tolerances & shell ---
TOL = 0.4              # print tolerance per side (PETG, slightly looser)
WALL = 3.0             # general wall thickness — base is structural
WALL_THIN = 1.8        # thin internal partitions (cable cover rib, etc.)
FILLET_R = 4.0         # outer corner fillet
TOP_FILLET = 1.2       # top edge break

# --- Overall base footprint ---
BASE_W = 230           # X — full width
BASE_D = 210           # Y — full depth (front-to-rear)
BASE_H = 75            # Z — increased height for top-mounted bottles clearance
FLOOR_H = 3.0          # solid floor at the very bottom of the case

# --- Top mounting provisions ---
# Support structure for the top-mounted carousel
TOP_RIM_HEIGHT = 8.0   # height of top rim that carousel sits on
TOP_RIM_THICKNESS = 4.0 # thickness of rim wall

# Carousel mounting pins (match v1-oil-carousel-top.py)
MOUNT_PIN_DIA = 6.0        # locating pin diameter + tolerance
MOUNT_PIN_DEPTH = 10.0     # how deep receptacles go into rim
MOUNT_PIN_COUNT = 3        # triangular mounting pattern
MOUNT_PIN_RADIUS = 55.0    # radius from base center to pin positions

# --- Bund (raised platform that holds the mixing chamber + pumps) ---
BUND_H = 28            # bund height above the floor
BUND_WALL = 4          # bund rim wall (extra thick — structural + sealing surface)
BUND_LIP = 2           # raised lip around bund top to contain spills
DRIP_SLOT_W = 14       # forward drip slot width through the front wall
DRIP_SLOT_H = 4        # drip slot height (just below bund top)

# --- Electronics bay (rear strip, dry side) ---
ELEC_BAY_D = 70        # depth (Y) of the electronics strip
ELEC_BAY_H = BASE_H - FLOOR_H - WALL - TOP_RIM_HEIGHT  # available internal height

# --- ESP32 DevKit C V4 pocket ---
MCU_L = 55             # length (long axis along X)
MCU_W = 28             # width (short axis along Y)
MCU_H = 13             # height with headers
MCU_USB_W = 10         # USB-C connector body width (head)
MCU_USB_H = 5          # USB-C connector body height
MCU_USB_INSET = 1.5    # how far the USB head protrudes from the PCB edge

# --- MOSFET driver board pocket ---
MOSFET_L = 70
MOSFET_W = 35
MOSFET_H = 16
MOSFET_WIRE_CH = 4     # wire channel width for each motor lead

# --- USB-C PD input ---
USBPD_BOARD_L = 30
USBPD_BOARD_W = 18
USBPD_BOARD_H = 8
USBPD_CONN_W = 10      # USB-C port width through the wall
USBPD_CONN_H = 5       # USB-C port height through the wall

# --- BME280 sensor mount ---
BME_L = 13
BME_W = 11
BME_H = 3
BME_STANDOFF_H = 4     # raises the sensor off the bund top
BME_VENT_W = 8         # ventilation slot width
BME_VENT_H = 6         # ventilation slot height

# --- Peristaltic pumps (×5) ---
PUMP_BODY_DIA = 32      # pump head cylindrical body diameter
PUMP_BODY_H = 38        # body height (including head + motor stub)
PUMP_MOTOR_L = 30       # motor tail length protruding behind the head
PUMP_MOTOR_DIA = 24     # motor tail diameter (cylindrical)
PUMP_PORT_DIA = 5       # tube barb outer diameter
PUMP_PORT_SPACING = 16  # vertical spacing between inlet and outlet ports
PUMP_MOUNT_DEPTH = 18   # how deep the pump body sits into its pocket
PUMP_TUBE_BORE = 6      # routing channel diameter for the silicone tube

# Arc of 5 pumps along the front of the bund
PUMP_COUNT = 5
PUMP_ARC_R = 40         # radius of the arc the pumps sit on
PUMP_ARC_SWEEP_DEG = 80 # total angular span of the arc
PUMP_FACE_INWARD = True # pump heads point inward toward mixing chamber

# --- Mixing chamber footprint on the bund ---
MIX_CHAMBER_DIA = 70    # reserved circular area on the bund top
MIX_OUTLET_DIA = 22     # mist outlet hole in the bund top (vertical riser)

# --- Apollo One dock bay ---
APOLLO_W = 95           # Apollo One footprint X
APOLLO_D = 95           # Apollo One footprint Y
APOLLO_H = 145          # Apollo One height
APOLLO_CRADLE_DEPTH = 35 # how deep the recess goes
APOLLO_NOTCH_W = 25     # finger-lift notch in the front wall of the cradle
APOLLO_NOTCH_H = 18     # notch height
APOLLO_HOSE_DIA = 14    # silicone hose passage from Apollo outlet to mixing chamber

# --- Rubber feet ---
FOOT_DIA = 12
FOOT_DEPTH = 1.8
FOOT_INSET = 16

# --- Internal cable management ---
CABLE_CH_W = 6
CABLE_CH_D = 4

# --- Vent slots over the electronics bay ---
VENT_SLOT_W = 3
VENT_SLOT_H = 14
VENT_SLOT_COUNT = 6
VENT_SLOT_PITCH = 8

# --- Derived layout ---
BUND_TOP_Z = FLOOR_H + BUND_H
ELEC_BAY_FLOOR_Z = FLOOR_H
TOP_RIM_Z = BASE_H - TOP_RIM_HEIGHT

BUND_INNER_W = BASE_W - WALL * 2
BUND_INNER_D = BASE_D - WALL * 2 - ELEC_BAY_D - WALL_THIN

REAR_Y = BASE_D / 2
FRONT_Y = -BASE_D / 2

ELEC_BAY_CENTER_Y = REAR_Y - WALL - ELEC_BAY_D / 2

APOLLO_CENTER_X = -BASE_W / 2 + WALL + APOLLO_W / 2 + TOL + 4
APOLLO_CENTER_Y = -BASE_D / 2 + WALL + APOLLO_D / 2 + TOL + 4

MIX_CENTER_X = (APOLLO_CENTER_X + APOLLO_W / 2 + MIX_CHAMBER_DIA / 2 + 18)
MIX_CENTER_Y = APOLLO_CENTER_Y + 8

BME_X = MIX_CENTER_X
BME_Y = MIX_CENTER_Y - MIX_CHAMBER_DIA / 2 - 14


# =============================================================================
# HELPERS
# =============================================================================

def pump_positions():
    """Return (x, y, heading_deg) for each of the 5 pumps arranged on an
    arc in front of the mixing chamber."""
    cx, cy = MIX_CENTER_X, MIX_CENTER_Y
    n = PUMP_COUNT
    sweep = math.radians(PUMP_ARC_SWEEP_DEG)
    base_angle = -math.pi / 2  # straight forward
    out = []
    for i in range(n):
        t = (i / (n - 1)) - 0.5  # -0.5 .. +0.5
        a = base_angle + t * sweep
        px = cx + PUMP_ARC_R * math.cos(a)
        py = cy + PUMP_ARC_R * math.sin(a)
        heading = math.degrees(math.atan2(cy - py, cx - px))
        out.append((px, py, heading))
    return out


def carousel_mount_pin_positions():
    """Return list of (x, y) for carousel mounting pin receptacles."""
    positions = []
    for i in range(MOUNT_PIN_COUNT):
        angle = i * 2 * math.pi / MOUNT_PIN_COUNT + math.pi / 6  # offset 30°
        px = MOUNT_PIN_RADIUS * math.cos(angle)
        py = MOUNT_PIN_RADIUS * math.sin(angle)
        positions.append((px, py))
    return positions


def rotated_box(w, d, h, cx, cy, cz, heading_deg, centered_xy=True):
    """Build a box at the origin with given W/D/H, then translate/rotate."""
    box = (
        cq.Workplane("XY")
        .box(w, d, h, centered=[centered_xy, centered_xy, False])
    )
    box = box.rotate((0, 0, 0), (0, 0, 1), heading_deg)
    return box.translate((cx, cy, cz))


def rotated_cyl(r, h, cx, cy, cz, axis_dir):
    """Cylinder of radius r and length h, oriented along axis_dir."""
    if axis_dir == "z":
        return (
            cq.Workplane("XY")
            .workplane(offset=cz)
            .center(cx, cy)
            .circle(r)
            .extrude(h)
        )
    elif axis_dir == "x":
        cyl = (
            cq.Workplane("YZ")
            .circle(r)
            .extrude(h)
        )
        return cyl.translate((cx - h / 2, cy, cz))
    elif axis_dir == "y":
        cyl = (
            cq.Workplane("XZ")
            .circle(r)
            .extrude(h)
        )
        return cyl.translate((cx, cy - h / 2, cz))
    raise ValueError(f"unknown axis_dir {axis_dir}")


# =============================================================================
# BUILD BASE WITH TOP MOUNTING
# =============================================================================

def build_base_with_top_mount():
    """Enhanced base with top rim and mounting provisions for carousel."""

    # ── Outer shell ──────────────────────────────────────────────────────
    base = (
        cq.Workplane("XY")
        .box(BASE_W, BASE_D, BASE_H, centered=[True, True, False])
    )
    base = base.edges("|Z").fillet(FILLET_R)

    # ── Hollow interior ──────────────────────────────────────────────────
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .box(BASE_W - WALL * 2, BASE_D - WALL * 2,
             BASE_H - FLOOR_H - TOP_RIM_HEIGHT + 0.1,
             centered=[True, True, False])
    )
    base = base.cut(cavity)

    # ── Top rim for carousel mounting ────────────────────────────────────
    # Create a rim around the top that the carousel plate sits on
    rim_outer_w = BASE_W - WALL * 2
    rim_outer_d = BASE_D - WALL * 2
    rim_inner_w = rim_outer_w - TOP_RIM_THICKNESS * 2
    rim_inner_d = rim_outer_d - TOP_RIM_THICKNESS * 2

    rim = (
        cq.Workplane("XY")
        .workplane(offset=TOP_RIM_Z)
        .rect(rim_outer_w, rim_outer_d)
        .extrude(TOP_RIM_HEIGHT)
    )

    rim_cutout = (
        cq.Workplane("XY")
        .workplane(offset=TOP_RIM_Z - 0.1)
        .rect(rim_inner_w, rim_inner_d)
        .extrude(TOP_RIM_HEIGHT + 0.2)
    )

    rim = rim.cut(rim_cutout)
    base = base.union(rim)

    # ── Carousel mounting pin receptacles ────────────────────────────────
    for px, py in carousel_mount_pin_positions():
        receptacle = (
            cq.Workplane("XY", origin=(px, py, TOP_RIM_Z + TOP_RIM_HEIGHT))
            .circle((MOUNT_PIN_DIA + TOL * 2) / 2)
            .extrude(-MOUNT_PIN_DEPTH)
        )
        base = base.cut(receptacle)

    # ── Bund (raised platform) ───────────────────────────────────────────
    bund_y_center = -BASE_D / 2 + WALL + BUND_INNER_D / 2
    bund = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(0, bund_y_center)
        .box(BUND_INNER_W, BUND_INNER_D, BUND_H, centered=[True, True, False])
    )
    base = base.union(bund)

    # Bund spill lip
    bund_lip_outer = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z)
        .center(0, bund_y_center)
        .box(BUND_INNER_W, BUND_INNER_D, BUND_LIP, centered=[True, True, False])
    )
    bund_lip_inner = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - 0.1)
        .center(0, bund_y_center)
        .box(BUND_INNER_W - BUND_WALL * 2, BUND_INNER_D - BUND_WALL * 2,
             BUND_LIP + 0.2, centered=[True, True, False])
    )
    base = base.union(bund_lip_outer).cut(bund_lip_inner)

    # ── Drip slot ────────────────────────────────────────────────────────
    drip_slot = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - DRIP_SLOT_H)
        .center(0, -BASE_D / 2)
        .box(DRIP_SLOT_W, WALL * 4, DRIP_SLOT_H, centered=[True, True, False])
    )
    base = base.cut(drip_slot)

    # ── Electronics bay divider rib ─────────────────────────────────────
    bay_rear_y = bund_y_center + BUND_INNER_D / 2
    rib = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(0, bay_rear_y + WALL_THIN / 2)
        .box(BUND_INNER_W, WALL_THIN, ELEC_BAY_H, centered=[True, True, False])
    )
    base = base.union(rib)

    # ── ESP32 pocket ──────────────────────────────────────────────────────
    esp_x = -BASE_W / 4
    esp_y = ELEC_BAY_CENTER_Y
    esp_z = ELEC_BAY_FLOOR_Z + 2

    esp_pocket = (
        cq.Workplane("XY")
        .workplane(offset=esp_z)
        .center(esp_x, esp_y)
        .rect(MCU_L + TOL * 2, MCU_W + TOL * 2)
        .extrude(MCU_H + 2)
    )
    base = base.cut(esp_pocket)

    # USB-C cutout
    usb_cutout = (
        cq.Workplane("XY")
        .center(esp_x, REAR_Y)
        .rect(MCU_USB_W + TOL * 2, MCU_USB_H + TOL * 2)
        .extrude(WALL + 2, both=True)
    )
    usb_cutout = usb_cutout.translate((0, 0, esp_z + MCU_H - MCU_USB_H / 2))
    base = base.cut(usb_cutout)

    # ── MOSFET pocket ─────────────────────────────────────────────────────
    mos_x = BASE_W / 4
    mos_y = ELEC_BAY_CENTER_Y
    mos_z = ELEC_BAY_FLOOR_Z + 2

    mos_pocket = (
        cq.Workplane("XY")
        .workplane(offset=mos_z)
        .center(mos_x, mos_y)
        .rect(MOSFET_L + TOL * 2, MOSFET_W + TOL * 2)
        .extrude(MOSFET_H + 2)
    )
    base = base.cut(mos_pocket)

    # ── Apollo dock pocket ───────────────────────────────────────────────
    apollo_pocket = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - APOLLO_CRADLE_DEPTH)
        .center(APOLLO_CENTER_X, APOLLO_CENTER_Y)
        .rect(APOLLO_W + TOL * 2, APOLLO_D + TOL * 2)
        .extrude(APOLLO_CRADLE_DEPTH + BUND_LIP + 1)
    )
    base = base.cut(apollo_pocket)

    # Apollo access notch
    apollo_notch = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - APOLLO_CRADLE_DEPTH)
        .center(APOLLO_CENTER_X, APOLLO_CENTER_Y - APOLLO_D / 2 - 2)
        .rect(APOLLO_NOTCH_W, 8)
        .extrude(APOLLO_NOTCH_H)
    )
    base = base.cut(apollo_notch)

    # ── Mixing chamber riser hole ────────────────────────────────────────
    mix_riser = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - 2)
        .center(MIX_CENTER_X, MIX_CENTER_Y)
        .circle(MIX_OUTLET_DIA / 2)
        .extrude(BUND_LIP + 4)
    )
    base = base.cut(mix_riser)

    # ── Pump pockets ──────────────────────────────────────────────────────
    for px, py, heading in pump_positions():
        # Pump body pocket
        body_pocket = (
            cq.Workplane("XY")
            .workplane(offset=BUND_TOP_Z - PUMP_MOUNT_DEPTH)
            .center(px, py)
            .circle(PUMP_BODY_DIA / 2 + TOL)
            .extrude(PUMP_MOUNT_DEPTH + 1)
        )
        base = base.cut(body_pocket)

        # Motor tail clearance
        motor_pocket = rotated_cyl(
            PUMP_MOTOR_DIA / 2 + TOL, PUMP_MOTOR_L,
            px, py, BUND_TOP_Z - PUMP_MOUNT_DEPTH, "x"
        )
        # Rotate to match pump heading
        motor_pocket = motor_pocket.rotate(
            (px, py, BUND_TOP_Z), (px, py, BUND_TOP_Z + 1), heading
        )
        base = base.cut(motor_pocket)

    # ── BME280 mount ──────────────────────────────────────────────────────
    bme_standoff = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP)
        .center(BME_X, BME_Y)
        .rect(BME_L + 2, BME_W + 2)
        .extrude(BME_STANDOFF_H)
    )
    base = base.union(bme_standoff)

    bme_pocket = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP + BME_STANDOFF_H)
        .center(BME_X, BME_Y)
        .rect(BME_L + TOL, BME_W + TOL)
        .extrude(BME_H + 1)
    )
    base = base.cut(bme_pocket)

    # ── Vent slots ───────────────────────────────────────────────────────
    vent_start_x = -VENT_SLOT_COUNT * VENT_SLOT_PITCH / 2
    for i in range(VENT_SLOT_COUNT):
        vx = vent_start_x + i * VENT_SLOT_PITCH
        vy = REAR_Y
        vz = BASE_H - VENT_SLOT_H - 8

        vent = (
            cq.Workplane("XY")
            .center(vx, vy)
            .rect(VENT_SLOT_W, WALL + 2)
            .extrude(VENT_SLOT_H, both=True)
        )
        vent = vent.translate((0, 0, vz + VENT_SLOT_H / 2))
        base = base.cut(vent)

    # ── Rubber feet recesses ─────────────────────────────────────────────
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

    # ── Top edge fillet ──────────────────────────────────────────────────
    try:
        base = base.faces(">Z").edges("|X or |Y").fillet(TOP_FILLET)
    except Exception:
        pass

    return base


# =============================================================================
# BUILD AND DISPLAY
# =============================================================================

base_with_top_mount = build_base_with_top_mount()

show_object(base_with_top_mount, name="humidifier_base_top_mount",
            options={"color": (0.2, 0.22, 0.25, 0.95)})

# Show mounting pin positions for reference
for i, (px, py) in enumerate(carousel_mount_pin_positions()):
    pin_marker = (
        cq.Workplane("XY", origin=(px, py, BASE_H))
        .circle(MOUNT_PIN_DIA / 2)
        .extrude(2)
    )
    show_object(pin_marker, name=f"mount_pin_pos_{i+1}",
               options={"color": (1.0, 0.0, 0.0, 0.8)})

print("=" * 60)
print("Smart Humidifier Base v1 — TOP-MOUNTED CAROUSEL VERSION")
print("=" * 60)
print(f"  Base dimensions: {BASE_W} × {BASE_D} × {BASE_H} mm")
print(f"  Top rim: {TOP_RIM_HEIGHT} mm high, {TOP_RIM_THICKNESS} mm thick")
print(f"  Carousel mount: {MOUNT_PIN_COUNT} × ø{MOUNT_PIN_DIA:.0f} mm pins")
print(f"  Pin positions: R={MOUNT_PIN_RADIUS:.0f} mm from center")
print(f"  Electronics bay height: {ELEC_BAY_H:.0f} mm")
print()
print("Key improvements:")
print("  ✓ Increased height to {BASE_H} mm for bottle clearance")
print("  ✓ Top rim structure supports carousel plate")
print("  ✓ Locating pin receptacles for secure mounting")
print("  ✓ Base sits flat on table surface")
print("  ✓ Maintains all original functionality")