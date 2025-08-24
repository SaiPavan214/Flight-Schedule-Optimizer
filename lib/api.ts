// API service for connecting to the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Flight {
  id: number;
  flight_number: string;
  airline: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  status: 'On Time' | 'Delayed' | 'Boarding' | 'Cancelled' | 'Departed';
  gate: string;
  terminal: string;
  aircraft: string;
  price?: number;
  created_at: string;
  updated_at?: string;
}

export interface Alert {
  id: number;
  type: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
  created_at: string;
  updated_at?: string;
}

export interface RunwayMetric {
  id: number;
  runway: string;
  utilization: number;
  capacity: number;
  delays: number;
  conflicts: number;
  timestamp: string;
  created_at: string;
}

export interface ChatMessage {
  message: string;
  context?: string;
}

export interface ChatResponse {
  response: string;
  confidence: number;
  sources?: string[];
}

export interface FlightSearchQuery {
  query: string;
  limit?: number;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // Flight endpoints
  async getFlights(params?: {
    skip?: number;
    limit?: number;
    origin?: string;
    destination?: string;
    airline?: string;
    status?: string;
  }): Promise<Flight[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/flights${queryString ? `?${queryString}` : ''}`;
    
    return this.request<Flight[]>(endpoint);
  }

  async getFlight(id: number): Promise<Flight> {
    return this.request<Flight>(`/flights/${id}`);
  }

  async searchFlightsNLP(query: FlightSearchQuery): Promise<Flight[]> {
    return this.request<Flight[]>('/flights/search/nlp', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  async getFlightStatistics(): Promise<any> {
    return this.request<any>('/flights/statistics/overview');
  }

  async getUpcomingFlights(hours: number = 24): Promise<Flight[]> {
    return this.request<Flight[]>(`/flights/upcoming/${hours}`);
  }

  async getDelayedFlights(): Promise<Flight[]> {
    return this.request<Flight[]>('/flights/delayed/all');
  }

  // Alert endpoints
  async getAlerts(params?: {
    skip?: number;
    limit?: number;
    alert_type?: string;
    resolved?: boolean;
    search?: string;
  }): Promise<Alert[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/alerts${queryString ? `?${queryString}` : ''}`;
    
    return this.request<Alert[]>(endpoint);
  }

  async getAlert(id: number): Promise<Alert> {
    return this.request<Alert>(`/alerts/${id}`);
  }

  async getActiveAlerts(): Promise<Alert[]> {
    return this.request<Alert[]>('/alerts/active/all');
  }

  async getCriticalAlerts(): Promise<Alert[]> {
    return this.request<Alert[]>('/alerts/critical/all');
  }

  async getRecentAlerts(hours: number = 24): Promise<Alert[]> {
    return this.request<Alert[]>(`/alerts/recent/${hours}`);
  }

  async getAlertStatistics(): Promise<any> {
    return this.request<any>('/alerts/statistics/overview');
  }

  async resolveAlert(id: number): Promise<Alert> {
    return this.request<Alert>(`/alerts/${id}/resolve`, {
      method: 'POST',
    });
  }

  // Runway endpoints
  async getRunwayMetrics(params?: {
    skip?: number;
    limit?: number;
    runway?: string;
    hours?: number;
  }): Promise<RunwayMetric[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const queryString = searchParams.toString();
    const endpoint = `/runways${queryString ? `?${queryString}` : ''}`;
    
    return this.request<RunwayMetric[]>(endpoint);
  }

  async getCurrentRunwayStatus(): Promise<any[]> {
    return this.request<any[]>('/runways/status/current');
  }

  async getRunwayStatistics(): Promise<any> {
    return this.request<any>('/runways/statistics/overview');
  }

  async getOptimizationRecommendations(): Promise<any> {
    return this.request<any>('/runways/optimization/recommendations');
  }

  async getRunwayUtilizationTrends(runway: string, hours: number = 24): Promise<any[]> {
    return this.request<any[]>(`/runways/${runway}/trends?hours=${hours}`);
  }

  async getPeakHoursAnalysis(runway: string, days: number = 7): Promise<any[]> {
    return this.request<any[]>(`/runways/${runway}/peak-hours?days=${days}`);
  }

  // Chat endpoints
  async sendChatMessage(message: ChatMessage): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify(message),
    });
  }

  async checkChatHealth(): Promise<any> {
    return this.request<any>('/chat/health');
  }

  // Health check
  async healthCheck(): Promise<any> {
    return this.request<any>('/health');
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing or custom instances
export { ApiService };
