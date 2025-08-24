'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Chatbot } from '@/components/chatbot';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Bot, Zap, Search, AlertTriangle, BarChart3 } from 'lucide-react';

export default function ChatPage() {
  const chatFeatures = [
    {
      icon: Search,
      title: "Flight Search",
      description: "Ask me to find flights using natural language",
      example: "Find me flights to London after 3 PM tomorrow"
    },
    {
      icon: AlertTriangle,
      title: "Airport Alerts",
      description: "Get real-time information about airport operations",
      example: "What's the current status of Runway 27L?"
    },
    {
      icon: BarChart3,
      title: "Analytics & Reports",
      description: "Ask about runway utilization and performance metrics",
      example: "Show me runway efficiency for today"
    },
    {
      icon: Bot,
      title: "General Assistance",
      description: "Get help with airport navigation and services",
      example: "Where can I find ground transportation?"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">Airport Chat Assistant</h1>
        <p className="text-muted-foreground text-lg">
          Get instant help with flights, operations, and airport services using natural language
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <Chatbot />
        </div>

        {/* Features & Help */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>AI Capabilities</span>
              </CardTitle>
              <CardDescription>
                What I can help you with
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {chatFeatures.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div key={index} className="space-y-2 pb-4 border-b last:border-b-0">
                    <div className="flex items-center space-x-2">
                      <Icon className="h-4 w-4 text-primary" />
                      <span className="font-medium text-sm">{feature.title}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {feature.description}
                    </p>
                    <div className="bg-muted rounded-lg p-2">
                      <p className="text-xs italic">"{feature.example}"</p>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Quick Tips</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <Badge variant="outline" className="w-fit">
                  Natural Language
                </Badge>
                <p className="text-sm text-muted-foreground">
                  Speak naturally - no need for specific commands or keywords
                </p>
              </div>
              <div className="space-y-2">
                <Badge variant="outline" className="w-fit">
                  Context Aware
                </Badge>
                <p className="text-sm text-muted-foreground">
                  I remember our conversation and can answer follow-up questions
                </p>
              </div>
              <div className="space-y-2">
                <Badge variant="outline" className="w-fit">
                  Real-time Data
                </Badge>
                <p className="text-sm text-muted-foreground">
                  All information is based on current airport operations data
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">AI Assistant</span>
                <Badge variant="default">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Flight Database</span>
                <Badge variant="default">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Real-time Updates</span>
                <Badge variant="default">Active</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Sample Conversations */}
      <Card>
        <CardHeader>
          <CardTitle>Sample Conversations</CardTitle>
          <CardDescription>
            Try these example conversations to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <h4 className="font-semibold">Flight Operations</h4>
              <div className="space-y-3">
                <div className="bg-muted rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium">User:</p>
                  <p className="text-sm italic">"What flights are departing from Terminal 1 in the next hour?"</p>
                </div>
                <div className="bg-muted rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium">User:</p>
                  <p className="text-sm italic">"Find me the quickest flight to Paris tomorrow morning"</p>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold">Operations & Alerts</h4>
              <div className="space-y-3">
                <div className="bg-muted rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium">User:</p>
                  <p className="text-sm italic">"Are there any delays or runway closures I should know about?"</p>
                </div>
                <div className="bg-muted rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium">User:</p>
                  <p className="text-sm italic">"How is runway utilization looking today?"</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}