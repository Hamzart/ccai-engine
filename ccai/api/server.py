"""
FastAPI server for CCAI chatbot.

This module provides a web API for interacting with the CCAI chatbot.
"""

import logging
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ccai.core.graph import ConceptGraph
from ccai.core.reasoning import ReasoningCore
from ccai.nlp.parser import QueryParser
from ccai.nlp.extractor import InformationExtractor
from ccai.nlp.primitives import PrimitiveManager
from ccai.nlp.sentiment import SentimentAnalyzer
from ccai.conversation.dialog import DialogManager
from ccai.conversation.context import ContextTracker
from ccai.conversation.intent import IntentClassifier
from ccai.user.profile import UserProfileManager
from ccai.user.personalization import PersonalizationAdapter, EntityExtractor
from ccai.nlg.generator import ResponseGenerator
from ccai.external.fusion import KnowledgeFusion
from ccai.core.subsystems.inheritance import InheritanceResolver
from ccai.core.subsystems.relation import RelationResolver
from ccai.core.subsystems.fuzzy import FuzzyMatch
from ccai.core.subsystems.bayes import BayesianUpdater
from ccai.core.subsystems.conflict import ConflictResolver
from ccai.core.subsystems.analogical import AnalogicalReasoner
from ccai.core.subsystems.temporal import TemporalReasoner
from ccai.core.subsystems.hypothetical import HypotheticalReasoner
from ccai.external.fusion import ExternalKnowledgeSubsystem
from ccai.llm.interface import LLMInterface

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="CCAI Chatbot API", description="API for interacting with the CCAI chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
storage_dir = Path("graph_data")
primitives_file = Path("primitives.json")
user_data_dir = Path("user_data")

# Ensure directories exist
storage_dir.mkdir(parents=True, exist_ok=True)
user_data_dir.mkdir(parents=True, exist_ok=True)

# Create global components
graph = ConceptGraph(storage_dir)
primitive_manager = PrimitiveManager(primitives_file)
query_parser = QueryParser()
extractor = InformationExtractor(graph, primitive_manager)
profile_manager = UserProfileManager(user_data_dir)
entity_extractor = EntityExtractor()
sentiment_analyzer = SentimentAnalyzer()
response_generator = ResponseGenerator()
personalization_adapter = PersonalizationAdapter(profile_manager)
fusion = KnowledgeFusion(graph)
llm_interface = LLMInterface()

# Initialize subsystems
subsystems = [
    InheritanceResolver(),
    RelationResolver(graph=graph),
    FuzzyMatch(),
    BayesianUpdater(),
    ConflictResolver(),
    AnalogicalReasoner(graph=graph),
    TemporalReasoner(),
    HypotheticalReasoner(graph=graph),
    ExternalKnowledgeSubsystem(graph=graph, fusion=fusion),
]

# Initialize reasoning core
reasoning_core = ReasoningCore(graph, subsystems)

# Load graph from disk
graph.load_from_disk()

# Always load the knowledge bases
kb_file = Path("knowledge.txt")
if kb_file.exists():
    logger.info("Loading knowledge base from knowledge.txt...")
    extractor.ingest_text(kb_file.read_text())
    graph.save_snapshot()

# Load common knowledge
common_kb_file = Path("common_knowledge.txt")
if common_kb_file.exists():
    logger.info("Loading common knowledge base...")
    extractor.ingest_text(common_kb_file.read_text())
    graph.save_snapshot()

# Active dialog managers for each user
dialog_managers: Dict[str, DialogManager] = {}

# WebSocket connections
websocket_connections: Dict[str, WebSocket] = {}


# Pydantic models for API
class Message(BaseModel):
    """Message sent by a user."""
    text: str
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    """Response from the chatbot."""
    text: str
    user_id: str
    message_id: str
    timestamp: float


class UserPreference(BaseModel):
    """User preference setting."""
    preference: str
    value: Any


# Helper functions
def get_dialog_manager(user_id: str) -> DialogManager:
    """Get or create a dialog manager for a user."""
    if user_id not in dialog_managers:
        dialog_managers[user_id] = DialogManager(
            graph=graph,
            reasoning_core=reasoning_core,
            extractor=extractor,
            query_parser=query_parser,
            response_generator=response_generator,
            sentiment_analyzer=sentiment_analyzer,
            profile_manager=profile_manager,
            personalization_adapter=personalization_adapter,
            entity_extractor=entity_extractor,
            llm_interface=llm_interface,
            current_user_id=user_id
        )
    return dialog_managers[user_id]


# API routes
@app.get("/")
async def root(request: Request):
    """Serve the chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: Message):
    """Process a chat message."""
    try:
        dialog_manager = get_dialog_manager(message.user_id)
        response = dialog_manager.process_message(message.text, message.user_id)
        
        return ChatResponse(
            text=response,
            user_id=message.user_id,
            message_id=str(uuid.uuid4()),
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/learn")
async def learn(message: Message):
    """Learn from a statement."""
    try:
        extractor.ingest_text(message.text)
        graph.save_snapshot()
        return {"status": "success", "message": "Knowledge acquired and saved."}
    except Exception as e:
        logger.error(f"Error learning from message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user preferences."""
    try:
        profile = profile_manager.get_profile(user_id)
        return profile.preferences
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/user/{user_id}/preferences")
async def set_user_preference(user_id: str, preference: UserPreference):
    """Set a user preference."""
    try:
        profile = profile_manager.get_profile(user_id)
        profile.set_preference(preference.preference, preference.value)
        profile_manager.save_profile(profile)
        return {"status": "success", "message": "Preference updated."}
    except Exception as e:
        logger.error(f"Error setting user preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile information."""
    try:
        profile = profile_manager.get_profile(user_id)
        return {
            "user_id": profile.user_id,
            "name": profile.name,
            "session_count": profile.session_count,
            "preferences": profile.preferences,
            "top_topics": profile.get_top_topics(),
            "top_entities": profile.get_top_entities(),
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    await websocket.accept()
    websocket_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("text", "")
            
            dialog_manager = get_dialog_manager(user_id)
            response = dialog_manager.process_message(message_text, user_id)
            
            await websocket.send_json({
                "text": response,
                "user_id": user_id,
                "message_id": str(uuid.uuid4()),
                "timestamp": time.time()
            })
    except WebSocketDisconnect:
        if user_id in websocket_connections:
            del websocket_connections[user_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)