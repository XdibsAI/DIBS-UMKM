from utils.errors import handle_errors, NotFoundError
"""Chat Routes"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from datetime import datetime, timezone
import uuid
import logging

from .models import SendMessageRequest, ChatMessage
from .core import ollama_ai
from auth.utils import get_current_user, TokenData
from chat.table_formatter import improve_table_formatting
from chat.language.language_detector import detect_language, enhance_prompt_with_language
from chat.command_parser import command_parser
from chat.dynamic_db import get_dynamic_db
from reminders.parser import reminder_parser
from reminders.models import get_reminder_manager

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
logger = logging.getLogger('DIBS1')

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

@router.get("/sessions")
@handle_errors
async def get_sessions(current_user: TokenData = Depends(get_current_user)):
    """Get user's chat sessions"""
    try:
        sessions = await db.fetch_all(
            """SELECT session_id, name, created_at, 
               (SELECT COUNT(*) FROM chat_messages WHERE session_id = s.session_id) as message_count
               FROM chat_sessions s 
               WHERE user_id = ? 
               ORDER BY created_at DESC""",
            (current_user.user_id,)
        )
        
        return {
            "status": "success",
            "data": {"data": [dict(s) for s in sessions]}
        }
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(500, str(e))

@router.post("/sessions")
async def create_session(
    name: str = None,
    current_user: TokenData = Depends(get_current_user)
):
    """Create new chat session"""
    try:
        session_id = str(uuid.uuid4())
        # Use UTC for consistency
        # Use local time for session name (user's timezone)
        from datetime import timedelta
        utc_now = datetime.now(timezone.utc)
        # Assume WIB (WIB) for Indonesian users
        wib_now = utc_now + timedelta(hours=7)
        session_name = name or f"Chat {wib_now.strftime('%H:%M')}"
        
        await db.execute(
            "INSERT INTO chat_sessions (session_id, user_id, name, created_at) VALUES (?, ?, ?, ?)",
            (session_id, current_user.user_id, session_name, datetime.now(timezone.utc).isoformat())
        )
        
        logger.info(f"✅ Session created: {session_id}")
        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "name": session_name,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(500, str(e))

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get session with messages"""
    try:
        # Get session
        session = await db.fetch_one(
            "SELECT * FROM chat_sessions WHERE session_id = ? AND user_id = ?",
            (session_id, current_user.user_id)
        )
        
        if not session:
            raise HTTPException(404, "Session not found")
        
        # Get messages
        messages = await db.fetch_all(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        )
        
        return {
            "status": "success",
            "data": {
                "session_id": session['session_id'],
                "name": session['name'],
                "created_at": session['created_at'],
                "messages": [
                    {
                        "role": m['role'],
                        "content": m['content'],
                        "created_at": m['created_at']
                    }
                    for m in messages
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(500, str(e))

from fastapi import Query
from inventory_ai.router import detect_inventory_intent
from inventory_ai.query import search_inventory_products, get_low_stock_products_local, build_stock_response, build_price_response, build_low_stock_response

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    use_nvidia: bool = Query(True),
    current_user: TokenData = Depends(get_current_user)
):
    """Send message and get AI response"""
    try:
        # Verify session ownership
        session = await db.fetch_one(
            "SELECT * FROM chat_sessions WHERE session_id = ? AND user_id = ?",
            (session_id, current_user.user_id)
        )
        
        if not session:
            raise HTTPException(404, "Session not found")
        
        # Save user message
        user_msg_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        await db.execute(
            "INSERT INTO chat_messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_msg_id, session_id, "user", request.message, created_at)
        )
        
        # Get conversation context (last 10 messages)
        context_messages = await db.fetch_all(
            "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT 10",
            (session_id,)
        )
        context = [{"role": m['role'], "content": m['content']} for m in reversed(list(context_messages))]
        
        # === REMINDER SYSTEM ===
        reminder_cmd = reminder_parser.parse(request.message)
        logger.info(f"🔍 Reminder parsed: {reminder_cmd}")
        
        if reminder_cmd and reminder_cmd.get('action') == 'create_reminder':
            logger.info(f"✅ Creating reminder: {reminder_cmd['title']}")
            
            try:
                reminder_mgr = get_reminder_manager()
                
                reminder_id = await reminder_mgr.create_reminder(
                    user_id=current_user.user_id,
                    session_id=session_id,
                    title=reminder_cmd['title'],
                    due_date=reminder_cmd['due_date'],
                    description=request.message
                )
                
                if reminder_id:
                    due_str = reminder_cmd['due_date'].strftime('%d %b %Y, %H:%M')
                    ai_response = f"✅ Pengingat berhasil dibuat!\n\n"
                    ai_response += f"📌 **Tentang:** {reminder_cmd['title']}\n"
                    ai_response += f"⏰ **Waktu:** {due_str}\n"
                    ai_response += f"🔔 Saya akan mengingatkan Anda saat waktunya tiba."
                    
                    logger.info(f"✅ Reminder saved: {reminder_id}")
                else:
                    ai_response = "❌ Gagal membuat pengingat"
                
                # Save and return
                assistant_msg_id = str(uuid.uuid4())
                await db.execute(
                    "INSERT INTO chat_messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                    (assistant_msg_id, session_id, "assistant", ai_response, datetime.now(timezone.utc).isoformat())
                )
                
                return {
                    "status": "success",
                    "data": {
                        "assistant_message": {
                            "role": "assistant",
                            "content": ai_response,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                }
                
            except Exception as e:
                logger.error(f"❌ Reminder error: {e}")
        # === END REMINDER ===

        
        # === LOCAL INVENTORY INTENT ===
        inventory_intent = detect_inventory_intent(request.message)

        if inventory_intent.matched:
            user_id = str(getattr(current_user, "user_id", getattr(current_user, "id", "")))

            if inventory_intent.intent == "low_stock":
                low_stock_items = await get_low_stock_products_local(db, user_id, threshold=5, limit=10)
                ai_response = build_low_stock_response(low_stock_items)
            else:
                products = await search_inventory_products(
                    db=db,
                    user_id=user_id,
                    product_query=inventory_intent.product_query,
                    size_value=inventory_intent.size_value,
                    size_unit=inventory_intent.size_unit,
                    limit=8,
                )

                if inventory_intent.intent == "check_price":
                    ai_response = build_price_response(
                        inventory_intent.product_query or request.message,
                        products,
                    )
                else:
                    ai_response = build_stock_response(
                        inventory_intent.product_query or request.message,
                        products,
                    )

            assistant_msg_id = str(uuid.uuid4())
            assistant_created_at = datetime.now(timezone.utc).isoformat()

            await db.execute(
                "INSERT INTO chat_messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (assistant_msg_id, session_id, "assistant", ai_response, assistant_created_at)
            )

            return {
                "status": "success",
                "data": {
                    "assistant_message": {
                        "role": "assistant",
                        "content": ai_response,
                        "created_at": assistant_created_at
                    }
                }
            }

        # Detect language and enhance prompt
        detected_lang = detect_language(request.message)
        enhanced_message = enhance_prompt_with_language(request.message, detected_lang)

        # Generate AI response
        ai_response = await ollama_ai.generate(
            enhanced_message,
            session_id=session_id,
            context=context,
            use_nvidia_override=use_nvidia
        )

        # Improve table formatting for mobile
        ai_response = improve_table_formatting(ai_response)

        # Save assistant message
        assistant_msg_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO chat_messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (assistant_msg_id, session_id, "assistant", ai_response, datetime.now(timezone.utc).isoformat())
        )

        logger.info(f"✅ Message processed in session {session_id}")
        return {
            "status": "success",
            "data": {
                "assistant_message": {
                    "role": "assistant",
                    "content": ai_response,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(500, str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete chat session"""
    try:
        await db.execute(
            "DELETE FROM chat_sessions WHERE session_id = ? AND user_id = ?",
            (session_id, current_user.user_id)
        )
        await db.execute(
            "DELETE FROM chat_messages WHERE session_id = ?",
            (session_id,)
        )
        
        logger.info(f"🗑️ Session deleted: {session_id}")
        return {"status": "success", "message": "Session deleted"}
    except Exception as e:
        logger.error(f"Delete session error: {e}")


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Upload image/document for AI analysis"""
    try:
        import os
        from pathlib import Path
        
        # Create uploads directory
        upload_dir = Path("/home/dibs/dibs1/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{current_user.user_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"📤 File uploaded: {file.filename} ({len(content)} bytes)")
        
        # Analyze based on type
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type in ['jpg', 'jpeg', 'png']:
            # Image analysis (basic for now)
            analysis = f"Gambar {file.filename} berhasil diupload. File size: {len(content)/1024:.1f}KB"
        elif file_type == 'pdf':
            analysis = f"Dokumen PDF {file.filename} berhasil diupload. Siap untuk dibaca."
        else:
            analysis = f"File {file.filename} berhasil diupload."
        
        return {
            "status": "success",
            "data": {
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "analysis": analysis
            }
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(500, str(e))

        raise HTTPException(500, str(e))

@router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Analyze uploaded image"""
    try:
        import os
        from pathlib import Path
        from PIL import Image
        import pytesseract
        
        # Save file
        upload_dir = Path("/home/dibs/dibs1/uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / f"{current_user.user_id}_{file.filename}"
        
        content_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(content_bytes)
        
        # Basic image info
        img = Image.open(file_path)
        width, height = img.size
        
        # OCR text extraction
        try:
            text = pytesseract.image_to_string(img)
            has_text = len(text.strip()) > 0
        except:
            text = ""
            has_text = False
        
        analysis = f"""📸 **Analisis Gambar: {file.filename}**

🔹 **Dimensi:** {width}x{height} pixels
🔹 **Format:** {img.format}
🔹 **Mode:** {img.mode}

"""
        
        if has_text:
            analysis += f"📝 **Text terdeteksi (OCR):**\n{text[:500]}\n\n"
        else:
            analysis += "ℹ️ Tidak ada text terdeteksi dalam gambar.\n\n"
        
        # Product detection (basic - bisa upgrade pakai AI vision API)
        filename_lower = file.filename.lower()
        if any(word in filename_lower for word in ['keripik', 'snack', 'makanan', 'produk']):
            analysis += "🏷️ **Kemungkinan:** Gambar produk makanan/snack\n"
            analysis += "💡 **Saran:** Upload gambar lebih jelas untuk analisa detail produk, ingredients, dan harga.\n"
        
        logger.info(f"✅ Image analyzed: {file.filename}")
        
        return {
            "status": "success",
            "data": {
                "filename": file.filename,
                "analysis": analysis,
                "has_text": has_text,
                "extracted_text": text[:1000] if has_text else None,
                "dimensions": {"width": width, "height": height},
                "file_path": str(file_path)
            }
        }
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(500, str(e))

@router.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Analyze uploaded document (PDF, DOC, TXT)"""
    try:
        import os
        from pathlib import Path
        
        upload_dir = Path("/home/dibs/dibs1/uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / f"{current_user.user_id}_{file.filename}"
        
        content_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(content_bytes)
        
        file_ext = file.filename.split('.')[-1].lower()
        
        # Extract text based on type
        text_content = ""
        
        if file_ext == 'txt':
            text_content = content_bytes.decode('utf-8', errors='ignore')
        
        elif file_ext == 'pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages[:5]:  # Max 5 pages
                        text_content += page.extract_text()
            except Exception as e:
                text_content = f"Error extracting PDF: {e}"
        
        elif file_ext in ['doc', 'docx']:
            try:
                import docx
                doc = docx.Document(file_path)
                text_content = "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                text_content = f"Error extracting DOC: {e}"
        
        elif file_ext == 'csv':
            text_content = content_bytes.decode('utf-8', errors='ignore')
        
        # Summary
        word_count = len(text_content.split())
        char_count = len(text_content)
        
        summary = f"""📄 **Analisis Dokumen: {file.filename}**

📊 **Statistik:**
- Format: {file_ext.upper()}
- Ukuran: {len(content_bytes)/1024:.1f} KB
- Jumlah kata: {word_count}
- Jumlah karakter: {char_count}

📝 **Preview konten:**
{text_content[:500]}...

✅ Dokumen berhasil diproses dan siap untuk dianalisa lebih lanjut.
"""
        
        logger.info(f"✅ Document analyzed: {file.filename}")
        
        return {
            "status": "success",
            "data": {
                "filename": file.filename,
                "summary": summary,
                "full_text": text_content[:5000],  # Max 5000 chars
                "word_count": word_count,
                "file_path": str(file_path)
            }
        }
        
    except Exception as e:
        logger.error(f"Document analysis error: {e}")
        raise HTTPException(500, str(e))
