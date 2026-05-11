"use client";

import { useEffect, useState } from "react";
import { KPICard } from "./kpi-card";
import { Activity, AlertTriangle, FileText, CheckCircle2, ShieldCheck, Clock } from "lucide-react";
import Link from "next/link";

export function UnifiedDashboard() {
  const [data, setData] = useState({
    kpis: {
      total_tickets: 0,
      open_tickets: 0,
      total_actions: 0
    },
    recent_reports: []
  });

  const fetchData = () => {
    fetch("http://localhost:8000/api/v1/dashboards/unified")
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.error("Failed to fetch dashboard data:", err));
  };

  useEffect(() => {
    fetchData();

    // Setup SSE connection for real-time updates
    const eventSource = new EventSource("http://localhost:8000/api/v1/stream/events");
    
    eventSource.onmessage = (event) => {
      fetchData();
    };

    return () => eventSource.close();
  }, []);

  return (
    <div className="space-y-8">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <KPICard 
          title="Total Tickets" 
          value={data.kpis.total_tickets} 
          icon={<FileText />}
          description="Global event volume"
          trend="+12%"
        />
        <KPICard 
          title="Open Incidents" 
          value={data.kpis.open_tickets} 
          icon={<AlertTriangle className="text-sentinel-amber" />}
          description="Requiring immediate review"
          trend="Active"
        />
        <KPICard 
          title="Agent Actions" 
          value={data.kpis.total_actions} 
          icon={<Activity className="text-sentinel-blue" />}
          description="Executed recommendations"
          trend="Live"
        />
        <KPICard 
          title="Security Status" 
          value="Secured" 
          icon={<ShieldCheck className="text-sentinel-green" />}
          description="Zero-trust layer active"
        />
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <div className="glass-card rounded-xl p-6 border border-border/50">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Latest Agent Intelligence
            </h3>
            <Link href="/tickets" className="text-sm font-medium text-primary hover:underline">View all tickets</Link>
          </div>
          
          <div className="space-y-4">
            {data.recent_reports && data.recent_reports.length > 0 ? (
              data.recent_reports.map((report: any) => (
                <div key={report.id} className="p-4 border border-border/30 rounded-lg bg-secondary/20 hover:bg-secondary/40 transition-colors">
                  <div className="flex justify-between items-center mb-3">
                    <span className="font-bold text-sentinel-blue text-sm">{report.department_id}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-widest ${
                      report.status === 'pending' ? 'badge-pending' : 
                      report.status === 'validated' ? 'badge-validated' : 
                      'badge-modified'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                  <p className="text-xs text-foreground line-clamp-2 mb-2 leading-relaxed italic">
                    "{report.content?.analysis}"
                  </p>
                  <div className="flex justify-between items-center mt-3 pt-3 border-t border-border/20">
                    <span className="text-[10px] text-muted-foreground font-mono">TKT #{report.ticket_id}</span>
                    <span className="text-[10px] font-bold text-muted-foreground uppercase">Confidence: {report.content?.confidence}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-muted-foreground border border-dashed border-border rounded-lg">
                <p>Waiting for intelligence reports...</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <div className="glass-card rounded-xl p-8 border border-border/50 bg-gradient-to-br from-primary/10 via-transparent to-transparent">
            <h3 className="text-2xl font-bold mb-4">System Capacity</h3>
            <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
              The multi-agent system is currently monitoring 14 banking sectors with 6 specialized department agents active. 
              Average response time for complex GGEI risk analysis: 4.2 seconds.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-background/50 p-4 rounded-lg border border-border/50">
                <div className="text-xs text-muted-foreground uppercase font-bold mb-1">Agents Online</div>
                <div className="text-xl font-bold">12 / 12</div>
              </div>
              <div className="bg-background/50 p-4 rounded-lg border border-border/50">
                <div className="text-xs text-muted-foreground uppercase font-bold mb-1">Queue Load</div>
                <div className="text-xl font-bold text-sentinel-green">Nominal</div>
              </div>
            </div>
          </div>
          
          <div className="glass-card rounded-xl p-6 border border-border/50 flex items-center justify-between group cursor-pointer hover:border-primary/50 transition-colors">
            <div>
              <h4 className="font-bold text-lg">Governance Audit Trail</h4>
              <p className="text-xs text-muted-foreground">Check cryptographically signed decision logs.</p>
            </div>
            <Link href="/audit" className="p-3 bg-secondary rounded-full group-hover:bg-primary group-hover:text-primary-foreground transition-all">
              <Activity className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
