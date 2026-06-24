import { Navigate } from "@/lib/router";

/**
 * Layout route guard for legacy Conference Room Chat surfaces.
 *
 * TraceGrid does not provide a human-facing report/chat surface. Keep the
 * legacy routes registered for compatibility, but always redirect them to the
 * collection network dashboard.
 */
export function ConferenceRoomChatGate() {
  return <Navigate to="/dashboard" replace />;
}
