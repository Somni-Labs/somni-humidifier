"""
Smart Humidifier — Main Enclosure Base — V1

Foundation of the unit. Houses all electronics, mounts the 5 peristaltic
pumps that meter scented oils into the mist stream, provides a side dock
for the Apollo One ultrasonic mister to sit alongside, and routes wiring
internally with a waterproof "wet side / dry side" split.

Top-down layout (looking at the unit from above, +Y is rear):

      ┌──────────────────────────────────────────────────────────────┐
      │  USB-C PD  ESP32 pocket    MOSFET driver pocket   [vents]    │  ← rear wall
      │  ────────────────────────────────────────────────────────    │
      │                                                              │
      │   ┌──────────────┐   ╭───────── mixing chamber ─────────╮    │
      │   │              │   │   (raised, waterproof bund)      │    │
      │   │  Apollo One  │   │                                  │    │
      │   │   dock bay   │   │     pump #1   #2   #3   #4   #5  │    │
      │   │              │   │     (arc, tubes drop to oils)    │    │
      │   └──────────────┘   ╰──────────────────────────────────╯    │
      │                              BME280 (near mist outlet)       │
      └──────────────────────────────────────────────────────────────┘
                                                                ← front

Wet side / dry side rule:
  - The mixing chamber sits on a raised bund inside the case. Any leak
    drains forward to the front lip and out via a drip slot, NEVER
    backward into the electronics bay.
  - Pump tube inlets (from oil bottles below) and outlets (to mixing
    chamber above) are routed through grommet holes in the bund — no
    electronics live directly beneath any of these holes.
  - Electronics live along the REAR strip of the case; pumps and Apollo
    dock live in the front. The two zones are separated by a printed
    rib that doubles as a cable channel cover.

Power & data:
  USB-C PD (rear) → distribution bus → ESP32 (3.3V via on-board LDO),
                                       MOSFET driver board (5V/12V rail,
                                       gates 5x pump motors), BME280
                                       (3.3V, I²C to ESP32).

Print plan:
  QIDI Q2 plate is 245×255mm. The base footprint as drawn is 230×210mm
  which fits comfortably. If a future revision grows past the plate, the
  base is intended to split along Y=0 into front (pumps + dock + mixing)
  and rear (electronics) halves, joined by dovetail keys — see TODO at
  the end of this file. V1 prints as a single part.

All measurements with `TODO` are placeholders pending caliper readings
of the real components (Apollo One, peristaltic pumps in hand, USB-C PD
breakout chosen, etc.). Replace these and re-render before printing.

Loadable by cadquery-server via show_object().
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
# Fits within QIDI Q2 245×255mm with margin. If future revisions grow,
# see SPLIT TODO at the bottom of this file.
BASE_W = 230           # X — full width
BASE_D = 210           # Y — full depth (front-to-rear)
BASE_H = 55            # Z — tall enough for oil bottles below the bund
                       # TODO: confirm once oil bottle dimensions are picked
FLOOR_H = 3.0          # solid floor at the very bottom of the case

# --- Bund (raised platform that holds the mixing chamber + pumps) ---
# Acts as the waterproof divider between the "wet" top zone and the
# "dry" electronics bay below. Any leak from the mixing chamber drains
# forward off the bund and out the front drip slot.
BUND_H = 28            # bund height above the floor (oil bottles fit beneath)
                       # TODO: caliper actual oil bottle height
BUND_WALL = 4          # bund rim wall (extra thick — structural + sealing surface)
BUND_LIP = 2           # raised lip around bund top to contain spills
DRIP_SLOT_W = 14       # forward drip slot width through the front wall
DRIP_SLOT_H = 4        # drip slot height (just below bund top)

# --- Electronics bay (rear strip, dry side) ---
# Runs the full width of the case along the rear wall. Houses ESP32,
# MOSFET driver, USB-C PD breakout, and the distribution bus.
ELEC_BAY_D = 70        # depth (Y) of the electronics strip
                       # measured from the rear wall inward
ELEC_BAY_H = BASE_H - FLOOR_H - WALL  # available internal height in the bay
                                      # (open top — lid will close it later)

# --- ESP32 DevKit C V4 pocket ---
# Same module as the pill dispenser. USB-C port faces the REAR (-Y wall
# in this design's convention) so it's accessible without opening the lid.
# NOTE: this design uses the +Y face as the rear wall. The USB cutout
# is in the +Y rear wall, in line with the ESP32's USB connector.
MCU_L = 55             # length (long axis along X)
MCU_W = 28             # width (short axis along Y)
MCU_H = 13             # height with headers
MCU_USB_W = 10         # USB-C connector body width (head)
MCU_USB_H = 5          # USB-C connector body height
MCU_USB_INSET = 1.5    # how far the USB head protrudes from the PCB edge
                       # TODO: confirm with caliper on actual board

# --- MOSFET driver board pocket ---
# Generic 5-channel N-MOSFET / IRF520 module strip. One channel per pump.
# Sits to the right of the ESP32 along the rear strip so the wires to
# each pump only need to travel forward, never crossing the ESP32.
# TODO: caliper actual board once selected. Reasonable placeholder for
# a 5-channel breakout: ~70×35×16mm including pin headers.
MOSFET_L = 70
MOSFET_W = 35
MOSFET_H = 16
MOSFET_WIRE_CH = 4     # wire channel width for each motor lead

# --- USB-C PD input ---
# Rear-accessible 60W USB-C PD trigger / breakout that feeds the
# distribution bus. Cutout in the rear wall mates with the breakout's
# connector. Distinct from the ESP32's data USB.
# TODO: pick a specific PD breakout and update dimensions.
USBPD_BOARD_L = 30
USBPD_BOARD_W = 18
USBPD_BOARD_H = 8
USBPD_CONN_W = 10      # USB-C port width through the wall
USBPD_CONN_H = 5       # USB-C port height through the wall

# --- BME280 sensor mount ---
# Tiny I²C module (~13×10×3mm PCB). Positioned at the front of the case
# near the mist outlet so it reads humidity from the mist plume rather
# than from the dry rear bay. Mounted on a printed standoff with a
# ventilation slot in the surrounding wall so air can flow past it.
BME_L = 13
BME_W = 11
BME_H = 3
BME_STANDOFF_H = 4     # raises the sensor off the bund top
BME_VENT_W = 8         # ventilation slot width
BME_VENT_H = 6         # ventilation slot height

# --- Peristaltic pumps (×5) ---
# Small 12V peristaltic pumps (e.g. Kamoer KP, generic Adafruit-style).
# Each pump has a roughly cylindrical body with a rectangular motor tail
# and two short barbed tube ports (inlet from oil bottle below, outlet
# to mixing chamber above).
# TODO: confirm all of these by caliper on the actual pumps once they
# arrive. Numbers below are reasonable placeholders for a generic
# 12V peristaltic dosing pump in the ~30mm body class.
PUMP_BODY_DIA = 32      # pump head cylindrical body diameter
PUMP_BODY_H = 38        # body height (including head + motor stub)
PUMP_MOTOR_L = 30       # motor tail length protruding behind the head
PUMP_MOTOR_DIA = 24     # motor tail diameter (cylindrical)
PUMP_PORT_DIA = 5       # tube barb outer diameter
PUMP_PORT_SPACING = 16  # vertical spacing between inlet and outlet ports
PUMP_MOUNT_DEPTH = 18   # how deep the pump body sits into its pocket
PUMP_TUBE_BORE = 6      # routing channel diameter for the silicone tube
                        # (slightly larger than tube OD for easy threading)

# Arc of 5 pumps along the front of the bund.
PUMP_COUNT = 5
PUMP_ARC_R = 95         # radius of the arc the pumps sit on
PUMP_ARC_SWEEP_DEG = 80 # total angular span of the arc
                        # (40° each side of center → gentle smile)
PUMP_FACE_INWARD = True # pump heads point inward toward mixing chamber

# --- Mixing chamber footprint on the bund ---
# This file does NOT model the mixing chamber itself (that's a separate
# part / work item). It only reserves the central area on the bund and
# routes 5 outlet tubes plus a feed from the Apollo One mist plume.
MIX_CHAMBER_DIA = 70    # reserved circular area on the bund top
                        # TODO: confirm once the mixing chamber is designed
MIX_OUTLET_DIA = 22     # mist outlet hole in the bund top (vertical riser)
                        # TODO: match to the mixing chamber's outlet stub

# --- Apollo One dock bay ---
# Recessed cradle on the LEFT side of the case where the Apollo One
# ultrasonic humidifier unit sits. The Apollo's mist outlet aligns with
# the mixing chamber feed via a short silicone hose between them.
# IMPORTANT: dimensions below are PLACEHOLDERS. Apollo One should be
# measured with calipers once it's in hand. The cradle is deliberately
# loose (uses TOL on all sides) so the unit can be lifted out for
# refilling the water bottle.
# TODO: replace ALL Apollo dimensions with measured values.
APOLLO_W = 95           # Apollo One footprint X
APOLLO_D = 95           # Apollo One footprint Y
APOLLO_H = 145          # Apollo One height (the bay only cradles the lower
                        # portion — the unit extends above the base)
APOLLO_CRADLE_DEPTH = 35 # how deep the recess goes (just enough to hold it)
APOLLO_NOTCH_W = 25     # finger-lift notch in the front wall of the cradle
APOLLO_NOTCH_H = 18     # notch height
APOLLO_HOSE_DIA = 14    # silicone hose passage from Apollo outlet to
                        # mixing chamber feed
                        # TODO: match to chosen hose ID + wall

# --- Rubber feet ---
FOOT_DIA = 12
FOOT_DEPTH = 1.8
FOOT_INSET = 16

# --- Internal cable management ---
# Cable channels run from the rear electronics bay forward to each pump
# and to the BME280. A removable rib (printed separately or just snaps
# in) covers them — that rib is NOT modeled here, just the channels
# themselves cut into the floor.
CABLE_CH_W = 6
CABLE_CH_D = 4

# --- Vent slots over the electronics bay ---
# Passive ventilation along the rear wall so the MOSFETs don't cook.
VENT_SLOT_W = 3
VENT_SLOT_H = 14
VENT_SLOT_COUNT = 6
VENT_SLOT_PITCH = 8

# --- Derived layout ---
# Bund occupies the front zone, leaving ELEC_BAY_D at the rear for
# electronics. Bund top sits at FLOOR_H + BUND_H.
BUND_TOP_Z = FLOOR_H + BUND_H
ELEC_BAY_FLOOR_Z = FLOOR_H

# The bund spans X across the whole interior but only fills the FRONT
# portion of Y, stopping ELEC_BAY_D shy of the rear wall.
BUND_INNER_W = BASE_W - WALL * 2
BUND_INNER_D = BASE_D - WALL * 2 - ELEC_BAY_D - WALL_THIN  # internal Y span

# Coordinates of important features (X, Y) in the base's centered frame.
# Rear wall is at +Y, front wall at -Y, left at -X, right at +X.
REAR_Y = BASE_D / 2
FRONT_Y = -BASE_D / 2

# Electronics bay center: midline between rear wall and bund rear edge.
ELEC_BAY_CENTER_Y = REAR_Y - WALL - ELEC_BAY_D / 2

# Apollo dock sits on the LEFT side of the bund.
APOLLO_CENTER_X = -BASE_W / 2 + WALL + APOLLO_W / 2 + TOL + 4
APOLLO_CENTER_Y = -BASE_D / 2 + WALL + APOLLO_D / 2 + TOL + 4

# Mixing chamber center: roughly center-right of the bund area,
# leaving room for the Apollo dock on the left.
MIX_CENTER_X = (APOLLO_CENTER_X + APOLLO_W / 2 + MIX_CHAMBER_DIA / 2 + 18)
MIX_CENTER_Y = APOLLO_CENTER_Y + 8  # slightly behind Apollo center

# BME280 mount: in front of the mixing chamber outlet, in the mist plume.
BME_X = MIX_CENTER_X
BME_Y = MIX_CENTER_Y - MIX_CHAMBER_DIA / 2 - 14


# =============================================================================
# HELPERS
# =============================================================================

def pump_positions():
    """Return (x, y, heading_deg) for each of the 5 pumps arranged on an
    arc in front of the mixing chamber.

    Pumps face inward toward the mixing chamber (heading is the direction
    the pump head's outlet barb points).
    """
    cx, cy = MIX_CENTER_X, MIX_CENTER_Y
    n = PUMP_COUNT
    sweep = math.radians(PUMP_ARC_SWEEP_DEG)
    # Arc opens toward -Y (front), so angle 0 means due south of mix center.
    base_angle = -math.pi / 2  # straight forward
    out = []
    for i in range(n):
        # Spread evenly across the sweep.
        t = (i / (n - 1)) - 0.5  # -0.5 .. +0.5
        a = base_angle + t * sweep
        px = cx + PUMP_ARC_R * math.cos(a)
        py = cy + PUMP_ARC_R * math.sin(a)
        # Heading: pump points BACK toward mixing chamber center.
        heading = math.degrees(math.atan2(cy - py, cx - px))
        out.append((px, py, heading))
    return out


def rotated_box(w, d, h, cx, cy, cz, heading_deg, centered_xy=True):
    """Build a box at the origin with given W/D/H, then translate/rotate
    so it sits at (cx, cy, cz) and its long axis (X) points along
    `heading_deg` (degrees, CCW from +X)."""
    box = (
        cq.Workplane("XY")
        .box(w, d, h, centered=[centered_xy, centered_xy, False])
    )
    box = box.rotate((0, 0, 0), (0, 0, 1), heading_deg)
    return box.translate((cx, cy, cz))


def rotated_cyl(r, h, cx, cy, cz, axis_dir):
    """Cylinder of radius r and length h, oriented along axis_dir
    ('x', 'y', 'z'), centered at (cx, cy, cz) for x/y axes and resting
    on cz for z axis."""
    if axis_dir == "z":
        return (
            cq.Workplane("XY")
            .workplane(offset=cz)
            .center(cx, cy)
            .circle(r)
            .extrude(h)
        )
    elif axis_dir == "x":
        # Cylinder along X: build on YZ plane.
        cyl = (
            cq.Workplane("YZ")
            .circle(r)
            .extrude(h)
        )
        # Extrudes in +X. Recenter so midpoint sits at cx.
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
# BUILD BASE
# =============================================================================

def build_base():
    """Main enclosure base — open-top tub, internal bund, electronics bay,
    pump pockets, Apollo dock, BME280 mount, vents, feet."""

    # ── Outer shell ──────────────────────────────────────────────────────
    base = (
        cq.Workplane("XY")
        .box(BASE_W, BASE_D, BASE_H, centered=[True, True, False])
    )
    base = base.edges("|Z").fillet(FILLET_R)

    # ── Hollow interior — full electronics-bay-depth cavity ──────────────
    # We carve out everything inside the walls down to FLOOR_H. The bund
    # is then added back in as a solid volume occupying the front zone.
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .box(BASE_W - WALL * 2, BASE_D - WALL * 2, BASE_H - FLOOR_H + 1,
             centered=[True, True, False])
    )
    base = base.cut(cavity)

    # ── Bund (raised platform for pumps + mixing chamber + Apollo) ───────
    # Spans the full inner width and the front portion of the depth,
    # stopping ELEC_BAY_D shy of the rear wall.
    bund_y_center = -BASE_D / 2 + WALL + BUND_INNER_D / 2
    bund = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(0, bund_y_center)
        .box(BUND_INNER_W, BUND_INNER_D, BUND_H,
             centered=[True, True, False])
    )
    base = base.union(bund)

    # Bund top spill lip — raised rim around the bund top so any drips
    # are contained and only escape via the forward drip slot.
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

    # Forward drip slot — through the bund's front wall AND the case's
    # front wall, so any spill drains out the front of the unit (away
    # from electronics, which live in the rear).
    drip_slot = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - DRIP_SLOT_H)
        .center(0, -BASE_D / 2)
        .box(DRIP_SLOT_W, WALL * 4, DRIP_SLOT_H,
             centered=[True, True, False])
    )
    base = base.cut(drip_slot)

    # ── Electronics bay floor — keep the rear strip hollow ───────────────
    # The cavity cut above already removed material in the bay; nothing
    # more to do here. The bay is bounded by the rear wall (+Y), the
    # bund's rear face (at bund_y_center + BUND_INNER_D/2), and the
    # left/right side walls.
    bay_rear_y = bund_y_center + BUND_INNER_D / 2  # bund's rear face

    # Cable-channel cover rib runs along the bund's rear face at floor
    # level, separating the bay from the bund-shadow zone. The rib has
    # gaps for wires to enter each pump's vertical riser.
    # We model it as a thin upstanding wall the height of the bay.
    rib = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(0, bay_rear_y + WALL_THIN / 2)
        .box(BUND_INNER_W, WALL_THIN, ELEC_BAY_H - 6,
             centered=[True, True, False])
    )
    base = base.union(rib)

    # ── ESP32 pocket (rear strip, left side) ─────────────────────────────
    esp_x = -BASE_W / 2 + WALL + MCU_L / 2 + 8
    esp_y = ELEC_BAY_CENTER_Y
    esp_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(esp_x, esp_y)
        .rect(MCU_L + TOL * 2, MCU_W + TOL * 2)
        .extrude(MCU_H + 2)
    )
    base = base.cut(esp_pocket)

    # USB-C cutout through the REAR wall, aligned with the ESP32's USB
    # connector. ESP32's USB is on the short end facing +Y (rear).
    esp_usb_cut = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 2)
        .center(esp_x, REAR_Y)
        .box(MCU_USB_W + 2, WALL * 4, MCU_USB_H + 2,
             centered=[True, True, False])
    )
    base = base.cut(esp_usb_cut)

    # ── MOSFET driver pocket (rear strip, middle) ────────────────────────
    mos_x = esp_x + MCU_L / 2 + MOSFET_L / 2 + 10
    mos_y = ELEC_BAY_CENTER_Y
    mos_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(mos_x, mos_y)
        .rect(MOSFET_L + TOL * 2, MOSFET_W + TOL * 2)
        .extrude(MOSFET_H + 2)
    )
    base = base.cut(mos_pocket)

    # ── USB-C PD input (rear strip, right side) ──────────────────────────
    pd_x = BASE_W / 2 - WALL - USBPD_BOARD_L / 2 - 8
    pd_y = ELEC_BAY_CENTER_Y
    pd_pocket = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 0.5)
        .center(pd_x, pd_y)
        .rect(USBPD_BOARD_L + TOL * 2, USBPD_BOARD_W + TOL * 2)
        .extrude(USBPD_BOARD_H + 2)
    )
    base = base.cut(pd_pocket)

    # PD USB-C jack through the rear wall.
    pd_usb_cut = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H + 2)
        .center(pd_x, REAR_Y)
        .box(USBPD_CONN_W + 2, WALL * 4, USBPD_CONN_H + 2,
             centered=[True, True, False])
    )
    base = base.cut(pd_usb_cut)

    # ── Rear-wall vent slots over the electronics bay ────────────────────
    vent_total_w = (VENT_SLOT_COUNT - 1) * VENT_SLOT_PITCH
    vent_start_x = -vent_total_w / 2
    vent_z = FLOOR_H + MOSFET_H + 6  # above the MOSFET so heat rises out
    for i in range(VENT_SLOT_COUNT):
        vx = vent_start_x + i * VENT_SLOT_PITCH
        # Shift the cluster slightly right to sit above the MOSFET.
        vx += (mos_x - 0)
        # Skip any slot that would collide with the USB-C cutouts.
        if abs(vx - pd_x) < (USBPD_CONN_W / 2 + VENT_SLOT_W) or \
           abs(vx - esp_x) < (MCU_USB_W / 2 + VENT_SLOT_W):
            continue
        slot = (
            cq.Workplane("XY")
            .workplane(offset=vent_z)
            .center(vx, REAR_Y)
            .box(VENT_SLOT_W, WALL * 4, VENT_SLOT_H,
                 centered=[True, True, False])
        )
        base = base.cut(slot)

    # ── Peristaltic pump mounts (5x along the arc) ───────────────────────
    # Each pump sits with its CYLINDRICAL HEAD pressed into a circular
    # pocket cut into the bund top, motor tail extending OUTWARD (away
    # from mixing chamber), tube ports facing INWARD toward the chamber.
    # Below each pump we cut a vertical tube channel through the bund
    # so the inlet hose can reach the oil bottle in the dry zone.
    for px, py, heading in pump_positions():
        # Body pocket: circular bore into the bund, deep enough that the
        # pump head is well retained.
        body_pocket = (
            cq.Workplane("XY")
            .workplane(offset=BUND_TOP_Z - PUMP_MOUNT_DEPTH)
            .center(px, py)
            .circle(PUMP_BODY_DIA / 2 + TOL)
            .extrude(PUMP_MOUNT_DEPTH + 1)
        )
        base = base.cut(body_pocket)

        # Motor tail clearance: cylinder along the pump's heading axis
        # pointing OUTWARD (away from mixing center). Since heading
        # points TOWARD center, the motor tail points opposite (+180°).
        tail_heading = heading + 180
        # Place the tail cylinder so its near end starts at the pump
        # body's outboard face.
        tail_cx = px + math.cos(math.radians(tail_heading)) * (PUMP_MOTOR_L / 2 + 2)
        tail_cy = py + math.sin(math.radians(tail_heading)) * (PUMP_MOTOR_L / 2 + 2)
        # We need a horizontal cylinder oriented along the heading axis.
        # Build along +X then rotate.
        motor_tail = (
            cq.Workplane("YZ")
            .circle(PUMP_MOTOR_DIA / 2 + TOL)
            .extrude(PUMP_MOTOR_L + 4)
        )
        # Motor tail center Z: half the body height above bund top floor
        motor_z = BUND_TOP_Z - PUMP_BODY_H / 2
        # Extruded in +X starting at origin; translate so it spans the
        # tail region centered on (tail_cx, tail_cy, motor_z).
        motor_tail = motor_tail.translate((-(PUMP_MOTOR_L + 4) / 2, 0, motor_z))
        motor_tail = motor_tail.rotate((0, 0, motor_z), (0, 0, 1), tail_heading)
        motor_tail = motor_tail.translate((tail_cx, tail_cy, 0))
        base = base.cut(motor_tail)

        # Tube channel from pump body down through the bund to the oil
        # bottle bay below. Two channels: inlet (rear/lower) and outlet
        # (forward/upper). For simplicity, V1 uses one combined slot at
        # the pump center — the silicone tube run can pick its own
        # path inside the slot.
        # TODO: split into separate inlet/outlet bores once port
        # geometry on the chosen pump is measured.
        tube_drop = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H - 0.5)
            .center(px, py)
            .circle(PUMP_TUBE_BORE / 2 + TOL)
            .extrude(BUND_H + 1)
        )
        base = base.cut(tube_drop)

        # Outlet routing channel along the bund TOP, from pump toward
        # the mixing chamber edge. Shallow groove so the tube can be
        # tucked down and not stick up into whatever sits on the bund.
        out_dx = MIX_CENTER_X - px
        out_dy = MIX_CENTER_Y - py
        out_len = math.hypot(out_dx, out_dy) - MIX_CHAMBER_DIA / 2
        out_heading = math.degrees(math.atan2(out_dy, out_dx))
        groove = (
            cq.Workplane("XY")
            .box(out_len, PUMP_TUBE_BORE + 1, PUMP_TUBE_BORE,
                 centered=[False, True, False])
        )
        groove = groove.rotate((0, 0, 0), (0, 0, 1), out_heading)
        groove = groove.translate((px, py, BUND_TOP_Z - PUMP_TUBE_BORE + 0.1))
        base = base.cut(groove)

    # ── Mixing chamber footprint (reserved bore through bund top) ────────
    # Vertical mist riser hole — the mixing chamber (modeled separately)
    # will seat into this and seal against the surrounding bund top.
    mix_riser = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - 2)
        .center(MIX_CENTER_X, MIX_CENTER_Y)
        .circle(MIX_OUTLET_DIA / 2)
        .extrude(BUND_LIP + 4)
    )
    base = base.cut(mix_riser)

    # Reserved annular ring on the bund top marking the chamber's
    # seating footprint. We engrave a shallow ring as a visual /
    # alignment guide for assembly.
    seat_outer = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP - 0.6)
        .center(MIX_CENTER_X, MIX_CENTER_Y)
        .circle(MIX_CHAMBER_DIA / 2 + 1)
        .extrude(0.8)
    )
    seat_inner = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP - 0.7)
        .center(MIX_CENTER_X, MIX_CENTER_Y)
        .circle(MIX_CHAMBER_DIA / 2 - 1)
        .extrude(1.0)
    )
    base = base.cut(seat_outer.cut(seat_inner))

    # ── Apollo One dock (left-side recessed cradle) ──────────────────────
    # Cut down into the bund top. Apollo sits in this well and can be
    # lifted straight up for refilling its water bottle.
    apollo_pocket = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - APOLLO_CRADLE_DEPTH)
        .center(APOLLO_CENTER_X, APOLLO_CENTER_Y)
        .rect(APOLLO_W + TOL * 2, APOLLO_D + TOL * 2)
        .extrude(APOLLO_CRADLE_DEPTH + BUND_LIP + 1)
    )
    base = base.cut(apollo_pocket)

    # Finger-lift notch in the FRONT face of the cradle so the user can
    # grip the Apollo One to lift it out for refilling.
    apollo_notch = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z - APOLLO_NOTCH_H)
        .center(APOLLO_CENTER_X, APOLLO_CENTER_Y - APOLLO_D / 2 - WALL / 2)
        .box(APOLLO_NOTCH_W, WALL * 3, APOLLO_NOTCH_H + BUND_LIP + 1,
             centered=[True, True, False])
    )
    base = base.cut(apollo_notch)

    # Hose passage from Apollo outlet to the mixing chamber feed.
    # Drilled horizontally through the bund wall between the two pockets.
    # The exact Z and entry point on the Apollo side is TODO once the
    # Apollo's mist outlet location is measured. Placeholder: high up
    # in the cradle, exiting on the side that faces the mixing chamber.
    hose_z = BUND_TOP_Z - 12  # TODO: confirm against Apollo mist outlet height
    hose_x_start = APOLLO_CENTER_X + APOLLO_W / 2
    hose_x_end = MIX_CENTER_X - MIX_CHAMBER_DIA / 2
    hose_len = hose_x_end - hose_x_start
    if hose_len > 0:
        hose = (
            cq.Workplane("YZ")
            .circle(APOLLO_HOSE_DIA / 2)
            .extrude(hose_len + 4)
        )
        hose = hose.translate((hose_x_start - 2,
                               (APOLLO_CENTER_Y + MIX_CENTER_Y) / 2,
                               hose_z))
        base = base.cut(hose)

    # ── BME280 sensor mount (front of the mixing chamber) ────────────────
    # A small standoff platform on the bund top with two M2 boss-pin
    # holes. The sensor PCB rests on the standoff and is held by a pair
    # of self-tap M2 screws (or just press-fit pins; either works for
    # such a small board).
    bme_pad = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP)
        .center(BME_X, BME_Y)
        .rect(BME_L + 4, BME_W + 4)
        .extrude(BME_STANDOFF_H)
    )
    base = base.union(bme_pad)
    # Pocket so the sensor sits flush — only its top is exposed.
    bme_pocket = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP + BME_STANDOFF_H - BME_H)
        .center(BME_X, BME_Y)
        .rect(BME_L + TOL * 2, BME_W + TOL * 2)
        .extrude(BME_H + 0.5)
    )
    base = base.cut(bme_pocket)
    # I²C wire pass-through from the BME280 pad down through the bund
    # and rearward into the electronics bay via the floor-level cable
    # channel.
    bme_wire = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H - 0.5)
        .center(BME_X, BME_Y)
        .rect(CABLE_CH_W, CABLE_CH_D)
        .extrude(BUND_H + BUND_LIP + BME_STANDOFF_H + 1)
    )
    base = base.cut(bme_wire)
    # Ventilation slot in the bund lip just in front of the sensor so
    # mist-laden air can reach it.
    bme_vent = (
        cq.Workplane("XY")
        .workplane(offset=BUND_TOP_Z + BUND_LIP - BME_VENT_H)
        .center(BME_X, BME_Y - (BME_W / 2 + 2))
        .box(BME_VENT_W, 6, BME_VENT_H + 1, centered=[True, True, False])
    )
    base = base.cut(bme_vent)

    # ── Cable channels in the floor (electronics bay → pumps & BME) ──────
    # Shallow grooves from the rear bay forward toward each pump's tube
    # drop and the BME wire run. Wires lay flat in these channels and a
    # snap-on cover (not modeled here) hides them.
    for px, py, _heading in pump_positions():
        dx = px - mos_x
        dy = py - mos_y
        seg_len = math.hypot(dx, dy)
        seg_heading = math.degrees(math.atan2(dy, dx))
        ch = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H - CABLE_CH_D + 0.1)
            .box(seg_len, CABLE_CH_W, CABLE_CH_D,
                 centered=[False, True, False])
        )
        ch = ch.rotate((0, 0, 0), (0, 0, 1), seg_heading)
        ch = ch.translate((mos_x, mos_y, 0))
        base = base.cut(ch)

    # BME wire channel (rear bay → BME mount on the bund).
    dx = BME_X - esp_x
    dy = BME_Y - esp_y
    seg_len = math.hypot(dx, dy)
    seg_heading = math.degrees(math.atan2(dy, dx))
    bme_ch = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H - CABLE_CH_D + 0.1)
        .box(seg_len, CABLE_CH_W, CABLE_CH_D, centered=[False, True, False])
    )
    bme_ch = bme_ch.rotate((0, 0, 0), (0, 0, 1), seg_heading)
    bme_ch = bme_ch.translate((esp_x, esp_y, 0))
    base = base.cut(bme_ch)

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

    # Top edge break.
    base = base.edges(">Z").fillet(TOP_FILLET)

    return base


# =============================================================================
# BUILD AND DISPLAY
# =============================================================================

base = build_base()

show_object(base, name="humidifier_base",
            options={"color": (0.2, 0.22, 0.25, 0.95)})


# =============================================================================
# TODO — follow-up work items for the next revision
# =============================================================================
# 1. Caliper-verify every dimension flagged TODO above:
#    - Apollo One footprint, height, mist-outlet location
#    - Chosen peristaltic pump body, motor tail, port spacing
#    - USB-C PD breakout footprint + connector position
#    - Oil bottle dimensions (sets BUND_H)
# 2. Lid / top cover (separate file): closes over electronics bay, has
#    cutouts that match the bund top, snap-fits to the base perimeter.
# 3. Mixing chamber (separate file): seats into the MIX_OUTLET_DIA bore,
#    receives 5 oil outlets + 1 Apollo mist hose, exhausts upward.
# 4. Cable-channel cover rib (separate file): clips over the floor
#    grooves and the rear-bay rib.
# 5. If footprint outgrows the QIDI Q2 plate (245×255mm), split this
#    base along Y=0 into "front" (pumps + dock + mixing) and "rear"
#    (electronics) halves joined by 4× dovetail keys + M3 cap screws.
