// [Task]: T011
// [From]: specs/004-phase-iv-kubernetes/tasks.md §Phase 2
// [Description]: Health check endpoint for Kubernetes liveness and readiness probes

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'todo-frontend',
    },
    { status: 200 }
  );
}
