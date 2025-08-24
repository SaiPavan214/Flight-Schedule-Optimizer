import { Flight, mockFlights } from './mockData';
import { format, parseISO, addHours, isBefore, isAfter } from 'date-fns';

export interface SearchQuery {
  destination?: string;
  origin?: string;
  time?: string;
  date?: string;
  airline?: string;
}

export function parseNaturalLanguageQuery(query: string): SearchQuery {
  const parsed: SearchQuery = {};
  const lowercaseQuery = query.toLowerCase();

  // Extract destination
  const toMatch = lowercaseQuery.match(/to\s+([a-z\s]+?)(?:\s|$|after|before|on|at)/);
  if (toMatch) {
    parsed.destination = toMatch[1].trim();
  }

  // Extract origin
  const fromMatch = lowercaseQuery.match(/from\s+([a-z\s]+?)(?:\s|$|to|after|before|on|at)/);
  if (fromMatch) {
    parsed.origin = fromMatch[1].trim();
  }

  // Extract time
  const timeMatch = lowercaseQuery.match(/(?:after|at|before)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)/);
  if (timeMatch) {
    parsed.time = timeMatch[1].trim();
  }

  // Extract date
  const dateMatch = lowercaseQuery.match(/(?:on|today|tomorrow|yesterday)/);
  if (dateMatch) {
    parsed.date = dateMatch[0].trim();
  }

  // Extract airline
  const airlineMatch = lowercaseQuery.match(/(?:british airways|lufthansa|american airlines|emirates|air france)/);
  if (airlineMatch) {
    parsed.airline = airlineMatch[0].trim();
  }

  return parsed;
}

export function searchFlights(query: string): Flight[] {
  const parsedQuery = parseNaturalLanguageQuery(query);
  let results = [...mockFlights];

  // Filter by destination
  if (parsedQuery.destination) {
    const destinationKeywords = parsedQuery.destination.split(' ');
    results = results.filter(flight => 
      destinationKeywords.some(keyword => 
        flight.destination.toLowerCase().includes(keyword) ||
        getCityName(flight.destination).toLowerCase().includes(keyword)
      )
    );
  }

  // Filter by origin
  if (parsedQuery.origin) {
    const originKeywords = parsedQuery.origin.split(' ');
    results = results.filter(flight => 
      originKeywords.some(keyword => 
        flight.origin.toLowerCase().includes(keyword) ||
        getCityName(flight.origin).toLowerCase().includes(keyword)
      )
    );
  }

  // Filter by airline
  if (parsedQuery.airline) {
    results = results.filter(flight => 
      flight.airline.toLowerCase().includes(parsedQuery.airline!)
    );
  }

  // Sort by relevance and time
  results.sort((a, b) => {
    const aTime = new Date(a.departureTime);
    const bTime = new Date(b.departureTime);
    return aTime.getTime() - bTime.getTime();
  });

  return results.slice(0, 10); // Return top 10 results
}

function getCityName(airportCode: string): string {
  const airports: Record<string, string> = {
    'LHR': 'London',
    'JFK': 'New York',
    'FRA': 'Frankfurt',
    'CDG': 'Paris',
    'LAX': 'Los Angeles',
    'ORD': 'Chicago',
    'DXB': 'Dubai',
    'NRT': 'Tokyo'
  };
  return airports[airportCode] || airportCode;
}

export function generateChatbotResponse(message: string): string {
  const lowercaseMessage = message.toLowerCase();

  if (lowercaseMessage.includes('flight') && lowercaseMessage.includes('search')) {
    return "I can help you search for flights using natural language! Try saying something like 'Find flights to London after 3 PM tomorrow' or 'Show me flights from New York to Paris'.";
  }

  if (lowercaseMessage.includes('runway') || lowercaseMessage.includes('delay')) {
    return "You can check our runway optimization dashboard for real-time runway status, capacity metrics, and delay information. Currently, Runway 27L is experiencing some delays due to maintenance.";
  }

  if (lowercaseMessage.includes('alert') || lowercaseMessage.includes('notification')) {
    return "Check the alerts page for the latest airport notifications. We currently have active alerts about runway closures and weather conditions.";
  }

  if (lowercaseMessage.includes('gate') || lowercaseMessage.includes('terminal')) {
    return "For gate and terminal information, please check your specific flight details. Most flights display gate assignments 2 hours before departure.";
  }

  if (lowercaseMessage.includes('weather')) {
    return "Current weather conditions show strong crosswinds expected between 15:00-18:00, which may cause some flight delays. Check the alerts page for the latest updates.";
  }

  if (lowercaseMessage.includes('hello') || lowercaseMessage.includes('hi')) {
    return "Hello! I'm your airport assistant. I can help you with flight searches, runway information, alerts, and general airport queries. What would you like to know?";
  }

  return "I'm here to help with airport operations, flight searches, runway information, and alerts. You can ask me about flight schedules, runway status, or any other airport-related questions!";
}