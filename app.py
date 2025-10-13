import streamlit as st
import random, json, datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# ===========================================
# 💪 AI Personalized Workout & Diet Planner
# ===========================================
st.set_page_config(page_title="AI Fitness & Diet Planner", page_icon="🏋️", layout="wide")

# ---- Initialize session state ----
if "history" not in st.session_state:
    st.session_state.history = []

# ---- Sidebar ----
st.sidebar.title("🏠 Navigation")
menu = st.sidebar.radio("Go to:", ["🏋️ Planner", "📜 History"])

# ---------------------------------------------
# BMI Calculation
def calculate_bmi(weight, height):
    if height == 0:
        return 0
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        status = "Underweight 😟"
    elif bmi < 25:
        status = "Normal ✅"
    elif bmi < 30:
        status = "Overweight ⚠️"
    else:
        status = "Obese 🚨"
    return round(bmi, 2), status

# ---------------------------------------------
# Generate AI-like meal suggestion
def generate_meal_plan(region, diet, budget):
    indian_meals = {
        "North": ["Rajma Chawal", "Paneer Bhurji", "Paratha with Curd"],
        "South": ["Idli Sambar", "Curd Rice", "Vegetable Upma"],
        "East": ["Poha", "Dal Khichdi", "Veg Thali"],
        "West": ["Thepla", "Sprout Salad", "Bajra Khichdi"]
    }
    nonveg_addons = ["Grilled Chicken", "Fish Curry", "Egg Bhurji"]
    vegan_addons = ["Tofu Stir Fry", "Soybean Curry"]

    base = indian_meals.get(region, indian_meals["North"])
    meal_plan = random.sample(base, 2)
    if diet == "Non-Vegetarian":
        meal_plan += [random.choice(nonveg_addons)]
    elif diet == "Vegan":
        meal_plan += [random.choice(vegan_addons)]
    return meal_plan

# ---------------------------------------------
# Generate workout plan
def generate_workout(goal, equipment):
    workouts = {
        "Weight Loss": ["Cardio", "Jump Rope", "HIIT", "Burpees", "Mountain Climbers"],
        "Muscle Gain": ["Pushups", "Squats", "Bench Press", "Deadlifts", "Lunges"],
        "Stay Fit": ["Yoga", "Cycling", "Stretching", "Jogging", "Planks"]
    }
    chosen = random.sample(workouts[goal], 3)
    if equipment == "None":
        chosen = [w for w in chosen if w not in ["Bench Press", "Deadlifts"]]
    return chosen[:3]

# ---------------------------------------------
# Generate downloadable PDF report
def generate_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "AI Workout & Diet Planner Report")

    c.setFont("Helvetica", 12)
    text = [
        f"Name: {data['name']}",
        f"Goal: {data['goal']}",
        f"Diet: {data['diet']}",
        f"Region: {data['region']}",
        f"BMI: {data['bmi']} ({data['bmi_status']})",
        "Workout Plan:",
        *[f"  - {w}" for w in data['workout']],
        "Diet Plan:",
        *[f"  - {m}" for m in data['meals']]
    ]
    y = 700
    for line in text:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

# ---------------------------------------------
# MAIN UI SECTION
if menu == "🏋️ Planner":
    st.title("🏋️ Personalized Workout & Diet Planner with AI")
    st.write("Get a personalized plan with Indian food suggestions and a detailed health report.")

    with st.form("fitness_form"):
        name = st.text_input("👤 Name")
        age = st.number_input("🎂 Age", 10, 80)
        weight = st.number_input("⚖️ Weight (kg)", 20, 200)
        height = st.number_input("📏 Height (cm)", 100, 220)
        goal = st.selectbox("🎯 Goal", ["Weight Loss", "Muscle Gain", "Stay Fit"])
        diet = st.selectbox("🍱 Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        region = st.selectbox("🌍 Region", ["North", "South", "East", "West"])
        budget = st.selectbox("💰 Budget", ["Low", "Medium", "High"])
        equipment = st.selectbox("🏋️ Equipment", ["None", "Basic (Dumbbells)", "Full Gym Access"])
        submitted = st.form_submit_button("✨ Generate Plan")

    if submitted:
        bmi, bmi_status = calculate_bmi(weight, height)
        workout = generate_workout(goal, equipment)
        meals = generate_meal_plan(region, diet, budget)
        plan = {
            "name": name,
            "goal": goal,
            "diet": diet,
            "region": region,
            "bmi": bmi,
            "bmi_status": bmi_status,
            "workout": workout,
            "meals": meals,
            "date": str(datetime.date.today())
        }

        st.session_state.history.append(plan)

        st.subheader("📊 BMI Result")
        st.info(f"Your BMI is **{bmi}** ({bmi_status})")

        st.subheader("🏋️ Workout Plan")
        st.write(", ".join(workout))

        st.subheader("🥗 Meal Plan")
        st.write(", ".join(meals))

        pdf_data = generate_pdf(plan)
        st.download_button("📥 Download PDF Report", data=pdf_data, file_name="fitness_plan.pdf")

# ---------------------------------------------
# HISTORY SECTION
elif menu == "📜 History":
    st.title("📜 Your Past Plans")
    if len(st.session_state.history) == 0:
        st.warning("No plans generated yet.")
    else:
        for idx, h in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"📅 {h['date']} — {h['name']} ({h['goal']})"):
                st.write(f"**BMI:** {h['bmi']} ({h['bmi_status']})")
                st.write(f"**Workout:** {', '.join(h['workout'])}")
                st.write(f"**Meals:** {', '.join(h['meals'])}")
