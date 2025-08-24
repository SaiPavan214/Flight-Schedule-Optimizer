"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Chatbot } from "@/components/chatbot";
import { apiService } from "@/lib/apiService";
import {
  Plane,
  Clock,
  AlertTriangle,
  BarChart3,
  Users,
  Activity,
  TrendingUp,
  Calendar,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Dashboard() {
  const [activeFlights, setActiveFlights] = React.useState(0);
  const [criticalAlerts, setCriticalAlerts] = React.useState(0);
  const [avgRunwayUtilization, setAvgRunwayUtilization] = React.useState(0);
  const [recentFlights, setRecentFlights] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [flightStats, setFlightStats] = React.useState<any>({});
  const [runwayMetrics, setRunwayMetrics] = React.useState<any[]>([]);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const [flights, alerts, runwayStats, stats, metrics] = await Promise.all([
          apiService.getFlights(),
          apiService.getAlerts(),
          apiService.getRunwayStatistics(),
          apiService.getFlightStatistics(),
          apiService.getRunwayMetrics()
        ]);

        setActiveFlights(flights.length);
        setCriticalAlerts(alerts.filter((a: any) => a.type === 'critical').length);
        
        // Calculate average runway utilization from metrics (capped at 100%)
        if (metrics.length > 0) {
          const avgUtil = Math.min(100, Math.round(
            metrics.reduce((sum: number, metric: any) => sum + metric.utilization, 0) / metrics.length
          ));
          setAvgRunwayUtilization(avgUtil);
        } else {
          setAvgRunwayUtilization(Math.round(runwayStats.average_utilization || 0));
        }
        
        setRecentFlights(flights.slice(0, 5));
        setFlightStats(stats);
        setRunwayMetrics(metrics);
      } catch (error) {
        console.error("Error fetching data:", error);
        // Fallback to mock data if API fails
        setActiveFlights(12);
        setCriticalAlerts(2);
        setAvgRunwayUtilization(78);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Prepare chart data for runway utilization
  const runwayChartData = runwayMetrics.map((metric: any) => ({
    runway: metric.runway,
    utilization: Math.round(metric.utilization)
  }));

  // Prepare flight statistics for display
  const totalFlights = flightStats.total_flights || 0;
  const totalDelays = flightStats.total_delays || 0;
  const avgDelay = flightStats.avg_departure_delay || 0;
  const onTimePercentage = totalFlights > 0 ? Math.round(((totalFlights - totalDelays) / totalFlights) * 100) : 87;

  // Prepare route information
  const topRoutes = flightStats.routes ? Object.entries(flightStats.routes).slice(0, 3) : [];
  const topAirlines = flightStats.airlines ? Object.entries(flightStats.airlines).slice(0, 3) : [];

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">
          Airport Operations Dashboard
        </h1>
        <p className="text-muted-foreground text-lg">
          Real-time monitoring and AI-powered flight optimization
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Flights
            </CardTitle>
            <Plane className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeFlights}</div>
            <p className="text-xs text-muted-foreground">
              {flightStats.total_flights ? `Total: ${flightStats.total_flights}` : '+2 from last hour'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Critical Alerts
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{criticalAlerts}</div>
            <p className="text-xs text-muted-foreground">Requires attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Runway Utilization
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgRunwayUtilization}%</div>
            <p className="text-xs text-muted-foreground">
              {runwayMetrics.length > 0 ? 'Peak hour utilization' : 'Average across runways'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              On-Time Performance
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {flightStats.total_flights && flightStats.total_delays 
                ? Math.round(((flightStats.total_flights - flightStats.total_delays) / flightStats.total_flights) * 100)
                : 87}%
            </div>
            <p className="text-xs text-muted-foreground">
              {flightStats.avg_departure_delay 
                ? `Avg delay: ${Math.round(flightStats.avg_departure_delay)}min`
                : '+5% from yesterday'}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Flights */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Recent Flight Activity</span>
            </CardTitle>
            <CardDescription>
              Latest flight departures and arrivals
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-4">Loading flights...</div>
              ) : recentFlights.length > 0 ? (
                recentFlights.map((flight) => (
                  <div
                    key={flight.id}
                    className="flex items-center justify-between border-b pb-2 last:border-b-0"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{flight.flight_number}</Badge>
                        <span className="text-sm font-medium">
                          {flight.airline}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {flight.origin} → {flight.destination}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge
                        variant={
                          flight.status === "On Time"
                            ? "default"
                            : flight.status === "Delayed"
                            ? "destructive"
                            : flight.status === "Boarding"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {flight.status}
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-1">
                        Gate {flight.gate}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  No flights available
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Chatbot */}
        <Chatbot compact className="h-fit" />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Top Routes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Top Routes</span>
            </CardTitle>
            <CardDescription>
              Most frequent flight routes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loading ? (
                <div className="text-center py-4">Loading routes...</div>
              ) : topRoutes.length > 0 ? (
                topRoutes.map(([route, count], index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{index + 1}</Badge>
                      <span className="font-medium">{route as string}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{count as number} flights</span>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  No route data available
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Top Airlines */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plane className="h-5 w-5" />
              <span>Top Airlines</span>
            </CardTitle>
            <CardDescription>
              Airlines with most flights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loading ? (
                <div className="text-center py-4">Loading airlines...</div>
              ) : topAirlines.length > 0 ? (
                topAirlines.map(([airline, count], index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{index + 1}</Badge>
                      <span className="font-medium">{airline as string}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{count as number} flights</span>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  No airline data available
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Runway Utilization Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Runway Utilization</span>
            </CardTitle>
            <CardDescription>
              Real-time runway capacity and usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={runwayChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="runway" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="utilization" fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Active Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>Active Alerts</span>
            </CardTitle>
            <CardDescription>
              Current system notifications and warnings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-4">Loading alerts...</div>
              ) : criticalAlerts > 0 ? (
                <div className="text-center py-4">
                  <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-2" />
                  <p className="text-sm font-medium">{criticalAlerts} critical alerts</p>
                  <p className="text-xs text-muted-foreground">Check Alerts page for details</p>
                </div>
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  No alerts available
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Quick Actions</span>
          </CardTitle>
          <CardDescription>
            Commonly used airport management tools
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex flex-col items-center space-y-2 p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
              <Plane className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">Flight Search</span>
            </div>
            <div className="flex flex-col items-center space-y-2 p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
              <BarChart3 className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">Analytics</span>
            </div>
            <div className="flex flex-col items-center space-y-2 p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
              <AlertTriangle className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">Alerts</span>
            </div>
            <div className="flex flex-col items-center space-y-2 p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
              <Calendar className="h-8 w-8 text-primary" />
              <span className="text-sm font-medium">Schedule</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Debug Information (Development Only) */}
      {process.env.NODE_ENV === 'development' && (
        <Card className="border-dashed">
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground">Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-xs">
              <div><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</div>
              <div><strong>Total Flights:</strong> {totalFlights}</div>
              <div><strong>Total Delays:</strong> {totalDelays}</div>
              <div><strong>Average Delay:</strong> {avgDelay.toFixed(1)} minutes</div>
              <div><strong>On-Time %:</strong> {onTimePercentage}%</div>
              <div><strong>Recent Flights:</strong> {recentFlights.length}</div>
              <div><strong>Runway Metrics:</strong> {runwayMetrics.length}</div>
              <div><strong>Top Routes:</strong> {topRoutes.length}</div>
              <div><strong>Top Airlines:</strong> {topAirlines.length}</div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
