# ExampleAppAOAI
ExampleAppAOAI


# Chat Application con Azure OpenAI Service, LangChain y Docker

## 📋 Descripción

Esta guía proporciona un ejemplo completo de cómo crear una aplicación de chat usando **Azure OpenAI Service**, LangChain y Python, containerizada con Docker para facilitar el despliegue y escalabilidad.

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Usuario       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Streamlit UI  │
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LangChain     │
│   (Orquestador) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Azure OpenAI    │
│    Service      │
│  (GPT-4/3.5)    │
└─────────────────┘
```

## 📦 Prerrequisitos

- Cuenta de Azure activa con suscripción
- Azure CLI instalado (opcional pero recomendado)
- Python 3.9 o superior
- Docker y Docker Compose
- Git
- Visual Studio Code (recomendado)

## 🚀 Configuración de Azure OpenAI Service

### Paso 1: Crear el Recurso de Azure OpenAI

#### Opción A: Usando el Portal de Azure

1. Inicia sesión en [Azure Portal](https://portal.azure.com)
2. Haz clic en **"Crear un recurso"**
3. Busca **"Azure OpenAI"**
4. Haz clic en **"Crear"**
5. Completa el formulario:
   ```
   Suscripción: Selecciona tu suscripción de Azure
   Grupo de recursos: Crea uno nuevo (ej: rg-openai-chat)
   Región: East US, West Europe, o France Central
   Nombre: openai-chat-service (debe ser único)
   Plan de precios: Standard S0
   ```
6. Haz clic en **"Revisar y crear"** y luego **"Crear"**
7. Espera a que el despliegue se complete (2-3 minutos)

#### Opción B: Usando Azure CLI

```bash
# Login a Azure
az login

# Crear grupo de recursos
az group create \
  --name rg-openai-chat \
  --location eastus

# Crear servicio de Azure OpenAI
az cognitiveservices account create \
  --name openai-chat-service \
  --resource-group rg-openai-chat \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes
```

### Paso 2: Desplegar Modelos

1. Una vez creado el recurso, ve a **Azure OpenAI Studio**:
   - URL: `https://oai.azure.com`
   - O desde el portal: Tu recurso > **"Go to Azure OpenAI Studio"**

2. En Azure OpenAI Studio:
   - Navega a **"Deployments"** en el menú izquierdo
   - Haz clic en **"Create new deployment"**

3. Configurar el deployment de GPT-4:
   ```
   Select a model: gpt-4 o gpt-4-32k
   Deployment name: gpt-4-chat
   Model version: Última disponible
   Deployment type: Standard
   Tokens per minute rate limit: 10K (ajusta según necesites)
   ```
   Haz clic en **"Create"**

4. (Opcional) Crear un deployment adicional de GPT-3.5:
   ```
   Select a model: gpt-35-turbo
   Deployment name: gpt-35-chat
   Model version: Última disponible
   Tokens per minute rate limit: 120K
   ```

### Paso 3: Obtener Credenciales de Acceso

1. En el Portal de Azure, ve a tu recurso de Azure OpenAI
2. En el menú izquierdo, selecciona **"Keys and Endpoint"**
3. Copia la siguiente información:

   ```
   KEY 1: ********************************
   Endpoint: https://openai-chat-service.openai.azure.com/
   Location: eastus
   ```

4. También necesitarás el nombre del deployment que creaste (ej: `gpt-4-chat`)

## 📁 Estructura del Proyecto

```
azure-openai-chat/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación Streamlit principal
│   ├── chat_engine.py          # Motor de chat con LangChain
│   ├── config.py               # Configuración y validaciones
│   └── utils.py                # Utilidades auxiliares
├── tests/
│   ├── __init__.py
│   └── test_connection.py      # Tests de conexión
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore                   # Archivos a ignorar en Git
├── Dockerfile                   # Configuración del contenedor
├── docker-compose.yml           # Orquestación de contenedores
├── requirements.txt             # Dependencias de Python
├── LICENSE                      # Licencia del proyecto
└── README.md                    # Este archivo
```

## 💻 Código de la Aplicación

### 1. requirements.txt

```txt
# Framework web
streamlit==1.30.0

# LangChain y Azure OpenAI
langchain==0.1.4
langchain-openai==0.0.5
openai==1.10.0

# Utilidades
python-dotenv==1.0.1
requests==2.31.0

# Para testing (opcional)
pytest==7.4.4
pytest-asyncio==0.23.3
```

### 2. .env.example

```env
# ===========================================
# Azure OpenAI Service Configuration
# ===========================================

# Endpoint de tu servicio de Azure OpenAI
# Ejemplo: https://tu-servicio.openai.azure.com/
AZURE_OPENAI_ENDPOINT=https://openai-chat-service.openai.azure.com/

# API Key (Key 1 o Key 2 desde Azure Portal)
AZURE_OPENAI_API_KEY=tu-clave-api-aqui

# Nombre del deployment del modelo
# Este debe coincidir exactamente con el nombre en Azure OpenAI Studio
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-chat

# Versión de la API de Azure OpenAI
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# ===========================================
# Application Settings
# ===========================================

# Título de la aplicación
APP_TITLE=Chat con Azure OpenAI

# Temperatura del modelo (0.0 - 2.0)
# Valores más bajos = respuestas más deterministas
# Valores más altos = respuestas más creativas
APP_TEMPERATURE=0.7

# Máximo de tokens en la respuesta
APP_MAX_TOKENS=2000

# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ===========================================
# Optional: Advanced Settings
# ===========================================

# System prompt personalizado
SYSTEM_PROMPT=Eres un asistente útil, amigable y profesional. Respondes de manera clara y concisa.

# Habilitar modo streaming
ENABLE_STREAMING=true

# Timeout para requests (en segundos)
REQUEST_TIMEOUT=30
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

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AzureOpenAIConfig:
    """Configuración de Azure OpenAI Service"""
    
    # Credenciales de Azure OpenAI
    ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Parámetros del modelo
    TEMPERATURE: float = float(os.getenv("APP_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("APP_MAX_TOKENS", "2000"))
    
    # Configuración de request
    TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida que todas las configuraciones requeridas estén presentes
        
        Returns:
            bool: True si la configuración es válida
            
        Raises:
            ValueError: Si falta alguna configuración requerida
        """
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
                f"Configuración incompleta. Faltan las siguientes variables: "
                f"{', '.join(missing_fields)}. "
                f"Por favor, revisa tu archivo .env"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validar formato del endpoint
        if not cls.ENDPOINT.startswith("https://"):
            raise ValueError(
                f"El endpoint debe comenzar con 'https://'. "
                f"Valor actual: {cls.ENDPOINT}"
            )
        
        # Validar rangos de parámetros
        if not 0 <= cls.TEMPERATURE <= 2:
            raise ValueError(
                f"La temperatura debe estar entre 0 y 2. "
                f"Valor actual: {cls.TEMPERATURE}"
            )
        
        if cls.MAX_TOKENS < 1:
            raise ValueError(
                f"MAX_TOKENS debe ser mayor a 0. "
                f"Valor actual: {cls.MAX_TOKENS}"
            )
        
        logger.info("✅ Configuración de Azure OpenAI validada correctamente")
        return True
    
    @classmethod
    def get_info(cls) -> dict:
        """Retorna información de configuración (sin datos sensibles)"""
        return {
            "endpoint": cls.ENDPOINT,
            "deployment": cls.DEPLOYMENT_NAME,
            "api_version": cls.API_VERSION,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "timeout": cls.TIMEOUT
        }


class AppConfig:
    """Configuración de la aplicación"""
    
    TITLE: str = os.getenv("APP_TITLE", "Chat con Azure OpenAI")
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "Eres un asistente útil, amigable y profesional. "
        "Respondes de manera clara y concisa."
    )
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
    
    @classmethod
    def get_info(cls) -> dict:
        """Retorna información de configuración de la app"""
        return {
            "title": cls.TITLE,
            "streaming_enabled": cls.ENABLE_STREAMING
        }
```

### 4. app/utils.py

```python
"""
Utilidades auxiliares para la aplicación
"""
import time
from typing import Generator
from datetime import datetime


def format_message_timestamp(timestamp: datetime = None) -> str:
    """
    Formatea un timestamp para mostrar en mensajes
    
    Args:
        timestamp: Timestamp a formatear, None para usar tiempo actual
        
    Returns:
        String formateado
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%H:%M:%S")


def typing_effect(text: str, delay: float = 0.03) -> Generator[str, None, None]:
    """
    Genera efecto de escritura carácter por carácter
    
    Args:
        text: Texto a mostrar
        delay: Delay entre caracteres
        
    Yields:
        Caracteres del texto
    """
    for char in text:
        yield char
        time.sleep(delay)


def estimate_tokens(text: str) -> int:
    """
    Estima el número de tokens en un texto
    Aproximación: 1 token ≈ 4 caracteres para español/inglés
    
    Args:
        text: Texto a estimar
        
    Returns:
        Número estimado de tokens
    """
    return len(text) // 4


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
```

### 5. app/chat_engine.py

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
from langchain.schema import BaseMessage

from app.config import AzureOpenAIConfig, AppConfig

logger = logging.getLogger(__name__)


class ChatEngine:
    """
    Motor de chat que gestiona conversaciones con Azure OpenAI Service
    """
    
    def __init__(self):
        """Inicializa el motor de chat"""
        
        # Validar configuración
        AzureOpenAIConfig.validate()
        
        logger.info("Inicializando ChatEngine con Azure OpenAI Service...")
        
        # Configurar el cliente de Azure OpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=AzureOpenAIConfig.ENDPOINT,
            api_key=AzureOpenAIConfig.API_KEY,
            azure_deployment=AzureOpenAIConfig.DEPLOYMENT_NAME,
            api_version=AzureOpenAIConfig.API_VERSION,
            temperature=AzureOpenAIConfig.TEMPERATURE,
            max_tokens=AzureOpenAIConfig.MAX_TOKENS,
            timeout=AzureOpenAIConfig.TIMEOUT,
            streaming=AppConfig.ENABLE_STREAMING
        )
        
        # Configurar memoria de conversación
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            input_key="input"
        )
        
        # Crear el prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(AppConfig.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        # Crear la cadena de conversación
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=False
        )
        
        logger.info("✅ ChatEngine inicializado correctamente")
    
    def send_message(self, message: str) -> str:
        """
        Envía un mensaje y obtiene la respuesta del modelo
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Respuesta del asistente
            
        Raises:
            Exception: Si hay un error en la comunicación con Azure OpenAI
        """
        try:
            logger.info(f"Enviando mensaje al modelo: {message[:50]}...")
            
            response = self.conversation.predict(input=message)
            
            logger.info(f"Respuesta recibida: {response[:50]}...")
            
            return response
            
        except Exception as e:
            error_msg = f"Error al procesar el mensaje: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def send_message_stream(self, message: str):
        """
        Envía un mensaje y obtiene la respuesta en modo streaming
        
        Args:
            message: Mensaje del usuario
            
        Yields:
            Fragmentos de la respuesta
        """
        try:
            logger.info(f"Enviando mensaje en modo streaming: {message[:50]}...")
            
            for chunk in self.conversation.stream({"input": message}):
                if "response" in chunk:
                    yield chunk["response"]
                    
        except Exception as e:
            error_msg = f"Error en streaming: {str(e)}"
            logger.error(error_msg)
            yield f"[Error: {error_msg}]"
    
    def clear_history(self) -> None:
        """Limpia el historial de conversación"""
        logger.info("Limpiando historial de conversación")
        self.memory.clear()
    
    def get_history(self) -> List[BaseMessage]:
        """
        Obtiene el historial de conversación
        
        Returns:
            Lista de mensajes del historial
        """
        return self.memory.chat_memory.messages
    
    def get_history_dict(self) -> List[Dict[str, str]]:
        """
        Obtiene el historial en formato de diccionario
        
        Returns:
            Lista de diccionarios con el historial
        """
        messages = self.get_history()
        return [
            {
                "role": msg.type,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def count_messages(self) -> int:
        """
        Cuenta el número de mensajes en el historial
        
        Returns:
            Número de mensajes
        """
        return len(self.memory.chat_memory.messages)
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Obtiene información sobre el modelo configurado
        
        Returns:
            Diccionario con información del modelo
        """
        return {
            "deployment": AzureOpenAIConfig.DEPLOYMENT_NAME,
            "temperature": AzureOpenAIConfig.TEMPERATURE,
            "max_tokens": AzureOpenAIConfig.MAX_TOKENS,
            "api_version": AzureOpenAIConfig.API_VERSION,
            "messages_in_history": self.count_messages()
        }
```

### 6. app/main.py

```python
"""
Aplicación principal de Streamlit para Chat con Azure OpenAI Service
"""
import streamlit as st
import logging
from datetime import datetime

from app.chat_engine import ChatEngine
from app.config import AzureOpenAIConfig, AppConfig
from app.utils import format_message_timestamp, estimate_tokens

logger = logging.getLogger(__name__)

# Configuración de la página
st.set_page_config(
    page_title=AppConfig.TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-container {
        background-color: #e8f4f8;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
    }
    .stChatMessage {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa el estado de la sesión de Streamlit"""
    
    # Inicializar el motor de chat
    if "chat_engine" not in st.session_state:
        try:
            with st.spinner("Conectando con Azure OpenAI Service..."):
                st.session_state.chat_engine = ChatEngine()
                logger.info("Motor de chat inicializado en session_state")
        except ValueError as e:
            st.error(f"❌ Error de configuración: {e}")
            st.info("👉 Por favor, verifica tu archivo .env y asegúrate de que todas las variables estén configuradas correctamente.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error al conectar con Azure OpenAI: {e}")
            st.stop()
    
    # Inicializar lista de mensajes
    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.info("Lista de mensajes inicializada")
    
    # Contador de mensajes
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0


def display_sidebar():
    """Muestra la barra lateral con información y controles"""
    
    with st.sidebar:
        st.markdown("### 🤖 Azure OpenAI Chat")
        st.markdown("---")
        
        # Información del servicio
        st.markdown("#### ℹ️ Información del Servicio")
        model_info = st.session_state.chat_engine.get_model_info()
        
        st.markdown(f"""
        <div class="info-box">
            <b>Deployment:</b> {model_info['deployment']}<br>
            <b>Temperatura:</b> {model_info['temperature']}<br>
            <b>Max Tokens:</b> {model_info['max_tokens']}<br>
            <b>API Version:</b> {model_info['api_version']}
        </div>
        """, unsafe_allow_html=True)
        
        # Estadísticas de la sesión
        st.markdown("#### 📊 Estadísticas de Sesión")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Mensajes",
                st.session_state.message_count
            )
        
        with col2:
            total_tokens = sum(
                estimate_tokens(msg["content"]) 
                for msg in st.session_state.messages
            )
            st.metric(
                "Tokens ~",
                f"{total_tokens:,}"
            )
        
        st.markdown("---")
        
        # Controles
        st.markdown("#### ⚙️ Controles")
        
        if st.button("🗑️ Limpiar Conversación", use_container_width=True, type="primary"):
            st.session_state.chat_engine.clear_history()
            st.session_state.messages = []
            st.session_state.message_count = 0
            st.rerun()
        
        if st.button("🔄 Reiniciar Aplicación", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        # Configuración avanzada (expandible)
        with st.expander("🔧 Configuración Avanzada"):
            config_info = AzureOpenAIConfig.get_info()
            st.json(config_info)
        
        # Enlaces útiles
        st.markdown("#### 🔗 Enlaces Útiles")
        st.markdown("""
        - [Azure OpenAI Service](https://azure.microsoft.com/products/ai-services/openai-service)
        - [Documentación](https://learn.microsoft.com/azure/ai-services/openai/)
        - [LangChain Docs](https://python.langchain.com/)
        """)
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<small>Powered by Azure OpenAI Service 🚀</small>",
            unsafe_allow_html=True
        )


def display_chat_interface():
    """Muestra la interfaz principal del chat"""
    
    # Header
    st.markdown(f'<div class="main-header">{AppConfig.TITLE}</div>', unsafe_allow_html=True)
    
    # Contenedor de mensajes
    chat_container = st.container()
    
    # Mostrar historial de mensajes
    with chat_container:
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Timestamp (solo en modo debug)
                if "timestamp" in message:
                    st.caption(f"🕐 {message['timestamp']}")
    
    # Input del usuario
    if prompt := st.chat_input("💬 Escribe tu mensaje aquí..."):
        
        # Agregar mensaje del usuario
        timestamp = format_message_timestamp()
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)
        st.session_state.message_count += 1
        
        # Mostrar mensaje del usuario
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(f"🕐 {timestamp}")
        
        # Obtener y mostrar respuesta del asistente
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                try:
                    # Modo streaming si está habilitado
                    if AppConfig.ENABLE_STREAMING:
                        full_response = ""
                        with st.spinner("Pensando..."):
                            response = st.session_state.chat_engine.send_message(prompt)
                            full_response = response
                            message_placeholder.markdown(full_response)
                    else:
                        with st.spinner("Generando respuesta..."):
                            response = st.session_state.chat_engine.send_message(prompt)
                            message_placeholder.markdown(response)
                            full_response = response
                    
                    # Timestamp de respuesta
                    response_timestamp = format_message_timestamp()
                    st.caption(f"🕐 {response_timestamp}")
                    
                    # Agregar respuesta al historial
                    assistant_message = {
                        "role": "assistant",
                        "content": full_response,
                        "timestamp": response_timestamp
                    }
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    error_message = f"❌ Error: {str(e)}"
                    message_placeholder.error(error_message)
                    logger.error(f"Error al procesar mensaje: {e}")


def main():
    """Función principal de la aplicación"""
    
    # Inicializar estado de sesión
    initialize_session_state()
    
    # Mostrar sidebar
    display_sidebar()
    
    # Mostrar interfaz de chat
    display_chat_interface()
    
    # Mensaje de bienvenida si no hay mensajes
    if len(st.session_state.messages) == 0:
        st.info(
            "👋 ¡Hola! Soy un asistente potenciado por Azure OpenAI Service. "
            "Escribe un mensaje para comenzar nuestra conversación."
        )
        
        # Ejemplos de preguntas
        st.markdown("#### 💡 Ejemplos de lo que puedes preguntar:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📚 Explícame qué es la computación en la nube"):
                st.session_state.example_question = "Explícame qué es la computación en la nube"
                st.rerun()
        
        with col2:
            if st.button("💻 Ayúdame a escribir código Python"):
                st.session_state.example_question = "Ayúdame a escribir un script en Python para procesar archivos CSV"
                st.rerun()
        
        with col3:
            if st.button("🎨 Dame ideas creativas"):
                st.session_state.example_question = "Dame 5 ideas creativas para un proyecto de fin de semana"
                st.rerun()


if __name__ == "__main__":
    main()
```

### 7. app/__init__.py

```python
"""
Aplicación de Chat con Azure OpenAI Service
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"
__description__ = "Aplicación de chat usando Azure OpenAI Service, LangChain y Streamlit"

# Exportar componentes principales
from app.chat_engine import ChatEngine
from app.config import AzureOpenAIConfig, AppConfig

__all__ = [
    "ChatEngine",
    "AzureOpenAIConfig",
    "AppConfig"
]
```

### 8. tests/test_connection.py

```python
"""
Tests de conexión con Azure OpenAI Service
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import AzureOpenAIConfig
from app.chat_engine import ChatEngine


def test_configuration():
    """Test de configuración"""
    print("\n" + "="*60)
    print("TEST 1: Validación de Configuración")
    print("="*60)
    
    try:
        AzureOpenAIConfig.validate()
        print("✅ Configuración válida")
        print(f"   Endpoint: {AzureOpenAIConfig.ENDPOINT}")
        print(f"   Deployment: {AzureOpenAIConfig.DEPLOYMENT_NAME}")
        print(f"   API Version: {AzureOpenAIConfig.API_VERSION}")
        return True
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        return False


def test_connection():
    """Test de conexión con Azure OpenAI"""
    print("\n" + "="*60)
    print("TEST 2: Conexión con Azure OpenAI Service")
    print("="*60)
    
    try:
        engine = ChatEngine()
        print("✅ Conexión establecida correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return False


def test_simple_query():
    """Test de consulta simple"""
    print("\n" + "="*60)
    print("TEST 3: Consulta Simple al Modelo")
    print("="*60)
    
    try:
        engine = ChatEngine()
        
        test_message = "Di 'Hola' si puedes leer este mensaje."
        print(f"📤 Enviando: {test_message}")
        
        response = engine.send_message(test_message)
        
        print(f"📥 Respuesta recibida:")
        print(f"   {response[:200]}...")
        print("✅ Consulta exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return False


def test_conversation():
    """Test de conversación con múltiples mensajes"""
    print("\n" + "="*60)
    print("TEST 4: Conversación con Memoria")
    print("="*60)
    
    try:
        engine = ChatEngine()
        
        # Primera pregunta
        msg1 = "Mi nombre es Juan."
        print(f"📤 Usuario: {msg1}")
        response1 = engine.send_message(msg1)
        print(f"📥 Asistente: {response1[:100]}...")
        
        # Segunda pregunta (prueba de memoria)
        msg2 = "¿Cuál es mi nombre?"
        print(f"\n📤 Usuario: {msg2}")
        response2 = engine.send_message(msg2)
        print(f"📥 Asistente: {response2[:100]}...")
        
        # Verificar que recuerda el nombre
        if "Juan" in response2 or "juan" in response2:
            print("✅ El modelo recuerda el contexto correctamente")
            return True
        else:
            print("⚠️  El modelo no recordó el contexto")
            return False
            
    except Exception as e:
        print(f"❌ Error en la conversación: {e}")
        return False


def test_model_info():
    """Test de información del modelo"""
    print("\n" + "="*60)
    print("TEST 5: Información del Modelo")
    print("="*60)
    
    try:
        engine = ChatEngine()
        info = engine.get_model_info()
        
        print("📊 Información del modelo:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        print("✅ Información obtenida correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al obtener información: {e}")
        return False


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🧪 SUITE DE TESTS - AZURE OPENAI CHAT")
    print("="*60)
    
    tests = [
        ("Configuración", test_configuration),
        ("Conexión", test_connection),
        ("Consulta Simple", test_simple_query),
        ("Conversación", test_conversation),
        ("Info del Modelo", test_model_info)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("📋 RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Resultados: {passed}/{total} tests pasados")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        return 0
    else:
        print("⚠️  Algunos tests fallaron. Revisa la configuración.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
```

## 🐳 Containerización con Docker

### 1. Dockerfile

```dockerfile
# ============================================
# Multi-stage build para optimizar el tamaño
# ============================================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY app/ ./app/
COPY tests/ ./tests/

# Actualizar PATH
ENV PATH=/root/.local/bin:$PATH

# Variables de entorno para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app

USER streamlit

# Exponer puerto
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

### 2. docker-compose.yml

```yaml
version: '3.8'

services:
  # ============================================
  # Servicio principal de la aplicación
  # ============================================
  azure-openai-chat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: azure-openai-chat-app
    
    # Mapeo de puertos
    ports:
      - "8501:8501"
    
    # Variables de entorno desde .env
    environment:
      # Azure OpenAI Configuration
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME}
      - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}
      
      # Application Settings
      - APP_TITLE=${APP_TITLE:-Chat con Azure OpenAI}
      - APP_TEMPERATURE=${APP_TEMPERATURE:-0.7}
      - APP_MAX_TOKENS=${APP_MAX_TOKENS:-2000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - SYSTEM_PROMPT=${SYSTEM_PROMPT:-Eres un asistente útil y profesional.}
      - ENABLE_STREAMING=${ENABLE_STREAMING:-true}
      - REQUEST_TIMEOUT=${REQUEST_TIMEOUT:-30}
    
    # Volúmenes para desarrollo
    volumes:
      - ./app:/app/app:ro
      - ./tests:/app/tests:ro
    
    # Política de reinicio
    restart: unless-stopped
    
    # Healthcheck
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Límites de recursos
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
    
    # Redes
    networks:
      - app-network
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

# ============================================
# Definición de redes
# ============================================
networks:
  app-network:
    driver: bridge

# ============================================
# Definición de volúmenes (si se necesitan)
# ============================================
# volumes:
#   app-data:
```

### 3. .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/

# Environment
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Tests
tests/__pycache__/
.pytest_cache/

# Documentation
*.md
!README.md

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

### 4. .gitignore

```
# ============================================
# Python
# ============================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/
.venv

# Distribution / packaging
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# ============================================
# Environment variables
# ============================================
.env
.env.local
.env.*.local

# ============================================
# IDEs
# ============================================
# VSCode
.vscode/
*.code-workspace

# PyCharm
.idea/
*.iml

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo
*~

# ============================================
# OS
# ============================================
# MacOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Linux
*~

# ============================================
# Logs
# ============================================
*.log
logs/
*.log.*

# ============================================
# Testing
# ============================================
.pytest_cache/
.coverage
htmlcov/
.tox/

# ============================================
# Docker
# ============================================
docker-compose.override.yml

# ============================================
# Temporary files
# ============================================
*.tmp
*.temp
*.bak
*.swp

# ============================================
# Streamlit
# ============================================
.streamlit/secrets.toml
```

## 🚀 Guía de Instalación y Ejecución

### Método 1: Ejecución Local (Sin Docker)

#### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/azure-openai-chat.git
cd azure-openai-chat
```

#### Paso 2: Crear Entorno Virtual de Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual

# En Windows
venv\Scripts\activate

# En Linux/macOS
source venv/bin/activate
```

#### Paso 3: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 4: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus credenciales
# En Windows: notepad .env
# En Linux/macOS: nano .env
```

Completar con tus credenciales de Azure:

```env
AZURE_OPENAI_ENDPOINT=https://tu-servicio.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-clave-aqui
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-chat
```

#### Paso 5: Probar la Conexión

```bash
# Ejecutar tests de conexión
python tests/test_connection.py
```

Si todo está configurado correctamente, deberías ver:
```
🎯 Resultados: 5/5 tests pasados
🎉 ¡Todos los tests pasaron exitosamente!
```

#### Paso 6: Ejecutar la Aplicación

```bash
streamlit run app/main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Método 2: Ejecución con Docker

#### Paso 1: Prerequisitos

Asegúrate de tener instalado:
- Docker Desktop (Windows/Mac) o Docker Engine (Linux)
- Docker Compose

Verifica la instalación:
```bash
docker --version
docker-compose --version
```

#### Paso 2: Configurar Variables de Entorno

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/azure-openai-chat.git
cd azure-openai-chat

# Crear archivo .env
cp .env.example .env

# Editar con tus credenciales
nano .env  # o tu editor preferido
```

#### Paso 3: Construir la Imagen

```bash
# Construir la imagen Docker
docker-compose build

# Ver la imagen creada
docker images | grep azure-openai-chat
```

#### Paso 4: Iniciar el Contenedor

```bash
# Iniciar en modo detached (background)
docker-compose up -d

# Ver los logs en tiempo real
docker-compose logs -f
```

#### Paso 5: Acceder a la Aplicación

Abre tu navegador y ve a: `http://localhost:8501`

#### Paso 6: Gestionar el Contenedor

```bash
# Ver estado del contenedor
docker-compose ps

# Detener el contenedor
docker-compose down

# Reiniciar el contenedor
docker-compose restart

# Ver logs
docker-compose logs -f azure-openai-chat

# Reconstruir después de cambios
docker-compose up -d --build

# Eliminar contenedor y volúmenes
docker-compose down -v
```

### Método 3: Desarrollo con Hot Reload

Para desarrollo activo con recarga automática:

```bash
# Sin Docker
streamlit run app/main.py --server.runOnSave=true

# Con Docker (los volúmenes ya están configurados)
docker-compose up
# Los cambios en app/ se reflejarán automáticamente
```

## 🧪 Testing y Validación

### Ejecutar Tests Completos

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows

# Ejecutar suite de tests
python tests/test_connection.py
```

### Tests Individuales

```python
# Test solo de configuración
python -c "from app.config import AzureOpenAIConfig; AzureOpenAIConfig.validate(); print('OK')"

# Test de conexión básica
python -c "from app.chat_engine import ChatEngine; engine = ChatEngine(); print('Conectado')"

# Test de consulta simple
python -c "from app.chat_engine import ChatEngine; engine = ChatEngine(); print(engine.send_message('Hola'))"
```

### Verificar Variables de Entorno

```bash
# Verificar que las variables están cargadas
python -c "from app.config import AzureOpenAIConfig; print(AzureOpenAIConfig.get_info())"
```

## 📊 Monitoreo y Observabilidad

### Logs de la Aplicación

```bash
# Ver logs en tiempo real (Docker)
docker-compose logs -f azure-openai-chat

# Ver últimas 100 líneas
docker-compose logs --tail=100 azure-openai-chat

# Buscar errores en logs
docker-compose logs azure-openai-chat | grep ERROR
```

### Monitoreo en Azure Portal

1. Ve a tu recurso de **Azure OpenAI** en el portal
2. Navega a **Monitoring** → **Metrics**
3. Métricas importantes a monitorear:
   - **Total Calls**: Número de llamadas a la API
   - **Total Tokens**: Tokens consumidos
   - **Latency**: Tiempo de respuesta
   - **HTTP Status**: Códigos de respuesta

4. Configurar alertas:
   - Ve a **Alerts** → **Create alert rule**
   - Configura umbrales para:
     - Alto consumo de tokens
     - Errores frecuentes
     - Latencia elevada

### Dashboard de Costos

```bash
# Ver costos estimados
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --query "[?contains(instanceName, 'openai')]" \
  --output table
```

## 🔧 Solución de Problemas Comunes

### Error: "Missing environment variables"

**Causa**: El archivo `.env` no existe o no tiene las variables necesarias.

**Solución**:
```bash
# Verificar que el archivo existe
ls -la .env

# Si no existe, crearlo desde el ejemplo
cp .env.example .env

# Verificar contenido
cat .env

# Verificar que se cargan las variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Endpoint:', os.getenv('AZURE_OPENAI_ENDPOINT'))"
```

### Error: "Authentication failed" o "401 Unauthorized"

**Causa**: La API Key es incorrecta o ha expirado.

**Solución**:
1. Ve al Portal de Azure
2. Navega a tu recurso de Azure OpenAI
3. Ve a **Keys and Endpoint**
4. Copia **KEY 1** o regenera las claves si es necesario
5. Actualiza tu `.env`:
   ```env
   AZURE_OPENAI_API_KEY=nueva-clave-aqui
   ```

### Error: "Deployment not found" o "404 Not Found"

**Causa**: El nombre del deployment no coincide.

**Solución**:
```bash
# Verificar deployments disponibles en Azure OpenAI Studio
# O usar Azure CLI:
az cognitiveservices account deployment list \
  --name tu-servicio-openai \
  --resource-group tu-grupo-recursos

# Actualizar .env con el nombre exacto
AZURE_OPENAI_DEPLOYMENT_NAME=nombre-exacto-del-deployment
```

### Error: "Rate limit exceeded" o "429 Too Many Requests"

**Causa**: Has excedido el límite de tokens por minuto.

**Solución**:
1. Ve a Azure OpenAI Studio → Deployments
2. Aumenta el límite de **Tokens Per Minute (TPM)**
3. O implementa rate limiting en la aplicación:

```python
# En app/chat_engine.py, agregar retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def send_message(self, message: str) -> str:
    # ... código existente
```

### Error: "Connection timeout"

**Causa**: Problemas de red o timeout muy bajo.

**Solución**:
```env
# Aumentar timeout en .env
REQUEST_TIMEOUT=60
```

### Contenedor Docker no inicia

```bash
# Ver logs detallados
docker-compose logs azure-openai-chat

# Verificar configuración
docker-compose config

# Reconstruir sin caché
docker-compose build --no-cache

# Verificar que el puerto no esté ocupado
# En Linux/macOS:
lsof -i :8501

# En Windows:
netstat -ano | findstr :8501
```

### Aplicación se congela o no responde

**Causa**: Modelo muy lento o MAX_TOKENS muy alto.

**Solución**:
```env
# Reducir tokens máximos
APP_MAX_TOKENS=1000

# Reducir temperatura si las respuestas son muy largas
APP_TEMPERATURE=0.5
```

## 🔐 Mejores Prácticas de Seguridad

### 1. Gestión de Secretos

**❌ No hacer**:
```python
# Nunca hardcodear credenciales
api_key = "sk-xxxxxxxxxxxxx"
```

**✅ Hacer**:
```python
# Usar variables de entorno
from app.config import AzureOpenAIConfig
api_key = AzureOpenAIConfig.API_KEY
```

### 2. Usar Azure Key Vault para Producción

```python
# Instalar SDK
# pip install azure-keyvault-secrets azure-identity

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Obtener secretos desde Key Vault
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://tu-keyvault.vault.azure.net/",
    credential=credential
)

api_key = client.get_secret("azure-openai-api-key").value
```

### 3. Rotar Claves Regularmente

```bash
# Regenerar clave en Azure
az cognitiveservices account keys regenerate \
  --name tu-servicio-openai \
  --resource-group tu-grupo-recursos \
  --key-name key1
```

### 4. Implementar Rate Limiting

```python
# En app/chat_engine.py
from datetime import datetime, timedelta

class ChatEngine:
    def __init__(self):
        self.request_count = 0
        self.reset_time = datetime.now() + timedelta(minutes=1)
    
    def check_rate_limit(self):
        if datetime.now() > self.reset_time:
            self.request_count = 0
            self.reset_time = datetime.now() + timedelta(minutes=1)
        
        if self.request_count >= 20:  # 20 requests por minuto
            raise Exception("Rate limit exceeded")
        
        self.request_count += 1
```

### 5. Logging Seguro

```python
# No loguear información sensible
logger.info(f"Conectando a {endpoint}")  # ✅ OK
logger.info(f"Using API key {api_key}")  # ❌ NO!
```

### 6. RBAC (Role-Based Access Control)

```bash
# Asignar rol de Cognitive Services User
az role assignment create \
  --role "Cognitive Services User" \
  --assignee tu-usuario@dominio.com \
  --scope /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account-name}
```

## 📈 Optimización y Mejores Prácticas

### 1. Optimizar Costos

```python
# Usar modelos apropiados según la tarea
# GPT-3.5-Turbo: Más rápido y económico para tareas simples
# GPT-4: Para tareas complejas que requieren mejor razonamiento

# Limitar tokens
APP_MAX_TOKENS=500  # Para respuestas cortas

# Ajustar temperatura
APP_TEMPERATURE=0.3  # Para respuestas más deterministas (menos tokens)
```

### 2. Implementar Caché

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(message: str) -> str:
    """Cachea respuestas para preguntas repetidas"""
    return self.send_message(message)
```

### 3. Prompt Engineering

```python
# Buenos prompts = mejores resultados + menos tokens

# ❌ Prompt vago
"Cuéntame sobre Python"

# ✅ Prompt específico
"Explica en 3 párrafos los beneficios de Python para data science"
```

### 4. Streaming para Mejor UX

```python
# Ya implementado en app/main.py
ENABLE_STREAMING=true
```

### 5. Monitoreo de Uso

```python
def log_usage(self, prompt_tokens: int, completion_tokens: int):
    """Registra uso de tokens"""
    total_cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
    logger.info(f"Tokens used: {prompt_tokens + completion_tokens}, Cost: ${total_cost:.4f}")
```

## 🚀 Despliegue en Producción

### Opción 1: Azure Container Apps

```bash
# 1. Login a Azure
az login

# 2. Crear Container Registry
az acr create \
  --resource-group rg-openai-chat \
  --name myopenairegistry \
  --sku Basic

# 3. Login al registry
az acr login --name myopenairegistry

# 4. Build y push
az acr build \
  --registry myopenairegistry \
  --image azure-openai-chat:latest \
  --file Dockerfile .

# 5. Crear Container App
az containerapp create \
  --name azure-openai-chat \
  --resource-group rg-openai-chat \
  --image myopenairegistry.azurecr.io/azure-openai-chat:latest \
  --target-port 8501 \
  --ingress external \
  --registry-server myopenairegistry.azurecr.io \
  --environment-variables \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
    AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME
```

### Opción 2: Azure App Service

```bash
# 1. Crear App Service Plan
az appservice plan create \
  --name openai-chat-plan \
  --resource-group rg-openai-chat \
  --sku B1 \
  --is-linux

# 2. Crear Web App
az webapp create \
  --resource-group rg-openai-chat \
  --plan openai-chat-plan \
  --name azure-openai-chat-app \
  --runtime "PYTHON:3.11"

# 3. Configurar deployment desde GitHub
az webapp deployment source config \
  --name azure-openai-chat-app \
  --resource-group rg-openai-chat \
  --repo-url https://github.com/tu-usuario/azure-openai-chat \
  --branch main \
  --manual-integration

# 4. Configurar variables de entorno
az webapp config appsettings set \
  --name azure-openai-chat-app \
  --resource-group rg-openai-chat \
  --settings \
    AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
    AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
    AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME
```

### Opción 3: Azure Kubernetes Service (AKS)

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: azure-openai-chat
spec:
  replicas: 3
  selector:
    matchLabels:
      app: azure-openai-chat
  template:
    metadata:
      labels:
        app: azure-openai-chat
    spec:
      containers:
      - name: chat-app
        image: myopenairegistry.azurecr.io/azure-openai-chat:latest
        ports:
        - containerPort: 8501
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-openai-secrets
              key: endpoint
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-openai-secrets
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

## 📚 Extensiones y Mejoras Futuras

### 1. Agregar RAG (Retrieval Augmented Generation)

```python
# Instalar dependencias adicionales
# pip install chromadb sentence-transformers

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGChatEngine(ChatEngine):
    def __init__(self, docs_path: str):
        super().__init__()
        
        # Cargar documentos
        loader = DirectoryLoader(docs_path)
        documents = loader.load()
        
        # Dividir en chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = splitter.split_documents(documents)
        
        # Crear vector store
        embeddings = HuggingFaceEmbeddings()
        self.vectorstore = Chroma.from_documents(texts, embeddings)
    
    def send_message_with_context(self, message: str) -> str:
        # Buscar documentos relevantes
        docs = self.vectorstore.similarity_search(message, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        
        # Agregar contexto al prompt
        enhanced_message = f"Contexto:\n{context}\n\nPregunta: {message}"
        
        return self.send_message(enhanced_message)
```

### 2. Agregar Autenticación

```python
# pip install streamlit-authenticator

import streamlit_authenticator as stauth

# En app/main.py
def add_authentication():
    authenticator = stauth.Authenticate(
        credentials,
        'cookie_name',
        'signature_key',
        cookie_expiry_days=30
    )
    
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status:
        return True
    elif authentication_status == False:
        st.error('Username/password es incorrecto')
        return False
    elif authentication_status == None:
        st.warning('Por favor ingresa username y password')
        return False
```

### 3. Agregar Análisis de Sentimiento

```python
# pip install textblob

from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analiza el sentimiento del mensaje"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        sentiment = "positivo"
    elif polarity < -0.1:
        sentiment = "negativo"
    else:
        sentiment = "neutral"
    
    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "subjectivity": blob.sentiment.subjectivity
    }
```

### 4. Agregar Export de Conversaciones

```python
import json
from datetime import datetime

def export_conversation(self) -> str:
    """Exporta la conversación a JSON"""
    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "messages": self.get_history_dict(),
        "model_info": self.get_model_info()
    }
    
    filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
    
    return filename
```

### 5. Agregar Multi-idioma

```python
# pip install langdetect deep-translator

from langdetect import detect
from deep_translator import GoogleTranslator

def translate_if_needed(text: str, target_lang: str = 'es') -> tuple:
    """Detecta idioma y traduce si es necesario"""
    detected_lang = detect(text)
    
    if detected_lang != target_lang:
        translator = GoogleTranslator(source=detected_lang, target=target_lang)
        translated = translator.translate(text)
        return translated, detected_lang
    
    return text, detected_lang
```

## 📚 Recursos Adicionales

### Documentación Oficial

- [Azure OpenAI Service](https://azure.microsoft.com/products/ai-services/openai-service)
- [Documentación Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Documentation](https://docs.docker.com/)

### Tutoriales y Guías

- [Azure OpenAI Quickstart](https://learn.microsoft.com/azure/ai-services/openai/quickstart)
- [LangChain with Azure OpenAI](https://python.langchain.com/docs/integrations/llms/azure_openai)
- [Best Practices for Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/concepts/best-practices)

### Comunidad y Soporte

- [Azure OpenAI Forum](https://learn.microsoft.com/answers/tags/387/azure-openai)
- [LangChain Discord](https://discord.gg/langchain)
- [Streamlit Community](https://discuss.streamlit.io/)

### Herramientas Útiles

- [Azure CLI](https://learn.microsoft.com/cli/azure/)
- [Azure OpenAI Studio](https://oai.azure.com/)
- [Postman Collection para Azure OpenAI](https://www.postman.com/)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas contribuir:

1. **Fork** el proyecto
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Guías de Contribución

- Sigue el estilo de código PEP 8
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación
- Describe claramente tus cambios en el PR

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Agradecimientos

- Equipo de Azure OpenAI Service
- Comunidad de LangChain
- Comunidad de Streamlit
- Todos los contribuidores

## 📞 Contacto y Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/azure-openai-chat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tu-usuario/azure-openai-chat/discussions)
- **Email**: tu-email@ejemplo.com

## 🎯 Roadmap

- [ ] Implementar RAG con documentos personalizados
- [ ] Agregar soporte multi-idioma
- [ ] Implementar autenticación de usuarios
- [ ] Agregar export de conversaciones a PDF
- [ ] Implementar análisis de sentimiento
- [ ] Agregar voice input/output
- [ ] Crear dashboard de analytics
- [ ] Implementar A/B testing de prompts
- [ ] Agregar integración con Azure Cognitive Search
- [ ] Crear versión móvil nativa

---

<div align="center">

**⭐ Si este proyecto te fue útil, ¡considera darle una estrella en GitHub! ⭐**

Desarrollado con ❤️ usando Azure OpenAI Service

[Reportar Bug](https://github.com/tu-usuario/azure-openai-chat/issues) · [Solicitar Feature](https://github.com/tu-usuario/azure-openai-chat/issues) · [Ver Demo](https://tu-demo.azurecontainerapps.io)

</div>
