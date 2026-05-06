"""
Gauge Reader Data Service
Reads live pressure data from gauge_status.json and updates the dashboard.
"""

export interface GaugeReading {
  pressure: number;
  unit: string;
  timestamp: number;
  gauge_name: string;
  detection_success: boolean;
  angle_degrees?: number;
}

export async function readGaugeStatus(filepath: string = '/gauge_status.json'): Promise<GaugeReading | null> {
  try {
    const response = await fetch(filepath);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error('Failed to read gauge status:', error);
    return null;
  }
}

// WebSocket connection for real-time updates (optional)
export class GaugeReaderWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(url: string = 'ws://localhost:5000'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('Connected to gauge reader WebSocket');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('Disconnected from gauge reader');
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = 1000 * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Attempting to reconnect in ${delay}ms...`);
      setTimeout(() => this.connect(), delay);
    }
  }

  onMessage(callback: (data: GaugeReading) => void) {
    if (this.ws) {
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          callback(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
    }
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
