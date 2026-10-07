from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import httpx
import json
import re

from .prompts import SYSTEM_PROMPT


# ============================================================
# Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"

OLLAMA_MODEL = "gemma4:e2b"


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="TouchGrass-AI",
    description="Local AI outdoor activity guide powered by Ollama",
    version="1.0.0"
)


# ============================================================
# Request Model
# ============================================================

class GuideRequest(BaseModel):

    location: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    activity: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    duration: str = Field(
        default="1-2 hours",
        max_length=50
    )

    fitness: str = Field(
        default="Beginner",
        max_length=50
    )

    preferences: str = Field(
        default="",
        max_length=500
    )

    constraints: str = Field(
        default="",
        max_length=500
    )


# ============================================================
# Build User Prompt
# ============================================================

def build_prompt(data: GuideRequest) -> str:

    return f"""
Create a personalized outdoor activity guide for this user.

USER INFORMATION
================

Area:
{data.location}

Desired outdoor activity:
{data.activity}

Available time:
{data.duration}

Fitness / experience:
{data.fitness}

Preferences:
{data.preferences if data.preferences else "None provided"}

Constraints:
{data.constraints if data.constraints else "None provided"}


INSTRUCTIONS
============

Create a realistic outdoor experience that encourages this
person to physically go outside.

The user has provided only a general area.

Do not invent exact trails, parks, opening hours, weather,
distances or current conditions.

If location-specific information is not known, recommend
the TYPE of outdoor place they should look for.

The final answer must follow the JSON structure specified
in the system instructions.

Keep the plan practical enough that the user can read it,
remember the important parts and then put their phone away.
"""


# ============================================================
# Extract JSON from Ollama Response
# ============================================================

def extract_json(text: str):

    if not text:
        raise ValueError(
            "Ollama returned an empty response."
        )

    text = text.strip()

    # Remove markdown code fences if model accidentally adds them.
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    # First attempt: entire response is JSON.
    try:

        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Second attempt: find JSON object in surrounding text.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        possible_json = text[start:end + 1]

        try:

            return json.loads(possible_json)

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "The AI returned invalid JSON."
    )


# ============================================================
# Home Page
# ============================================================

@app.get("/")
async def home():

    return FileResponse(
        "static/index.html"
    )


# ============================================================
# Health Check
# ============================================================

@app.get("/api/health")
async def health():

    try:

        async with httpx.AsyncClient(
            timeout=5
        ) as client:

            response = await client.get(
                "http://localhost:11434/api/tags"
            )

            response.raise_for_status()

            data = response.json()

        models = [
            model.get("name", "")
            for model in data.get("models", [])
        ]

        model_available = any(
            OLLAMA_MODEL in model
            for model in models
        )

        return {
            "status": "ok",
            "ollama": True,
            "model": OLLAMA_MODEL,
            "model_available": model_available,
            "models": models
        }

    except httpx.ConnectError:

        return {
            "status": "ok",
            "ollama": False,
            "model": OLLAMA_MODEL,
            "model_available": False,
            "models": []
        }

    except Exception as error:

        return {
            "status": "ok",
            "ollama": False,
            "model": OLLAMA_MODEL,
            "model_available": False,
            "error": str(error)
        }


# ============================================================
# Generate Outdoor Guide
# ============================================================

@app.post("/api/guide")
async def generate_guide(request: GuideRequest):

    prompt = build_prompt(request)

    payload = {
        "model": OLLAMA_MODEL,

        "messages": [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        "stream": False,

        # Ask Ollama for JSON.
        "format": "json",

        "options": {
            "temperature": 0.7
        }
    }

    print()
    print("=" * 60)
    print("🌱 TouchGrass-AI")
    print("=" * 60)

    print(
        f"📍 Location: {request.location}"
    )

    print(
        f"🌳 Activity: {request.activity}"
    )

    print(
        f"⏱ Duration: {request.duration}"
    )

    print(
        f"💪 Fitness: {request.fitness}"
    )

    print(
        f"🤖 Model: {OLLAMA_MODEL}"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # Call Ollama
    # --------------------------------------------------------

    try:

        async with httpx.AsyncClient(
            timeout=180
        ) as client:

            response = await client.post(
                OLLAMA_URL,
                json=payload
            )

            print(
                f"📡 Ollama status: {response.status_code}"
            )

            response.raise_for_status()

            ollama_result = response.json()

    except httpx.ConnectError:

        print(
            "❌ Could not connect to Ollama."
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Cannot connect to Ollama. "
                "Please make sure Ollama is running "
                "on localhost:11434."
            )
        )

    except httpx.TimeoutException:

        print(
            "❌ Ollama request timed out."
        )

        raise HTTPException(
            status_code=504,
            detail=(
                "Ollama took too long to generate the guide. "
                "The model may need more time on your machine."
            )
        )

    except httpx.HTTPStatusError as error:

        print(
            "❌ Ollama HTTP error:"
        )

        print(
            error.response.text
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Ollama returned an error: "
                + error.response.text
            )
        )

    except Exception as error:

        print(
            "❌ Unexpected Ollama error:"
        )

        print(
            str(error)
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    # --------------------------------------------------------
    # Extract model response
    # --------------------------------------------------------

    try:

        model_response = (
            ollama_result
            .get("message", {})
            .get("content", "")
        )

        if not model_response:

            print(
                "❌ Ollama returned no message content."
            )

            print(
                ollama_result
            )

            raise ValueError(
                "Ollama returned no message content."
            )

        print()
        print("🤖 AI RESPONSE")
        print("-" * 60)
        print(model_response)
        print("-" * 60)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not read Ollama response: "
                + str(error)
            )
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        guide = extract_json(
            model_response
        )

    except ValueError as error:

        print()
        print(
            "❌ Failed to parse AI JSON."
        )

        print(
            model_response
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI returned an invalid response. "
                "Please try again."
            )
        )

    # --------------------------------------------------------
    # Validate minimum structure
    # --------------------------------------------------------

    if not isinstance(guide, dict):

        raise HTTPException(
            status_code=500,
            detail="AI returned an unexpected response format."
        )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    print()
    print(
        "✅ TouchGrass guide generated successfully!"
    )

    print("=" * 60)
    print()

    return {
        "success": True,
        "model": OLLAMA_MODEL,
        "guide": guide
    }


# ============================================================
# Static Files
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static"
)
