from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from utils.data_extractors import extract_from_url, extract_from_pdf, extract_from_docx, encode_image_to_base64

from graph_logic import content_pipeline, ContentCreationState

app = FastAPI(title = "Multi-Agent Content Creation API", description="OmniContent AI: automated content generation with topic-based, URL, document, image inputs — multi-agent approval workflow and version tracking.", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate_content")
async def generate_content(
    input_type: str = Form(...), 
    topic: str = Form(...), 
    platform: str = Form(...), 
    tone: str = Form(...), 
    keywords: str = Form(...), 
    objective: str = Form(""),
    target_audience: str = Form(""),
    brand_voice: str = Form(""),
    cta: str = Form(""),
    url: str | None = Form(None), 
    file: UploadFile | None = File(None), 
    image: UploadFile | None = File(None)):
    raw_context = ""
    image_base64 = ""
    
    print(f" GET REQUEST: Start processing input of type '{input_type}'...")

    try:
        if input_type == "url" and url:
            raw_context = extract_from_url(url)
        elif input_type == "pdf" and file:
            file_bytes = await file.read()
            raw_context = extract_from_pdf(file_bytes)
        elif input_type == "docx" and file:
            file_bytes = await file.read()
            raw_context = extract_from_docx(file_bytes)
        elif input_type == "image" and image:
            image_bytes = await image.read()
            image_base64 = encode_image_to_base64(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing input: {str(e)}")

    init_state = ContentCreationState(
        topic = topic,
        platform = platform,
        tone = tone,
        keywords = keywords,
        objective = objective,
        target_audience = target_audience,
        brand_voice = brand_voice,
        cta = cta,
        input_type = input_type,
        raw_context = raw_context,
        clean_context = "",
        image_base64 = image_base64,
        current_draft = "",
        editor_feedback = "",
        is_approved = False,
        iteration = 0,
    )

    print("Initializing the multi-agent pipeline...")
    
    final_state = content_pipeline.invoke(init_state)

    return {
        "status" : "success",
        "platform": final_state["platform"],
        "content": final_state["current_draft"],
        "iterations_count": final_state["iteration"],
        "editor_feedback": final_state["editor_feedback"]
    }
