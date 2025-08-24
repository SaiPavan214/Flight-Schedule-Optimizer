import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime, timedelta
from ..config import settings

class GeminiService:
    def __init__(self):
        self.api_key_available = bool(settings.google_api_key and settings.google_api_key != "your_gemini_api_key_here")
        
        if self.api_key_available:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini AI: {e}")
                self.api_key_available = False
        else:
            print("Warning: Google API key not configured. Using fallback responses.")
        
        # Airport and airline mappings for better context
        self.airport_codes = {
            'lhr': 'London Heathrow',
            'jfk': 'New York JFK',
            'fra': 'Frankfurt',
            'cdg': 'Paris Charles de Gaulle',
            'lax': 'Los Angeles',
            'ord': 'Chicago O\'Hare',
            'dxb': 'Dubai',
            'nrt': 'Tokyo Narita',
            'syd': 'Sydney',
            'sin': 'Singapore',
            'hkg': 'Hong Kong',
            'bom': 'Mumbai',
            'del': 'Delhi',
            'pek': 'Beijing',
            'shanghai': 'PVG',
            'beijing': 'PEK',
            'tokyo': 'NRT',
            'london': 'LHR',
            'new york': 'JFK',
            'paris': 'CDG',
            'frankfurt': 'FRA',
            'dubai': 'DXB',
            'singapore': 'SIN',
            'sydney': 'SYD'
        }
        
        self.airlines = {
            'british airways': 'BA',
            'lufthansa': 'LH',
            'american airlines': 'AA',
            'emirates': 'EK',
            'air france': 'AF',
            'united airlines': 'UA',
            'delta': 'DL',
            'qatar airways': 'QR',
            'singapore airlines': 'SQ',
            'cathay pacific': 'CX'
        }

    async def parse_flight_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language flight search query using Gemini AI
        """
        prompt = f"""
        You are an airport flight search assistant. Parse the following natural language query and extract flight search parameters.
        
        Query: "{query}"
        
        Extract and return ONLY a JSON object with the following structure:
        {{
            "origin": "airport code or city name",
            "destination": "airport code or city name", 
            "date": "YYYY-MM-DD or relative date like 'today', 'tomorrow'",
            "time": "HH:MM or relative time like 'morning', 'afternoon', 'evening'",
            "airline": "airline name or code",
            "max_price": "numeric value if mentioned",
            "direct_only": "boolean if direct flights only requested"
        }}
        
        Rules:
        - If a field is not mentioned, set it to null
        - Convert city names to airport codes when possible
        - Handle relative dates (today, tomorrow, next week)
        - Handle relative times (morning = 06:00-12:00, afternoon = 12:00-18:00, evening = 18:00-24:00)
        - Return ONLY the JSON object, no other text
        """
        
        try:
            response = await self._generate_response(prompt)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return self._normalize_search_params(parsed)
            else:
                return self._fallback_parse(query)
        except Exception as e:
            print(f"Error parsing query with Gemini: {e}")
            return self._fallback_parse(query)

    async def generate_chatbot_response(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate contextual chatbot response using Gemini AI
        """
        system_prompt = """
        You are an AI assistant for an airport operations management system. You help users with:
        1. Flight information and searches
        2. Airport operations and runway status
        3. Real-time alerts and notifications
        4. General airport assistance
        
        Be helpful, concise, and professional. If you don't have specific information, suggest where they can find it.
        """
        
        user_prompt = f"""
        User message: "{message}"
        {f"Context: {context}" if context else ""}
        
        Provide a helpful response that addresses the user's query. If they're asking about flights, runway status, or alerts, 
        acknowledge their request and suggest they check the relevant dashboard sections.
        """
        
        try:
            response = await self._generate_response(system_prompt + "\n\n" + user_prompt)
            return {
                "response": response,
                "confidence": 0.9,
                "sources": ["airport_operations_database"]
            }
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return {
                "response": "I'm having trouble processing your request right now. Please try again or check the relevant dashboard sections for the information you need.",
                "confidence": 0.3,
                "sources": []
            }

    async def analyze_runway_optimization(self, runway_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze runway data and provide optimization recommendations using Gemini AI
        """
        prompt = f"""
        You are an airport operations analyst. Analyze the following runway utilization data and provide optimization recommendations:
        
        Runway Data: {json.dumps(runway_data, indent=2)}
        
        Provide a JSON response with:
        {{
            "analysis": "brief analysis of current runway utilization",
            "recommendations": [
                {{
                    "type": "immediate|strategic",
                    "action": "specific action to take",
                    "impact": "expected improvement",
                    "priority": "high|medium|low"
                }}
            ],
            "efficiency_score": "0-100 score",
            "bottlenecks": ["list of identified bottlenecks"]
        }}
        
        Focus on practical, actionable recommendations for airport operations.
        """
        
        try:
            response = await self._generate_response(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._default_optimization_response()
        except Exception as e:
            print(f"Error analyzing runway optimization: {e}")
            return self._default_optimization_response()

    async def _generate_response(self, prompt: str) -> str:
        """Generate response from Gemini AI"""
        if not self.api_key_available:
            # Return a fallback response when API key is not available
            return self._generate_fallback_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback responses when Gemini AI is not available"""
        prompt_lower = prompt.lower()
        
        # Flight search related responses
        if any(word in prompt_lower for word in ['flight', 'fly', 'airline', 'destination']):
            return "I can help you find flights! Please use the Flight Search page or ask me specific questions about flights, routes, or airlines."
        
        # Airport operations related responses
        if any(word in prompt_lower for word in ['runway', 'gate', 'terminal', 'delay']):
            return "For real-time airport operations information, please check the Analytics page for runway status and the Alerts page for current notifications."
        
        # General airport assistance
        if any(word in prompt_lower for word in ['help', 'assist', 'where', 'how']):
            return "I'm here to help with airport operations! You can ask me about flights, check runway status, view alerts, or get general airport information. For detailed data, please use the respective dashboard sections."
        
        # Default response
        return "I'm your airport operations assistant. I can help you with flight information, runway status, alerts, and general airport questions. Please let me know what you need!"

    def _normalize_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate search parameters"""
        normalized = {}
        
        # Normalize airport codes
        if params.get('origin'):
            normalized['origin'] = self._normalize_airport_code(params['origin'])
        if params.get('destination'):
            normalized['destination'] = self._normalize_airport_code(params['destination'])
        
        # Normalize airline codes
        if params.get('airline'):
            normalized['airline'] = self._normalize_airline_code(params['airline'])
        
        # Handle dates
        if params.get('date'):
            normalized['date'] = self._parse_date(params['date'])
        
        # Handle times
        if params.get('time'):
            normalized['time'] = self._parse_time(params['time'])
        
        # Other parameters
        for key in ['max_price', 'direct_only']:
            if key in params:
                normalized[key] = params[key]
        
        return normalized

    def _normalize_airport_code(self, code_or_city: str) -> str:
        """Convert city names to airport codes"""
        code_or_city_lower = code_or_city.lower().strip()
        return self.airport_codes.get(code_or_city_lower, code_or_city.upper())

    def _normalize_airline_code(self, airline: str) -> str:
        """Convert airline names to codes"""
        airline_lower = airline.lower().strip()
        return self.airlines.get(airline_lower, airline.upper())

    def _parse_date(self, date_str: str) -> str:
        """Parse relative dates to YYYY-MM-DD format"""
        today = datetime.now()
        
        if date_str.lower() == 'today':
            return today.strftime('%Y-%m-%d')
        elif date_str.lower() == 'tomorrow':
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'next week' in date_str.lower():
            return (today + timedelta(days=7)).strftime('%Y-%m-%d')
        else:
            # Try to parse as YYYY-MM-DD
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                return today.strftime('%Y-%m-%d')

    def _parse_time(self, time_str: str) -> str:
        """Parse relative times to HH:MM format"""
        time_str_lower = time_str.lower().strip()
        
        if 'morning' in time_str_lower:
            return '09:00'
        elif 'afternoon' in time_str_lower:
            return '14:00'
        elif 'evening' in time_str_lower:
            return '18:00'
        elif 'night' in time_str_lower:
            return '22:00'
        else:
            # Try to parse as HH:MM
            try:
                datetime.strptime(time_str, '%H:%M')
                return time_str
            except ValueError:
                return '12:00'

    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Fallback parsing when Gemini fails"""
        query_lower = query.lower()
        parsed = {}
        
        # Simple keyword extraction
        for city, code in self.airport_codes.items():
            if city in query_lower:
                if 'from' in query_lower and query_lower.index('from') < query_lower.index(city):
                    parsed['origin'] = code
                elif 'to' in query_lower and query_lower.index('to') < query_lower.index(city):
                    parsed['destination'] = code
        
        for airline, code in self.airlines.items():
            if airline in query_lower:
                parsed['airline'] = code
        
        return parsed

    def _default_optimization_response(self) -> Dict[str, Any]:
        """Default response when optimization analysis fails"""
        return {
            "analysis": "Unable to analyze runway data at this time",
            "recommendations": [
                {
                    "type": "immediate",
                    "action": "Monitor runway utilization patterns",
                    "impact": "Better understanding of traffic flow",
                    "priority": "medium"
                }
            ],
            "efficiency_score": 75,
            "bottlenecks": ["Analysis temporarily unavailable"]
        }

# Global instance
gemini_service = GeminiService()
