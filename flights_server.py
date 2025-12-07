from mcp.server.fastmcp import FastMCP
import os 
import json
from datetime import datetime

mcp=FastMCP(name="flights server")
FLIGHTS_PATH = os.path.join(os.path.dirname(__file__), "flights.json")
def _load_flights():
    with open(FLIGHTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("flights", [])
@mcp.resource("flights://today")
def flights_resource():
    """
    Resource qui expose la liste des vols du jour.
    L'URL 'flights://today' sera visible par Copilot/Claude.
    """
    with open(FLIGHTS_PATH, "r", encoding="utf-8") as f:
        return f.read()
@mcp.tool()
def find_flight(flight_number: str) -> str:
    """Trouve un vol par son numéro (ex: AF1234)"""
 
    flights = _load_flights()
 
    for flight in flights:
        if flight.get("flight_number", "").upper() == flight_number.upper():
            return f"""
                 Vol {flight["flight_number"]} ({flight["airline"]})
            {flight["departure_city"]} → {flight["arrival_city"]}
            Départ : {flight["departure_time"]} | Arrivée : {flight["arrival_time"]}
            Statut : {flight["status"]}
            """
    return f"Vol {flight_number} non trouvé aujourd'hui."
@mcp.tool()
def flights_to(destination: str) -> str:
    """Liste tous les vols à destination d'une ville aujourd'hui."""
    flights = _load_flights()
    matches = [f for f in flights if destination.lower() in f["arrival_city"].lower()]
    if not matches:
        return f"Aucun vol trouvé vers {destination.title()} aujourd'hui."
    result = f"Vols vers {destination.title()} ({len(matches)} trouvé(s)) :\n\n"
    for f in matches:
        result += f"• {f['flight_number']} ({f['airline']}) → {f['arrival_city']} à {f['arrival_time']} – {f['status']}\n"
    return result.strip()


# ───────────────────────────────────────────────────────────────
#   TOOL 3 : filtrer par statut (retardé, annulé, à l’heure…)
#   
# ───────────────────────────────────────────────────────────────
@mcp.tool()
def flights_by_status(status: str) -> str:
    """Retourne les vols ayant un statut donné (ex : 'retardé', 'annulé')."""
    flights = _load_flights()
    matches = [f for f in flights if f["status"].lower() == status.lower()]

    if not matches:
        return f"Aucun vol avec le statut '{status}'."

    result = f"Vols avec statut '{status}' ({len(matches)} trouvés) :\n\n"
    for f in matches:
        result += (
            f"• {f['flight_number']} – {f['departure_city']} → "
            f"{f['arrival_city']} – Départ {f['departure_time']}\n"
        )

    return result.strip()


# ───────────────────────────────────────────────────────────────
#   TOOL 4 : tool métier (libre)
#   Exemple : obtenir les vols qui partent dans moins de 2 heures
# ───────────────────────────────────────────────────────────────
@mcp.tool()
def next_departures(hours: int = 2) -> str:
    """
    Renvoie les vols dont le départ est dans moins de X heures.
    Logique métier utile pour un tableau d'affichage.
    """
    flights = _load_flights()
    now = datetime.now()

    soon_flights = []

    for f in flights:
        try:
            dt = datetime.strptime(f["departure_time"], "%H:%M")
            dt = dt.replace(
                year=now.year, month=now.month, day=now.day
            )
            if 0 <= (dt - now).total_seconds() <= hours * 3600:
                soon_flights.append(f)
        except:
            pass  # ignore erreur format

    if not soon_flights:
        return f"Aucun vol dans les {hours} prochaines heures."

    result = f"Vols qui partent dans moins de {hours} heures :\n\n"
    for f in soon_flights:
        result += (
            f"• {f['flight_number']} – Départ à {f['departure_time']} "
            f"vers {f['arrival_city']} ({f['status']})\n"
        )

    return result.strip()


if __name__ == "__main__":
    
    mcp.run(transport="stdio")
