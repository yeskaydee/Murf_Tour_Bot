# 🗺️ Murf Guide Bot - AI-Powered Virtual Tour Guide

## **What is it?**

The Murf Guide Bot is an intelligent, multilingual virtual tour guide that operates through Telegram. It combines cutting-edge AI technologies to provide real-time tourism assistance with voice interaction capabilities.

## **Core Purpose & Use Cases**

This bot is designed for **tourists and travelers** who need:

- 📍 **Location-based guidance** - Get information about nearby attractions, restaurants, and points of interest
- 🗣️ **Multilingual support** - Communicate in 20+ languages including English, Spanish, French, German, Hindi, Tamil, Chinese, Japanese, and more
- 🎤 **Voice interaction** - Speak naturally and receive audio responses
- 🚶 **Navigation assistance** - Get walking directions to destinations
- 💬 **Real-time Q&A** - Ask questions about local culture, history, and practical travel information

## **Key Technologies & Integrations**

### 🤖 **AI & Language Processing**

- **Azure OpenAI** - Powers the intelligent tour guide responses
- **Whisper AI** - Converts speech to text for voice input
- **Murf AI** - High-quality text-to-speech in multiple languages and accents
- **Murf Translation** - Real-time text translation between languages

### 🗺️ **Location & Navigation**

- **OpenRouteService API** - Provides walking directions and geocoding
- **Reverse geocoding** - Converts coordinates to readable location names
- **Real-time location tracking** - Updates user position for contextual responses

### 💬 **Communication Platform**

- **Telegram Bot API** - Main interface for user interaction
- **Flask Web Server** - Handles webhook communications and API endpoints
- **WebSocket connections** - Real-time audio streaming for TTS

## **How It Works**

1. **User Setup**: Users start the bot, share their location, and select their preferred language and message type (text, audio, or both)

2. **Voice/Text Input**: Users can either:

   - Speak into the bot (voice gets transcribed by Whisper)
   - Type their questions directly

3. **Intelligent Processing**:

   - The bot analyzes the user's location and query
   - Uses Azure OpenAI to generate contextual, helpful responses
   - Detects if the user is asking for directions and extracts destination names

4. **Multilingual Output**:

   - Translates responses to the user's preferred language
   - Converts text to natural-sounding speech using Murf AI
   - Sends both text and audio responses based on user preferences

5. **Navigation Support**:
   - Provides step-by-step walking directions
   - Geocodes destination names to coordinates
   - Offers route optimization

## **Technical Architecture**

```
User → Telegram Bot → Flask App → AI Services
                ↓
        Location Services → Navigation APIs
                ↓
        Translation → TTS → Audio Response
```

## **Key Features**

✅ **20+ Languages Supported** - From English variants to regional languages like Hindi, Tamil, Bengali  
✅ **Voice-First Interface** - Natural speech interaction with high-quality audio responses  
✅ **Location-Aware** - Contextual responses based on user's current position  
✅ **Real-Time Translation** - Seamless language switching  
✅ **Walking Directions** - Step-by-step navigation guidance  
✅ **Persistent User Preferences** - Remembers language and message type settings  
✅ **Live Location Updates** - Tracks user movement for better assistance

## **Target Audience**

- **International tourists** visiting new cities
- **Business travelers** needing local guidance
- **Language learners** practicing in real-world contexts
- **Accessibility users** who prefer voice interaction
- **Solo travelers** seeking instant local knowledge

## **Project Structure**

```
Murf_Guide_Bot/
├── app.py                 # Main Flask application
├── flask_app.py          # Voice translation endpoint
├── bot/
│   ├── handlers.py       # Telegram bot command handlers
│   ├── global_state.py   # User data management
│   └── utils.py          # Utility functions
├── services/
│   ├── tour_guide_llm.py # Azure OpenAI integration
│   ├── murf_tts.py       # Text-to-speech service
│   ├── murf_translate.py # Translation service
│   ├── whisper_stt.py    # Speech-to-text service
│   ├── routing.py        # Navigation and directions
│   └── geoLocation.py    # Location services
├── Variables.py          # Language and voice mappings
├── cfg.py               # Configuration settings
└── requirements.txt     # Python dependencies
```

## **Supported Languages**

| Language         | Code  | Voice ID       |
| ---------------- | ----- | -------------- |
| English (US)     | en-US | en-US-natalie  |
| English (UK)     | en-UK | en-UK-theo     |
| English (India)  | en-IN | en-IN-aarav    |
| Spanish (Mexico) | es-MX | es-MX-carlos   |
| Spanish (Spain)  | es-ES | es-ES-carla    |
| French           | fr-FR | fr-FR-axel     |
| German           | de-DE | de-DE-matthias |
| Hindi            | hi-IN | hi-IN-kabir    |
| Tamil            | ta-IN | ta-IN-mani     |
| Chinese          | zh-CN | zh-CN-tao      |
| Japanese         | ja-JP | ja-JP-denki    |
| Korean           | ko-KR | ko-KR-hwan     |

_And many more..._

## **Getting Started**

### Prerequisites

- Python 3.8+
- Telegram Bot Token
- Azure OpenAI API Key
- Murf AI API Key
- OpenRouteService API Key

### Installation

```bash
git clone <repository-url>
cd Murf_Tour_Bot
pip install -r requirements.txt
```

### Configuration

Set up your environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_telegram_token"
export AZURE_OPENAI_API_KEY="your_azure_key"
export MURF_API_KEY="your_murf_key"
export ORS_API_KEY="your_ors_key"
```

### Running the Bot

```bash
python -m bot.handlers
```

## **Use Cases & Examples**

### 🗣️ **Voice Interaction**

User: _"Where can I find good coffee near me?"_
Bot: _Provides audio response in user's language with nearby coffee shop recommendations_

### 🗺️ **Navigation**

User: _"How do I get to the Red Fort?"_
Bot: _Extracts destination, provides step-by-step walking directions_

### 🌍 **Multilingual Support**

User: _"¿Dónde está el museo más cercano?"_ (Spanish)
Bot: _Responds in Spanish with museum information and directions_

### 📍 **Location-Based Recommendations**

User: _"What's interesting around here?"_
Bot: _Analyzes current location and suggests nearby attractions, restaurants, and points of interest_

## **Technical Highlights**

- **Real-time WebSocket TTS**: High-quality audio streaming using Murf AI
- **Intelligent Query Processing**: Azure OpenAI-powered contextual responses
- **Multi-modal Input**: Supports both voice and text input seamlessly
- **Location Intelligence**: Uses coordinates and reverse geocoding for precise assistance
- **Scalable Architecture**: Modular service-based design for easy maintenance

## **Future Enhancements**

- 🖼️ **Image Recognition** - Identify landmarks from photos
- 📊 **Offline Mode** - Basic functionality without internet
- 🎯 **Personalization** - Learn user preferences over time
- 🔔 **Push Notifications** - Alert users about nearby events
- 🤝 **Group Tours** - Coordinate multiple users on guided tours

---

This project represents a sophisticated integration of multiple AI services to create a truly intelligent, multilingual travel companion that bridges language barriers and provides contextual, location-aware assistance to travelers worldwide.
