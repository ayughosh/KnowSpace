import os
from ollama import chat
from langdetect import detect, LangDetectException
from flask import(Blueprint, render_template, request, redirect, url_for, flash, current_app, abort)
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfReader
import whisper
import requests
from flask_login import login_required, current_user
from app.database_utils import db,Entry,User
main=Blueprint("main",__name__)
ALLOWED_EXTENSIONS={"wav", "mp3", "mp4", "m4a", "flac", "ogg","webm","pdf","doc","docx","txt"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

#load Whisper models once at startup
MODEL=whisper.load_model("base")

def transcribe_with_whisper(path_to_file):
    """
    Run Whisper on the saved audio file.
    Returns the raw transcription text.
    """
    result=MODEL.transcribe(path_to_file)
    return result["text"]

# app/utils.py  (or wherever your helper lives)


def summarize_with_gemma(text_to_summarize: str) -> str:
    """
    Send the text to your local Ollama (Gemma) endpoint and
    return a summary in the ORIGINAL language.
    """
    # 1) Try to auto-detect language
    try:
        lang_code = detect(text_to_summarize)
    except LangDetectException:
        lang_code = "original language"

    # 2) Build a system prompt that tells Gemma to keep the same language
    system_prompt = (
        "You are a friendly, concise summarization assistant. "
        f"The user’s text is in {lang_code}. "
        "Always produce your summary in the same language as the input."
    )

    # 3) Wrap the user’s text in a clear instruction
    user_prompt = (
        "Here is the text to summarize (keep your output in the same language):\n\n"
        "```text\n"
        f"{text_to_summarize}\n"
        "```"
    )

    # 4) Call Gemma
    resp = chat(
        model="gemma:2b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        # optional tuning:
        #max_tokens=256,
        #temperature=0.5,
        # server="http://localhost:11435",
    )

    return resp["message"]["content"].strip()


@main.route("/")
def home():
     # Render a real home page, not just redirect
    return render_template("home.html")


@main.route("/upload", methods=["GET","POST"])
def upload_audio():
    """
    GET:Render a simple file-upload form.
    POST: Validate audio, save to uploads/,run Whisper, run Gemma,
            then render summary.html with both transcript and summary.
    """
    if request.method=="POST":
        file = request.files.get("file")
        raw_text = request.form.get("text", "").strip()
        detected_type="txt"
        
        #Only treat the file if it exists and has a filename
        has_file=bool(file and file.filename)

        # If the user did *not* upload a file *and* did *not* paste text:
        if not has_file and not raw_text:
            flash("Please choose a file or enter text to summarize.", "warning")
            return redirect(request.url)

        text_to_summarize = None
        
        # 1. Handle document uploads: PDF, DOC, DOCX, TXT
        if has_file:
            ext=file.filename.rsplit(".",1)[-1].lower()
            if ext =="pdf":
                detected_type="pdf"
                reader=PdfReader(file)
                pages=[page.extract_text() or "" for page in reader.pages]
                text_to_summarize="\n".join(pages)
            elif ext in ["doc", "docx"]:
                detected_type="docx"
                doc=Document(file)
                paras=[p.text for p in doc.paragraphs if p.text]
                text_to_summarize="\n".join(paras)
            elif ext=="txt":
                detected_type="txt"
                #read raw text
                raw=file.read()
                text_to_summarize=raw.decode("utf-8", errors="ignore")
            # NEW: Handle any audio file (including our recorded .webm blob)
            elif ext in ("wav","mp3","m4a","flac","ogg","webm"):
                detected_type="audio"
                # If we have an audio file, we'll save it and run Whisper
                upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
                file.save(upload_path)
                # 2️⃣ transcribe it
                try:
                    text_to_summarize = transcribe_with_whisper(upload_path)
                except Exception as e:
                    flash(f"Whisper transcription failed: {e}", "danger")
                    return redirect(request.url)
                
                
        if not text_to_summarize and raw_text:
            # If the user pasted text, use that
            text_to_summarize = raw_text.strip()


        if not text_to_summarize and has_file and allowed_file(file.filename):
            # If we have a file and it's an audio file, save it
            filename=secure_filename(file.filename)
            upload_path=os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(upload_path)
            
        #1. Run Whisper transcription
            try:
                text_to_summarize=transcribe_with_whisper(upload_path)
            except Exception as e:
                flash(f"Whisper transcription failed: {e}","danger")
                return redirect(request.url)
            
        if not text_to_summarize:
            flash("Unsupported file type or no text to summarize. Please provide a PDF, Word, or text file.", "warning")
            return redirect(request.url)
            #2. Run Gemma summarization
        try:
            summary = summarize_with_gemma(text_to_summarize)
            #persist the "memory" entry
            entry=Entry(entry_type=detected_type, content=text_to_summarize, summary=summary)
            if current_user.is_authenticated:
                entry.user_id=current_user.id
                db.session.add(entry)
                db.session.commit()
        except Exception as e:
            flash(f"Gemma summarization failed: {e}", "danger")
            return redirect(request.url)
        #3. Render a result page showing both transcript and summary
        return render_template("summary.html", transcript=text_to_summarize, summary=summary)
    #If GET, show the upload form
    return render_template("upload.html")
    
@main.route("/history")
@login_required
def history():
    #pull all entries for the current user
    entries=Entry.query.filter(Entry.user_id==current_user.id).order_by(Entry.timestamp.desc()).all()
    return render_template("history.html", entries=entries)
@main.route("/history/<int:id>")
def view_entry(id):
    e = Entry.query.get_or_404(id)
    if e.user_id != current_user.id:
       abort(403)
    return render_template("entry.html", entry=e)

