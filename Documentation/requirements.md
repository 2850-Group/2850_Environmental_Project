# Requirements

## Project Overview
App displaying live data analytics of farmers' crops so that risks can be detected early and future growth can be predicted.

---

## Functional Requirements

### Dashboard
- Display current sensor readings per site in a card-based interface
- Each card shows key metrics: temperature, humidity, air quality
- Clicking a card reveals more detailed information
- Three levels of detail: overview, analysis, raw data
- Navigation flow: Dashboard home -> Alert summary / Data trends -> Card -> Further details

### Sensor Data
The system must capture and display the following measures:
- Temperature and humidity
- Plant wetness
- Light levels (day/night)
- Pest/insect count
- Site status: normal, concerning, critical
- Signals from pest traps

### Alerts
- Display current active alerts with a plain-language explanation
- Alert severity levels: Safe, Warning, Critical
- Alert history log showing: cause of trigger, when it occurred, simple explanation
- Alerts use colour and icons , designed with colour-blind accessibility in mind

### Visualisations
- Line charts: pest pressure trends over time
- Bar charts: comparing sites with each other
- Heatmap: showing which weeks/months are better or worse
- Alert history log

### Scanner
- Users can scan a plant and receive a result
- Result must be in plain language with a recommended action
- Camera access required

### Map
- Map view showing affected sites and areas

### Login / Accounts
- User login functionality
- Accounts stored in database

---

## Non-Functional Requirements

### Accessibility
- Colour and icons used together for alerts, not colour alone
- Designed with colour-blind users in mind
- All language must be plain and avoid technical terminology
- WCAG compliance

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
- Python + SQLite + pandas + kivy

### Architecture
- Data layer: load CSV, validate rows, log data quality issues
- Logic layer: output alert events
- Presentation layer: frontend renders the app
