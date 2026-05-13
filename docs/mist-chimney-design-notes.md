# Mist Chimney and Outlet Nozzle Design

## Overview

The mist chimney is the most visible component of the smart humidifier, designed for desktop placement in bedrooms and offices. It channels atomized water+oil upward through an aesthetically pleasing directional nozzle.

## Design File

`designs/v1-mist-chimney.py` - CadQuery design implementation

## Key Specifications

### Chimney Tube
- **Inner Diameter**: 35mm (target range: 30-40mm)
- **Outer Diameter**: 42mm (3.5mm wall thickness)
- **Height**: 70mm above mixing chamber (target: 60-80mm)
- **Internal Surface**: Smooth walls to minimize condensation drip-back
- **External Taper**: Subtle 5% taper toward top for aesthetics

### Directional Nozzle
- **Outlet Diameter**: 25mm
- **Angle**: 15° upward for mist direction
- **Anti-drip Lip**: 2mm inward curve to prevent condensation rundown
- **Shape**: Elliptical for improved flow characteristics

### Connection System
- **Snap Ring**: 50mm diameter for attachment to mixing chamber
- **Connection Height**: 8mm with snap groove
- **Groove Dimensions**: 2mm width × 1.5mm depth
- **Lead-in Chamfer**: 1mm for easier assembly

### Aesthetic Features
- **Fillet Radius**: 3mm throughout for smooth organic curves
- **Minimal Seams**: Single-piece design where possible
- **Removable**: Snap-on attachment for easy cleaning

## Design Considerations

### Flow Dynamics
- Internal flow guide creates gentle taper in top 30% of chimney
- Accelerates mist toward outlet while reducing turbulence
- Nozzle opening sized at 80% of body diameter for velocity increase

### Anti-Condensation Features
- Smooth internal surfaces minimize droplet formation
- Anti-drip lip prevents exterior condensation rundown
- Removable design allows soaking in vinegar for mineral deposit removal

### Manufacturing Compatibility
- Wall thickness optimized for 3D printing/injection molding
- Snap-fit tolerances designed for typical manufacturing variations
- Filleted edges reduce stress concentrations

## TODO Items

### Flow Optimization
- [ ] CFD analysis to verify mist flow characteristics
- [ ] Test optimal inner diameter for flow rate vs. velocity
- [ ] Validate nozzle angle for desired mist reach

### Mechanical Design
- [ ] Test snap-fit force requirements
- [ ] Verify wall thickness for durability
- [ ] Manufacturing constraint review for chosen production method

### User Experience
- [ ] Surface finish specifications for easy cleaning
- [ ] Color and material selection for desktop aesthetics
- [ ] Assembly/disassembly force testing

## Integration Points

### With Mixing Chamber
- Snap-on connection at base of chimney
- Sealing requirements for mist containment
- Alignment features for consistent assembly

### With Electronics Housing
- Clearance requirements for internal components
- Cable routing considerations if sensors needed
- Vibration isolation from ultrasonic transducer

## Testing Requirements

### Performance Testing
- Mist output pattern and reach measurements
- Condensation buildup over extended operation
- Cleaning effectiveness and reassembly ease

### Durability Testing
- Repeated assembly/disassembly cycles
- Mineral deposit resistance
- Snap-fit retention over time

## Design Evolution

This is v1 of the mist chimney design. Future iterations may include:

- Adjustable nozzle angle mechanism
- Integrated LED mood lighting
- Scent diffusion optimization
- Smart sensors for mist quality monitoring

---

**Status**: Initial design complete, pending prototype testing
**Next Steps**: Manufacturing review and flow testing
**Dependencies**: Mixing chamber interface specification