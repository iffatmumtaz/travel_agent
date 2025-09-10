from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, AsyncOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import asyncio

# Load environment
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

# Gemini Client Setup
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Travel Agent Definition
TravelAgent = Agent(
    name="Travel Planner",
    instructions=(
        "You're a smart travel assistant. Based on user preferences, suggest destinations, "
        "create detailed itineraries, estimate budgets, share visa/weather info, and give travel tips. "
        "Always be concise, friendly, and practical."
    )
)

# Async function to get AI-generated travel plan
async def get_travel_plan(prompt):
    try:
        response = await Runner.run(TravelAgent, input=prompt, run_config=config)
        return response.final_output
    except Exception as e:
        return f"❌ Error: {e}"

# Streamlit UI
st.set_page_config(page_title="Travel AI Agent 🌍", page_icon="🧳")

# History
if "travel_history" not in st.session_state:
    st.session_state.travel_history = []

# Sidebar
st.sidebar.title("🌴 Plan Your Trip")
trip_type = st.sidebar.selectbox("Trip Type", ["Adventure",
    "Relaxation",
    "Culture",
    "Food",
    "Nature & Wildlife",
    "Beach & Islands",
    "History & Heritage",
    "Honeymoon",
    "Family Friendly",
    "Luxury",
    "Backpacking",
    "Religious / Spiritual",
    "Solo Travel",
    "Shopping",
    "Festivals & Events"])
days = st.sidebar.slider("Trip Duration", 3, 30, 7)
month = st.sidebar.selectbox("Month", ["June", "July", "August", "September"])
budget = st.sidebar.selectbox("Budget", ["Low", "Medium", "High"])
hint = st.sidebar.text_input("Destination Preference (optional)")
dark_mode = st.sidebar.checkbox("🌗 Dark Mode", value=False)

# Light/Dark styling..
if dark_mode:
    st.markdown("""<style>body { background-color: #0e1117; color: white; }</style>""", unsafe_allow_html=True)


# Pehle banaye gaye plans list ko dikhta h..
st.sidebar.markdown("## ✈️ Past Plans")
for i, item in enumerate(reversed(st.session_state.travel_history), 1):
    st.sidebar.markdown(f"**{i}.** {item['query'][:25]}...")
    if st.sidebar.button(f"View {i}", key=f"view_{i}"):
        st.session_state["viewed_plan"] = item

# View selected plan
if "viewed_plan" in st.session_state:
    vp = st.session_state["viewed_plan"]
    st.subheader("📌 Previous Plan")
    st.markdown(f"**Query:** {vp['query']}")
    st.success(vp["response"])

# Main area
st.title("🧳 Your Personal Trip Planner")
st.markdown("Plan your dream trip with the power of AI. Gemini will guide your journey!")

query = st.text_input("📝 Describe your ideal trip:", placeholder="e.g. 5-day family trip in July with history and food")

if st.button("Get Travel Plan"):
    if not query.strip():
        st.warning("Please describe your trip.")
    else:
        with st.spinner("Planning your trip..."):
            # AI ke liye final prompt banana
            prompt = (
                f"Plan a {days}-day {trip_type.lower()} trip in {month} with a {budget.lower()} budget. "
                f"{'Prefer ' + hint + '.' if hint else ''} {query} "
                "Include destination suggestions, daily itinerary, weather, visa guidance for Pakistani citizens, and travel tips."
            )
            # AI se response lena
            answer = asyncio.run(get_travel_plan(prompt))

             # Is plan ko history me save karne ka work krta h
            st.session_state.travel_history.append({
                "query": query,
                "response": answer
            })

            st.subheader("🌍 Gemini Travel Plan")
            st.success(answer)

# Footer
st.markdown("---")
st.markdown("🌍 **Travel AI Agent** &copy; 2025 | Created by Iffat Mumtaz")
st.markdown("📧 Contact: `mumtaziffat0@gmail.com` | 🔗 [GitHub](https://github.com/iffatmumtaz)")