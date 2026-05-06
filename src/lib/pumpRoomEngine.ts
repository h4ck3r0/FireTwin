/**
 * Pump Room System Logic Engine
 * 
 * Manages the state and decision logic for the Fire Safety Pump Room
 * including pump status, readiness checks, and system diagnostics.
 */

export interface PumpRoomState {
  // Pressure and Levels
  headerPressure: number; // 0-12 bar
  dieselLevel: number; // 0-200 liters
  waterLevel: number; // 0-300 kL
  batteryHealth: 'Healthy' | 'Low' | 'Critical';

  // Pump Status
  electricPump: PumpStatus;
  dieselPump: PumpStatus;
  jockeyPump: PumpStatus;

  // Derived Status
  fireReadiness: 'READY' | 'NEEDS_ATTENTION' | 'CRITICAL';
  systemHealth: 'HEALTHY' | 'WARNING' | 'CRITICAL';
}

export interface PumpStatus {
  mode: 'ON' | 'OFF';
  status: 'Running' | 'Standby' | 'Fault' | 'Offline';
  runHours: number;
  efficiency: number; // 0-100%
  lastServiceDate?: string;
}

export class PumpRoomEngine {
  private state: PumpRoomState;

  constructor(initialState?: Partial<PumpRoomState>) {
    this.state = {
      headerPressure: 2.5,
      dieselLevel: 150,
      waterLevel: 250,
      batteryHealth: 'Healthy',
      electricPump: {
        mode: 'OFF',
        status: 'Standby',
        runHours: 125,
        efficiency: 98,
      },
      dieselPump: {
        mode: 'OFF',
        status: 'Standby',
        runHours: 45,
        efficiency: 95,
      },
      jockeyPump: {
        mode: 'ON',
        status: 'Running',
        runHours: 3200,
        efficiency: 92,
      },
      fireReadiness: 'READY',
      systemHealth: 'HEALTHY',
      ...initialState,
    };

    this.evaluateStatus();
  }

  /**
   * Update header pressure
   */
  setHeaderPressure(pressure: number): void {
    this.state.headerPressure = Math.max(0, Math.min(12, pressure));
    this.evaluateStatus();
  }

  /**
   * Update diesel level
   */
  setDieselLevel(level: number): void {
    this.state.dieselLevel = Math.max(0, Math.min(200, level));
    this.evaluateStatus();
  }

  /**
   * Update water level
   */
  setWaterLevel(level: number): void {
    this.state.waterLevel = Math.max(0, Math.min(300, level));
    this.evaluateStatus();
  }

  /**
   * Update battery health
   */
  setBatteryHealth(health: 'Healthy' | 'Low' | 'Critical'): void {
    this.state.batteryHealth = health;
    this.evaluateStatus();
  }

  /**
   * Toggle pump mode
   */
  togglePump(pump: 'electric' | 'diesel' | 'jockey'): void {
    const pumpKey = `${pump}Pump` as keyof PumpRoomState;
    const pumpStatus = this.state[pumpKey] as PumpStatus;
    
    pumpStatus.mode = pumpStatus.mode === 'ON' ? 'OFF' : 'ON';
    
    // Update running status
    if (pumpStatus.mode === 'ON') {
      pumpStatus.status = 'Running';
      pumpStatus.runHours += 0.1; // Simulate run hour increment
    } else {
      pumpStatus.status = 'Standby';
    }

    this.evaluateStatus();
  }

  /**
   * Set pump to specific mode
   */
  setPumpMode(pump: 'electric' | 'diesel' | 'jockey', mode: 'ON' | 'OFF'): void {
    const pumpKey = `${pump}Pump` as keyof PumpRoomState;
    const pumpStatus = this.state[pumpKey] as PumpStatus;
    
    pumpStatus.mode = mode;
    pumpStatus.status = mode === 'ON' ? 'Running' : 'Standby';

    this.evaluateStatus();
  }

  /**
   * Core decision logic for fire readiness
   * 
   * CRITICAL: Diesel < 10L OR Battery is 'Critical' OR Water < 50 kL OR Pressure < 1.5 bar OR Pressure > 10 bar
   * NEEDS_ATTENTION: Diesel < 50L OR Battery is 'Low' OR Water < 100 kL OR Pressure < 2.0 bar OR Pressure > 8 bar
   */
  private evaluateFireReadiness(): 'READY' | 'NEEDS_ATTENTION' | 'CRITICAL' {
    // Critical conditions
    if (
      this.state.dieselLevel < 10 ||
      this.state.batteryHealth === 'Critical' ||
      this.state.waterLevel < 50 ||
      this.state.headerPressure < 1.5 ||
      this.state.headerPressure > 10
    ) {
      return 'CRITICAL';
    }

    // Warning conditions
    if (
      this.state.dieselLevel < 50 ||
      this.state.batteryHealth === 'Low' ||
      this.state.waterLevel < 100 ||
      this.state.headerPressure < 2.0 ||
      this.state.headerPressure > 8
    ) {
      return 'NEEDS_ATTENTION';
    }

    // All systems good
    return 'READY';
  }

  /**
   * Core decision logic for system status
   * 
   * CRITICAL: Pressure < 1.5 bar OR Pressure > 10 bar (with pump off)
   * WARNING: Pressure < 2.0 bar OR Pressure > 9 bar, OR Low pressure with jockey not running
   */
  private evaluateSystemHealth(): 'HEALTHY' | 'WARNING' | 'CRITICAL' {
    const jockey = this.state.jockeyPump;
    const pressure = this.state.headerPressure;

    // Critical: Dangerously low pressure or dangerously high pressure
    if ((pressure < 1.5 && jockey.mode === 'OFF') || pressure > 10) {
      return 'CRITICAL';
    }

    // Warning: Low pressure conditions
    if (pressure < 2.0 && jockey.status !== 'Running') {
      return 'WARNING';
    }

    // Warning: High pressure building up
    if (pressure > 9) {
      return 'WARNING';
    }

    // Warning: Any pump in fault state
    if (
      this.state.electricPump.status === 'Fault' ||
      this.state.dieselPump.status === 'Fault' ||
      this.state.jockeyPump.status === 'Fault'
    ) {
      return 'WARNING';
    }

    return 'HEALTHY';
  }

  /**
   * Evaluate all system statuses
   */
  private evaluateStatus(): void {
    this.state.fireReadiness = this.evaluateFireReadiness();
    this.state.systemHealth = this.evaluateSystemHealth();
  }

  /**
   * Get current state
   */
  getState(): PumpRoomState {
    return { ...this.state };
  }

  /**
   * Get diagnostics
   */
  getDiagnostics() {
    return {
      timestamp: new Date().toISOString(),
      pressure: this.state.headerPressure,
      diesel: this.state.dieselLevel,
      water: this.state.waterLevel,
      battery: this.state.batteryHealth,
      fireReadiness: this.state.fireReadiness,
      systemHealth: this.state.systemHealth,
      pumps: {
        electric: {
          mode: this.state.electricPump.mode,
          status: this.state.electricPump.status,
          hours: this.state.electricPump.runHours.toFixed(1),
          efficiency: this.state.electricPump.efficiency,
        },
        diesel: {
          mode: this.state.dieselPump.mode,
          status: this.state.dieselPump.status,
          hours: this.state.dieselPump.runHours.toFixed(1),
          efficiency: this.state.dieselPump.efficiency,
        },
        jockey: {
          mode: this.state.jockeyPump.mode,
          status: this.state.jockeyPump.status,
          hours: this.state.jockeyPump.runHours.toFixed(1),
          efficiency: this.state.jockeyPump.efficiency,
        },
      },
    };
  }
}
