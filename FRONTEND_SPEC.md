# N.O.V.A Frontend Specification

## Tech Stack
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS (glassmorphism)
- ReactFlow/D3.js
- socket.io-client
- framer-motion

## File Structure
```
/app
  /page.tsx         # Main dashboard
  /layout.tsx       # Root layout
/components
  OrbitGraph.tsx    # Node visualization
  InsightFeed.tsx   # Real-time event feed  
  ControlPanel.tsx  # Action buttons
/lib
  socket.ts         # WebSocket client
/styles
  globals.css       # Glassmorphism styles
```

## Implementation Steps

1. Setup glassmorphism styles in globals.css
2. Create socket.io client connection
3. Build OrbitGraph component with:
   - Node rendering
   - Orbit animations
   - Interaction handlers
4. Implement InsightFeed with:
   - Real-time updates
   - Scroll behavior
   - Message formatting
5. Create ControlPanel with:
   - Deepen/Pivot/Archive buttons
   - API call handlers
6. Assemble dashboard layout
7. Add framer-motion transitions