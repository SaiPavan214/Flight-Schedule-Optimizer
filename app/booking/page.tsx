'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiService } from '@/lib/apiService';
import { Search, Plane, Clock, MapPin, DollarSign } from 'lucide-react';
import { format, parseISO } from 'date-fns';

export default function FlightBooking() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    try {
      const searchResults = await apiService.searchFlightsNLP(query);
      setResults(searchResults);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const exampleQueries = [
    "Find flights to London after 3 PM tomorrow",
    "Show me flights from New York to Paris",
    "British Airways flights to Dubai",
    "Next available flight to Tokyo"
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">Intelligent Flight Search</h1>
        <p className="text-muted-foreground text-lg">
          Use natural language to find the perfect flight
        </p>
      </div>

      {/* Search Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-6 w-6" />
            <span>Natural Language Search</span>
          </CardTitle>
          <CardDescription>
            Search for flights using everyday language - try "Find flights to London after 3 PM"
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., Find the next available flight to London after 3 PM tomorrow"
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={isSearching}>
              {isSearching ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setQuery(example);
                    setTimeout(() => handleSearch(), 100);
                  }}
                  className="text-xs"
                >
                  {example}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      {hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plane className="h-6 w-6" />
              <span>Search Results</span>
            </CardTitle>
            <CardDescription>
              {isSearching 
                ? 'Searching flights...' 
                : `Found ${results.length} flights matching your query`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isSearching ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12">
                <Plane className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No flights found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search terms or try one of the example queries above.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((flight) => (
                  <Card key={flight.id} className="border-2 hover:border-primary/50 transition-colors">
                    <CardContent className="p-6">
                      <div className="grid md:grid-cols-4 gap-4 items-center">
                        {/* Flight Info */}
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="text-sm">
                              {flight.flight_number}
                            </Badge>
                            <span className="font-medium">{flight.airline}</span>
                          </div>
                          <p className="text-sm text-muted-foreground">{flight.aircraft}</p>
                        </div>

                        {/* Route */}
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <MapPin className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">{flight.origin} → {flight.destination}</span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Terminal {flight.terminal}, Gate {flight.gate}
                          </p>
                        </div>

                        {/* Times */}
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              {format(parseISO(flight.departure_time), 'HH:mm')}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Arrives {format(parseISO(flight.arrival_time), 'HH:mm')}
                          </p>
                        </div>

                        {/* Price & Status */}
                        <div className="space-y-2 text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <DollarSign className="h-4 w-4 text-muted-foreground" />
                            <span className="text-lg font-bold">
                              {flight.price ? `$${flight.price}` : 'N/A'}
                            </span>
                          </div>
                          <div className="space-y-1">
                            <Badge 
                              variant={
                                flight.status === 'On Time' ? 'default' :
                                flight.status === 'Delayed' ? 'destructive' :
                                flight.status === 'Boarding' ? 'secondary' : 'outline'
                              }
                            >
                              {flight.status}
                            </Badge>
                            <Button size="sm" className="w-full">
                              Book Flight
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* AI Features Info */}
      <Card>
        <CardHeader>
          <CardTitle>AI-Powered Features</CardTitle>
          <CardDescription>
            Our intelligent search understands natural language and finds the best matches
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <h3 className="font-semibold">Natural Language Processing</h3>
              <p className="text-sm text-muted-foreground">
                Search using everyday language instead of complex forms and filters.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">Time-Based Matching</h3>
              <p className="text-sm text-muted-foreground">
                Automatically finds flights closest to your preferred departure time.
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">Smart Recommendations</h3>
              <p className="text-sm text-muted-foreground">
                Get personalized suggestions based on your search patterns and preferences.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}