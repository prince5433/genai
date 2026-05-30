// MCP server class import: yahin se server object banega
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
// Zod import: input validation/schema define karne ke liye
import { z } from 'zod';
// STDIO transport import: server ka input/output stdio par chalega
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
// Axios import: HTTP requests bhejne ke liye
import axios from 'axios';

// Server instance banate hain with name & version metadata
const server = new McpServer({
  // Server ka naam
  name: 'My Server',
  // Server ka version
  version: '1.0.0',
});

// 'add' tool register kar rahe hain
server.tool('add', { a: z.number(), b: z.number() }, async function ({ a, b }) {
  // Do numbers ka sum nikalte hain
  const sum = a + b;
  // MCP response format me text return karte hain
  return { content: [{ type: 'text', text: String(sum) }] };
});

// 'weather' tool register kar rahe hain
server.tool(
  // Tool ka naam
  'weather',
  // Input schema: city string hona chahiye
  { city: z.string().describe('Name of the city') },
  // Tool handler: city ke basis par weather nikalta hai
  async function ({ city }) {
    // wttr.in se weather data fetch karte hain
    const response = await axios.get(`https://wttr.in/${city}?format=%C+%t`, {
      // Response ko JSON me parse karne ka hint
      responseType: 'json',
    });
    // Response ko MCP text content me wrap karke return karte hain
    return { content: [{ type: 'text', text: JSON.stringify(response.data) }] };
  }
);

// STDIO transport initialize karte hain
const transport = new StdioServerTransport();
// Server ko transport se connect karke start karte hain
await server.connect(transport);

// Start
//   |
//   v
// Import deps (McpServer, zod, StdioServerTransport, axios)
//   |
//   v
// Create server (name, version)
//   |
//   v
// Register tool "add"
//   |
//   v
// Register tool "weather"
//   |
//   v
// Create STDIO transport
//   |
//   v
// Connect server to transport
//   |
//   v
// Ready to handle tool calls