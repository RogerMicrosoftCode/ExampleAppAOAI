# Chat Application con Azure OpenAI, Microsoft Teams y Azure Bot Service

## 📋 Descripción

Esta guía proporciona un ejemplo completo de cómo crear una aplicación de chat usando **Azure OpenAI Service**, **LangChain**, **Microsoft Teams** y **Azure Bot Service**, containerizada con Docker. La aplicación incluye tanto una interfaz web (Streamlit) como integración completa con Microsoft Teams.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  Microsoft Teams                     │
│                   (Frontend)                         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Azure Bot Service                       │
│         (Bot Framework Connector)                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│             Bot Application                          │
│        (Bot Framework SDK + LangChain)               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│           Azure OpenAI Service                       │
│              (GPT-4 / GPT-3.5)                       │
└─────────────────────────────────────────────────────┘

                  Aplicación Web (Opcional)
┌─────────────────────────────────────────────────────┐
│              Streamlit UI                            │
│         (Interfaz Web Alternativa)                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
               (Mismo Backend)
```

## 📦 Prerrequisitos

- Cuenta de Azure activa con suscripción
- Microsoft 365 / Office 365 con permisos de administración
- Azure CLI instalado
- Python 3.9 o superior
- Docker y Docker Compose
- Git
- Node.js 16+ (para Teams App Studio)

## 🚀 Parte 1: Configuración de Azure OpenAI Service

### Paso 1: Crear Recurso de Azure OpenAI

```bash
# Login a Azure
az login

# Crear grupo de recursos
az group create \
  --name rg-openai-teams-bot \
  --location eastus

# Crear servicio de Azure OpenAI
az cognitiveservices account create \
  --name openai-teams-service \
  --resource-group rg-openai-teams-bot \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes
```

### Paso 2: Desplegar Modelo GPT-4

1. Ve a [Azure OpenAI Studio](https://oai.azure.com)
2. Navega a **Deployments** > **Create new deployment**
3. Configurar:
   ```
   Model: gpt-4 o gpt-35-turbo
   Deployment name: gpt-4-teams
   Version: Última disponible
   Tokens per minute: 10K-120K
   ```

### Paso 3: Obtener Credenciales

```bash
# Obtener endpoint y keys
az cognitiveservices account show \
  --name openai-teams-service \
  --resource-group rg-openai-teams-bot \
  --query "properties.endpoint"

az cognitiveservices account keys list \
  --name openai-teams-service \
  --resource-group rg-openai-teams-bot
```

## 🤖 Parte 2: Configuración de Azure Bot Service

### Paso 1: Crear Azure Bot

```bash
# Crear App Registration en Azure AD
az ad app create \
  --display-name "Teams OpenAI Bot" \
  --available-to-other-tenants false

# Guardar el Application (client) ID
APP_ID=$(az ad app list --display-name "Teams OpenAI Bot" --query "[0].appId" -o tsv)

# Crear client secret
az ad app credential reset \
  --id $APP_ID \
  --append \
  --years 2

# Crear Azure Bot
az bot create \
  --resource-group rg-openai-teams-bot \
  --name teams-openai-bot \
  --kind registration \
  --sku F0 \
  --appid $APP_ID \
  --endpoint https://tu-bot-app.azurecontainerapps.io/api/messages
```

### Paso 2: Configurar Canal de Teams

```bash
# Habilitar canal de Microsoft Teams
az bot msteams create \
  --resource-group rg-openai-teams-bot \
  --name teams-openai-bot \
  --enable-calling false \
  --calling-web-hook ""
```

### Paso 3: Permisos de API

En el Portal de Azure:
1. Ve a **Azure Active Directory** > **App registrations**
2. Busca "Teams OpenAI Bot"
3. Ve a **API permissions** > **Add a permission**
4. Agrega:
   - Microsoft Graph API:
     - `User.Read` (Delegated)
     - `offline_access` (Delegated)

## 📁 Estructura del Proyecto

```
azure-openai-teams-bot/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Configuración
│   ├── chat_engine.py               # Motor de chat con LangChain
│   └── utils.py                     # Utilidades
├── bot/
│   ├── __init__.py
│   ├── bot_app.py                   # Aplicación principal del bot
│   ├── teams_bot.py                 # Lógica del bot de Teams
│   ├── conversation_manager.py      # Gestión de conversaciones
│   └── cards.py                     # Adaptive Cards para Teams
├── web/
│   └── streamlit_app.py             # Interfaz web opcional
├── tests/
│   ├── test_connection.py
│   └── test_bot.py
├── teams/
│   ├── manifest.json                # Manifest de Teams
│   ├── color.png                    # Icono color
│   └── outline.png                  # Icono outline
├── .env.example
├── .gitignore
├── Dockerfile.bot                   # Dockerfile para el bot
├── Dockerfile.web                   # Dockerfile para web
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 💻 Código de la Aplicación

### 1. requirements.txt

```txt
# Framework web
streamlit==1.30.0
aiohttp==3.9.1

# Bot Framework
botbuilder-core==4.15.0
botbuilder-schema==4.15.0
botbuilder-integration-aiohttp==4.15.0

# LangChain y Azure OpenAI
langchain==0.1.4
langchain-openai==0.0.5
openai==1.10.0

# Utilidades
python-dotenv==1.0.1
requests==2.31.0
pydantic==2.5.3

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3

# Adaptive Cards
adaptivecards==0.1.0
```

### 2. .env.example

```env
# ===========================================
# Azure OpenAI Service Configuration
# ===========================================
AZURE_OPENAI_ENDPOINT=https://openai-teams-service.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-clave-api-aqui
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-teams
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# ===========================================
# Azure Bot Service Configuration
# ===========================================
# Microsoft App ID (Application ID del Bot)
MICROSOFT_APP_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Microsoft App Password (Client Secret del Bot)
MICROSOFT_APP_PASSWORD=tu-client-secret-aqui

# Bot Service Endpoint
BOT_ENDPOINT=https://tu-bot-app.azurecontainerapps.io/api/messages

# ===========================================
# Application Settings
# ===========================================
APP_TITLE=Teams OpenAI Assistant
APP_TEMPERATURE=0.7
APP_MAX_TOKENS=2000
LOG_LEVEL=INFO
SYSTEM_PROMPT=Eres un asistente útil de Microsoft Teams. Respondes de manera clara y profesional.

# ===========================================
# Teams Settings
# ===========================================
TEAMS_APP_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ENABLE_PROACTIVE_MESSAGES=false

# ===========================================
# Server Configuration
# ===========================================
BOT_PORT=3978
WEB_PORT=8501
HOST=0.0.0.0
```

### 3. app/config.py

```python
"""
Configuración centralizada de la aplicación
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AzureOpenAIConfig:
    """Configuración de Azure OpenAI Service"""
    
    ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    TEMPERATURE: float = float(os.getenv("APP_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("APP_MAX_TOKENS", "2000"))
    TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        required_fields = {
            "ENDPOINT": cls.ENDPOINT,
            "API_KEY": cls.API_KEY,
            "DEPLOYMENT_NAME": cls.DEPLOYMENT_NAME
        }
        
        missing_fields = [
            field for field, value in required_fields.items() 
            if not value or value.strip() == ""
        ]
        
        if missing_fields:
            error_msg = (
                f"Azure OpenAI: Faltan configuraciones: {', '.join(missing_fields)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not cls.ENDPOINT.startswith("https://"):
            raise ValueError(f"El endpoint debe comenzar con 'https://'")
        
        logger.info("✅ Configuración de Azure OpenAI validada")
        return True


class BotConfig:
    """Configuración de Azure Bot Service"""
    
    APP_ID: str = os.getenv("MICROSOFT_APP_ID", "")
    APP_PASSWORD: str = os.getenv("MICROSOFT_APP_PASSWORD", "")
    BOT_ENDPOINT: str = os.getenv("BOT_ENDPOINT", "")
    PORT: int = int(os.getenv("BOT_PORT", "3978"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    @classmethod
    def validate(cls) -> bool:
        required_fields = {
            "APP_ID": cls.APP_ID,
            "APP_PASSWORD": cls.APP_PASSWORD
        }
        
        missing_fields = [
            field for field, value in required_fields.items() 
            if not value or value.strip() == ""
        ]
        
        if missing_fields:
            error_msg = (
                f"Bot Service: Faltan configuraciones: {', '.join(missing_fields)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("✅ Configuración de Bot Service validada")
        return True


class AppConfig:
    """Configuración de la aplicación"""
    
    TITLE: str = os.getenv("APP_TITLE", "Teams OpenAI Assistant")
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "Eres un asistente útil de Microsoft Teams. "
        "Respondes de manera clara y profesional."
    )
    ENABLE_PROACTIVE: bool = os.getenv("ENABLE_PROACTIVE_MESSAGES", "false").lower() == "true"
    TEAMS_APP_ID: str = os.getenv("TEAMS_APP_ID", "")
```

### 4. app/chat_engine.py

```python
"""
Motor de chat usando LangChain y Azure OpenAI Service
"""
import logging
from typing import List, Dict, Optional
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from app.config import AzureOpenAIConfig, AppConfig

logger = logging.getLogger(__name__)


class ChatEngine:
    """Motor de chat que gestiona conversaciones con Azure OpenAI Service"""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa el motor de chat
        
        Args:
            session_id: ID de sesión para mantener conversaciones separadas
        """
        AzureOpenAIConfig.validate()
        
        self.session_id = session_id or "default"
        logger.info(f"Inicializando ChatEngine para sesión: {self.session_id}")
        
        # Configurar Azure OpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=AzureOpenAIConfig.ENDPOINT,
            api_key=AzureOpenAIConfig.API_KEY,
            azure_deployment=AzureOpenAIConfig.DEPLOYMENT_NAME,
            api_version=AzureOpenAIConfig.API_VERSION,
            temperature=AzureOpenAIConfig.TEMPERATURE,
            max_tokens=AzureOpenAIConfig.MAX_TOKENS,
            timeout=AzureOpenAIConfig.TIMEOUT,
        )
        
        # Memoria de conversación
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            input_key="input"
        )
        
        # Crear prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(AppConfig.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        # Crear cadena de conversación
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=False
        )
        
        logger.info(f"✅ ChatEngine inicializado para sesión: {self.session_id}")
    
    async def send_message_async(self, message: str) -> str:
        """
        Envía un mensaje de forma asíncrona
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Respuesta del asistente
        """
        try:
            logger.info(f"[{self.session_id}] Mensaje recibido: {message[:50]}...")
            
            response = await self.conversation.apredict(input=message)
            
            logger.info(f"[{self.session_id}] Respuesta generada: {response[:50]}...")
            
            return response
            
        except Exception as e:
            error_msg = f"Error al procesar mensaje: {str(e)}"
            logger.error(f"[{self.session_id}] {error_msg}")
            return f"Lo siento, ocurrió un error al procesar tu mensaje. Por favor, intenta de nuevo."
    
    def send_message(self, message: str) -> str:
        """
        Envía un mensaje de forma síncrona
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Respuesta del asistente
        """
        try:
            logger.info(f"[{self.session_id}] Procesando mensaje...")
            response = self.conversation.predict(input=message)
            return response
        except Exception as e:
            logger.error(f"[{self.session_id}] Error: {str(e)}")
            return "Lo siento, ocurrió un error al procesar tu mensaje."
    
    def clear_history(self) -> None:
        """Limpia el historial de conversación"""
        logger.info(f"[{self.session_id}] Limpiando historial")
        self.memory.clear()
    
    def get_history(self) -> List[Dict[str, str]]:
        """Obtiene el historial de conversación"""
        messages = self.memory.chat_memory.messages
        return [
            {
                "role": msg.type,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def get_message_count(self) -> int:
        """Cuenta mensajes en el historial"""
        return len(self.memory.chat_memory.messages)
```

### 5. bot/teams_bot.py

```python
"""
Bot de Microsoft Teams usando Bot Framework SDK
"""
import logging
from typing import List
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    CardFactory,
    MessageFactory
)
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    ChannelAccount,
    Attachment,
    HeroCard,
    CardAction,
    ActionTypes
)

from app.chat_engine import ChatEngine
from bot.conversation_manager import ConversationManager
from bot.cards import AdaptiveCards

logger = logging.getLogger(__name__)


class TeamsBot(ActivityHandler):
    """
    Bot de Microsoft Teams con integración de Azure OpenAI
    """
    
    def __init__(self):
        """Inicializa el bot"""
        super().__init__()
        self.conversation_manager = ConversationManager()
        logger.info("✅ TeamsBot inicializado")
    
    async def on_message_activity(self, turn_context: TurnContext):
        """
        Maneja mensajes entrantes
        
        Args:
            turn_context: Contexto de la conversación
        """
        try:
            # Obtener información del usuario y conversación
            user_id = turn_context.activity.from_property.id
            conversation_id = turn_context.activity.conversation.id
            user_message = turn_context.activity.text
            
            logger.info(f"Mensaje de {user_id} en {conversation_id}: {user_message[:50]}...")
            
            # Comandos especiales
            if user_message.lower().startswith("/"):
                await self._handle_command(turn_context, user_message.lower())
                return
            
            # Obtener o crear engine de chat para esta conversación
            chat_engine = self.conversation_manager.get_or_create_engine(conversation_id)
            
            # Mostrar indicador de escritura
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )
            
            # Obtener respuesta del modelo
            response = await chat_engine.send_message_async(user_message)
            
            # Enviar respuesta
            await turn_context.send_activity(
                MessageFactory.text(response)
            )
            
            logger.info(f"Respuesta enviada a {user_id}")
            
        except Exception as e:
            logger.error(f"Error en on_message_activity: {e}")
            await turn_context.send_activity(
                "Lo siento, ocurrió un error al procesar tu mensaje. "
                "Por favor, intenta de nuevo."
            )
    
    async def on_members_added_activity(
        self, 
        members_added: List[ChannelAccount], 
        turn_context: TurnContext
    ):
        """
        Maneja cuando se agregan miembros a la conversación
        
        Args:
            members_added: Lista de miembros agregados
            turn_context: Contexto de la conversación
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                # Enviar mensaje de bienvenida
                welcome_card = AdaptiveCards.create_welcome_card()
                message = MessageFactory.attachment(welcome_card)
                await turn_context.send_activity(message)
    
    async def _handle_command(self, turn_context: TurnContext, command: str):
        """
        Maneja comandos especiales del bot
        
        Args:
            turn_context: Contexto de la conversación
            command: Comando a ejecutar
        """
        conversation_id = turn_context.activity.conversation.id
        
        if command == "/help":
            help_card = AdaptiveCards.create_help_card()
            await turn_context.send_activity(
                MessageFactory.attachment(help_card)
            )
        
        elif command == "/clear" or command == "/reset":
            # Limpiar historial de conversación
            chat_engine = self.conversation_manager.get_or_create_engine(conversation_id)
            chat_engine.clear_history()
            
            await turn_context.send_activity(
                "✅ Historial de conversación limpiado. "
                "Podemos empezar una nueva conversación."
            )
        
        elif command == "/stats":
            # Mostrar estadísticas
            chat_engine = self.conversation_manager.get_or_create_engine(conversation_id)
            message_count = chat_engine.get_message_count()
            
            stats_card = AdaptiveCards.create_stats_card(message_count)
            await turn_context.send_activity(
                MessageFactory.attachment(stats_card)
            )
        
        elif command == "/about":
            about_card = AdaptiveCards.create_about_card()
            await turn_context.send_activity(
                MessageFactory.attachment(about_card)
            )
        
        else:
            await turn_context.send_activity(
                f"Comando desconocido: {command}\n"
                "Usa /help para ver los comandos disponibles."
            )
    
    async def on_conversation_update_activity(self, turn_context: TurnContext):
        """
        Maneja actualizaciones de conversación
        
        Args:
            turn_context: Contexto de la conversación
        """
        # Llamar al handler base
        await super().on_conversation_update_activity(turn_context)
    
    async def on_teams_members_added(
        self,
        members_added: List[ChannelAccount],
        team_info: any,
        turn_context: TurnContext
    ):
        """
        Maneja cuando se agregan miembros a un team
        
        Args:
            members_added: Lista de miembros agregados
            team_info: Información del team
            turn_context: Contexto de la conversación
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"¡Bienvenido al team, {member.name}! 👋\n"
                    "Soy tu asistente de IA. Escribe /help para ver qué puedo hacer."
                )
```

### 6. bot/conversation_manager.py

```python
"""
Gestor de conversaciones para múltiples usuarios/canales
"""
import logging
from typing import Dict
from app.chat_engine import ChatEngine

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Gestiona múltiples instancias de chat engines para diferentes conversaciones
    """
    
    def __init__(self):
        """Inicializa el gestor de conversaciones"""
        self.engines: Dict[str, ChatEngine] = {}
        logger.info("ConversationManager inicializado")
    
    def get_or_create_engine(self, conversation_id: str) -> ChatEngine:
        """
        Obtiene o crea un engine de chat para una conversación
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            ChatEngine para la conversación
        """
        if conversation_id not in self.engines:
            logger.info(f"Creando nuevo ChatEngine para conversación: {conversation_id}")
            self.engines[conversation_id] = ChatEngine(session_id=conversation_id)
        
        return self.engines[conversation_id]
    
    def remove_engine(self, conversation_id: str) -> bool:
        """
        Elimina un engine de chat
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            True si se eliminó, False si no existía
        """
        if conversation_id in self.engines:
            logger.info(f"Eliminando ChatEngine para conversación: {conversation_id}")
            del self.engines[conversation_id]
            return True
        return False
    
    def get_active_conversations_count(self) -> int:
        """
        Obtiene el número de conversaciones activas
        
        Returns:
            Número de conversaciones
        """
        return len(self.engines)
    
    def clear_all(self):
        """Limpia todas las conversaciones"""
        logger.info("Limpiando todas las conversaciones")
        self.engines.clear()
```

### 7. bot/cards.py

```python
"""
Adaptive Cards para Microsoft Teams
"""
from botbuilder.schema import Attachment
from botbuilder.core import CardFactory


class AdaptiveCards:
    """Generador de Adaptive Cards para Teams"""
    
    @staticmethod
    def create_welcome_card() -> Attachment:
        """Crea una tarjeta de bienvenida"""
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "👋 ¡Hola! Soy tu Asistente de IA",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Accent"
                },
                {
                    "type": "TextBlock",
                    "text": "Estoy potenciado por Azure OpenAI y puedo ayudarte con:",
                    "wrap": True,
                    "spacing": "Medium"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "💬",
                            "value": "Responder preguntas"
                        },
                        {
                            "title": "📝",
                            "value": "Redactar documentos"
                        },
                        {
                            "title": "💡",
                            "value": "Generar ideas"
                        },
                        {
                            "title": "🔍",
                            "value": "Analizar información"
                        },
                        {
                            "title": "💻",
                            "value": "Ayudar con código"
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "**Comandos disponibles:**",
                    "weight": "Bolder",
                    "spacing": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "• /help - Ver ayuda\n• /clear - Limpiar conversación\n• /stats - Ver estadísticas\n• /about - Información del bot",
                    "wrap": True,
                    "spacing": "Small"
                },
                {
                    "type": "TextBlock",
                    "text": "¡Escribe un mensaje para comenzar! 🚀",
                    "wrap": True,
                    "spacing": "Medium",
                    "color": "Good"
                }
            ]
        }
        return CardFactory.adaptive_card(card)
    
    @staticmethod
    def create_help_card() -> Attachment:
        """Crea una tarjeta de ayuda"""
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "📚 Centro de Ayuda",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Accent"
                },
                {
                    "type": "TextBlock",
                    "text": "**Comandos Disponibles:**",
                    "weight": "Bolder",
                    "spacing": "Medium"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "/help",
                            "value": "Muestra esta ayuda"
                        },
                        {
                            "title": "/clear",
                            "value": "Limpia el historial de conversación"
                        },
                        {
                            "title": "/stats",
                            "value": "Muestra estadísticas de la conversación"
                        },
                        {
                            "title": "/about",
                            "value": "Información sobre el bot"
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "**Cómo usar el bot:**",
                    "weight": "Bolder",
                    "spacing": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "1. Simplemente escribe tu pregunta o solicitud\n2. El bot mantiene el contexto de la conversación\n3. Usa /clear si quieres empezar una nueva conversación\n4. Puedes hacer preguntas en cualquier idioma",
                    "wrap": True,
                    "spacing": "Small"
                }
            ]
        }
        return CardFactory.adaptive_card(card)
    
    @staticmethod
    def create_stats_card(message_count: int) -> Attachment:
        """Crea una tarjeta de estadísticas"""
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "📊 Estadísticas de la Conversación",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Accent"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Mensajes en conversación:",
                            "value": str(message_count)
                        },
                        {
                            "title": "Estado:",
                            "value": "✅ Activa"
                        },
                        {
                            "title": "Modelo:",
                            "value": "Azure OpenAI (GPT-4)"
                        }
                    ]
                }
            ]
        }
        return CardFactory.adaptive_card(card)
    
    @staticmethod
    def create_about_card() -> Attachment:
        """Crea una tarjeta con información del bot"""
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "ℹ️ Acerca del Bot",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Accent"
                },
                {
                    "type": "TextBlock",
                    "text": "**Teams OpenAI Assistant**",
                    "weight": "Bolder",
                    "spacing": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "Un asistente de IA inteligente para Microsoft Teams, potenciado por Azure OpenAI Service y LangChain.",
                    "wrap": True,
                    "spacing": "Small"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "Versión:",
                            "value": "1.0.0"
                        },
                        {
                            "title": "Tecnologías:",
                            "value": "Azure OpenAI, Bot Framework, LangChain"
                        },
                        {
                            "title": "Funcionalidades:",
                            "value": "Chat conversacional con contexto"
                        }
                    ],
                    "spacing": "Medium"
                }
            ]
        }
        return CardFactory.adaptive_card(card)
```

### 8. bot/bot_app.py

```python
"""
Aplicación principal del bot usando aiohttp
"""
import sys
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    TurnContext,
)
from botbuilder.schema import Activity

from app.config import BotConfig, AzureOpenAIConfig
from bot.teams_bot import TeamsBot

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validar configuraciones
try:
    BotConfig.validate()
    AzureOpenAIConfig.validate()
except ValueError as e:
    logger.error(f"Error de configuración: {e}")
    sys.exit(1)

# Configurar Bot Framework Adapter
SETTINGS = BotFrameworkAdapterSettings(
    app_id=BotConfig.APP_ID,
    app_password=BotConfig.APP_PASSWORD
)
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Manejador de errores del adapter
async def on_error(context: TurnContext, error: Exception):
    """
    Maneja errores del bot
    
    Args:
        context: Contexto del turno
        error: Error ocurrido
    """
    logger.error(f"Error en el bot: {error}", exc_info=True)
    
    await context.send_activity(
        "Lo siento, ocurrió un error. Por favor, intenta de nuevo más tarde."
    )


ADAPTER.on_turn_error = on_error

# Crear instancia del bot
BOT = TeamsBot()


# Endpoint para mensajes del bot
async def messages(req: Request) -> Response:
    """
    Endpoint principal que recibe mensajes de Bot Framework
    
    Args:
        req: Request HTTP
        
    Returns:
        Response HTTP
    """
    if req.content_type == "application/json":
        body = await req.json()
    else:
        return Response(status=415)  # Unsupported Media Type
    
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    
    try:
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            return web.json_response(data=response.body, status=response.status)
        return Response(status=201)
    except Exception as e:
        logger.error(f"Error procesando actividad: {e}")
        return Response(status=500)


# Endpoint de health check
async def health(req: Request) -> Response:
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "teams-openai-bot"
    })


# Crear aplicación web
APP = web.Application()
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/health", health)
APP.router.add_get("/", health)


if __name__ == "__main__":
    try:
        logger.info("="*60)
        logger.info("🤖 Iniciando Teams OpenAI Bot")
        logger.info("="*60)
        logger.info(f"Puerto: {BotConfig.PORT}")
        logger.info(f"Host: {BotConfig.HOST}")
        logger.info(f"Bot ID: {BotConfig.APP_ID}")
        logger.info("="*60)
        
        web.run_app(
            APP,
            host=BotConfig.HOST,
            port=BotConfig.PORT
        )
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
        sys.exit(1)
```

### 9. teams/manifest.json

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
  "manifestVersion": "1.16",
  "version": "1.0.0",
  "id": "REEMPLAZAR-CON-TU-TEAMS-APP-ID",
  "packageName": "com.azure.openai.teamsbot",
  "developer": {
    "name": "Tu Organización",
    "websiteUrl": "https://www.tuorganizacion.com",
    "privacyUrl": "https://www.tuorganizacion.com/privacy",
    "termsOfUseUrl": "https://www.tuorganizacion.com/terms"
  },
  "icons": {
    "color": "color.png",
    "outline": "outline.png"
  },
  "name": {
    "short": "AI Assistant",
    "full": "Azure OpenAI Teams Assistant"
  },
  "description": {
    "short": "Asistente de IA para Teams",
    "full": "Asistente de inteligencia artificial potenciado por Azure OpenAI Service para ayudarte en tus tareas diarias en Microsoft Teams."
  },
  "accentColor": "#0078D4",
  "bots": [
    {
      "botId": "REEMPLAZAR-CON-TU-BOT-APP-ID",
      "scopes": [
        "personal",
        "team",
        "groupchat"
      ],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": [
            "personal",
            "team",
            "groupchat"
          ],
          "commands": [
            {
              "title": "help",
              "description": "Muestra información de ayuda"
            },
            {
              "title": "clear",
              "description": "Limpia el historial de conversación"
            },
            {
              "title": "stats",
              "description": "Muestra estadísticas de la conversación"
            },
            {
              "title": "about",
              "description": "Información sobre el bot"
            }
          ]
        }
      ]
    }
  ],
  "permissions": [
    "identity",
    "messageTeamMembers"
  ],
  "validDomains": []
}
```

## 🐳 Dockerización

### 1. Dockerfile.bot

```dockerfile
# Multi-stage build para el bot
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas
COPY --from=builder /root/.local /root/.local

# Copiar código
COPY app/ ./app/
COPY bot/ ./bot/

# Actualizar PATH
ENV PATH=/root/.local/bin:$PATH

# Crear usuario no-root
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Exponer puerto del bot
EXPOSE 3978

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3978/health || exit 1

# Comando de inicio
CMD ["python", "bot/bot_app.py"]
```

### 2. Dockerfile.web

```dockerfile
# Dockerfile para interfaz web Streamlit (opcional)
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app/ ./app/
COPY web/ ./web/

# Variables de entorno para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Exponer puerto
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "web/streamlit_app.py"]
```

### 3. docker-compose.yml

```yaml
version: '3.8'

services:
  # ============================================
  # Bot de Teams
  # ============================================
  teams-bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    container_name: azure-openai-teams-bot
    ports:
      - "3978:3978"
    environment:
      # Azure OpenAI
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME}
      - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
      
      # Bot Service
      - MICROSOFT_APP_ID=${MICROSOFT_APP_ID}
      - MICROSOFT_APP_PASSWORD=${MICROSOFT_APP_PASSWORD}
      - BOT_PORT=3978
      - HOST=0.0.0.0
      
      # App Settings
      - APP_TEMPERATURE=${APP_TEMPERATURE:-0.7}
      - APP_MAX_TOKENS=${APP_MAX_TOKENS:-2000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - SYSTEM_PROMPT=${SYSTEM_PROMPT}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3978/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - bot-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ============================================
  # Interfaz Web (Opcional)
  # ============================================
  web-app:
    build:
      context: .
      dockerfile: Dockerfile.web
    container_name: azure-openai-web
    ports:
      - "8501:8501"
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME}
      - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
      - APP_TITLE=${APP_TITLE}
    restart: unless-stopped
    networks:
      - bot-network
    profiles:
      - web  # Solo se inicia si se especifica el perfil 'web'

networks:
  bot-network:
    driver: bridge
```

## 🚀 Instalación y Despliegue

### Paso 1: Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/azure-openai-teams-bot.git
cd azure-openai-teams-bot

# Crear archivo .env
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

### Paso 2: Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar bot localmente
python bot/bot_app.py
```

### Paso 3: Usar ngrok para Testing Local

```bash
# Instalar ngrok
# https://ngrok.com/download

# Ejecutar ngrok
ngrok http 3978

# Copiar la URL HTTPS generada (ej: https://abc123.ngrok.io)
# Actualizar el endpoint en Azure Bot Service:
# https://abc123.ngrok.io/api/messages
```

### Paso 4: Ejecutar con Docker

```bash
# Solo bot
docker-compose up -d teams-bot

# Bot + Web
docker-compose --profile web up -d

# Ver logs
docker-compose logs -f teams-bot
```

## 🚀 Despliegue en Azure

### Opción 1: Azure Container Apps

```bash
# Variables
RESOURCE_GROUP="rg-openai-teams-bot"
LOCATION="eastus"
ACR_NAME="myopenairegistry"
BOT_APP_NAME="teams-openai-bot"

# Crear Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic

# Login al registry
az acr login --name $ACR_NAME

# Build y push imagen del bot
az acr build \
  --registry $ACR_NAME \
  --image teams-bot:latest \
  --file Dockerfile.bot .

# Crear Container Apps Environment
az containerapp env create \
  --name teams-bot-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Desplegar bot
az containerapp create \
  --name $BOT_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment teams-bot-env \
  --image $ACR_NAME.azurecr.io/teams-bot:latest \
  --target-port 3978 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --min-replicas 1 \
  --max-replicas 3 \
  --secrets \
    azure-openai-key=$AZURE_OPENAI_API_KEY \
    bot-password=$MICROSOFT_APP_PASSWORD \
  --env-vars \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_API_KEY=secretref:azure-openai-key \
    AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME \
    MICROSOFT_APP_ID=$MICROSOFT_APP_ID \
    MICROSOFT_APP_PASSWORD=secretref:bot-password

# Obtener URL del bot
BOT_URL=$(az containerapp show \
  --name $BOT_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo "Bot URL: https://$BOT_URL/api/messages"
```

### Opción 2: Azure App Service

```bash
# Crear App Service Plan
az appservice plan create \
  --name bot-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Crear Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan bot-plan \
  --name $BOT_APP_NAME \
  --deployment-container-image-name $ACR_NAME.azurecr.io/teams-bot:latest

# Configurar variables de entorno
az webapp config appsettings set \
  --name $BOT_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
    AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME \
    MICROSOFT_APP_ID=$MICROSOFT_APP_ID \
    MICROSOFT_APP_PASSWORD=$MICROSOFT_APP_PASSWORD
```

### Paso Final: Actualizar Bot Endpoint

```bash
# Actualizar endpoint del bot en Azure
az bot update \
  --resource-group $RESOURCE_GROUP \
  --name teams-openai-bot \
  --endpoint "https://$BOT_URL/api/messages"
```

## 📱 Configurar Teams App

### Paso 1: Preparar el Manifest

1. Editar `teams/manifest.json`:
   ```json
   {
     "id": "TU-TEAMS-APP-ID-AQUI",
     "bots": [
       {
         "botId": "TU-MICROSOFT-APP-ID-AQUI"
       }
     ]
   }
   ```

2. Agregar iconos:
   - `color.png` (192x192 px)
   - `outline.png` (32x32 px)

### Paso 2: Crear Package de Teams

```bash
# Crear ZIP del manifest
cd teams
zip -r teams-app.zip manifest.json color.png outline.png
cd ..
```

### Paso 3: Instalar en Teams

1. Abrir Microsoft Teams
2. Ir a **Apps** en la barra lateral
3. Clic en **Manage your apps**
4. Clic en **Upload an app** > **Upload a custom app**
5. Seleccionar `teams-app.zip`
6. Clic en **Add** para agregar el bot

### Paso 4: Probar el Bot

1. Busca tu bot en Teams
2. Inicia una conversación
3. Escribe "Hola" para probar
4. Usa `/help` para ver comandos

## 🧪 Testing

### Test de Conexión Azure OpenAI

```bash
python tests/test_connection.py
```

### Test Manual del Bot

```bash
# Terminal 1: Iniciar bot
python bot/bot_app.py

# Terminal 2: Enviar request de prueba
curl -X POST http://localhost:3978/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "text": "Hola",
    "from": {
      "id": "test-user"
    },
    "conversation": {
      "id": "test-conversation"
    }
  }'
```

## 🔧 Solución de Problemas

### Bot no responde en Teams

1. Verificar endpoint en Azure Bot Service
2. Verificar que el bot esté ejecutándose
3. Revisar logs del bot:
   ```bash
   docker-compose logs -f teams-bot
   ```

### Error de Autenticación

```bash
# Verificar credenciales del bot
az bot show \
  --resource-group rg-openai-teams-bot \
  --name teams-openai-bot

# Regenerar password si es necesario
az ad app credential reset --id $MICROSOFT_APP_ID
```

### Error "401 Unauthorized"

- Verificar MICROSOFT_APP_ID y MICROSOFT_APP_PASSWORD
- Verificar que el endpoint del bot esté actualizado
- Verificar que el bot tenga los permisos correctos

### Conversaciones no mantienen contexto

- Verificar que ConversationManager esté funcionando
- Revisar logs para errores de memoria
- Verificar que conversation_id sea consistente

## 📚 Recursos Adicionales

- [Bot Framework Documentation](https://docs.microsoft.com/bot-framework/)
- [Teams App Development](https://docs.microsoft.com/microsoftteams/platform/)
- [Azure Bot Service](https://azure.microsoft.com/services/bot-services/)
- [Adaptive Cards](https://adaptivecards.io/)

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

<div align="center">

**⭐ ¡Dale una estrella si este proyecto te ayudó! ⭐**

Desarrollado con ❤️ usando Azure OpenAI + Teams

</div>
