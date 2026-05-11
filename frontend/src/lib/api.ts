const API_BASE = "http://localhost:8000/api/v1";

export async function fetchTickets() {
  const res = await fetch(`${API_BASE}/tickets/`);
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

export async function fetchTicket(id: string) {
  const res = await fetch(`${API_BASE}/tickets/${id}`);
  if (!res.ok) throw new Error("Failed to fetch ticket");
  return res.json();
}

export async function fetchReports(ticketId: string) {
  const res = await fetch(`${API_BASE}/reports/ticket/${ticketId}`);
  if (!res.ok) throw new Error("Failed to fetch reports");
  return res.json();
}

export async function submitEvent(payload: any) {
  const res = await fetch(`${API_BASE}/inputs/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to submit event");
  return res.json();
}

export async function validateReport(reportId: number, actionTaken: string) {
  const res = await fetch(`${API_BASE}/reports/${reportId}/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action_taken: actionTaken }),
  });
  if (!res.ok) throw new Error("Failed to validate report");
  return res.json();
}

export async function invalidateReport(reportId: number) {
  const res = await fetch(`${API_BASE}/reports/${reportId}/invalidate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to invalidate report");
  return res.json();
}

export async function modifyReport(reportId: number, content: any) {
  const res = await fetch(`${API_BASE}/reports/${reportId}/modify`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error("Failed to modify report");
  return res.json();
}

export async function fetchAuditLog(params?: { ticket_id?: string; dept_id?: string }) {
  const url = new URL(`${API_BASE}/audit/`);
  if (params?.ticket_id) url.searchParams.append("ticket_id", params.ticket_id);
  if (params?.dept_id) url.searchParams.append("dept_id", params.dept_id);
  
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch audit log");
  return res.json();
}
