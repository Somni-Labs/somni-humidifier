# Drop-In Assembly: Snap-Fit Pockets + Wire Channels

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add snap-fit retention features to every component pocket and a wire channel network on the base floor so assembly is drop-in with no tools.

**Architecture:** All changes go into `build_base()` in the single CadQuery model file. Retention features (rail slots, snap tabs, shelf ledges) are added to existing pockets. Wire channels are 3mm×3mm grooves cut into the base floor, connecting electronics → dividers → pumps/atomizer. Cross-divider wire ports let cables pass between zones. After each task, run the collision analysis script and syntax-check before committing.

**Tech Stack:** CadQuery 2.x (Python), cadquery-server for rendering, kubectl for server restart.

**File:** `designs/v2-oil-diffuser.py` (all tasks modify this single file)

**Validation after every task:**
```bash
python3 -m py_compile designs/v2-oil-diffuser.py   # syntax check
# Then run inline collision analysis (see Task 7)
```

**Restart CadQuery server after final push:**
```bash
kubectl rollout restart deploy/cadquery-server -n utilities
```

---

### Task 1: Add Parametric Constants for Retention + Channels

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — constants section (after line ~170, before capacitive touch buttons)

- [ ] **Step 1: Add retention feature constants**

Insert after the `BME280_H = 5` line (around line 170):

```python
# --- PCB retention features ---
# Rail slots (ESP32, MOSFET board, PD trigger) — board slides in from top
RAIL_GROOVE_W = 1.2          # groove width in pocket wall
RAIL_GROOVE_D = 1.5          # groove depth into pocket wall
RAIL_CLEARANCE = 0.3         # clearance per side
RAIL_LIFT = 2.0              # board sits this far above pocket floor
RAIL_CHAMFER = 0.5           # entry chamfer at top of rail

# Snap tabs (buck converter, atomizer driver) — press-fit nubs
SNAP_NUB_W = 1.5             # nub width along pocket wall
SNAP_NUB_H = 1.0             # nub protrusion from wall
SNAP_NUB_ANGLE = 45          # entry ramp angle (degrees)

# Pump shelf ledges — anti-vibration lips inside pump pockets
PUMP_LEDGE_LIP = 1.0         # ledge protrusion into pocket
PUMP_LEDGE_H = 1.5           # ledge thickness (Z)

# --- Wire channel network ---
CHANNEL_W = 3.0              # channel width (open-top groove)
CHANNEL_D = 3.0              # channel depth into floor
CHANNEL_NOTCH_W = 3.0        # notch width where channel meets pocket wall
CHANNEL_NOTCH_H = 3.0        # notch height in pocket wall

# Cross-divider wire ports
WIRE_PORT_W = 5.0            # oval port width
WIRE_PORT_H = 4.0            # oval port height
WIRE_PORT_Z = FLOOR_H + 1   # port bottom Z position
```

- [ ] **Step 2: Syntax check**

```bash
python3 -m py_compile designs/v2-oil-diffuser.py
```

Expected: no output (success).

- [ ] **Step 3: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): add parametric constants for snap-fit retention and wire channels"
```

---

### Task 2: Add Rail Slots to ESP32, MOSFET Board, and PD Trigger Pockets

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — inside `build_base()`, after each pocket cut

Rail slots are two parallel grooves on opposing pocket walls (along the board's long axis). The board slides in from the top between the grooves. Each groove is a thin rectangular extrusion added (union) to the pocket wall, creating a lip the board edge rests on.

Implementation pattern for each pocket: after the `base = base.cut(pocket)` line, add two rail ledges as `base = base.union(rail)`. The rails are thin slabs that protrude `RAIL_GROOVE_D` into the pocket from the ±X walls, at Z = pocket_floor + RAIL_LIFT, running the full Y-length of the pocket.

- [ ] **Step 1: Add rails to PD+Buck pocket**

After the `base = base.cut(pd_buck_pocket)` line, add:

```python
    # Rail slots for PD trigger board (slides in from top)
    # Rails on ±X walls of the pocket, at Z = FLOOR_H + RAIL_LIFT
    _pdb_pocket_hw = (_pd_buck_w + 2) / 2  # half-width of pocket in X
    for _rail_side in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + RAIL_LIFT)
            .center(elec_col_x + _rail_side * (_pdb_pocket_hw - RAIL_GROOVE_D / 2),
                    pd_buck_y)
            .rect(RAIL_GROOVE_D, _pd_buck_d)
            .extrude(_pd_buck_h - RAIL_LIFT)
        )
        base = base.union(rail)
```

- [ ] **Step 2: Add rails to MOSFET board pocket**

After the `base = base.cut(mosfet_pocket)` line, add:

```python
    # Rail slots for MOSFET board (slides in from top)
    _mos_pocket_hw = (MOSFET_BOARD_D + 2) / 2  # half-width in X
    for _rail_side in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + RAIL_LIFT)
            .center(elec_col_x + _rail_side * (_mos_pocket_hw - RAIL_GROOVE_D / 2),
                    mosfet_y)
            .rect(RAIL_GROOVE_D, MOSFET_BOARD_W)
            .extrude(MOSFET_BOARD_H + 2 - RAIL_LIFT)
        )
        base = base.union(rail)
```

- [ ] **Step 3: Add rails to ESP32 pocket**

After the `base = base.cut(esp32_pocket)` line, add:

```python
    # Rail slots for ESP32 (slides in from top)
    _esp_pocket_hw = (ESP32_D + 2) / 2  # half-width in X
    for _rail_side in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_H + RAIL_LIFT)
            .center(elec_col_x + _rail_side * (_esp_pocket_hw - RAIL_GROOVE_D / 2),
                    esp32_y)
            .rect(RAIL_GROOVE_D, ESP32_W)
            .extrude(ESP32_H + 2 - RAIL_LIFT)
        )
        base = base.union(rail)
```

- [ ] **Step 4: Syntax check**

```bash
python3 -m py_compile designs/v2-oil-diffuser.py
```

- [ ] **Step 5: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): add rail slot retention to ESP32, MOSFET, and PD trigger pockets"
```

---

### Task 3: Add Snap Tabs to Buck Converter and Atomizer Driver Pockets

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — inside `build_base()`

Snap tabs are small nubs on opposing pocket walls. Each nub is a small rectangular protrusion at mid-height of the board. The entry side is chamfered (ramped) so the board slides in, then the flat retention face holds it.

Since CadQuery can't easily model a 45° chamfered nub at this scale, we approximate each snap tab as a small rectangular block protruding from the wall. The chamfer is implied by the PETG flex — the board pushes past the nub and clicks.

- [ ] **Step 1: Add snap tabs to buck converter (inside the PD+Buck pocket)**

The buck converter sits on the pocket floor. Add snap nubs on the ±X walls at Z = FLOOR_H + BUCK_CONV_H / 2 (mid-height of the buck board).

After the rail slots for the PD+Buck pocket, add:

```python
    # Snap tabs for buck converter (lower board in the Z-stack)
    _buck_mid_z = FLOOR_H + BUCK_CONV_H / 2
    for _snap_side in [-1, 1]:
        snap = (
            cq.Workplane("XY")
            .workplane(offset=_buck_mid_z - SNAP_NUB_W / 2)
            .center(elec_col_x + _snap_side * (_pdb_pocket_hw - SNAP_NUB_H / 2),
                    pd_buck_y)
            .rect(SNAP_NUB_H, SNAP_NUB_W)
            .extrude(SNAP_NUB_W)
        )
        base = base.union(snap)
```

- [ ] **Step 2: Add snap tabs to atomizer driver pocket (in wet zone)**

After the `base = base.cut(atm_driver_pocket)` line, add:

```python
    # Snap tabs for atomizer driver board
    _atm_pocket_hw = (ATOMIZER_DRIVER_W + 2) / 2  # pocket has +2 tolerance
    _atm_mid_z = FLOOR_H + 3  # mid-height of 6mm pocket
    for _snap_side in [-1, 1]:
        snap = (
            cq.Workplane("XY")
            .workplane(offset=_atm_mid_z - SNAP_NUB_W / 2)
            .center(_atm_drv_x + _snap_side * (_atm_pocket_hw - SNAP_NUB_H / 2),
                    _atm_drv_y)
            .rect(SNAP_NUB_H, SNAP_NUB_W)
            .extrude(SNAP_NUB_W)
        )
        base = base.union(snap)
```

- [ ] **Step 3: Syntax check**

```bash
python3 -m py_compile designs/v2-oil-diffuser.py
```

- [ ] **Step 4: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): add snap tab retention to buck converter and atomizer driver pockets"
```

---

### Task 4: Add Shelf Ledges to Pump Pockets

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — inside `build_base()`, pump pocket loop

Each pump pocket gets a thin shelf ledge on two opposing walls (±Y sides). The pump drops in and rests on the ledges, preventing lateral movement during vibration.

- [ ] **Step 1: Add ledges to pump pockets**

Inside the pump pocket loop, after `base = base.cut(pump_pocket)`, add:

```python
        # Shelf ledges on ±Y walls of pump pocket (anti-vibration)
        _pump_pocket_hd = (PUMP_BODY_D + 2) / 2  # half-depth with tolerance
        for _ledge_side in [-1, 1]:
            ledge = (
                cq.Workplane("XY")
                .workplane(offset=FLOOR_H)
                .center(PUMP_CENTER_X,
                        py + _ledge_side * (_pump_pocket_hd - PUMP_LEDGE_LIP / 2))
                .rect(PUMP_BODY_W - 4, PUMP_LEDGE_LIP)
                .extrude(PUMP_LEDGE_H)
            )
            base = base.union(ledge)
```

- [ ] **Step 2: Syntax check**

```bash
python3 -m py_compile designs/v2-oil-diffuser.py
```

- [ ] **Step 3: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): add shelf ledge retention to pump pockets"
```

---

### Task 5: Cut Wire Channel Network into Base Floor

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — inside `build_base()`, new section after electronics pockets

Wire channels are 3mm wide × 3mm deep grooves cut into the base floor. Each channel is a `box().translate()` positioned at `Z = FLOOR_H - CHANNEL_D/2` (half-sunken into the floor). All channels run at the floor surface level.

- [ ] **Step 1: Add power trunk channel**

After the USB-C cutout, add a new section:

```python
    # === WIRE CHANNEL NETWORK (3mm × 3mm open-top floor grooves) ===

    # Power trunk: runs along electronics column (X=elec_col_x) from
    # USB-C port (rear wall) all the way to PD+Buck pocket (front).
    # Single straight channel spanning the full electronics column.
    _power_trunk_y_start = pd_buck_y - _pd_buck_d / 2 - 2  # front of PD pocket
    _power_trunk_y_end = interior_y_max  # rear wall (USB-C side)
    _power_trunk_len = _power_trunk_y_end - _power_trunk_y_start
    power_trunk = (
        cq.Workplane("XY")
        .box(CHANNEL_W, _power_trunk_len, CHANNEL_D)
        .translate((elec_col_x, (_power_trunk_y_start + _power_trunk_y_end) / 2,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(power_trunk)
```

- [ ] **Step 2: Add signal trunk channel (ESP32 ↔ MOSFET)**

```python
    # Signal trunk: short channel bridging the 3mm gap between MOSFET and ESP32.
    _sig_y_start = mosfet_y + MOSFET_BOARD_W / 2  # MOSFET rear edge
    _sig_y_end = esp32_y - ESP32_W / 2             # ESP32 front edge
    _sig_len = max(_sig_y_end - _sig_y_start, 1)   # at least 1mm
    signal_trunk = (
        cq.Workplane("XY")
        .box(CHANNEL_W, _sig_len + 4, CHANNEL_D)   # +4 to overlap into pockets
        .translate((elec_col_x, (_sig_y_start + _sig_y_end) / 2,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(signal_trunk)
```

- [ ] **Step 3: Add pump power spur channels**

These run from the MOSFET pocket's left wall across the floor to the right divider, one per pump.

```python
    # Pump power spurs: MOSFET pocket → right divider, one per pump Y position.
    # Each spur runs along X from the MOSFET pocket left edge to the right divider.
    _spur_x_start = DIVIDER_DRY_X + WALL_INNER / 2 + 1  # just past divider
    _spur_x_end = elec_col_x - MOSFET_BOARD_D / 2 - 1   # just before MOSFET pocket
    _spur_len = _spur_x_end - _spur_x_start
    for py in pump_y_positions:
        pump_spur = (
            cq.Workplane("XY")
            .box(_spur_len, CHANNEL_W, CHANNEL_D)
            .translate(((_spur_x_start + _spur_x_end) / 2, py,
                         FLOOR_H + CHANNEL_D / 2))
        )
        base = base.cut(pump_spur)
```

- [ ] **Step 4: Add a collector channel along the MOSFET pocket's left wall**

The 5 pump spurs need to connect to the MOSFET pocket. Add a short vertical (Y-direction) collector channel running along the left edge of the MOSFET pocket, from pump_0 Y to pump_4 Y.

```python
    # Collector channel: runs along Y at the MOSFET pocket's left edge,
    # connecting all 5 pump spur endpoints.
    _collector_x = _spur_x_end + CHANNEL_W / 2
    _collector_y_start = pump_y_positions[0]
    _collector_y_end = pump_y_positions[-1]
    _collector_len = _collector_y_end - _collector_y_start + CHANNEL_W
    collector = (
        cq.Workplane("XY")
        .box(CHANNEL_W, _collector_len, CHANNEL_D)
        .translate((_collector_x, (_collector_y_start + _collector_y_end) / 2,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(collector)
```

- [ ] **Step 5: Syntax check**

```bash
python3 -m py_compile designs/v2-oil-diffuser.py
```

- [ ] **Step 6: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): add power trunk, signal trunk, and pump spur wire channels"
```

---

### Task 6: Add Atomizer Spur, LED Spur, and Cross-Divider Wire Ports

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — inside `build_base()`, continuing wire channel section

- [ ] **Step 1: Add atomizer spur channel**

The atomizer spur runs from the MOSFET pocket → along the front wall (Y≈-64.6) → through the right divider → across the pump row floor → through the left divider → to the atomizer driver pocket.

```python
    # Atomizer spur: MOSFET pocket → front wall → right divider → pump row → left divider → wet zone
    _atm_spur_y = interior_y_min + 3  # 3mm from front wall, clear of pump_0

    # Segment 1: MOSFET pocket left edge → right divider (in dry zone)
    _atm_seg1_x_start = DIVIDER_DRY_X + WALL_INNER / 2 + 1
    _atm_seg1_x_end = elec_col_x - MOSFET_BOARD_D / 2 - 1
    atm_seg1 = (
        cq.Workplane("XY")
        .box(_atm_seg1_x_end - _atm_seg1_x_start, CHANNEL_W, CHANNEL_D)
        .translate(((_atm_seg1_x_start + _atm_seg1_x_end) / 2, _atm_spur_y,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_seg1)

    # Segment 1b: Y-direction channel from MOSFET pocket front edge to _atm_spur_y
    _atm_seg1b_y_start = _atm_spur_y
    _atm_seg1b_y_end = mosfet_y - MOSFET_BOARD_W / 2  # MOSFET front edge
    atm_seg1b = (
        cq.Workplane("XY")
        .box(CHANNEL_W, abs(_atm_seg1b_y_end - _atm_seg1b_y_start), CHANNEL_D)
        .translate((_atm_seg1_x_end, (_atm_seg1b_y_start + _atm_seg1b_y_end) / 2,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_seg1b)

    # Segment 2: across pump row floor (right divider → left divider)
    _atm_seg2_x_start = DIVIDER_WET_X - WALL_INNER / 2 - 1
    _atm_seg2_x_end = DIVIDER_DRY_X - WALL_INNER / 2 + 1
    atm_seg2 = (
        cq.Workplane("XY")
        .box(abs(_atm_seg2_x_end - _atm_seg2_x_start), CHANNEL_W, CHANNEL_D)
        .translate(((_atm_seg2_x_start + _atm_seg2_x_end) / 2, _atm_spur_y,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_seg2)

    # Segment 3: wet zone floor, from left divider to atomizer driver pocket
    # L-shaped: first along Y from _atm_spur_y up to _atm_drv_y, then along X to _atm_drv_x
    _atm_seg3a_y_len = abs(_atm_drv_y - _atm_spur_y)
    atm_seg3a = (
        cq.Workplane("XY")
        .box(CHANNEL_W, _atm_seg3a_y_len, CHANNEL_D)
        .translate((DIVIDER_WET_X - WALL_INNER / 2 - 3,
                     (_atm_spur_y + _atm_drv_y) / 2,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_seg3a)

    _atm_seg3b_x_start = _atm_drv_x + ATOMIZER_DRIVER_W / 2 + 1
    _atm_seg3b_x_end = DIVIDER_WET_X - WALL_INNER / 2 - 3
    atm_seg3b = (
        cq.Workplane("XY")
        .box(abs(_atm_seg3b_x_end - _atm_seg3b_x_start), CHANNEL_W, CHANNEL_D)
        .translate(((_atm_seg3b_x_start + _atm_seg3b_x_end) / 2, _atm_drv_y,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(atm_seg3b)
```

- [ ] **Step 2: Add LED spur channel**

```python
    # LED spur: ESP32 pocket rear edge → rear-right corner (LED strip entry)
    _led_spur_y_start = esp32_y + ESP32_W / 2  # ESP32 rear edge
    _led_spur_y_end = interior_y_max - 2        # near rear wall
    led_spur = (
        cq.Workplane("XY")
        .box(CHANNEL_W, _led_spur_y_end - _led_spur_y_start, CHANNEL_D)
        .translate((elec_col_x, (_led_spur_y_start + _led_spur_y_end) / 2,
                     FLOOR_H + CHANNEL_D / 2))
    )
    base = base.cut(led_spur)
```

- [ ] **Step 3: Add cross-divider wire ports**

Cut oval-ish ports through the divider walls for wires to pass between zones.

```python
    # Cross-divider wire ports — oval holes for wire pass-through

    # Right divider: 5 pump wire ports (one per pump Y position)
    for py in pump_y_positions:
        pump_wire_port = (
            cq.Workplane("XY")
            .workplane(offset=WIRE_PORT_Z)
            .center(DIVIDER_DRY_X, py)
            .rect(WALL_INNER + 2, WIRE_PORT_W)
            .extrude(WIRE_PORT_H)
        )
        base = base.cut(pump_wire_port)

    # Right divider: atomizer spur port (front, Y ≈ -64.6)
    atm_port_right = (
        cq.Workplane("XY")
        .workplane(offset=WIRE_PORT_Z)
        .center(DIVIDER_DRY_X, _atm_spur_y)
        .rect(WALL_INNER + 2, WIRE_PORT_W)
        .extrude(WIRE_PORT_H)
    )
    base = base.cut(atm_port_right)

    # Left divider: atomizer spur port (matching, same Y)
    atm_port_left = (
        cq.Workplane("XY")
        .workplane(offset=WIRE_PORT_Z)
        .center(DIVIDER_WET_X, _atm_spur_y)
        .rect(WALL_INNER + 2, WIRE_PORT_W)
        .extrude(WIRE_PORT_H)
    )
    base = base.cut(atm_port_left)
```

- [ ] **Step 4: Add pocket wall notches**

Cut small notches at the base of pocket walls where wire channels enter, so wires aren't pinched.

```python
    # Pocket wall notches — where wire channels meet pocket edges
    # Each electronics pocket gets a notch on the side facing the power trunk.

    # PD+Buck pocket — notch on +Y wall (facing power trunk)
    pd_notch = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(elec_col_x, pd_buck_y + _pd_buck_d / 2 + 0.5)
        .rect(CHANNEL_NOTCH_W, 2)
        .extrude(CHANNEL_NOTCH_H)
    )
    base = base.cut(pd_notch)

    # MOSFET pocket — notch on −X wall (facing pump spurs) and ±Y walls (power/signal)
    mos_notch_left = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(elec_col_x - MOSFET_BOARD_D / 2 - 0.5, mosfet_y)
        .rect(2, CHANNEL_NOTCH_W)
        .extrude(CHANNEL_NOTCH_H)
    )
    base = base.cut(mos_notch_left)

    # ESP32 pocket — notch on +Y wall (LED spur) and −Y wall (signal trunk)
    esp_notch_rear = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_H)
        .center(elec_col_x, esp32_y + ESP32_W / 2 + 0.5)
        .rect(CHANNEL_NOTCH_W, 2)
        .extrude(CHANNEL_NOTCH_H)
    )
    base = base.cut(esp_notch_rear)
```

- [ ] **Step 5: Syntax check**

```bash
python3 -m py_compile designs/v2-oil-diffuser.py
```

- [ ] **Step 6: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): add atomizer spur, LED spur, cross-divider wire ports, and pocket notches"
```

---

### Task 7: Run Collision Analysis and Update Assembly Summary

**Files:**
- Modify: `designs/v2-oil-diffuser.py` — assembly summary section at bottom

- [ ] **Step 1: Run collision analysis**

Run the same AABB collision analysis as before (same standalone script pattern) to verify no retention features or channels created unexpected overlaps. The rails/tabs are part of the base geometry (unioned in), not separate components, so the component-vs-component check stays the same — but verify visually that the channels don't cut through divider walls unintentionally.

```bash
python3 -m py_compile designs/v2-oil-diffuser.py && echo "SYNTAX OK"
```

- [ ] **Step 2: Update assembly summary**

Add wire routing and retention info to the print summary at the bottom of the file. After the existing "--- Connections ---" section, add:

```python
print(f"--- Assembly (drop-in) ---")
print(f"Rail slots:  ESP32, MOSFET board, PD trigger (slide in from top)")
print(f"Snap tabs:   Buck converter, atomizer driver (press-fit)")
print(f"Shelf ledge: {PUMP_COUNT}x pump pockets (anti-vibration lips)")
print(f"Swing latch: {BOTTLE_COUNT}x bottle wells (hinged clips)")
print()
print(f"--- Wire Channels ({CHANNEL_W}x{CHANNEL_D}mm floor grooves) ---")
print(f"Power trunk: USB-C → PD trigger → buck → MOSFET board + ESP32")
print(f"Signal trunk:ESP32 ↔ MOSFET board (6 GPIO)")
print(f"Pump spurs:  MOSFET → right divider → {PUMP_COUNT}x pumps")
print(f"Atm spur:    MOSFET → dry zone → pump row → wet zone → atomizer driver")
print(f"LED spur:    ESP32 → rear-right LED strip entry")
print(f"Wire ports:  {PUMP_COUNT + 2}x cross-divider ({WIRE_PORT_W}x{WIRE_PORT_H}mm)")
```

- [ ] **Step 3: Commit**

```bash
git add designs/v2-oil-diffuser.py
git commit -m "feat(v3.0): update assembly summary with retention and wire channel info"
```

---

### Task 8: Push and Verify Render

- [ ] **Step 1: Push to remote**

```bash
git push origin main
```

- [ ] **Step 2: Restart CadQuery server**

```bash
kubectl rollout restart deploy/cadquery-server -n utilities
kubectl rollout status deploy/cadquery-server -n utilities --timeout=120s
```

- [ ] **Step 3: Verify in browser**

Open the CadQuery viewer and confirm:
- Rail slots visible inside ESP32, MOSFET, PD trigger pockets (thin ledges on pocket walls)
- Pump pockets show shelf ledges on ±Y walls
- Wire channels visible as grooves on the base floor
- Cross-divider ports visible as rectangular holes in both divider walls
- No broken geometry or missing faces

---

## Execution Notes

- All edits go into `build_base()` in the single file `designs/v2-oil-diffuser.py`
- Rail slots and snap tabs are **unioned** into the base (they add material into pockets)
- Wire channels and ports are **cut** from the base (they remove material)
- CadQuery `box().translate()` is the reliable pattern for positioned cuts (not workplane offsets at large Y)
- After each task, syntax check before committing
- The file is ~1610 lines; all edits are in `build_base()` (lines ~340–630)
- Author email for commits: `gerardo.palacios@somni-labs.io`
