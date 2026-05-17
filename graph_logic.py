from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv(override=True)

writer_llm = ChatGroq(
    model_name=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    temperature=0.7,
)

editor_llm = ChatGroq(
    model_name=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    temperature=0.0,
)

vision_llm = ChatGroq(
    model_name=os.getenv("LLM_VISION_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    temperature=0.7,
)

PLATFORM_RULES = {
    "Facebook": (
        "Format: Story-telling or listicle post, 150-500 words. "
        "Use emojis moderately. End with a CTA (question or engagement prompt). "
        "Tone should be friendly and viral-worthy. Include 3-5 hashtags at the end."
    ),
    "Instagram": (
        "Format: Short caption, 50-150 words. Start with a strong 1-line hook. "
        "Use plenty of emojis. End with a CTA. "
        "MUST include 15-25 relevant hashtags at the end, one per line."
    ),
    "LinkedIn": (
        "Format: Professional post, 200-600 words. Open with a curiosity-driven hook. "
        "Use bullet points for readability. Tone must be serious and insight-driven. "
        "Use no more than 3 emojis. End with an open-ended networking question."
    ),
    "Blog": (
        "Format: SEO-friendly blog post, 600-1200 words. Include an H1 title and H2/H3 sections. "
        "Engaging introduction, body with concrete examples, conclusion with key takeaways. "
        "No emojis. Professional and detailed language."
    ),
    "Email": (
        "Format: Marketing email, 100-300 words. Compelling subject line (stated at the top). "
        "Content goes straight to the value for the reader. "
        "End with 1 clear CTA button (e.g., [Learn More] or [Sign Up]). "
        "Friendly but professional tone."
    ),
    "Tiktok": (
        "Format: Short video script, 60-90 seconds. Start with a shocking 3-second hook. "
        "Split into short segments (10-15 seconds each). "
        "Use Gen-Z language, trending references. End with a follow/like CTA. "
        "Include 5-10 trending hashtags at the end."
    ),
}


class ContentCreationState(TypedDict):
    topic: str
    platform: str
    tone: str
    keywords: str
    objective: str
    target_audience: str
    brand_voice: str
    cta: str

    input_type: str
    raw_context: str | None
    clean_context: str | None
    image_base64: str | None

    current_draft: str
    editor_feedback: str
    is_approved: bool
    iteration: int


def data_prep_node(state: ContentCreationState):
    """Summarize raw_context into clean_context via LLM."""
    raw_context = state.get("raw_context") or ""
    if not raw_context:
        return {"clean_context": ""}

    sys_prompt = "You are a data analyst. Your task is to read raw text (which may contain junk, ads, HTML code), and extract the technical specifications, main points, or core message."
    user_prompt = f"Please extract the most important information from the following data to use as material for writing a marketing article:\n\n{raw_context}"

    response = writer_llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=user_prompt),
    ])
    return {"clean_context": response.content}


def writer_node(state: ContentCreationState):
    topic = state.get("topic", "")
    platform = state["platform"]
    tone = state["tone"]
    keywords = state["keywords"]
    objective = state.get("objective", "")
    target_audience = state.get("target_audience", "")
    brand_voice = state.get("brand_voice", "")
    cta = state.get("cta", "")
    feedback = state.get("editor_feedback", "")
    iteration = state.get("iteration", 0)
    input_type = state.get("input_type", "topic")
    clean_context = state.get("clean_context") or ""
    image_base64 = state.get("image_base64") or ""

    platform_rules = PLATFORM_RULES.get(platform, "")
    sys_prompt = (
        f"You are an expert Copywriter for {platform}. "
        f"Writing tone: {tone}.\n\n"
        f"PLATFORM RULES:\n{platform_rules}\n\n"
        f"CONTENT BRIEF:\n"
        f"- Objective: {objective or 'General content'}\n"
        f"- Target audience: {target_audience or 'General audience'}\n"
        f"- Brand voice: {brand_voice or 'Default'}\n"
        f"- Desired CTA: {cta or 'None specified'}\n"
        f"\nYou MUST tailor your writing style, vocabulary, and structure to match "
        f"the target audience and brand voice above. If a CTA is specified, "
        f"weave it naturally into the content."
    )
    user_prompt = f"Write content about: '{topic}' using the following reference material:\n{clean_context}"

    if clean_context:
        user_prompt += f"\n\nREFERENCE MATERIAL:\n{clean_context}"
    
    if feedback:
        user_prompt += (
            f"\n\nYour previous draft was REJECTED. Feedback:\n{feedback}\n"
            "Please fix the errors above and rewrite a more perfect version."
        )
        
    if input_type == "image" and image_base64:
        print(f"WRITER (Circle {iteration + 1}): Looking at the image and writing an article for {platform}...")
        message_content = [
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }},
        ]
        response = vision_llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=message_content),
        ])
    else:
        print(f"WRITER (Circle {iteration + 1}): Thinking and writing for {platform}...")
        response = writer_llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=user_prompt),
        ])

    return {
        "current_draft": response.content,
        "iteration": iteration + 1,
        "is_approved": False,
        "editor_feedback": "",
    }


def editor_node(state: ContentCreationState):
    current_draft = state["current_draft"]
    platform = state["platform"]
    keywords = state["keywords"]
    objective = state.get("objective", "")
    target_audience = state.get("target_audience", "")
    brand_voice = state.get("brand_voice", "")
    cta = state.get("cta", "")

    platform_rules = PLATFORM_RULES.get(platform, "")
    sys_prompt = (
        "You are a strict Managing Editor. Review the draft based on:\n"
        f"1. PLATFORM RULES ({platform}):\n{platform_rules}\n"
        f"2. Required keywords: {keywords}\n"
        f"3. Content objective: {objective or 'General'}\n"
        f"4. Target audience: {target_audience or 'General'}\n"
        f"5. Brand voice: {brand_voice or 'Default'}\n"
        f"6. Required CTA: {cta or 'None'}\n\n"
        "OUTPUT RULES:\n"
        "- If the content meets all standards, your output MUST start with exactly: APPROVED\n"
        "- If it needs work, your output MUST start with exactly: REJECTED, followed by detailed feedback."
    )

    user_prompt = f"Draft to review:\n\n{current_draft}"
    response = editor_llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=user_prompt)
    ])

    content = response.content.strip()
    if content.upper().startswith("APPROVED"):
        return {"is_approved": True, "editor_feedback": ""}
    else:
        fb = content[len("REJECTED"):].strip() if content.upper().startswith("REJECTED") else content
        return {"is_approved": False, "editor_feedback": fb}


def routing_logic(state: ContentCreationState):
    if state["is_approved"] == True : return "finish"
    elif state["iteration"] >= 3 : return "finish"
    else: return "rewrite"


workflow = StateGraph(ContentCreationState)
workflow.add_node("data_prep", data_prep_node)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

workflow.set_entry_point("data_prep")
workflow.add_edge("data_prep", "writer")
workflow.add_edge("writer", "editor")
workflow.add_conditional_edges(
    "editor",
    routing_logic,
    {"finish": END, "rewrite": "writer"},
)

content_pipeline = workflow.compile()
