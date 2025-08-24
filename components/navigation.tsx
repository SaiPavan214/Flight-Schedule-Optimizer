"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/mode-toggle";
import {
  Plane,
  Search,
  AlertTriangle,
  BarChart3,
  MessageSquare,
  Target,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: BarChart3 },
  { name: "Flight Booking", href: "/booking", icon: Search },
  { name: "Alerts", href: "/alerts", icon: AlertTriangle },
  { name: "Runway Analytics", href: "/analytics", icon: Plane },
  {
    name: "Schedule Optimization",
    href: "/schedule-optimization",
    icon: Target,
  },
  { name: "Chat Assistant", href: "/chat", icon: MessageSquare },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Link href="/" className="flex items-center space-x-2">
          <Plane className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl">AirportOps</span>
        </Link>

        <nav className="flex items-center space-x-1 ml-8">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.name} href={item.href}>
                <Button
                  variant={pathname === item.href ? "default" : "ghost"}
                  size="sm"
                  className={cn(
                    "flex items-center space-x-2",
                    pathname === item.href &&
                      "bg-primary text-primary-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.name}</span>
                </Button>
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto">
          <ModeToggle />
        </div>
      </div>
    </header>
  );
}
