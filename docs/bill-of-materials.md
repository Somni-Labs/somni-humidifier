# Bill of Materials — Somni Smart Humidifier

Component sourcing for the multi-scent ultrasonic humidifier (HUM-12).

Total power budget: **~1.5 A @ 5 V** (5 pumps × 150 mA + atomizer 500 mA + ESP32 250 mA).

Estimated total cost (single prototype, USD): **~$95–$130**, excluding shipping and 3D-printed parts.

## Status legend

- `selected` — primary choice, order this
- `alt` — drop-in alternative if primary is out of stock
- `verify` — physical measurement required before final CAD

---

## Electronics

### Controller — ESP32 DevKit C V4 *(selected)*

- **Why:** Wi-Fi + BLE, dual-core, native ESPHome support → Home Assistant in one config block.
- **Footprint:** 55 × 28 × 13 mm (30-pin variant). `verify` PCB width since clone boards vary 27–30 mm.
- **Logic level:** 3.3 V. All MOSFET drivers and the atomizer board must accept 3.3 V triggers.
- **Power:** USB-C on the board itself is **not** used for system power — fed from the 5 V rail via `5V` and `GND` pins. USB only for flashing/console.
- **Suppliers:**
  - Espressif official via DigiKey / Mouser — ~$12
  - AliExpress / Amazon clones — ~$6–8 (acceptable, but verify the CP2102 USB-UART, not CH340)
- **Estimated unit cost:** $8

### Ultrasonic atomizer module — 20 mm piezo + driver board, 113 kHz *(selected)*

- **Topology:** Separate piezo disc + driver PCB (not a sealed "humidifier head"). Lets us mount the disc at the bottom of the mixing chamber and route the driver elsewhere.
- **Disc:** 20 mm diameter, 113 kHz resonance. 25 mm / 1.7 MHz alternative produces finer mist but draws more current — stick with 20 mm for the 1.5 A budget.
- **Driver requirements:**
  - 5 V supply, **logic-level enable pin** (3.3 V-tolerant — confirm in datasheet, some modules need a level shifter)
  - Built-in dry-run / no-water protection — non-negotiable, piezos crack within seconds when run dry
- **Candidate modules:**
  - "20mm 113KHz ultrasonic atomizer driver board with switch control" — AliExpress, ~$4–6
  - DIYables ultrasonic mist maker module — Amazon, ~$10
- **`verify`:** disc + driver PCB dimensions for CAD pocket. Driver boards are typically 35 × 25 mm but vary.
- **Estimated unit cost:** $7

### Peristaltic pumps — 5 × Kamoer KFS (or equivalent), 6 V DC *(selected)*

- **Why peristaltic:** Essential oils degrade in plastic and have variable viscosity. Peristaltic isolates the fluid inside the tubing — only the silicone tube contacts the oil, and the pump head can be back-flushed.
- **Spec:**
  - 6 V DC nominal — runs slower at 5 V (acceptable; we don't need top speed for dosing), or add a 6 V boost if accuracy matters
  - 1–2 ml/min flow rate
  - 3 mm ID silicone tubing compatible
  - Stall current ~200 mA, running current ~120–150 mA → 5 pumps × 150 mA = 750 mA
- **Candidates:**
  - **Kamoer KFS-S04A** — 6 V, ~1.5 ml/min, ~$10 each (Kamoer official store / AliExpress)
  - **Generic 6 V peristaltic dosing pump** (Amazon "INTLLAB" or unbranded) — ~$6–8 each, lower QC
- **`verify`:** pump body L × W × H for CAD mounting pockets (typically ~58 × 38 × 27 mm but varies).
- **Estimated unit cost:** $8–10 × 5 = **$40–50**

### MOSFET drivers — 5 × IRLZ44N logic-level N-channel modules *(selected)*

- **Why a module, not a bare FET:** Pre-built modules include a 10 kΩ pulldown on the gate (so the pump can't twitch on during ESP32 boot) and a flyback diode (essential for inductive pump motors).
- **Why IRLZ44N specifically:** True logic-level — fully on at Vgs = 3.3 V (Rds(on) ≈ 25 mΩ). Avoid IRF540 (needs ~10 V Vgs, will dissipate as heat at 3.3 V).
- **Alternative:** AO3400 or similar SOIC logic-FET breakouts work too.
- **PWM:** ESP32 LEDC can drive these at any frequency, but pumps don't need PWM speed control — simple ON/OFF for dosing duration.
- **Suppliers:** AliExpress / Amazon — "IRLZ44N MOSFET module" — ~$1.50–2 each.
- **Estimated unit cost:** $2 × 5 = **$10**

### Environment sensor — BME280 breakout *(selected)*

- **Interface:** I²C (address 0x76 or 0x77 — both supported by ESPHome `bme280` component).
- **Why BME280, not DHT22:** ±3 % RH accuracy, ±0.5 °C, includes pressure. Required for closed-loop humidity control (setpoint − measured → PID or hysteresis).
- **Mounting:** External to the mist plume — exhaust airflow path or device side, not above the reservoir.
- **Supplier:** Adafruit (#2652, $15) or generic AliExpress breakout (~$3 — Bosch counterfeits exist; for prototype accept the risk, for production switch to authentic).
- **Estimated unit cost:** $4 (generic) / $15 (Adafruit)

### Water level sensor — capacitive non-contact *(selected)*

- **Why non-contact / capacitive:** Resistive probes corrode in days and contaminate the water. Capacitive strips sense water through the tank wall — no liquid contact.
- **Candidate:** "XKC-Y25-V" or "XKC-Y25-T12V" non-contact liquid level sensor — 5 V supply, digital output, mounts with adhesive on the outside of an acrylic or PETG reservoir wall ≤ 4 mm thick.
- **Logic:** 5 V output → either use a 3.3 V variant ("XKC-Y25-T12V" has a 3.3 V version) or add a voltage divider / level shifter into a GPIO.
- **Supplier:** AliExpress / Amazon — ~$5–8.
- **Estimated unit cost:** $7

### Power — USB-C PD trigger board, 5 V / 3 A *(selected)*

- **Why PD trigger:** Lets us power the whole device from any USB-C PD wall adapter (15 W+). Avoids a bespoke barrel-jack supply.
- **Spec:** Fixed 5 V output, ≥ 3 A capable (headroom over the 1.5 A budget). Solder pads for direct wiring.
- **Candidates:**
  - "ZY12PDN" — programmable PD trigger, ~$4
  - "CH224K" breakout — simple resistor-set voltage, ~$3
- **Note:** Pair with a 20 W+ PD wall brick (not included in BOM — assume user-supplied or commodity Anker/Apple).
- **Estimated unit cost:** $4

### Misc electronics

- Dupont jumper kit (M-F, F-F, M-M, 20 cm) — $3
- JST-XH 2-pin / 3-pin connectors for pump + sensor pigtails (so the lid can be detached from the base for service) — $4
- 5 V buck for the ESP32 rail if pump inrush sags the supply (optional, defer until bench-tested) — $2
- Perfboard or custom PCB for MOSFET array + connectors — $5 perfboard, $15 PCB (defer to v2)

**Electronics subtotal:** ~$85

---

## Mechanical / fluidics

### Essential oil bottles — 5 × 5 ml amber glass, 18 mm neck *(selected)*

- **Standard neck:** "18-415" thread — 18 mm outer diameter, 415 thread style (2-turn coarse). Confirms compatibility with off-the-shelf orifice reducers and dropper caps.
- **`verify`:** Even within "18 mm neck," actual thread pitch can be 18-400 (1.5 turn) or 18-415 (2 turn). Measure thread pitch and major diameter on the chosen bottle before printing the cap/holder.
- **Supplier:** Amazon multi-pack — ~$1–2 per bottle.
- **Estimated unit cost:** $1.50 × 5 = **$7.50**

### Silicone tubing — 3 mm ID × 5 mm OD, food-grade, ~250 cm *(selected)*

- **ID 3 mm** matches the pump rotors and standard 3 mm barbs.
- **OD 5 mm** gives a 1 mm wall — enough for the peristaltic squeeze without splitting.
- **Food-grade silicone** (platinum-cure preferred) — won't leach into the oil, won't harden from limonene/linalool exposure as fast as PVC or vinyl.
- **Length:** ~50 cm per pump run (bottle → pump → mixing chamber) × 5 = 250 cm. Order 3 m to have offcuts.
- **Supplier:** Amazon / aquarium suppliers / McMaster-Carr.
- **Estimated unit cost:** ~$8 for 3 m

### Barb fittings — 3 mm, ~10 pieces *(selected)*

- **Where:** Bottle-cap pickup tubes, mixing chamber inlets, optional T-junctions if we want a shared output manifold.
- **Material:** Stainless steel preferred for the wet side; PP / PE acceptable for non-wetted joints.
- **Pack:** Generic 3 mm hose-barb kit (straight, elbow, T) — ~$8 for 20 pieces.
- **Estimated unit cost:** $8

### O-rings — assorted nitrile/silicone *(selected)*

- **Uses:**
  - Bottle cap seals (around the dip-tube grommet)
  - Mixing chamber lid (so vibration / condensate doesn't leak)
  - Atomizer disc seal (between the disc and the chamber floor — critical, this is where water sits)
- **Pack:** Standard metric O-ring kit (1.5–3 mm cross-section, 5–25 mm ID range) — ~$10.
- **`verify`:** Once the atomizer disc is in hand, measure its diameter and pick the matching O-ring.
- **Estimated unit cost:** $10

### Reservoir + enclosure — 3D printed *(out of scope for BOM)*

PETG for wet parts (mixing chamber, lid), PLA acceptable for dry electronics enclosure. Filament cost folded into the prototype budget elsewhere.

**Mechanical subtotal:** ~$35

---

## Verification checklist *(blocks CAD start)*

Mark each item once the physical part is on the bench:

- [ ] Ultrasonic module: measure disc diameter, driver PCB L × W × H, mounting hole pitch
- [ ] Peristaltic pump: measure body L × W × H, shaft / inlet / outlet positions, mounting screw pattern
- [ ] 5 ml bottle: confirm neck OD and thread pitch (calipers + thread gauge)
- [ ] Power: bench-measure actual current with all pumps running + atomizer on, confirm < 2.5 A so the PD trigger has headroom
- [ ] Water level sensor: confirm trigger distance through the chosen reservoir wall material/thickness

## Open questions

- **Atomizer mount orientation:** disc-down (water above) is standard but means leaks fall into the electronics. Disc-side with a wick is leak-tolerant but reduces output. Decide before chamber CAD.
- **Mixing strategy:** dose-then-atomize (pumps deliver oil to a small reservoir above the disc, atomizer aerosolizes the mix) vs. dose-into-mist (oil drips onto the mist stream post-atomization). First is simpler; second avoids fouling the disc with oil residue. Bench-test both before committing.
- **Pump duty cycle:** 1–2 ml/min is the *rated* spec at 6 V. At 5 V the actual delivered volume per second needs calibration — plan a "prime + measure" routine in ESPHome.
