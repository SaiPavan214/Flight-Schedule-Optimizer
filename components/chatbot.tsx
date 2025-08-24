"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageSquare, Send, Bot, User } from "lucide-react";
import dynamic from "next/dynamic";
import { apiService } from "@/lib/apiService";

const RunwayChart = dynamic(() => import("@/components/RunwayChart"), {
  ssr: false,
});

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface ChatbotProps {
  className?: string;
  compact?: boolean;
}

export function Chatbot({ className, compact = false }: ChatbotProps) {
  const [alerts, setAlerts] = useState([
    { id: "1", message: "Runway 3 maintenance scheduled at 2 PM." },
    { id: "2", message: "Runway 1 experiencing delays due to weather." },
    { id: "3", message: "Runway 5 closed for emergency repairs." },
  ]);

  const [runwayUsage, setRunwayUsage] = useState([
    { id: "1", runway: "Runway 1", capacity: "80%", usage: "75%" },
    { id: "2", runway: "Runway 2", capacity: "70%", usage: "60%" },
    { id: "3", runway: "Runway 3", capacity: "90%", usage: "90%" },
    { id: "4", runway: "Runway 4", capacity: "60%", usage: "50%" },
    { id: "5", runway: "Runway 5", capacity: "85%", usage: "80%" },
  ]);

  const [notifications, setNotifications] = useState([
    { id: "1", message: "System update scheduled for midnight." },
    { id: "2", message: "Weather alert: Heavy rain expected tomorrow." },
    { id: "3", message: "Runway 2 lighting system under inspection." },
  ]);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your airport assistant. How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchRunwayData = async () => {
      try {
        const data = await apiService.getRunwayOptimizationData();
        console.log("Runway Data:", data);
      } catch (error) {
        console.error("Error fetching runway data:", error);
      }
    };

    fetchRunwayData();
  }, []);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await apiService.sendChatMessage(input); // Pass input directly as a string
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error("Chat error:", error);
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content:
          "Sorry, I'm having trouble connecting to the server. Please try again later.",
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (compact) {
    return (
      <Card className={className}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center space-x-2 text-base">
            <MessageSquare className="h-5 w-5" />
            <span>Quick Chat</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ScrollArea className="h-40">
            <div className="space-y-2">
              {messages.slice(-2).map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start space-x-2 ${
                    message.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {message.sender === "bot" && (
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                      <Bot className="h-3 w-3 text-primary-foreground" />
                    </div>
                  )}
                  <div className="bg-muted rounded-lg px-3 py-2 text-sm">
                    {message.content}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex items-start space-x-2">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                    <Bot className="h-3 w-3 text-primary-foreground" />
                  </div>
                  <div className="bg-muted rounded-lg px-3 py-2 text-sm">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
          <div className="flex space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="text-sm"
            />
            <Button size="sm" onClick={handleSendMessage} disabled={isLoading}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <MessageSquare className="h-6 w-6" />
          <span>Airport Dashboard</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Runway Analytics */}
        <div>
          <h2 className="text-lg font-bold">Runway Analytics</h2>
          <table className="table-auto w-full text-sm">
            <thead>
              <tr>
                <th className="px-4 py-2">Runway</th>
                <th className="px-4 py-2">Utilization</th>
                <th className="px-4 py-2">Average Delay</th>
              </tr>
            </thead>
            <tbody>
              {runwayUsage.map((runway) => (
                <tr key={runway.id}>
                  <td className="border px-4 py-2">{runway.runway}</td>
                  <td className="border px-4 py-2">{runway.capacity}</td>
                  <td className="border px-4 py-2">{runway.usage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Active Alerts */}
        <div>
          <h2 className="text-lg font-bold">Active Alerts</h2>
          <ul className="list-disc pl-5">
            {alerts.map((alert) => (
              <li key={alert.id} className="text-sm">
                {alert.message}
              </li>
            ))}
          </ul>
        </div>

        {/* Current System Notifications */}
        <div>
          <h2 className="text-lg font-bold">Current System Notifications</h2>
          <ul className="list-disc pl-5">
            {notifications.map((notification) => (
              <li key={notification.id} className="text-sm">
                {notification.message}
              </li>
            ))}
          </ul>
        </div>

        {/* Existing messages section */}
        <ScrollArea className="h-96">
          <div className="space-y-4 pr-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.sender === "bot" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary-foreground" />
                  </div>
                )}
                <div
                  className={`rounded-lg px-4 py-3 max-w-[80%] ${
                    message.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                {message.sender === "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary-foreground" />
                </div>
                <div className="bg-muted rounded-lg px-4 py-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about flights, runways, alerts, or anything else..."
          />
          <Button onClick={handleSendMessage} disabled={isLoading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
