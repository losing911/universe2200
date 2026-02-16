"""
Universe 2200 - Read-Only API Server (Process B)

Role: Reader
Responsibilities:
- Serve content from data/public/ JSON cache
- Provide readonly endpoints for UI/Broadcast

Constraints:
- No Runtime injection
- No Simulation Logic
- No Write endpoints
"""

# Simply re-export the broadcast API
from api.broadcast_api import app

# That's it! No wrapping needed.
# The broadcast_api already handles all read-only endpoints.
