# 🔥 FireDesk - Digital Twin Pump Room Controller

A professional Digital Twin Dashboard for Fire Safety Pump Room systems built with React (Next.js), Tailwind CSS, and advanced logic engines.

## 🎯 Features

### Core Components
- **Fire Readiness Card**: Displays system readiness status (READY / NEEDS ATTENTION / CRITICAL)
- **Header Pressure Gauge**: Professional radial gauge showing live PSI/bar readings
- **Support Systems**: Diesel level, water volume, and battery health monitoring
- **Pump Availability Grid**: Detailed cards for Electric, Diesel, and Jockey pumps
- **Control Panel**: Interactive manual controls for all system parameters

### Logic Engine
```
IF Header Pressure < 2.0 bar AND Jockey Pump is OFF → Status = 'CRITICAL'
IF Diesel < 50L OR Battery is 'Low' → Fire Readiness = 'NEEDS ATTENTION'
IF Diesel < 10L OR Battery is 'Critical' → Fire Readiness = 'CRITICAL'
```

### Professional Design
- Dark-themed sidebar with collapsible controls
- Industrial white/gray dashboard area
- High-contrast status colors (Green/Red/Blue)
- Smooth animations and transitions
- Real-time state updates

## 🛠 Tech Stack

- **Framework**: Next.js 14
- **UI Library**: React 18
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **Language**: TypeScript

## 📦 Installation

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup

1. **Clone/Navigate to project**:
```bash
cd /home/h4ck3r/Projects/FireDesk
```

2. **Install dependencies**:
```bash
npm install
```

3. **Run development server**:
```bash
npm run dev
```

4. **Open in browser**:
```
http://localhost:3000
```

## 🎮 Usage

### Manual Controls (Sidebar)
- **Header Pressure**: Adjust 0-12 bar with +0.5/-0.5 quick buttons
- **Diesel Level**: Set 0-200 liters with ±10L quick adjustments
- **Water Level**: Configure 0-300 kL with ±10kL buttons
- **Battery Health**: Toggle between Healthy/Low/Critical states
- **Pump Controls**: Turn Electric, Diesel, and Jockey pumps ON/OFF

### Dashboard View
- **Fire Readiness**: Immediate status indicator with system health
- **Radial Gauge**: Real-time header pressure with visual thresholds
- **Support Systems**: Monitor fuel, water, and battery status
- **Pump Cards**: View individual pump modes, status, hours, and efficiency
- **Diagnostics**: System overview and key metrics

## 📊 System States

### Fire Readiness States
| State | Condition | Color |
|-------|-----------|-------|
| READY | All systems normal | 🟢 Green |
| NEEDS ATTENTION | Low fuel/battery | 🟡 Amber |
| CRITICAL | Critical fuel/battery | 🔴 Red |

### System Health States
| State | Condition |
|-------|-----------|
| HEALTHY | All systems operating normally |
| WARNING | Pressure low or pump fault |
| CRITICAL | Pressure critical with jockey pump off |

## 🏗 Project Structure

```
FireDesk/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main dashboard
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   ├── ControlPanel.tsx      # Manual controls
│   │   ├── FireReadinessCard.tsx # Status card
│   │   ├── RadialGauge.tsx       # Pressure gauge
│   │   ├── SupportSystemRow.tsx  # Support systems
│   │   └── PumpCard.tsx          # Pump status cards
│   └── lib/
│       └── pumpRoomEngine.ts     # Logic engine
├── public/                        # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## 🎨 Design Highlights

### Professional Aesthetic
- Dark sidebar (#1a1f2e) with industrial styling
- Light dashboard area with clear card layouts
- Subtle shadows and professional borders
- High-contrast status indicators

### Responsive Design
- Collapsible sidebar for mobile
- Grid layout adapts to screen size
- Touch-friendly controls
- Optimized for all device sizes

### Real-Time Updates
- Automatic pressure fluctuations when jockey pump is running
- Smooth gauge animations
- Instant state synchronization
- Live efficiency tracking

## 🔧 Customization

### Change Pressure Thresholds
Edit `src/lib/pumpRoomEngine.ts`, line 119:
```typescript
const PRESSURE_THRESHOLD = 2.0; // Change critical threshold
```

### Modify Color Scheme
Edit `tailwind.config.js`:
```javascript
colors: {
  status: {
    ready: '#10b981',    // Green
    warning: '#f59e0b',  // Amber
    critical: '#ef4444', // Red
  }
}
```

### Adjust Gauge Ranges
Edit `src/components/RadialGauge.tsx` for custom max values and thresholds.

## 📖 API Reference

### PumpRoomEngine

```typescript
// Create engine instance
const engine = new PumpRoomEngine();

// Update sensors
engine.setHeaderPressure(2.5);
engine.setDieselLevel(150);
engine.setWaterLevel(250);
engine.setBatteryHealth('Healthy');

// Control pumps
engine.togglePump('jockey');
engine.setPumpMode('electric', 'ON');

// Get current state
const state = engine.getState();
const diagnostics = engine.getDiagnostics();
```

## 🧪 Testing

The logic engine includes comprehensive state management:
- Pressure validation (0-12 bar)
- Fuel level tracking (0-200L)
- Water capacity (0-300 kL)
- Battery health monitoring
- Pump status simulation
- Run hours tracking

## 🚀 Deployment

### Build for Production
```bash
npm run build
npm start
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Docker
Create `Dockerfile`:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD npm start
```

## 📱 Browser Support
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎓 Key Concepts

### Digital Twin
This dashboard simulates a real pump room by:
1. Tracking sensor inputs (pressure, levels, battery)
2. Running decision logic (readiness checks)
3. Visualizing system state in real-time
4. Allowing manual control inputs
5. Providing diagnostics and status

### Pump Room Logic
The system implements industrial-standard decision logic:
- **Jockey Pump**: Maintains header pressure automatically
- **Electric Pump**: Primary pump for normal operation
- **Diesel Pump**: Backup pump when electric fails
- **Readiness Checks**: Multi-condition evaluation
- **Pressure Monitoring**: Continuous gauge display

## 📞 Support

For issues or questions:
1. Check the component documentation in code
2. Review the PumpRoomEngine logic
3. Inspect browser console for errors
4. Verify Tailwind CSS is properly built

## 📄 License

This project is part of the FireDesk series - Professional Fire Safety Systems.

## 🔄 Future Enhancements

- [ ] Historical data logging
- [ ] Trend charts and analytics
- [ ] Email/SMS alerts
- [ ] Multi-room dashboard
- [ ] Remote monitoring API
- [ ] Mobile app (React Native)
- [ ] Dark/Light theme toggle
- [ ] Export reports

## 🎉 Credits

Built with Next.js, React, and Tailwind CSS for professional fire safety systems.

---

**Status**: ✅ Production Ready  
**Last Updated**: May 5, 2026  
**Version**: 1.0.0

🔥 FireDesk - Professional Pump Room Control System
