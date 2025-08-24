"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { apiService } from "@/lib/apiService";
import { 
  Clock, 
  AlertTriangle, 
  TrendingUp, 
  Plane, 
  Calendar,
  BarChart3,
  Activity,
  Target
} from "lucide-react";

interface OptimalTimes {
  best_departure_hours: number[];
  worst_departure_hours: number[];
  best_arrival_hours: number[];
  worst_arrival_hours: number[];
  recommendations: string[];
}

interface BusyTimeSlots {
  peak_hours: number[];
  quiet_hours: number[];
  congestion_score: { [key: number]: number };
  recommendations: string[];
}

interface CascadingDelays {
  total_cascading_flights: number;
  high_impact_flights: Array<{
    flight_number: string;
    route: string;
    cascade_impact: number;
    delay_minutes: number;
  }>;
  recommendations: string[];
}

interface RunwayCapacity {
  bottlenecks: Array<{
    hour: number;
    utilization: number;
    flight_count: number;
  }>;
  underutilized_slots: Array<{
    hour: number;
    utilization: number;
    flight_count: number;
  }>;
  optimization_opportunities: string[];
}

interface ScheduleOptimizationSummary {
  airport_code: string;
  optimal_times: OptimalTimes;
  busy_time_slots: BusyTimeSlots;
  capacity_analysis: RunwayCapacity;
  cascading_delays_count: number;
  recommendations: {
    timing: string[];
    avoidance: string[];
    capacity: string[];
    cascading: string[];
  };
}

export default function ScheduleOptimizationPage() {
  const [airportCode, setAirportCode] = useState("BOM");
  const [summary, setSummary] = useState<ScheduleOptimizationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flightNumber, setFlightNumber] = useState("");
  const [newDepartureTime, setNewDepartureTime] = useState("");
  const [optimizationResult, setOptimizationResult] = useState<any>(null);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getScheduleOptimizationSummary(airportCode);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch optimization data");
    } finally {
      setLoading(false);
    }
  };

  const optimizeFlight = async () => {
    if (!flightNumber || !newDepartureTime) {
      setError("Please provide both flight number and new departure time");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await apiService.optimizeFlightSchedule(flightNumber, newDepartureTime);
      setOptimizationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to optimize flight schedule");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [airportCode]);

  const availableAirports = ["BOM", "DEL", "BLR", "HYD", "CCU"];

  if (loading && !summary) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Flight Schedule Optimization</h1>
          <p className="text-muted-foreground">
            AI-powered flight scheduling optimization and analysis
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Label htmlFor="airport-select">Airport:</Label>
          <select
            id="airport-select"
            value={airportCode}
            onChange={(e) => setAirportCode(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            {availableAirports.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
          <Button onClick={fetchSummary} disabled={loading}>
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="optimal-times">Optimal Times</TabsTrigger>
          <TabsTrigger value="busy-slots">Busy Slots</TabsTrigger>
          <TabsTrigger value="cascading">Cascading Delays</TabsTrigger>
          <TabsTrigger value="capacity">Runway Capacity</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Optimal Departure Hours</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summary?.optimal_times?.best_departure_hours?.length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Best hours for departures
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Peak Hours</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summary?.busy_time_slots?.peak_hours?.length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Hours to avoid
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Cascading Delays</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summary?.cascading_delays_count || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  High impact flights
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Bottlenecks</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summary?.capacity_analysis?.bottlenecks?.length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Capacity constraints
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Key Recommendations</CardTitle>
              <CardDescription>
                AI-generated insights for schedule optimization
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {summary?.recommendations?.timing?.map((rec, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <Target className="h-4 w-4 text-blue-500 mt-1" />
                  <p className="text-sm">{rec}</p>
                </div>
              ))}
              {summary?.recommendations?.avoidance?.map((rec, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <AlertTriangle className="h-4 w-4 text-orange-500 mt-1" />
                  <p className="text-sm">{rec}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="optimal-times" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Optimal Takeoff & Landing Times</CardTitle>
              <CardDescription>
                Best and worst times for departures and arrivals based on delay analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3 text-green-600">Best Departure Hours</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary?.optimal_times?.best_departure_hours?.map((hour) => (
                      <Badge key={hour} variant="secondary" className="text-green-700">
                        {hour}:00
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 text-red-600">Worst Departure Hours</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary?.optimal_times?.worst_departure_hours?.map((hour) => (
                      <Badge key={hour} variant="destructive">
                        {hour}:00
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 text-green-600">Best Arrival Hours</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary?.optimal_times?.best_arrival_hours?.map((hour) => (
                      <Badge key={hour} variant="secondary" className="text-green-700">
                        {hour}:00
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 text-red-600">Worst Arrival Hours</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary?.optimal_times?.worst_arrival_hours?.map((hour) => (
                      <Badge key={hour} variant="destructive">
                        {hour}:00
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-semibold mb-3">Timing Recommendations</h4>
                <div className="space-y-2">
                  {summary?.optimal_times?.recommendations?.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <Clock className="h-4 w-4 text-blue-500 mt-1" />
                      <p className="text-sm">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="busy-slots" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Busy Time Slots Analysis</CardTitle>
              <CardDescription>
                Identify peak and quiet hours to optimize scheduling
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3 text-red-600">Peak Hours (Avoid)</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary?.busy_time_slots?.peak_hours?.map((hour) => (
                      <Badge key={hour} variant="destructive">
                        {hour}:00
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    High congestion and delays expected
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 text-green-600">Quiet Hours (Recommended)</h4>
                  <div className="flex flex-wrap gap-2">
                    {summary?.busy_time_slots?.quiet_hours?.map((hour) => (
                      <Badge key={hour} variant="secondary" className="text-green-700">
                        {hour}:00
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    Low congestion, optimal for scheduling
                  </p>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-semibold mb-3">Congestion Score by Hour</h4>
                <div className="grid grid-cols-6 gap-2">
                  {Array.from({ length: 24 }, (_, hour) => {
                    const score = summary?.busy_time_slots?.congestion_score?.[hour] || 0;
                    const isPeak = summary?.busy_time_slots?.peak_hours?.includes(hour);
                    const isQuiet = summary?.busy_time_slots?.quiet_hours?.includes(hour);
                    
                    let variant: "default" | "secondary" | "destructive" = "default";
                    if (isPeak) variant = "destructive";
                    else if (isQuiet) variant = "secondary";
                    
                    return (
                      <div key={hour} className="text-center">
                        <Badge variant={variant} className="w-full justify-center">
                          {hour}:00
                        </Badge>
                        <div className="text-xs mt-1">{score.toFixed(1)}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-semibold mb-3">Avoidance Recommendations</h4>
                <div className="space-y-2">
                  {summary?.busy_time_slots?.recommendations?.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <AlertTriangle className="h-4 w-4 text-orange-500 mt-1" />
                      <p className="text-sm">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cascading" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cascading Delay Analysis</CardTitle>
              <CardDescription>
                Identify flights with the biggest impact on schedule delays
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">
                    {summary?.cascading_delays_count || 0}
                  </div>
                  <p className="text-sm text-muted-foreground">High Impact Flights</p>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-semibold mb-3">Flights with Highest Cascade Impact</h4>
                <div className="space-y-3">
                  {summary?.capacity_analysis?.bottlenecks?.map((flight, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Plane className="h-5 w-5 text-blue-500" />
                        <div>
                          <p className="font-medium">Route: {flight.hour}:00</p>
                          <p className="text-sm text-muted-foreground">
                            Utilization: {flight.utilization.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      <Badge variant="destructive">
                        {flight.flight_count} flights
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-semibold mb-3">Cascade Prevention Recommendations</h4>
                <div className="space-y-2">
                  {summary?.recommendations?.cascading?.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <TrendingUp className="h-4 w-4 text-blue-500 mt-1" />
                      <p className="text-sm">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="capacity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Runway Capacity Analysis</CardTitle>
              <CardDescription>
                Identify bottlenecks and optimization opportunities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3 text-red-600">Bottlenecks (Over 80% Utilization)</h4>
                  <div className="space-y-2">
                    {summary?.capacity_analysis?.bottlenecks?.map((bottleneck, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border rounded">
                        <span className="font-medium">{bottleneck.hour}:00</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm">{bottleneck.flight_count} flights</span>
                          <Badge variant="destructive">
                            {bottleneck.utilization.toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 text-green-600">Underutilized Slots (Under 40%)</h4>
                  <div className="space-y-2">
                    {summary?.capacity_analysis?.underutilized_slots?.map((slot, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border rounded">
                        <span className="font-medium">{slot.hour}:00</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm">{slot.flight_count} flights</span>
                          <Badge variant="secondary" className="text-green-700">
                            {slot.utilization.toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="font-semibold mb-3">Capacity Optimization Opportunities</h4>
                <div className="space-y-2">
                  {summary?.capacity_analysis?.optimization_opportunities?.map((opp, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <Activity className="h-4 w-4 text-blue-500 mt-1" />
                      <p className="text-sm">{opp}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Flight Schedule Optimization Tool</CardTitle>
          <CardDescription>
            Test the impact of changing departure times for specific flights
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="flight-number">Flight Number</Label>
              <Input
                id="flight-number"
                placeholder="e.g., AI101"
                value={flightNumber}
                onChange={(e) => setFlightNumber(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="departure-time">New Departure Time</Label>
              <Input
                id="departure-time"
                type="time"
                value={newDepartureTime}
                onChange={(e) => setNewDepartureTime(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={optimizeFlight} disabled={loading || !flightNumber || !newDepartureTime}>
                {loading ? "Optimizing..." : "Optimize Schedule"}
              </Button>
            </div>
          </div>

          {optimizationResult && (
            <div className="mt-4 p-4 border rounded-lg bg-muted">
              <h4 className="font-semibold mb-2">Optimization Result:</h4>
              <pre className="text-sm overflow-auto">
                {JSON.stringify(optimizationResult, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
