# Requirements

## Project Overview
App displaying live data analytics of crops so that risks can be detected early and future growth can be predicted.


## Functional Requirements

### Dashboard
- Display current sensor readings per site in a card-based interface
- Each card shows key metrics: temperature, humidity, air quality
- Clicking a card reveals more detailed information
- Three levels of detail: overview, analysis, raw data

### Sensor Data

- Temperature and humidity
- Plant wetness
- Light levels (day/night)
- Pest/insect count
- Site status: normal, concerning, critical
- Signals from pest traps
- Dashboard home -> Alert summary / 
Data trends etc. -> click on a card -> 
further details displayed​

### Alerts
- Display current active alerts with a plain-language explanation
- Alert severity levels: safe, warning, critical
- Alert history log showing: cause of trigger, when it occurred, simple explanation
- Alerts use colour and icons, designed with colour-blind accessibility in mind

### Visualisations
- Line charts: pest pressure trends over time
- Bar charts: comparing sites with each other
- Heatmap: showing which weeks/months are better or worse
- Alert history log

### Scanner
- Users can scan a plant and receive a result
- Camera access required
- Result must be in plain language with a recommended action

### Map
- Map view showing affected sites and areas

### Login / Accounts



## Non-Functional Requirements

### Accessibility
- Colour and icons used together for alerts (Designed with colour-blind users in mind)
- All language must be plain and avoid technical terminology

### Mobile-First
- Optimised for mobile devices
- Large buttons and simple navigation
- Minimal text for quick reading
- Must work well in the field while inspecting crops

### Performance
- Must handle packet loss from LoRaWAN sensors gracefully
- Data layer must log data quality issues when rows are missing or invalid


## Technical Requirements

### Hardware
- Sensor data collected via LoRaWAN sensors
- Data provided as CSV files

### Software Stack
- Python + SQLite + pandas

### Architecture
- Data layer: load CSV, validate rows, log data quality issues
- Logic layer: output alert events
- Presentation layer: frontend renders the app