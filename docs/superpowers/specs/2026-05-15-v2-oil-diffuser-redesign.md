# Somni Oil Diffuser V2 — "Night City" Cyberpunk Desktop Diffuser

**Date:** 2026-05-15
**Status:** Approved
**Replaces:** V1 humidifier design (overengineered, bottles hung below base)

## Overview

Ground-up redesign of the Somni smart humidifier as a **cyberpunk-styled oil diffuser**. The primary purpose is automated scent blending via Home Assistant, not room humidification. Five essential oil bottles sit upright inside the device, each fed by a peristaltic dosing pump that delivers oil directly into a small water reservoir. An ultrasonic atomizer vaporizes the water+oil mix and mist exits through an angular exhaust port on top.

The device is a single self-contained unit with cyberpunk aesthetics: hex mesh panels with LED glow-through, angular faceted surfaces, panel lines, and a thruster-style exhaust vent.

## Key Design Decisions

- **Oil diffuser, not humidifier** — small reservoir (~200-300ml), optimized for scent delivery
- **Upright bottles** — no inversion, no gravity feed, no threaded receivers. Pumps pull oil through tubes
- **Dose into water** — oil is pumped directly into the reservoir, atomizer vaporizes the mix
- **Two-part enclosure** — base + top shell, connected via magnets
- **Separate access points** — water fill port with silicone plug, hinged bottle hatch on the side
- **Cyberpunk aesthetic** — hex mesh, angular facets, LED glow-through, matte black PETG

## Form Factor

- **Footprint:** ~160 × 160mm
- **Height:** ~130mm total (base ~70mm + top shell ~60mm)
- **Shape:** Angular, tapered sides (5-8° inward draft from base to top). Not a plain box — chamfered break lines across faces like mech suit panel lines.
- **Print bed:** Fits QIDI Q2 (245 × 255mm) with margin
- **Material:** Matte black PETG

## Base Unit (~70mm tall)

Houses all the functional internals. Sits flat on rubber feet.

### Wet Zone (~60% of floor area)

- Water reservoir basin — waterproof PETG, ~200-300ml capacity
- Ultrasonic atomizer disk (20mm, 113kHz) mounted at the bottom on a sealed pad
- Oil dosing tubes terminate here — pumps deliver oil directly into the water
- Capacitive water level sensor mounted on the outside wall (no water contact)

### Dry Zone (~40% of floor area)

- Separated from wet zone by a sealed internal wall
- ESP32 DevKit C V4 — Wi-Fi/BLE, ESPHome firmware
- 5× IRLZ44N MOSFET driver modules (one per pump)
- USB-C PD trigger board (5V/3A input) — port on the back panel
- BME280 environment sensor (mounted on the exterior side, away from mist)
- WS2812B LED strip (addressable RGB) — mounted behind hex mesh panels
- Wiring, perfboard/PCB for MOSFET array

### Pumps (on the divider wall)

- 5× peristaltic dosing pumps mounted along the wet/dry divider wall
- Tubing from bottles (top shell) → through pumps → output into reservoir
- Pumps bridge both zones: intake side faces up (dry, connects to bottles), output side faces into reservoir

## Top Shell (~60mm tall)

Locks onto the base via alignment pins + magnets. Removable for deep cleaning.

### Bottle Compartment

- 5 cylindrical wells (~25mm diameter, ~45mm deep) arranged in a row or slight arc
- Holds standard 5ml essential oil bottles (22mm dia) upright with clearance
- Each well has a small silicone tube routed down through the shell into the base, dipped into the bottle
- Bottles stick up slightly above the wells for easy grab-and-swap
- Access via a hinged panel on one side — push-to-release latch, swings open

### Mist Channel

- Integrated passage from the reservoir below to the exhaust port on top
- Replaces the separate mixing chamber and chimney from V1 — just a short internal chimney molded into the shell
- No separate pieces — one continuous path

### Water Fill Port

- ~30mm hole on the top surface with a silicone plug
- Located away from the mist outlet and bottle hatch
- Pull plug, pour water, replace plug

### Exhaust Port

- Angular diamond or chevron-shaped opening on top
- Internal vanes direct mist upward and slightly forward
- Hero design element — the most visible feature of the device
- Looks like a thruster vent from Night City tech

## Cyberpunk Aesthetic

### Hex Mesh Panels

- 2-3 side faces feature hexagonal cutout patterns
- Hex cells ~8-10mm across, 1.5mm walls between cells
- Dual purpose: ventilation for electronics bay + LED glow-through
- Printable without supports (hex openings are vertical)

### Angular Facets & Panel Lines

- Sides taper inward 5-8° from base to top
- At least two faces have a chamfered break line running horizontally — like armor panel seams
- Sharp, intentional geometry — nothing rounded or soft

### LED Lighting

- WS2812B addressable RGB strip inside, behind hex mesh panels
- Driven by ESP32 via ESPHome `light` component
- States:
  - Cyan glow — idle/running
  - Pulse effect — dosing oil
  - Red — water low
  - Configurable via Home Assistant (color, brightness, effects)
- Ambient, not blinding — light bleeds through hex mesh

### Surface Finish

- Matte black PETG for the main body
- Optional accent pieces in contrasting color (gunmetal gray or dark translucent PETG for hex frames)
- Small "SOMNI" debossed on the back panel near USB-C port

## Connection Between Base and Top Shell

- **Alignment:** 3-4 locating pins on the base rim, matching holes in the top shell
- **Retention:** Neodymium magnets (6mm × 3mm disc, ~4 pieces) press-fit into pockets on both halves
- **Tube routing:** Small pass-through holes with silicone grommets at the base/shell interface for oil tubing. Tubes are long enough to set the top aside without disconnecting.
- **LED wiring:** Single 3-pin JST connector for the LED strip — disconnects when you lift the top shell

## Electronics & Firmware

Same BOM components from V1, rearranged for the new layout:

| Component | Qty | Purpose |
|-----------|-----|---------|
| ESP32 DevKit C V4 | 1 | Controller, Wi-Fi/BLE, ESPHome |
| 20mm ultrasonic atomizer + driver | 1 | Water+oil vaporization |
| Peristaltic pump (Kamoer KFS or equiv) | 5 | Individual oil dosing |
| IRLZ44N MOSFET module | 5 | Pump switching (3.3V logic) |
| BME280 breakout | 1 | Humidity/temp sensing |
| Capacitive water level sensor | 1 | Low-water detection |
| USB-C PD trigger (CH224K/ZY12PDN) | 1 | 5V/3A power input |
| WS2812B LED strip | 1 | Ambient lighting through hex mesh |
| Silicone tubing (3mm ID) | ~3m | Oil routing |
| Neodymium magnets (6×3mm) | ~8 | Base-to-shell retention |

ESPHome firmware from V1 (HUM-6) is still valid — pump control, atomizer enable, humidity sensor, HA entities. Add LED strip control via ESPHome `neopixelbus` or `fastled` component.

## What This Replaces

The V1 design had 6 separate CadQuery files:
- `v1-humidifier-base.py` — overbuilt base with Apollo dock, bund, pump arc
- `v1-mixing-chamber.py` — standalone cylindrical chamber (80mm, didn't fit the base's 70mm footprint)
- `v1-mist-chimney.py` — separate chimney piece with snap ring (didn't fit the chamber)
- `v1-oil-carousel.py` — threaded receivers, bottles hung below the base
- `v1-oil-carousel-top.py` — partial fix, still overengineered
- `v1-full-assembly.py` — assembly that showed all the dimensional conflicts

All replaced by a single `v2-oil-diffuser.py` CadQuery file (or split into `v2-base.py` + `v2-top-shell.py` if the single file gets unwieldy).

## Print Considerations

- All parts printable on QIDI Q2 (245 × 255mm build plate)
- PETG for all parts (water-resistant, heat-tolerant near atomizer)
- Base prints upside-down (flat top surface on bed) for clean reservoir floor
- Top shell prints right-side-up
- Hex mesh panels are vertical — no supports needed for hex cutouts
- Exhaust port vanes may need minimal supports depending on overhang angle

## Open Items

- **Exact reservoir capacity** — finalize once internal layout is modeled. Target 200-300ml.
- **Pump mounting detail** — exact bracket design depends on which Kamoer model is purchased (HUM-13: measure components)
- **LED strip length** — depends on how many hex panels and their perimeter
- **Magnet pocket depth** — standard 6×3mm neo magnets, but verify pull force is enough to hold the shell secure
- **Atomizer seal** — O-ring spec depends on physical disk measurement (from BOM verify checklist)
