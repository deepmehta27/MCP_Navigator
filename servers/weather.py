from mcp.server.fastmcp import FastMCP 
import httpx

mcp = FastMCP("Weather Server")

async def _geocode(city: str):
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            return None
        x = data["results"][0]
        return x["latitude"], x["longitude"], x["name"], x.get("country_code")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get current weather summary for a city (e.g., 'New York')."""
    g = await _geocode(location)
    if not g:
        return f"Couldn’t find '{location}'."
    lat, lon, name, country = g
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current_weather": True},
        )
        r.raise_for_status()
        cur = r.json().get("current_weather") or {}
    if not cur:
        return f"No weather data for {name}."
    return f"{name}, {country}: {cur.get('temperature')}°C, wind {cur.get('windspeed')} km/h."

if __name__ == "__main__":
    # serves MCP at http://localhost:8000/mcp
    mcp.run(transport="streamable-http")