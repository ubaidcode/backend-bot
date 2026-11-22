import streamlit as st
from google import genai
from google.genai import types
from groq import Groq

# =========================================================
# API KEYS AUR MODELS — APNI KEYS YAHAN PASTE KAREIN
# =========================================================


GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

GEMINI_MODEL = "gemini-3.6-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"

# =========================================================
# BOT INSTRUCTIONS
# =========================================================
SYSTEM_INSTRUCTION = """
You are the official AI Help Assistant for a Daily Task Management website.

ABOUT THE WEBSITE:
This website helps people organize their daily work. Users can create and
assign their own tasks, save tasks for later, set dates and times, work
through their task lists, mark tasks as completed themselves, and review
their pending tasks and overall progress. The purpose is to help users stay
organized, manage their time, remember responsibilities, and complete work
in a planned and disciplined way.

YOUR ROLE:
1. Explain the website's purpose and its task-management features in simple,
   clear, professional language.
2. Guide users on how they can create their own tasks, give tasks a title
   and description, choose a date or time, save them, and later return to
   complete them.
3. Explain how users can mark a task as completed themselves and understand
   pending/completed task lists and progress indicators.
4. Give practical suggestions for planning daily, weekly, study, personal,
   and work-related tasks.
5. Answer normal general questions politely and helpfully.
6. If a question is completely unrelated to the website, you may give a
   brief helpful answer, then politely mention that it is outside the main
   purpose of this Daily Task Management website and guide the user back
   to relevant help.
7. If the user asks how to use a feature that has not been confirmed as
   available, do not pretend it exists. Say that the feature may depend on
   the website's current version.
8. Never claim to know a user's saved tasks, account details, schedule,
   completion status, or personal progress.

STRICT PERMISSIONS:
- You are an information and guidance chatbot only.
- You do NOT have access to the website, user accounts, task records,
  database, authentication, or progress data.
- You cannot create, assign, save, edit, delete, schedule, check off,
  complete, or restore tasks.
- Never say that you have performed any action.
- If a user asks you to perform a task action, explain politely that they
  must do it themselves on the main website.
- Do not ask users to share passwords, OTPs, API keys, or private account data.

RESPONSE STYLE:
- Be professional, respectful, friendly, and easy to understand.
- Prefer concise answers, but explain step by step when the user needs help.
- Use headings or numbered steps when useful.
- Reply in the language used by the user. If the user writes in Roman Urdu,
  reply in Roman Urdu. If the user writes in English, reply in English.
- Do not invent website features, policies, or technical details.
- Stay focused on helping users understand and use the Daily Task Management
  website.
"""

# =========================================================
# STREAMLIT PAGE
# =========================================================
st.set_page_config(
    page_title="Daily Task AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Daily Task AI Assistant")
st.write(
    "Apne Daily Task Management website ke bare mein sawal poochein. "
    "Main aapko features samajhne aur tasks plan karne mein guide kar sakta hoon."
)

with st.sidebar:
    st.header("AI Configuration")
    st.caption("Gemini primary hai. Gemini fail ho to Groq backup automatically try hoga.")

    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def ask_gemini(api_key, model, messages):
    client = genai.Client(api_key=api_key)
    contents = []
    for item in messages:
        role = "user" if item["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=item["content"])]
            )
        )

    result = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.6,
            max_output_tokens=1200
        )
    )
    if not result.text:
        raise RuntimeError("Gemini returned an empty response.")
    return result.text


def ask_groq(api_key, model, messages):
    client = Groq(api_key=api_key)
    groq_messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION}
    ]
    for item in messages:
        groq_messages.append({
            "role": item["role"],
            "content": item["content"]
        })

    result = client.chat.completions.create(
        model=model,
        messages=groq_messages,
        temperature=0.6,
        max_tokens=1200
    )
    answer = result.choices[0].message.content
    if not answer:
        raise RuntimeError("Groq returned an empty response.")
    return answer


prompt = st.chat_input("Apna sawal yahan likhein...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    history_for_request = st.session_state.messages.copy()
    answer = None
    used_provider = None
    errors = []

    with st.chat_message("assistant"):
        with st.spinner("AI jawab tayyar kar raha hai..."):

            # Gemini is the primary provider.
            if GEMINI_API_KEY.strip() and GEMINI_MODEL.strip() and GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE":
                try:
                    answer = ask_gemini(
                        GEMINI_API_KEY.strip(),
                        GEMINI_MODEL.strip(),
                        history_for_request
                    )
                    used_provider = "Gemini"
                except Exception as exc:
                    errors.append(f"Gemini: {str(exc)[:250]}")

            # Automatically try Groq if Gemini is unavailable or fails.
            if answer is None and GROQ_API_KEY.strip() and GROQ_MODEL.strip() and GROQ_API_KEY != "PASTE_YOUR_GROQ_API_KEY_HERE":
                try:
                    answer = ask_groq(
                        GROQ_API_KEY.strip(),
                        GROQ_MODEL.strip(),
                        history_for_request
                    )
                    used_provider = "Groq backup"
                except Exception as exc:
                    errors.append(f"Groq: {str(exc)[:250]}")

            if answer is not None:
                st.markdown(answer)
                st.caption(f"Response provider: {used_provider}")
            else:
                if (GEMINI_API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE" and
                        GROQ_API_KEY == "PASTE_YOUR_GROQ_API_KEY_HERE"):
                    answer = (
                        "Pehle app.py ke top par GEMINI_API_KEY ya GROQ_API_KEY "
                        "variable mein apni API key paste karein."
                    )
                elif (GROQ_API_KEY == "PASTE_YOUR_GROQ_API_KEY_HERE" and errors):
                    answer = (
                        "Gemini API se jawab nahi mil saka aur Groq backup "
                        "key bhi enter nahi ki gayi. API key, model name, "
                        "internet aur API quota check karein."
                    )
                else:
                    answer = (
                        "Dono AI services se jawab nahi mil saka. API keys, "
                        "model names, internet connection aur usage limits "
                        "check karein."
                    )
                st.error(answer)
                if errors:
                    with st.expander("Technical error details"):
                        for error in errors:
                            st.code(error)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

st.divider()
