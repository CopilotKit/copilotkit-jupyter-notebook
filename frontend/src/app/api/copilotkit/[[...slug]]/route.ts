import { HttpAgent } from "@ag-ui/client";
import {
  CopilotRuntime,
  createCopilotEndpoint,
  InMemoryAgentRunner,
} from "@copilotkit/runtime/v2";
import { handle } from "hono/vercel";

const agent = new HttpAgent({
  url: process.env.LANGGRAPH_DEPLOYMENT_URL || "http://localhost:8000",
});

const runtime = new CopilotRuntime({
  agents: {
    // @ts-expect-error - Version mismatch between @ag-ui/client versions
    default: agent,
  },
  runner: new InMemoryAgentRunner(),
});

const app = createCopilotEndpoint({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handle(app);
export const POST = handle(app);
