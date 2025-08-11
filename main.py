import os
import asyncio
import sys
from pydantic import BaseModel, Field
from typing import Literal

from fastmcp import FastMCP

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "mystery_game_token")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER", "YOUR_WHATSAPP_NUMBER_HERE")
PORT = int(os.getenv("PORT", 8000))


# The map of the crime scene and locations of clues/suspects
crime_scene = {
    "foyer": {
        "description": "You stand in the grand foyer of Blackwood Manor. A grand staircase leads up. The ballroom is to the west and the library is to the east. The victim, Lord Alistair Blackwood, lies on the floor.",
        "exits": {"west": "ballroom", "east": "library"},
        "items": ["body"],
        "suspects": []
    },
    "ballroom": {
        "description": "A vast, empty ballroom. Champagne glasses are scattered on a table. A set of muddy footprints leads to the garden door.",
        "exits": {"east": "foyer"},
        "items": ["muddy footprints", "champagne glasses"],
        "suspects": ["Lady Victoria"] # The Widow
    },
    "library": {
        "description": "A cozy library lined with bookshelves. A fireplace crackles softly. A half-empty glass of whiskey sits on a small table next to a wingback chair.",
        "exits": {"west": "foyer", "north": "study"},
        "items": ["whiskey glass", "fireplace"],
        "suspects": []
    },
    "study": {
        "description": "Lord Alistair's private study. A large mahogany desk is covered in papers. One of the drawers is slightly ajar.",
        "exits": {"south": "library"},
        "items": ["desk", "papers"],
        "suspects": ["Mr. Giles"] # The Butler
    }
}

# Hidden truth of the murder and the initial game state
game_state = {
    "player_location": "foyer",
    "player_inventory": [], # Hold collected clues
    "truth": {
        "killer": "Mr. Giles",
        "weapon": "poison",
        "motive": "blackmail"
    },
    "clues": {
        "body": "You examine the body. There are no visible wounds, but you notice a faint, bitter almond smell.",
        "whiskey glass": "The glass contains whiskey laced with a fast-acting poison. This was the murder weapon.",
        "desk": "You search the desk and find a hidden compartment containing a threatening letter.",
        "letter": "The letter, from Mr. Giles, reads: 'I know your secret, Alistair. Pay me, or everyone will know.' This reveals the motive.",
        "muddy footprints": "A red herring. The footprints belong to the gardener, who is innocent."
    },
    "interrogations": {
        "Lady Victoria": "She sobs, 'I loved him! I was in the ballroom all evening, I saw nothing!' (A lie, she knows about the blackmail).",
        "Mr. Giles": "He stands rigidly. 'I was polishing silver in the pantry, sir. A terrible tragedy.' (A lie, he was in the study)."
    },
    "known_facts": set(), # Facts the player has uncovered
    "game_over": False
}

class GameTurnResult(BaseModel):
    """ Standard response after every player action."""
    message: str = Field(description="The description of the result of the action to show the player.")
    known_facts: list[str] = Field(description="A list of facts the player has uncovered.")
    current_location: str = Field(description="The player's current location.")
    game_over: bool = Field(description="Is the game over?")

app = FastMCP(
    name="MurderMysteryGame",
    instructions="A server that runs a murder mystery game. Use tools like 'go', 'examine', 'interrogate', 'collect', 'accuse', and 'validate'."
)

# Game Tools 
@app.tool(description="A required tool for Puch AI to validate the server owner.")
async def validate() -> str:
    """
    Puch AI calls this tool to verify the server.
    It must return your WhatsApp number as a string.
    """
    if MY_WHATSAPP_NUMBER == "YOUR_WHATSAPP_NUMBER_HERE":
        print("🚨 WARNING: Please set MY_WHATSAPP_NUMBER in the script.", file=sys.stderr)
        return "ERROR: WhatsApp number not configured by server owner."
        
    return MY_WHATSAPP_NUMBER

@app.tool(description="Starts a new mystery and describes the crime scene.")
async def start_game() -> GameTurnResult:
    """Resets the game to its initial state."""
    game_state["player_location"] = "foyer"
    game_state["player_inventory"] = []
    game_state["known_facts"] = set()
    game_state["game_over"] = False
    start_room = crime_scene[game_state["player_location"]]
    return GameTurnResult(
        message=f"The mystery begins! {start_room['description']}",
        known_facts=list(game_state["known_facts"]),
        current_location=game_state["player_location"],
        game_over=game_state["game_over"]
    )

@app.tool(description="Moves the player in a specified direction (north, south, east, west).")
async def go(direction: Literal["north", "south", "east", "west"]) -> GameTurnResult:
    location = game_state["player_location"]
    room = crime_scene[location]
    if direction in room["exits"]:
        game_state["player_location"] = room["exits"][direction]
        new_room = crime_scene[game_state["player_location"]]
        message = f"You go {direction}. {new_room['description']}"
    else:
        message = f"You can't go {direction}."
    return GameTurnResult(
        message=message,
        known_facts=list(game_state["known_facts"]),
        current_location=game_state["player_location"],
        game_over=game_state["game_over"]
    )

@app.tool(description="Examines the current room or a specific object/person in it.")
async def examine(target: str) -> GameTurnResult:
    location = game_state["player_location"]
    room = crime_scene[location]
    
    if target == "room":
        message = room["description"]
        if room["items"]:
            message += f" You see: {', '.join(room['items'])}."
        if room["suspects"]:
            message += f" {', '.join(room['suspects'])} is also here."
    elif target in room["items"]:
        message = game_state["clues"].get(target, f"You examine the {target}, but find nothing unusual.")
        if target == "body": game_state["known_facts"].add("The victim was poisoned.")
        if target == "whiskey glass": game_state["known_facts"].add("The weapon was a poisoned whiskey glass.")
        if target == "desk": 
            message += " You should try to 'collect' the 'letter'."
    else:
        message = f"There is no '{target}' to examine here."
        
    return GameTurnResult(
        message=message,
        known_facts=list(game_state["known_facts"]),
        current_location=location,
        game_over=game_state["game_over"]
    )

@app.tool(description="Collects a specific clue and adds it to your notebook.")
async def collect(clue: str) -> GameTurnResult:
    location = game_state["player_location"]
    if clue == "letter" and "desk" in crime_scene[location]["items"]:
        game_state["player_inventory"].append("threatening letter")
        game_state["known_facts"].add("The motive was blackmail by Mr. Giles.")
        message = "You take the letter. It's a key piece of evidence!"
    else:
        message = f"You can't collect '{clue}' here."
        
    return GameTurnResult(
        message=message,
        known_facts=list(game_state["known_facts"]),
        current_location=location,
        game_over=game_state["game_over"]
    )

@app.tool(description="Interrogates a suspect in the current room.")
async def interrogate(suspect_name: Literal["Lady Victoria", "Mr. Giles"]) -> GameTurnResult:
    location = game_state["player_location"]
    room = crime_scene[location]
    if suspect_name in room["suspects"]:
        message = f"You question {suspect_name}. {game_state['interrogations'][suspect_name]}"
    else:
        message = f"{suspect_name} is not in this room."
        
    return GameTurnResult(
        message=message,
        known_facts=list(game_state["known_facts"]),
        current_location=location,
        game_over=game_state["game_over"]
    )

@app.tool(description="Make a final accusation to solve the crime.")
async def accuse(killer: str, weapon: str, motive: str) -> GameTurnResult:
    truth = game_state["truth"]
    if killer == truth["killer"] and weapon == truth["weapon"] and motive == truth["motive"]:
        message = f"You lay out the evidence. {killer} confesses! The motive was indeed {motive}, and the weapon was {weapon}. You've solved the case! YOU WIN!"
        game_state["game_over"] = True
    else:
        message = "Your accusation is incorrect. The real killer slips away, and the case goes cold. GAME OVER."
        game_state["game_over"] = True
        
    return GameTurnResult(
        message=message,
        known_facts=list(game_state["known_facts"]),
        current_location=game_state["player_location"],
        game_over=game_state["game_over"]
    )
