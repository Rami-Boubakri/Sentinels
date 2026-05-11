"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchTicket } from "@/lib/api";
import { LivePipeline } from "@/components/live-pipeline";
import { ArrowLeft, FileText } from "lucide-react";
import Link from "next/link";

export default function TicketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticketId = params.id as string;
  const [ticket, setTicket] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTicket(ticketId)
      .then(setTicket)
      .catch(() => {
        // Handle 404 or error
        router.push("/tickets");
      })
      .finally(() => setLoading(false));
  }, [ticketId, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="spinner w-8 h-8"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/tickets" className="p-2 bg-secondary text-secondary-foreground rounded-full hover:bg-secondary/80 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">TKT-{String(ticket.id).padStart(4, '0')}</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide border ${
              ticket.status === 'open' ? 'bg-sentinel-amber/10 border-sentinel-amber/30 text-sentinel-amber' : 'bg-sentinel-blue/10 border-sentinel-blue/30 text-sentinel-blue'
            }`}>
              {ticket.status}
            </span>
          </div>
          <p className="text-muted-foreground flex items-center gap-2 mt-1">
            <FileText className="w-4 h-4" />
            Customer: <span className="font-medium text-foreground">{ticket.customer_id}</span>
          </p>
        </div>
      </div>

      {/* The main live pipeline component handles the rest */}
      <LivePipeline ticketId={ticketId} initialPayload={ticket.input_payload} />
    </div>
  );
}
