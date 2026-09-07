---
name: cleo-ecosystem
description: Arquitectura, protocolos, memoria activa e integraciones de Cleo (Frontier y Conquista), ecosistema de voz Cartesia, Trello, GitHub, Google Suite, CUGDL Moodle y WhatsApp.
---

# Cleo Ecosystem & Frontier Architecture

Este skill codifica el conocimiento maestro, estado de infraestructura y capacidades de **Cleo** en sus dos dimensiones para Ibrahim García:
1. **Cleo Frontier (AGY / Gemini Pro / Flash)**: La mente estratega en entorno de desarrollo profundo, razonamiento complejo y arquitectura de software.
2. **Cleo Conquista (Local 24/7 / Telegram Bot / Ollama)**: La secretaria y cómplice local (estilo C.C. de Code Geass), residente en D:\cleo, que corre en hardware local con AMD Radeon RX 6600, voz neuronal Cartesia Sonic 3.5 y schedulers automatizados.

---

## 🏛️ 1. Infraestructura y Almacenamiento Local (D:\cleo)
- **Directorio Raíz**: D:\cleo (Regla crítica: la unidad C: nunca se llena con modelos ni logs pesados).
- **Entorno Virtual**: D:\cleo\.venv\Scripts\python.exe (Python 3.11).
- **Ollama**:
  - Modelos en: D:\ollama\models ($env:OLLAMA_MODELS = D:\ollama\models).
  - Modelo personalizado: cleo-conquista (cuantizado en GPU, bloqueado en VRAM con keep_alive: -1).
- **Lanzador Independiente de Windows**: D:\cleo\iniciar_cleo.bat (dispara iniciar_cleo.ps1), levantando Ollama warmup, WhatsApp daemon y Telegram bot sin depender de AGY.

---

## 🎙️ 2. Motor de Voz y Fonética (D:\cleo\voice\engine.py)
- **TTS Primario**: **Cartesia Sonic 3.5** con voz **Laura** (1cc00672-e9d4-455e-b3fb-31dfb7aad231) a ~135ms de latencia.
- **TTS Fallback**: Edge-TTS Neural (es-MX-DaliaNeural).
- **STT**: `faster-whisper` (`base`, `device="cpu"`, `compute_type="int8"`, `beam_size=1`, guardado en `D:\cleo\voice\models`). Inferencia casi instantánea (~1s para audios de 20s).
- **Normalizador Fonético (`_phonetic_normalization`)**:
  - mise -> míis (pronunciación francesa gastronómica de *mise en place*).
  - gh#X o gh #X -> issue número X,.
  - Fechas (YYYY-MM-DD) -> fechas naturales en español (ej. 7 de septiembre de dos mil veintiséis, jamás dos cero dos seis).
  - Acentuación forzada para síntesis correcta (mañana, días).

---

## 🔗 3. Integraciones Activas
1. **Trello (D:\cleo\integrations\trello.py)**:
   - Tableros: *Deadlines & Chips*, *Atelier*, *Bug Tracker*, *Tareas Personales*.
   - Monitoreo activo de tickets de `mise` y `bizops`.
2. **GitHub (`D:\cleo\integrations\github_sync.py`)**:
   - Monitorea commits, PRs e issues asignados en `ibrahim-agent-core`, `mise_work`, `bizops-hub`, `reviews-lcp-gdl`.
3. **Google Workspace (D:\cleo\integrations\google_suite.py)**:
   - Cuenta Académica: 9 cursos activos de Google Classroom + Calendar académico.
   - Cuenta Personal: Eventos de Google Calendar personal.
4. **Mi CUGDL / UDG Moodle (D:\cleo\integrations\cugdl_moodle.py)**:
   - 5 materias activas (CCOS26B_235942, MLIB26B_225272, MAC26B_225299, RC26B_225132, SO26B_236407).
   - Cookie viva: MoodleSession en D:\cleo\.env.
5. **WhatsApp Daemon (D:\cleo\whatsapp\service.js & integrations\whatsapp_digest.py)**:
   - Baileys multi-device daemon autenticado en D:\cleo\whatsapp\auth_info_baileys.
   - Captura mensajes entrantes en ecent_unread.json y los inyecta en el prompt de Cleo.

---

## 🧠 4. Memoria Dinámica en Disco
Cleo Conquista actualiza su propio cerebro cuando el usuario le da instrucciones:
- **D:\cleo\data\memoria_activa.md**: Tareas vivas, pendientes inmediatos y estado de proyectos (etiqueta [ACTUALIZAR_MEMORIA: ...]).
- **D:\cleo\data\perfil.md**: Preferencias personales, hábitos y datos biográficos de Ibrahim (etiqueta [RECORDAR_PERFIL: ...]).

---

## ⏰ 5. Cron & Proactividad (D:\cleo\cron\scheduler.py)
- **Zona Horaria**: America/Mexico_City.
- **06:00 AM - Briefing Matutino**: Clima en Zapopan/Guadalajara, tráfico sugerido, tickets de Mise/Bizops, clases de Classroom/Moodle y audio sintetizado con Laura a Telegram.
- **21:30 PM - Debriefing Nocturno**: Chequeo de avances del día y actualización de memoria activa.