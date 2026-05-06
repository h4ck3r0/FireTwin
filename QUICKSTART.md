# 🚀 FireDesk - Quick Start Guide

Get up and running with the FireDesk Pump Room Controller in 5 minutes!

## Prerequisites

- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (or yarn, pnpm)
- **Git**: For version control

Check versions:
```bash
node --version
npm --version
```

## Installation (3 Steps)

### Step 1: Navigate to Project
```bash
cd /home/h4ck3r/Projects/FireDesk
```

### Step 2: Install Dependencies
```bash
npm install
```

This installs:
- Next.js 14
- React 18
- Tailwind CSS 3
- Lucide React icons
- TypeScript support

### Step 3: Start Development Server
```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

## Access Dashboard

Open your browser:
```
http://localhost:3000
```

You should see the professional FireDesk dashboard with:
- Dark sidebar on the left
- Light dashboard area on the right
- Real-time pump room controls

## First Steps

### 1. Explore the Sidebar
- Click the **Menu** button to toggle sidebar
- You'll see **Manual Controls** section
- Adjust Header Pressure, Diesel Level, Water Level
- Toggle pump ON/OFF switches

### 2. Monitor the Dashboard
- **Fire Readiness Card**: Shows system status
- **Header Pressure Gauge**: Live pressure reading
- **Support Systems**: Fuel, water, battery status
- **Pump Status**: Individual pump information

### 3. Test the Logic
Try these scenarios:

**Scenario 1: Low Pressure (Critical)**
- Move Header Pressure slider to 1.5 bar
- Turn Jockey Pump OFF
- Watch status change to CRITICAL

**Scenario 2: Low Fuel (Warning)**
- Reduce Diesel Level to 40 liters
- Fire Readiness shows "NEEDS ATTENTION"

**Scenario 3: Normal Operation**
- Pressure at 2.5 bar
- Diesel at 150 liters
- Battery Healthy
- Status shows "READY"

## Available Commands

```bash
# Development server (with hot reload)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Main dashboard
│   ├── layout.tsx            # HTML structure
│   └── globals.css           # Global styles
├── components/
│   ├── ControlPanel.tsx      # Controls sidebar
│   ├── FireReadinessCard.tsx # Status card
│   ├── RadialGauge.tsx       # Pressure gauge
│   ├── SupportSystemRow.tsx  # Support cards
│   └── PumpCard.tsx          # Pump cards
└── lib/
    └── pumpRoomEngine.ts     # Logic engine
```

## Key Features to Try

### 1. Real-Time Pressure Fluctuation
- Turn Jockey Pump ON
- Watch pressure fluctuate naturally (2.4-2.7 bar)
- This simulates actual pump behavior

### 2. Radial Gauge
- Move pressure slider
- See smooth gauge animation
- Color changes: Green → Amber → Red based on thresholds

### 3. Support Systems
- Toggle Battery between Healthy/Low/Critical
- Watch Diesel warning appear when fuel < 50L
- Monitor water level with circular progress

### 4. Pump Cards
- See run hours increase when pumps are ON
- Efficiency bars show pump health
- Status updates in real-time

## Logic Engine Explained

The system uses smart decision-making:

```
CRITICAL CONDITIONS:
├─ Pressure < 2.0 bar AND Jockey Pump OFF
├─ Diesel < 10 liters
└─ Battery = Critical

WARNING CONDITIONS:
├─ Pressure < 2.5 bar AND Jockey not running properly
├─ Diesel < 50 liters
├─ Battery = Low
└─ Any pump in Fault state

READY CONDITIONS:
└─ All sensors normal and above thresholds
```

## Troubleshooting

### Port 3000 Already in Use
```bash
# Find and kill process on port 3000
lsof -i :3000
kill -9 <PID>

# Or use different port
npm run dev -- -p 3001
```

### Tailwind Styles Not Loading
```bash
# Rebuild Tailwind CSS
npm run dev

# Or manually rebuild
npx tailwindcss -i ./src/app/globals.css -o ./src/app/output.css
```

### TypeScript Errors
```bash
# Check types
npx tsc --noEmit

# Fix issues and restart server
npm run dev
```

### Node Modules Issues
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Keyboard Shortcuts

- `Ctrl+C` - Stop dev server
- `Ctrl+Shift+R` - Hard refresh browser (clear cache)
- `F12` - Open browser dev tools
- `Ctrl+,` - VS Code settings

## Performance Tips

### Optimize for Local Development
1. Close unused browser tabs
2. Disable browser extensions during testing
3. Use Chrome DevTools Lighthouse for performance metrics

### Monitor in Production
```bash
npm run build  # Build optimized version
npm start      # Start production server
```

## Next Steps

### Customize the Dashboard
1. Edit color scheme in `tailwind.config.js`
2. Modify pump thresholds in `src/lib/pumpRoomEngine.ts`
3. Add new controls in `src/components/ControlPanel.tsx`

### Add Features
- Historical data logging
- Export diagnostics as PDF
- Email alerts
- Dark/Light theme toggle

### Deploy Online
```bash
# Deploy to Vercel (free)
npm install -g vercel
vercel

# Or deploy to other platforms (Netlify, AWS, etc.)
```

## Resources

- **Next.js Docs**: https://nextjs.org/docs
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Lucide Icons**: https://lucide.dev

## Common Patterns

### Add New Sensor
1. Update `PumpRoomState` in `pumpRoomEngine.ts`
2. Add setter method in `PumpRoomEngine` class
3. Create UI component in `components/`
4. Connect to main dashboard in `app/page.tsx`

### Add Alert System
```typescript
// In pumpRoomEngine.ts
if (state.headerPressure < 1.5) {
  // Trigger alert
  console.warn('CRITICAL PRESSURE!');
}
```

### Real-Time Data
```typescript
// In page.tsx
useEffect(() => {
  const interval = setInterval(() => {
    updateState();
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

## Help & Support

If you encounter issues:

1. **Check browser console** (F12)
   - Look for red error messages
   - Read error details carefully

2. **Check terminal output**
   - Look for build errors
   - Verify all dependencies installed

3. **Restart everything**
   ```bash
   # Stop server (Ctrl+C)
   # Clear cache
   rm -rf .next
   # Restart
   npm run dev
   ```

4. **Review documentation**
   - Check README.md for features
   - Read component comments
   - Review logic engine comments

## Quick Reference

| Task | Command |
|------|---------|
| Start dev | `npm run dev` |
| Build prod | `npm run build` |
| Run prod | `npm start` |
| Lint code | `npm run lint` |
| View logs | Check terminal |
| Access UI | `http://localhost:3000` |
| Edit styles | `tailwind.config.js` |
| Edit logic | `src/lib/pumpRoomEngine.ts` |
| Edit UI | `src/components/` |

## That's It!

You're now ready to use FireDesk! 

Start the server with `npm run dev` and open http://localhost:3000 to see your pump room controller in action.

Happy monitoring! 🔥

---

**Need help?** Check README.md for detailed documentation or review component code comments.
