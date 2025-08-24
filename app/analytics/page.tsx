"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiService } from "@/lib/apiService";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  Legend,
} from "recharts";
import {
  Plane,
  TrendingUp,
  AlertTriangle,
  Clock,
  Activity,
  Target,
  Zap,
  BarChart3,
  PieChartIcon,
  TrendingDown,
} from "lucide-react";

interface TimeSeriesData {
  time: string;
  flights: number;
  delays: number;
  capacity: number;
}

export default function AnalyticsPage() {
  const [selectedTimeRange, setSelectedTimeRange] = useState<
    "24h" | "7d" | "30d"
  >("24h");
  const [loading, setLoading] = useState(true);
  const [runwayMetrics, setRunwayMetrics] = useState<any[]>([]);
  const [flightStats, setFlightStats] = useState<any>({});
  const [runwayAnalytics, setRunwayAnalytics] = useState<any>({});
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        const [metrics, stats, analytics, alertsData] = await Promise.all([
          apiService.getRunwayMetrics(),
          apiService.getFlightStatistics(),
          apiService.getRunwayOptimizationData(),
          apiService.getAlerts()
        ]);

        setRunwayMetrics(metrics);
        setFlightStats(stats);
        setRunwayAnalytics(analytics);
        setAlerts(alertsData);
      } catch (error) {
        console.error("Error fetching analytics data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  // Generate time series data based on real runway metrics
  const generateTimeSeriesData = (): TimeSeriesData[] => {
    if (!runwayMetrics.length) return [];
    
    return runwayMetrics.map((metric: any) => ({
      time: metric.runway,
      flights: Math.round(metric.utilization * metric.capacity / 100),
      delays: metric.delays || 0,
      capacity: metric.capacity || 60,
    }));
  };

  const timeSeriesData = generateTimeSeriesData();

  // Flight status distribution based on real data
  const flightStatusData = [
    { 
      name: "On Time", 
      value: flightStats.total_flights && flightStats.total_delays 
        ? Math.round(((flightStats.total_flights - flightStats.total_delays) / flightStats.total_flights) * 100)
        : 65, 
      color: "#22c55e" 
    },
    { 
      name: "Delayed", 
      value: flightStats.total_flights && flightStats.total_delays 
        ? Math.round((flightStats.total_delays / flightStats.total_flights) * 100)
        : 20, 
      color: "#ef4444" 
    },
    { 
      name: "Peak Time", 
      value: flightStats.peak_time_flights && flightStats.total_flights
        ? Math.round((flightStats.peak_time_flights / flightStats.total_flights) * 100)
        : 10, 
      color: "#3b82f6" 
    },
    { 
      name: "Weekend", 
      value: flightStats.weekend_flights && flightStats.total_flights
        ? Math.round((flightStats.weekend_flights / flightStats.total_flights) * 100)
        : 5, 
      color: "#8b5cf6" 
    },
  ];

  // Runway efficiency metrics based on real data
  const runwayEfficiencyData = runwayMetrics.map((runway: any) => ({
    ...runway,
    efficiency: Math.round((runway.utilization / runway.capacity) * 100),
    conflictRate: Math.round((runway.delays / Math.max(runway.utilization, 1)) * 100),
  }));

  // Peak hours analysis based on real data
  const peakHoursData = runwayAnalytics.peak_hours ? 
    Object.entries(runwayAnalytics.peak_hours).map(([hour, data]: [string, any]) => ({
      hour: `${hour}:00`,
      traffic: data.flight_count || 0,
      delays: Math.round(data.Departure_Delay_Minutes || 0)
    })) : [
      { hour: "06:00", traffic: 85, delays: 5 },
      { hour: "09:00", traffic: 95, delays: 12 },
      { hour: "12:00", traffic: 90, delays: 8 },
      { hour: "15:00", traffic: 92, delays: 15 },
      { hour: "18:00", traffic: 98, delays: 18 },
    ];

  const totalFlights = flightStats.total_flights || 0;
  const avgDelay = Math.round(flightStats.avg_departure_delay || 0);
  const totalConflicts = runwayMetrics.reduce(
    (sum, r) => sum + r.delays,
    0
  );

  // Calculate average efficiency from real data
  const avgEfficiency = runwayMetrics.length > 0 
    ? Math.round(runwayMetrics.reduce((sum, r) => sum + r.utilization, 0) / runwayMetrics.length)
    : 78;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Runway Analytics</h1>
          <p className="text-muted-foreground text-lg">
            Loading analytics data...
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse">
                  <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">
          Runway Analytics & Optimization
        </h1>
        <p className="text-muted-foreground text-lg">
          Real-time insights into runway performance, capacity utilization, and
          optimization opportunities
        </p>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Flights
            </CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalFlights}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +12% from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Avg Efficiency
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgEfficiency}%</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +3% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Delays</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgDelay}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingDown className="inline h-3 w-3 mr-1 text-green-500" />
              -8% improvement
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conflicts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalConflicts}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingDown className="inline h-3 w-3 mr-1 text-green-500" />
              -2 from last hour
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="runway">Runway Analysis</TabsTrigger>
          <TabsTrigger value="capacity">Capacity Planning</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Flight Traffic Over Time */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Flight Traffic Analysis</span>
                </CardTitle>
                <CardDescription>
                  Flight volume and delays throughout the day
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="flights"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      name="Flights"
                    />
                    <Line
                      type="monotone"
                      dataKey="delays"
                      stroke="hsl(var(--destructive))"
                      strokeWidth={2}
                      name="Delays"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Flight Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChartIcon className="h-5 w-5" />
                  <span>Flight Status Distribution</span>
                </CardTitle>
                <CardDescription>
                  Current status breakdown of all flights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={flightStatusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {flightStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Real-time Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Real-time Insights</span>
              </CardTitle>
              <CardDescription>
                Live data insights from your flight operations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {flightStats.total_flights || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Total Flights</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-destructive">
                    {flightStats.total_delays || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Delayed Flights</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {flightStats.avg_flight_duration ? Math.round(flightStats.avg_flight_duration) : 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Avg Duration (min)</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Peak Hours Analysis */}
        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Peak Hours Analysis</span>
              </CardTitle>
              <CardDescription>
                Traffic patterns and congestion throughout the day
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={peakHoursData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="traffic"
                    fill="hsl(var(--primary))"
                    name="Traffic %"
                  />
                  <Bar
                    dataKey="delays"
                    fill="hsl(var(--destructive))"
                    name="Delays"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="runway" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Runway Utilization */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Plane className="h-5 w-5" />
                  <span>Runway Utilization</span>
                </CardTitle>
                <CardDescription>
                  Current capacity usage by runway
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={runwayMetrics} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis dataKey="runway" type="category" />
                    <Tooltip />
                    <Bar
                      dataKey="utilization"
                      fill="hsl(var(--primary))"
                      name="Utilization %"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Runway Efficiency */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="h-5 w-5" />
                  <span>Efficiency Metrics</span>
                </CardTitle>
                <CardDescription>
                  Performance indicators by runway
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="10%"
                    outerRadius="80%"
                    data={runwayEfficiencyData}
                  >
                    <RadialBar
                      dataKey="efficiency"
                      cornerRadius={10}
                      fill="hsl(var(--primary))"
                      label={{ position: "insideStart", fill: "#fff" }}
                    />
                    <Legend />
                    <Tooltip />
                  </RadialBarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Runway Details Table */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Runway Metrics</CardTitle>
              <CardDescription>
                Comprehensive breakdown of runway performance indicators
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Runway</th>
                      <th className="text-left p-2">Utilization</th>
                      <th className="text-left p-2">Capacity</th>
                      <th className="text-left p-2">Delays</th>
                      <th className="text-left p-2">Conflicts</th>
                      <th className="text-left p-2">Efficiency</th>
                      <th className="text-left p-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runwayEfficiencyData.map((runway, index) => (
                      <tr key={index} className="border-b">
                        <td className="p-2 font-medium">{runway.runway}</td>
                        <td className="p-2">{runway.utilization}%</td>
                        <td className="p-2">{runway.capacity}</td>
                        <td className="p-2">{runway.delays}</td>
                        <td className="p-2">{runway.conflicts}</td>
                        <td className="p-2">{runway.efficiency}%</td>
                        <td className="p-2">
                          <Badge
                            variant={
                              runway.efficiency > 90
                                ? "default"
                                : runway.efficiency > 75
                                ? "secondary"
                                : "destructive"
                            }
                          >
                            {runway.efficiency > 90
                              ? "Optimal"
                              : runway.efficiency > 75
                              ? "Good"
                              : "Needs Attention"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="capacity" className="space-y-6">
          {/* Capacity Planning Dashboard */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Capacity Trends</span>
                </CardTitle>
                <CardDescription>
                  Historical capacity utilization patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="capacity"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      name="Capacity Usage %"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>Real-time Load</span>
                </CardTitle>
                <CardDescription>
                  Current system load and bottlenecks
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {runwayMetrics.map((runway, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Runway {runway.runway}</span>
                      <span>{runway.utilization}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          runway.utilization > 90
                            ? "bg-destructive"
                            : runway.utilization > 75
                            ? "bg-yellow-500"
                            : "bg-primary"
                        }`}
                        style={{ width: `${runway.utilization}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Capacity Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5" />
                <span>Capacity Alerts</span>
              </CardTitle>
              <CardDescription>
                Automated alerts for capacity management
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alerts.map((alert, index) => (
                  <div key={index} className={`border-l-4 ${
                    alert.severity === 'high' ? 'border-l-destructive' :
                    alert.severity === 'medium' ? 'border-l-yellow-500' :
                    'border-l-blue-500'
                  } pl-4`}>
                    <h4 className={`font-medium ${
                      alert.severity === 'high' ? 'text-destructive' :
                      alert.severity === 'medium' ? 'text-yellow-600' :
                      'text-blue-600'
                    }`}>
                      {alert.title}
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      {alert.message}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-6">
          {/* AI Optimization Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>AI-Powered Optimization</span>
              </CardTitle>
              <CardDescription>
                Machine learning recommendations for improved efficiency
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <h4 className="font-semibold">Immediate Actions</h4>
                  <div className="space-y-3">
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg dark:bg-green-950 dark:border-green-800">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="font-medium text-green-800 dark:text-green-200">
                          Route Optimization
                        </span>
                      </div>
                      <p className="text-sm text-green-700 dark:text-green-300">
                        Redirect 3 flights from 27R to 09L to balance load (Est.
                        12% efficiency gain)
                      </p>
                    </div>
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-950 dark:border-blue-800">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="font-medium text-blue-800 dark:text-blue-200">
                          Timing Adjustment
                        </span>
                      </div>
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        Adjust BA123 departure by 5 minutes to reduce ground
                        holding time
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold">Strategic Recommendations</h4>
                  <div className="space-y-3">
                    <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg dark:bg-purple-950 dark:border-purple-800">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                        <span className="font-medium text-purple-800 dark:text-purple-200">
                          Capacity Planning
                        </span>
                      </div>
                      <p className="text-sm text-purple-700 dark:text-purple-300">
                        Consider opening additional runway during peak hours
                        (18:00-20:00)
                      </p>
                    </div>
                    <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg dark:bg-orange-950 dark:border-orange-800">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                        <span className="font-medium text-orange-800 dark:text-orange-200">
                          Resource Allocation
                        </span>
                      </div>
                      <p className="text-sm text-orange-700 dark:text-orange-300">
                        Deploy additional ground crew to Gate A12 for faster
                        turnaround
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Optimization Impact Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Projected Impact Analysis</CardTitle>
              <CardDescription>
                Estimated improvements from implementing optimization
                recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-green-600">+15%</div>
                  <p className="text-sm text-muted-foreground">
                    Efficiency Improvement
                  </p>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-blue-600">-8min</div>
                  <p className="text-sm text-muted-foreground">
                    Average Delay Reduction
                  </p>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-3xl font-bold text-purple-600">
                    $2.3M
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Annual Savings
                  </p>
                </div>
              </div>

              <div className="mt-6 flex space-x-2">
                <Button className="flex-1">
                  Implement All Recommendations
                </Button>
                <Button variant="outline" className="flex-1">
                  Simulate Impact
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
