# Murder Mystery MCP Server for Puch AI

This project is an interactive, conversational detective game built to run with [Puch AI](https://puch.ai/), a WhatsApp-only AI agent.

Players step into the role of a detective to solve the murder of Lord Alistair Blackwood. By investigating rooms, examining clues, and interrogating suspects, you can piece together the motive, the weapon, and the killer's identity, all through natural language commands in your WhatsApp chat.

This server was built for the Puch AI hackathon using Python, FastMCP, and is deployed on Render.

**Play the Live Game:** [https://puch.ai/mcp/u7kVc1s1wY](https://puch.ai/mcp/u7kVc1s1wY)

## Features

* **Conversational Gameplay:** Uses natural language to interact with the game world.
* **Interactive Story:** A branching narrative with puzzles, clues, and red herrings.
* **Stateful Game Engine:** The MCP server manages the player's location, inventory, and the state of the mystery.
* **Puch AI Integration:** Includes a `validate` tool for seamless connection with the Puch AI platform.
* **Multiple Tools:** The game is powered by a suite of MCP tools, including `go`, `examine`, `collect`, `interrogate`, and `accuse`.

## Deployment

This server is designed for easy deployment on a platform like [Render](https://render.com/).

### 1. Project Structure

The repository contains two main Python files:
* `main.py`: Contains all the game logic, including the world map, clues, and the definitions for all the MCP tools.
* `server.py`: A simple runner script that imports the application from `main.py` and starts the server.

### 2. Requirements

* fastmcp>=2.0
* pydantic>=2.0.0
* uvicorn>=0.29.0

## 3. Setting Up ngrok

**ngrok** is used to create a secure, public URL to your local machine, allowing you to test your server with the Puch AI platform before deploying.

**1. Sign Up for ngrok:**
Go to the [ngrok dashboard](https://dashboard.ngrok.com/signup) and create a free account.

**2. Download ngrok:**
Download the ngrok executable for your operating system from the [download page](https://ngrok.com/download). Unzip the file to a location you can easily access.

**3. Connect Your Account:**
To connect your account, you'll need your authtoken. Find it on your ngrok dashboard. Then, run the following command in your terminal, replacing `YOUR_AUTHTOKEN` with the token you copied:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

---
## 4. Local Setup

To run this project on your local machine, follow these steps:

**1. Clone the repository:**
```bash
git clone https://github.com/NarainBK/Murder_Mystery_MCP.git
cd Murder_Mystery_MCP
```

**2. Create a .env file:**
```bash
TOKEN="YOUR-SECRET-TOKEN"
MY_NUMBER="YOUR_MOBILE_NUMBER_HERE_WITH_COUNTRY_CODE"
```

**3. Install dependencies:**
```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**4. Run the server:**
```bash
python server.py
```

**5. Connect to ngrok:**
Open a second, separate terminal window and run the following command. This starts the tunnel to your local server.
```bash
ngrok http 8000
```

**6. Connect to Puch AI**
* Open Puch AI in WhatsApp
* Use the connect command:
```bash
/mcp connect https://your-domain.ngrok.app/mcp your_secret_token_here
```

* Debug Mode:
To get more detailed error messages:
```bash
/mcp diagnostics-level debug
```
