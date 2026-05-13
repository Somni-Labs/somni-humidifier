# Unified Humidifier Assembly View

## Problem

The somni-humidifier has four separate CadQuery design files that each render in isolation in cadquery-server. They share no coordinate system and you can't see how the pieces fit together — the mixing chamber floats in space with no relation to the base that houses it, the chimney has no connection to the chamber it sits on, and the oil carousel has no spatial relationship to the bund it mounts under.

## Solution

A single `v1-full-assembly.py` file in `designs/` that inlines the build logic from all four components and renders them together in their correct spatial positions. Each component gets a distinct semi-transparent color.

## Approach

**Self-contained assembly file (option A).** cadquery-server executes each `.py` file independently with no inter-file import support (files are symlinked to `/projects/` root, not a Python package). The assembly file duplicates the build functions from each component file with a unified constants section at the top.

**Dimensional mismatches assembled as-is (option C).** Known conflicts (mixing chamber 80mm OD vs. base's 70mm reserved footprint, chimney snap ring vs. chamber wall sizing) are left visible in the assembly. Seeing the overlaps in 3D is the point — it informs what needs to change in V2.

## Components and Positions

The base's coordinate system is the assembly origin. All positions derived from `v1-humidifier-base.py` constants.

### 1. Base (origin)
- **Source**: `v1-humidifier-base.py` → `build_base()`
- **Position**: Z=0 (the assembly origin)
- **Dimensions**: 230 x 210 x 55mm
- **Color**: dark gray `(0.2, 0.22, 0.25, 0.6)` — semi-transparent so internals are visible

### 2. Mixing Chamber
- **Source**: `v1-mixing-chamber.py` — rebuild the chamber body inline (the original file uses module-level imperative code, not a single build function, so the assembly file wraps it in a `build_mixing_chamber()` function)
- **Position**: translate to `(MIX_CENTER_X, MIX_CENTER_Y, BUND_TOP_Z)` where:
  - `MIX_CENTER_X ≈ 52.9mm` (derived from Apollo dock position + offsets)
  - `MIX_CENTER_Y ≈ 3.4mm`
  - `BUND_TOP_Z = 31mm` (FLOOR_H + BUND_H = 3 + 28)
- **Dimensions**: 80mm OD x 60mm tall (NOTE: overflows the base's 70mm reserved footprint — intentional, shows the mismatch)
- **Color**: light blue `(0.68, 0.85, 0.90, 0.5)`

### 3. Mist Chimney
- **Source**: `v1-mist-chimney.py` → `assemble_mist_chimney()`
- **Position**: stacked on top of the mixing chamber — translate to `(MIX_CENTER_X, MIX_CENTER_Y, BUND_TOP_Z + CHAMBER_HEIGHT)` where CHAMBER_HEIGHT = 60mm, so Z = 91mm
- **Note**: The chimney's snap ring (50mm dia) connects to the mixing chamber's top. The chimney extends 70mm + 15mm nozzle above that.
- **Color**: light green `(0.56, 0.93, 0.56, 0.45)`

### 4. Oil Carousel Plate + Ghost Bottles
- **Source**: `v1-oil-carousel.py` → `assemble_oil_carousel()` + `create_reference_bottle()`
- **Position**: mounted under the base, centered under the pump arc area. The carousel plate's top surface aligns with the underside of the base floor (Z=0). Translate to `(MIX_CENTER_X, MIX_CENTER_Y, 0)` with the plate and receivers extending downward (negative Z). The carousel is already built with receivers in negative Z and plate at Z=0..PLATE_THICKNESS, so translate to `(MIX_CENTER_X, MIX_CENTER_Y, -PLATE_THICKNESS)` to place the plate flush against the base floor.
- **Ghost bottles**: rendered in amber at 35% opacity hanging below the carousel
- **Color**: carousel plate in neutral `(0.85, 0.82, 0.78, 0.5)`, bottles in amber `(1.0, 0.55, 0.0, 0.35)`

## File Structure

```
designs/
  v1-full-assembly.py      ← NEW — unified assembly view
  v1-humidifier-base.py    ← unchanged (standalone detail view)
  v1-mixing-chamber.py     ← unchanged
  v1-mist-chimney.py       ← unchanged
  v1-oil-carousel.py       ← unchanged
  test-single-receiver.py  ← unchanged
```

## What the Assembly File Contains

1. **Module docstring** explaining the assembly purpose and known dimensional mismatches
2. **Unified constants section** — all dimensions from all four files, organized by component, with comments noting conflicts
3. **Build functions** — one per component, inlined from the source files:
   - `build_base()` — from v1-humidifier-base.py (verbatim)
   - `build_mixing_chamber()` — wrapped from v1-mixing-chamber.py's imperative code
   - `build_mist_chimney()` — from v1-mist-chimney.py's `assemble_mist_chimney()`
   - `build_oil_carousel()` — from v1-oil-carousel.py's `assemble_oil_carousel()`
   - `build_reference_bottles()` — from v1-oil-carousel.py's `create_reference_bottle()`
4. **Assembly section** — calls each build function, translates to position, renders with `show_object()`
5. **Print summary** — dimensions, position offsets, known conflicts

## Simplifications

The assembly file should **simplify** the component builds where it can to keep the file manageable:

- **Skip the base's internal detail** (cable channels, component pockets, vent slots) — just build the outer shell + bund + Apollo dock + pump mounts. The full detail is in the standalone file.
- **Skip the mixing chamber's internal detail** (baffle, nozzle taper) — just the outer shell, chimney stub, and oil inlet holes.
- **Skip the oil carousel's tube routing channels and position labels** — just the plate, receivers, and reference bottles.
- **Keep the chimney complete** — it's already simple (~160 lines).

This keeps the assembly under ~600 lines while showing how everything fits spatially.

## Known Dimensional Conflicts (visible in assembly)

| Conflict | File A | File B | Impact |
|----------|--------|--------|--------|
| Chamber OD | mixing-chamber: 80mm | base: reserves 70mm | Chamber overflows bund footprint by 5mm per side |
| Chimney snap ring | mist-chimney: 50mm dia | mixing-chamber: 40mm chimney OD | Snap ring wider than chimney stub — needs interface redesign |
| Oil inlet count | mixing-chamber: 5 ports | oil-carousel: 5 bottles | Match (good) |
| Chimney height | mist-chimney: 70mm standalone | mixing-chamber: 30mm internal | These are different chimneys — the standalone one replaces the internal stub |

These conflicts are left visible so the next design iteration can resolve them with caliper measurements and test prints.
