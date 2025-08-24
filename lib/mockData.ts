export interface Flight {
  id: string;
  flightNumber: string;
  airline: string;
  origin: string;
  destination: string;
  departureTime: string;
  arrivalTime: string;
  status: 'On Time' | 'Delayed' | 'Boarding' | 'Cancelled' | 'Departed';
  gate: string;
  terminal: string;
  aircraft: string;
  price?: number;
}

export interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
}

export interface RunwayMetric {
  runway: string;
  utilization: number;
  capacity: number;
  delays: number;
  conflicts: number;
}

export const mockFlights: Flight[] = [
  {
    id: '1',
    flightNumber: 'BA123',
    airline: 'British Airways',
    origin: 'LHR',
    destination: 'JFK',
    departureTime: '2025-01-16T14:30:00Z',
    arrivalTime: '2025-01-16T18:45:00Z',
    status: 'On Time',
    gate: 'A12',
    terminal: 'T1',
    aircraft: 'Boeing 777',
    price: 899
  },
  {
    id: '2',
    flightNumber: 'LH456',
    airline: 'Lufthansa',
    origin: 'FRA',
    destination: 'CDG',
    departureTime: '2025-01-16T15:15:00Z',
    arrivalTime: '2025-01-16T16:30:00Z',
    status: 'Boarding',
    gate: 'B7',
    terminal: 'T2',
    aircraft: 'Airbus A320',
    price: 245
  },
  {
    id: '3',
    flightNumber: 'AA789',
    airline: 'American Airlines',
    origin: 'LAX',
    destination: 'ORD',
    departureTime: '2025-01-16T16:00:00Z',
    arrivalTime: '2025-01-16T21:30:00Z',
    status: 'Delayed',
    gate: 'C15',
    terminal: 'T3',
    aircraft: 'Boeing 737',
    price: 456
  },
  {
    id: '4',
    flightNumber: 'EK101',
    airline: 'Emirates',
    origin: 'DXB',
    destination: 'LHR',
    departureTime: '2025-01-16T09:00:00Z',
    arrivalTime: '2025-01-16T13:15:00Z',
    status: 'Departed',
    gate: 'A1',
    terminal: 'T1',
    aircraft: 'Airbus A380',
    price: 1299
  },
  {
    id: '5',
    flightNumber: 'AF202',
    airline: 'Air France',
    origin: 'CDG',
    destination: 'NRT',
    departureTime: '2025-01-17T10:30:00Z',
    arrivalTime: '2025-01-18T05:45:00Z',
    status: 'On Time',
    gate: 'D8',
    terminal: 'T2',
    aircraft: 'Boeing 787',
    price: 1150
  }
];

export const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'critical',
    title: 'Runway 27L Closure',
    message: 'Runway 27L is temporarily closed due to maintenance work. Expected reopening at 17:00.',
    timestamp: '2025-01-16T14:15:00Z',
    resolved: false
  },
  {
    id: '2',
    type: 'warning',
    title: 'Weather Advisory',
    message: 'Strong crosswinds expected between 15:00-18:00. Possible flight delays.',
    timestamp: '2025-01-16T13:45:00Z',
    resolved: false
  },
  {
    id: '3',
    type: 'info',
    title: 'Ground Services Update',
    message: 'Ground services on standby for Flight AZ123 at Gate B12.',
    timestamp: '2025-01-16T14:00:00Z',
    resolved: true
  }
];

export const mockRunwayMetrics: RunwayMetric[] = [
  { runway: '27L', utilization: 85, capacity: 100, delays: 12, conflicts: 2 },
  { runway: '27R', utilization: 92, capacity: 100, delays: 18, conflicts: 4 },
  { runway: '09L', utilization: 76, capacity: 100, delays: 8, conflicts: 1 },
  { runway: '09R', utilization: 68, capacity: 100, delays: 5, conflicts: 0 }
];