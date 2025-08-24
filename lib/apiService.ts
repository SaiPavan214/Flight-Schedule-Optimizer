// API service for connecting to the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiService = {
  async getFlights() {
    try {
      const response = await fetch(`${API_BASE_URL}/flights/recent/today`);
      if (!response.ok) {
        throw new Error(`Failed to fetch flights: ${response.statusText}`);
      }
      const data = await response.json();
      return data.map((flight: any) => ({
        id: `${flight.Flight_Number}_${flight.Date}`,
        flight_number: flight.Flight_Number,
        airline: flight.Flight_Number.substring(0, 2),
        origin: flight.Route.split('-')[0],
        destination: flight.Route.split('-')[1],
        departure_time: flight.STD_DateTime,
        arrival_time: flight.STA_DateTime,
        status: flight.Departure_Delay_Minutes > 0 ? 'Delayed' : 'On Time',
        gate: 'TBD',
        terminal: 'T1',
        aircraft: 'Boeing 737',
        price: Math.floor(Math.random() * 500) + 200
      }));
    } catch (error) {
      console.error('Error fetching flights:', error);
      // Fallback to mock data
      return [
        {
          id: 1,
          flight_number: "BA123",
          airline: "British Airways",
          origin: "LHR",
          destination: "JFK",
          departure_time: "2024-01-15T14:00:00Z",
          arrival_time: "2024-01-15T20:00:00Z",
          status: "On Time",
          gate: "A12",
          terminal: "T1",
          aircraft: "Boeing 777",
          price: 899
        }
      ];
    }
  },

  async getAlerts() {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/active/all`);
      if (!response.ok) {
        throw new Error(`Failed to fetch alerts: ${response.statusText}`);
      }
      const data = await response.json();
      return data.map((alert: any) => ({
        id: alert.id,
        type: alert.type,
        title: alert.title,
        message: alert.message,
        timestamp: alert.timestamp,
        resolved: alert.resolved
      }));
    } catch (error) {
      console.error('Error fetching alerts:', error);
      // Fallback to mock data
      return [
        {
          id: 1,
          type: "critical",
          title: "Runway Closure",
          message: "Runway 27L temporarily closed",
          timestamp: "2024-01-15T10:00:00Z",
          resolved: false
        }
      ];
    }
  },

  async getRunwayStatistics() {
    try {
      const response = await fetch(`${API_BASE_URL}/runways/statistics/overview`);
      if (!response.ok) {
        throw new Error(`Failed to fetch runway statistics: ${response.statusText}`);
      }
      const data = await response.json();
      return { 
        average_utilization: Math.round((data.total_flights / 500) * 100) || 78,
        total_flights: data.total_flights || 0,
        avg_delays: data.average_delays || 0
      };
    } catch (error) {
      console.error('Error fetching runway statistics:', error);
      return { average_utilization: 78 };
    }
  },

  async searchFlightsNLP(query: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/flights/search/nlp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Failed to search flights: ${response.statusText}`);
      }

      const data = await response.json();
      return data.map((flight: any) => ({
        id: `${flight.Flight_Number}_${flight.Date}`,
        flight_number: flight.Flight_Number,
        airline: flight.Flight_Number.substring(0, 2),
        origin: flight.Route.split('-')[0],
        destination: flight.Route.split('-')[1],
        departure_time: flight.STD_DateTime,
        arrival_time: flight.STA_DateTime,
        status: flight.Departure_Delay_Minutes > 0 ? 'Delayed' : 'On Time',
        gate: 'TBD',
        terminal: 'T1',
        aircraft: 'Boeing 737',
        price: Math.floor(Math.random() * 500) + 200
      }));
    } catch (error) {
      console.error('Error searching flights:', error);
      return [];
    }
  },

  async sendChatMessage(message: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  },

  async getRunwayOptimizationData() {
    try {
      const response = await fetch(`${API_BASE_URL}/runways/optimization/recommendations`);
      if (!response.ok) {
        throw new Error('Failed to fetch runway optimization data');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in getRunwayOptimizationData:', error);
      throw error;
    }
  },

  async getFlightStatistics() {
    try {
      const response = await fetch(`${API_BASE_URL}/flights/statistics/overview`);
      if (!response.ok) {
        throw new Error('Failed to fetch flight statistics');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching flight statistics:', error);
      return {};
    }
  },

  async getRunwayMetrics() {
    try {
      const response = await fetch(`${API_BASE_URL}/runways/`);
      if (!response.ok) {
        throw new Error('Failed to fetch runway metrics');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching runway metrics:', error);
      return [];
    }
  },

  // Schedule Optimization APIs
  async getOptimalTimes(airportCode: string = "BOM") {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule-optimization/optimal-times/${airportCode}`);
      if (!response.ok) throw new Error('Failed to fetch optimal times');
      return await response.json();
    } catch (error) {
      console.error('Error fetching optimal times:', error);
      return null;
    }
  },

  async getBusyTimeSlots(airportCode: string = "BOM") {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule-optimization/busy-time-slots/${airportCode}`);
      if (!response.ok) throw new Error('Failed to fetch busy time slots');
      return await response.json();
    } catch (error) {
      console.error('Error fetching busy time slots:', error);
      return null;
    }
  },

  async optimizeFlightSchedule(flightNumber: string, newDepartureTime: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule-optimization/optimize-flight/${flightNumber}?new_departure_time=${newDepartureTime}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to optimize flight schedule');
      return await response.json();
    } catch (error) {
      console.error('Error optimizing flight schedule:', error);
      return null;
    }
  },

  async getCascadingDelays(minCascadeImpact: number = 30) {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule-optimization/cascading-delays?min_cascade_impact=${minCascadeImpact}`);
      if (!response.ok) throw new Error('Failed to fetch cascading delays');
      return await response.json();
    } catch (error) {
      console.error('Error fetching cascading delays:', error);
      return null;
    }
  },

  async getRunwayCapacityAnalysis(airportCode: string = "BOM") {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule-optimization/runway-capacity/${airportCode}`);
      if (!response.ok) throw new Error('Failed to fetch runway capacity analysis');
      return await response.json();
    } catch (error) {
      console.error('Error fetching runway capacity analysis:', error);
      return null;
    }
  },

  async getScheduleOptimizationSummary(airportCode: string = "BOM") {
    try {
      const response = await fetch(`${API_BASE_URL}/schedule-optimization/summary/${airportCode}`);
      if (!response.ok) throw new Error('Failed to fetch schedule optimization summary');
      return await response.json();
    } catch (error) {
      console.error('Error fetching schedule optimization summary:', error);
      return null;
    }
  }
};
