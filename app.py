# =========================================
# FINAL PRO VERSION: LOGIN + DASHBOARD
# =========================================

from flask import Flask, render_template, request, redirect, session
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = "secret123"

# =========================================
# MODEL
# =========================================
np.random.seed(42)

data = {
    "Study_Hours": np.random.randint(1, 10, 100),
    "Sleep_Hours": np.random.randint(4, 10, 100),
    "Attendance": np.random.randint(50, 100, 100),
    "Previous_Marks": np.random.randint(40, 100, 100)
}

df = pd.DataFrame(data)

df["Final_Marks"] = (
    df["Study_Hours"] * 5 +
    df["Sleep_Hours"] * 2 +
    df["Attendance"] * 0.3 +
    df["Previous_Marks"] * 0.5 +
    np.random.randint(-10, 10, 100)
)

X = df[["Study_Hours", "Sleep_Hours", "Attendance", "Previous_Marks"]]
y = df["Final_Marks"]

model = LinearRegression()
model.fit(X, y)

# =========================================
# FILES
# =========================================
if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["username", "password"]).to_csv("users.csv", index=False)

if not os.path.exists("data.csv"):
    pd.DataFrame(columns=[
        "user", "Study_Hours", "Sleep_Hours",
        "Attendance", "Previous_Marks",
        "Predicted_Marks", "Grade"
    ]).to_csv("data.csv", index=False)

# =========================================
# FUNCTIONS
# =========================================
def get_grade(m):
    if m >= 90: return "A+"
    elif m >= 75: return "A"
    elif m >= 60: return "B"
    elif m >= 50: return "C"
    else: return "Fail"

def get_insights(study, sleep, attendance, marks):
    insights = []
    if study < 4: insights.append("Increase study hours")
    if sleep < 6: insights.append("Improve sleep")
    if attendance < 75: insights.append("Low attendance risk")
    if marks > 85: insights.append("Excellent performance")
    if marks < 50: insights.append("Needs improvement")
    return insights

# =========================================
# ROUTES
# =========================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        users = pd.read_csv("users.csv")

        if ((users["username"] == u) & (users["password"] == p)).any():
            session["user"] = u
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        users = pd.read_csv("users.csv")
        new = pd.DataFrame([{"username": u, "password": p}])
        new.to_csv("users.csv", mode='a', header=False, index=False)

        return redirect("/")

    return render_template("signup.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    result = None
    insights = []
    history = []
    avg = 0

    if request.method == "POST":
        study = float(request.form["study"])
        sleep = float(request.form["sleep"])
        attendance = float(request.form["attendance"])
        prev = float(request.form["previous"])

        pred = model.predict([[study, sleep, attendance, prev]])[0]
        pred = max(0, min(100, pred))

        grade = get_grade(pred)
        insights = get_insights(study, sleep, attendance, pred)

        result = {"marks": round(pred, 2), "grade": grade}

        new = pd.DataFrame([{
            "user": session["user"],
            "Study_Hours": study,
            "Sleep_Hours": sleep,
            "Attendance": attendance,
            "Previous_Marks": prev,
            "Predicted_Marks": pred,
            "Grade": grade
        }])
        new.to_csv("data.csv", mode='a', header=False, index=False)

    df = pd.read_csv("data.csv")
    user_data = df[df["user"] == session["user"]]

    if not user_data.empty:
        history = user_data["Predicted_Marks"].tail(10).tolist()
        avg = round(user_data["Predicted_Marks"].mean(), 2)

    return render_template("dashboard.html",
result=result,
insights=insights,
history=history,
avg=avg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)