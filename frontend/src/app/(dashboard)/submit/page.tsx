"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitEvent } from "@/lib/api";
import { Send, AlertTriangle, ChevronDown, Loader2 } from "lucide-react";

const EVENT_TYPES = [
  { value: "early_warning",         label: "Early Warning Signal" },
  { value: "loan_restructuring",    label: "Loan Restructuring" },
  { value: "credit_review",         label: "Credit Review" },
  { value: "npl_alert",             label: "NPL Alert" },
  { value: "regulatory_inquiry",    label: "Regulatory Inquiry" },
  { value: "customer_complaint",    label: "Customer Complaint" },
  { value: "voluntary_restructuring", label: "Voluntary Restructuring" },
  { value: "dora_event",            label: "DORA Event" },
  { value: "it_incident",           label: "IT Incident" },
  { value: "audit_request",         label: "Audit Request" },
  { value: "provisioning_update",   label: "Provisioning Update" },
  { value: "collection_action",     label: "Collection Action" },
];

const EXAMPLE_PAYLOAD = {
  customer_id: "CUST-OPT-007",
  event_type: "voluntary_restructuring",
  details: "Optima Retail Group (SME, TPME segment, loan TND 1.2M) has proactively contacted STB requesting a voluntary restructuring of their loan before entering delinquency. Company context: operates 4 retail outlets in Sfax medina. Revenue dropped 28% post-COVID recovery stall and due to new competing mall opening nearby. Current DPD: 0 (customer is proactive). Request: 6-month principal moratorium + interest rate reduction from 9.5% to 7.5%. Financial docs submitted: latest balance sheet shows equity still positive (TND 340K) but cash flow is negative for last 2 quarters. Guarantees: personal guarantee from owner + stock pledge (TND 280K). Branch manager (Dir. Régionale Sfax) recommends the restructuring as the owner is cooperative and sector recovery likely within 12-18 months.",
};

export default function SubmitEventPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState(EXAMPLE_PAYLOAD);

  const charCount = formData.details.length;
  const charLimit = 8000;
  const charPct = Math.min((charCount / charLimit) * 100, 100);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await submitEvent({ source: "dashboard", payload: formData });
      if (res.ticket_id) {
        router.push(`/tickets/${res.ticket_id}`);
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || "Submission failed — check backend logs.";
      setError(msg);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight mb-1">Submit New Event</h1>
        <p className="text-muted-foreground text-sm">
          Trigger the multi-agent pipeline. Input passes through the Security Layer before routing.
        </p>
      </div>

      <div className="glass-card rounded-xl p-6 border border-border">
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Customer ID */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Customer ID</label>
            <input
              type="text"
              value={formData.customer_id}
              onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
              placeholder="e.g. CUST-XYZ-001"
              maxLength={64}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sentinel-blue/40 focus:border-sentinel-blue/50 transition-colors"
              required
            />
          </div>

          {/* Event Type */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Event Type</label>
            <div className="relative">
              <select
                value={formData.event_type}
                onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                className="w-full appearance-none bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sentinel-blue/40 focus:border-sentinel-blue/50 transition-colors pr-10"
              >
                {EVENT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            </div>
          </div>

          {/* Details */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Event Details</label>
              <span className={`text-xs font-mono tabular-nums ${charCount > charLimit * 0.9 ? "text-sentinel-red" : "text-muted-foreground"}`}>
                {charCount.toLocaleString()} / {charLimit.toLocaleString()}
              </span>
            </div>
            <textarea
              value={formData.details}
              onChange={(e) => setFormData({ ...formData, details: e.target.value })}
              className="w-full h-52 bg-background border border-border rounded-md p-3 text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-sentinel-blue/40 focus:border-sentinel-blue/50 transition-colors resize-none"
              maxLength={charLimit}
              required
            />
            {/* Character bar */}
            <div className="h-0.5 rounded-full bg-border overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${charPct}%`,
                  backgroundColor: charPct > 90 ? "var(--sentinel-red)" : charPct > 70 ? "var(--sentinel-amber)" : "var(--sentinel-blue)",
                }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              The Security Layer will scan for prompt injection before this reaches any agent.
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-sentinel-red/10 border border-sentinel-red/25 rounded-md p-3 flex gap-2.5 text-sm text-sentinel-red">
              <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Warning */}
          <div className="bg-sentinel-amber/8 border border-sentinel-amber/20 rounded-md p-3 flex gap-2.5 text-sm text-sentinel-amber">
            <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">This will activate the orchestrator.</p>
              <p className="opacity-75 text-xs mt-0.5">Relevant department agents will be assigned and begin analysis immediately.</p>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-sentinel-blue hover:bg-sentinel-blue/90 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg flex justify-center items-center gap-2 transition-all text-sm"
          >
            {isSubmitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Launching pipeline...</>
            ) : (
              <><Send className="w-4 h-4" /> Launch Pipeline</>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}