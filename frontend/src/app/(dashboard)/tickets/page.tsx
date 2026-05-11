"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchTickets } from "@/lib/api";
import { Ticket, Clock, ArrowRight, Activity, AlertCircle } from "lucide-react";

export default function TicketsPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTickets()
      .then(setTickets)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Active Tickets</h1>
          <p className="text-muted-foreground">Manage and monitor orchestration pipelines for all events.</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="spinner w-8 h-8"></div>
        </div>
      ) : tickets.length === 0 ? (
        <div className="text-center py-20 glass-card rounded-xl border border-dashed border-border">
          <Ticket className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No active tickets</h3>
          <p className="text-muted-foreground mb-6">Submit a new event to trigger the multi-agent system.</p>
          <Link href="/submit" className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium inline-block">
            Submit Event
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {tickets.map(ticket => (
            <Link key={ticket.id} href={`/tickets/${ticket.id}`} className="group">
              <div className="glass-card rounded-xl p-5 hover:border-primary/50 transition-colors flex flex-col md:flex-row md:items-center gap-6">
                
                <div className="flex items-center gap-4 md:w-1/4">
                  <div className={`p-3 rounded-xl ${ticket.status === 'open' ? 'bg-sentinel-amber/10 text-sentinel-amber' : 'bg-sentinel-blue/10 text-sentinel-blue'}`}>
                    {ticket.status === 'open' ? <Activity className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg leading-none mb-1 text-foreground">TKT-{String(ticket.id).padStart(4, '0')}</h3>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" /> 
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="md:w-1/3">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Customer</div>
                  <div className="font-medium text-foreground">{ticket.customer_id}</div>
                </div>

                <div className="md:w-1/4">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Progress</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary" 
                        style={{ width: ticket.report_count ? `${(ticket.validated_count / ticket.report_count) * 100}%` : '0%' }}
                      />
                    </div>
                    <span className="text-xs font-medium">
                      {ticket.validated_count}/{ticket.report_count}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-end flex-1">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide border ${
                    ticket.status === 'open' ? 'bg-sentinel-amber/10 border-sentinel-amber/30 text-sentinel-amber' : 'bg-sentinel-blue/10 border-sentinel-blue/30 text-sentinel-blue'
                  }`}>
                    {ticket.status}
                  </span>
                  <ArrowRight className="w-5 h-5 ml-4 text-muted-foreground group-hover:text-primary transition-colors transform group-hover:translate-x-1" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
