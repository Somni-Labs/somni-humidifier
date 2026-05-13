# Smart Humidifier ESPHome Configuration

This directory contains the ESPHome firmware configuration for the Somni Smart Humidifier based on ESP32 DevKit C V4.

## Files

- `smart-humidifier.yaml` - Main ESPHome configuration
- `secrets.yaml.template` - Template for WiFi and API credentials
- `secrets.yaml` - Your actual secrets (not tracked in git)

## Hardware Setup

### GPIO Pin Assignments

| GPIO | Function | Description |
|------|----------|-------------|
| 16-20 | Oil Pumps 1-5 | MOSFET gate control for peristaltic pumps |
| 21 | Atomizer | Ultrasonic mister control (PWM capable) |
| 22/23 | I2C SDA/SCL | BME280 sensor communication |
| 34 | Water Level | Capacitive water level sensor (analog) |
| 25 | Status LED | WS2812B addressable LED (optional) |

### Required Components

1. **ESP32 DevKit C V4** - Main controller
2. **BME280 Sensor** - Temperature, humidity, and pressure
3. **5x Peristaltic Pumps** - Essential oil dosing
4. **5x N-Channel MOSFETs** - Pump control (e.g., IRLB8721)
5. **Ultrasonic Atomizer** - Mist generation
6. **Capacitive Water Level Sensor** - Low water detection
7. **WS2812B LED** (optional) - Status indication

## Home Assistant Integration

### Available Entities

#### Switches
- `switch.humidifier_power` - Master atomizer control
- `switch.auto_humidity` - Enable/disable closed-loop mode
- `switch.oil_pump_1` through `switch.oil_pump_5` - Individual pump control

#### Sensors
- `sensor.humidity` - Ambient humidity (BME280)
- `sensor.temperature` - Ambient temperature (BME280) 
- `sensor.pressure` - Barometric pressure (BME280)
- `sensor.water_level` - Water level percentage
- `binary_sensor.water_level_low` - Low water alert

#### Number Controls
- `number.mist_intensity` - Atomizer PWM intensity (0-100%)
- `number.target_humidity` - Humidity setpoint for auto mode (30-80%)
- `number.oil_dose_1` through `number.oil_dose_5` - Pump runtime per dose (0-30s)
- `number.dose_interval` - Time between dose cycles (1-60 min)

#### Select Controls
- `select.oil_blend_preset` - Predefined blend recipes

#### Status & Control
- `text_sensor.device_status` - Current operating mode
- `button.manual_dose` - Trigger immediate oil dose
- `button.stop_all_pumps` - Emergency stop all pumps
- `light.status_led` - RGB status indicator

## Blend Presets

The following presets are built-in and automatically configure oil doses:

| Preset | Oil 1 (Lavender) | Oil 2 (Eucalyptus) | Oil 3 (Peppermint) | Oil 4 (Chamomile) | Oil 5 (Rosemary) |
|--------|------------------|-------------------|-------------------|------------------|------------------|
| **Lavender** | 5s | - | - | - | - |
| **Eucalyptus** | - | 4s | - | - | - |
| **Peppermint** | - | - | 3s | - | - |
| **Relaxation** | 3s | 1s | - | 1s | - |
| **Focus** | - | 2s | 2s | - | 1s |
| **Sleep** | 4s | - | - | 2s | - |
| **Custom 1-3** | User configurable | | | | |

## Safety Features

### Dry-Run Protection
- Continuous water level monitoring
- Automatic atomizer shutdown when water level < 20%
- Emergency stop for all pumps during low water condition

### Auto-Humidity Control
- Closed-loop control maintains target humidity ±2%
- Starts atomizer when humidity drops below target
- Stops atomizer when humidity exceeds target
- Operates only when water level is adequate

### Deep Sleep Mode
- When humidifier is off, ESP32 enters deep sleep after 60 minutes
- Wakes on Home Assistant command or boot button press
- Reduces power consumption during idle periods

## Installation

1. **Setup Secrets**
   ```bash
   cp secrets.yaml.template secrets.yaml
   # Edit secrets.yaml with your WiFi credentials
   ```

2. **Install ESPHome**
   ```bash
   pip install esphome
   ```

3. **Compile and Upload**
   ```bash
   esphome compile smart-humidifier.yaml
   esphome upload smart-humidifier.yaml
   ```

4. **Add to Home Assistant**
   - Device should auto-discover via mDNS
   - Or manually add via "ESPHome" integration

## Customization

### Adjusting Blend Presets
Edit the `oil_blend_preset` select action in the YAML to modify preset recipes or add new ones.

### Calibrating Water Level Sensor
Adjust the percentage calculation in the water level sensor lambda function based on your sensor's voltage range.

### Modifying Auto-Humidity Thresholds
Change the ±2% deadband in the humidity sensor's `on_value` action for different control behavior.

### Adding Physical Controls
Uncomment and configure additional GPIO pins for physical buttons or switches if desired.

## Troubleshooting

### Common Issues

1. **Device won't connect to WiFi**
   - Check secrets.yaml credentials
   - Device will create "Smart-Humidifier-Fallback" AP if WiFi fails

2. **Pumps not working**
   - Verify MOSFET wiring and gate voltages
   - Check pump power supply (typically 12V)

3. **Inaccurate humidity readings**
   - BME280 may need calibration offset
   - Check I2C wiring (pullup resistors may be needed)

4. **Water level sensor erratic**
   - Capacitive sensors can be noisy
   - Adjust sliding window filter settings
   - Ensure sensor is properly grounded

### Debug Logging
Set logger level to `DEBUG` in the YAML for detailed troubleshooting information.

## Safety Warnings

- **Electrical Safety**: Use proper MOSFETs rated for your pump current
- **Water Safety**: Keep all electronics away from water/mist
- **Oil Safety**: Use only water-soluble essential oils designed for diffusers
- **Ventilation**: Ensure adequate room ventilation when using essential oils