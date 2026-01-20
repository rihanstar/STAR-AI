from flask import Flask, render_template, request, jsonify
import os
import time
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATION ---
# Render Environment Variable se Key uthayega
api_key = os.getenv("GEMINI_API_KEY")

# --- MODEL SETUP (DIRECT CONNECTION) ---
# Hum complex checking hata kar seedha connect kar rahe hain
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ SUCCESS: Connected to Gemini AI")
    except Exception as e:
        model = None
        print(f"❌ API ERROR: {e}")
else:
    model = None
    print("⚠️ WARNING: GEMINI_API_KEY not found in Render Environment Variables!")

# --- COLLEGE DATABASE (LOCAL DATA) ---
COLLEGE_DATA = {
    ("principle", "principal"): "Star AI Database: The Principal of K.J. Somaiya College is **Dr. Vijay Thange Sir**.",
    
    ("library", "time"): "Star AI Database: Library timings are **9:00 AM to 1:00 PM** and **2:00 PM to 4:15 PM**.",
    
    ("fy", "class"): "Star AI Database: 90% of lectures are held in **Hall S-75 (4th Floor)**.",
    
    ("hod", "bcs"): "Star AI Database: The HOD of the BCS Department is **Mr. Jadhav Sir**.",
    
    ("python", "teacher"): "Star AI Database: The Advance Python teacher for S.Y.B.C.S is **Prof. A.D. Aware**.",
    
    ("topper",): "Star AI Database: For the 2024-25 Batch (FYBCS):\n• Semester 1: **Rihan Pathan** (9.45 CGPA)\n• Semester 2: **Srushti Ashtekar** (9.73 CGPA).",
    
    ("friday", "lecture"): "Star AI Database: On Fridays, S.Y.B.C.S has lectures for **OE (English)** and **Computer Networks**.",
    
    ("cr", "sybcs"): "Star AI Database: The Class Representative (CR) of S.Y.B.C.S is **Rihan Pathan**.",
    
    ("monday", "lecture"): "Star AI Database: On Mondays, lectures are scheduled for **AEC (Hindi)** and **Data Structures**.",
    
    ("admission",): "Star AI Database: **No, admissions are currently closed.** The admission period is typically from June to October.",
    
    ("canteen",): "Star AI Database: Canteen Menu & Prices:\n• Vadapav: ₹15\n• Samosa: ₹15\n• Poha: ₹20\n• Chai: ₹5",
    
    ("126",): "Star AI Database: Roll No. 126 in S.Y.B.C.S belongs to student **Rihan Pathan**.",
    
    ("timing", "sybcs"): "Star AI Database: The timing for S.Y.B.C.S classes is from **12:00 PM to 2:00 PM**.",
    
    ("math", "teacher"): "Star AI Database: The Mathematics teacher for S.Y.B.C.S is **Jayshree Kadam Ma'am**.",

    # --- TIME TABLE & SCHEDULE (S.Y.B.Sc. CS) ---
    ("timetable", "schedule", "routine"): "STAR AI DATABASE: The Time Table for S.Y.B.Sc.(CS) (Sem-II) is active w.e.f 29/12/2025. You can ask for specific days like 'Monday schedule' or 'Practical batches'.",

    # --- MONDAY ---
    ("monday", "schedule"): "STAR AI DATABASE: **Monday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-B, Math: Batch-A, Python: Batch-C, CN: Batch-D)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: AEC (Hindi)<br>• 01:00-02:00 PM: DS-II (Prof. K.D. Nirmal)<br>• 02:00-03:00 PM: CC",

    # --- TUESDAY ---
    ("tuesday", "schedule"): "STAR AI DATABASE: **Tuesday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-C, Math: Batch-B, Python: Batch-D, CN: Batch-E)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: AEC (Hindi)<br>• 01:00-02:00 PM: DS-II (Prof. K.D. Nirmal)<br>• 02:00-03:00 PM: CC",

    # --- WEDNESDAY ---
    ("wednesday", "schedule"): "STAR AI DATABASE: **Wednesday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-D, Elec: Batch-C, Python: Batch-E, CN: Batch-F)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: Math (JLK) / Electronics (USH)<br>• 01:00-02:00 PM: DBMS-II (Prof. K.D. Nirmal)",

    # --- THURSDAY ---
    ("thursday", "schedule"): "STAR AI DATABASE: **Thursday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-E, Elec: Batch-D, Python: Batch-F, CN: Batch-A)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: Math (JLK) / Electronics (USH)<br>• 01:00-02:00 PM: DBMS-II (Prof. K.D. Nirmal)",

    # --- FRIDAY ---
    ("friday", "schedule"): "STAR AI DATABASE: **Friday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-F, Elec: Batch-E, Python: Batch-A, CN: Batch-B)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: OE English (Prof. M.H. Aher)<br>• 01:00-02:00 PM: CN (Prof. U.S. Hon)",

    # --- SATURDAY ---
    ("saturday", "schedule"): "STAR AI DATABASE: **Saturday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-A, Elec: Batch-F, Python: Batch-B, CN: Batch-C)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: OE English (Prof. M.H. Aher)<br>• 01:00-02:00 PM: Adv. Python (Prof. A.D. Aware)",

    # --- TEACHERS ---
    ("nirmal", "kdn", "ds teacher"): "STAR AI DATABASE: Prof. K.D. Nirmal (KDN) teaches Data Structures (DS) and DBMS.",
    ("kadam", "jlk", "math teacher"): "STAR AI DATABASE: Prof. J.L. Kadam (JLK) teaches Mathematics.",
    ("hon", "ush", "electronics teacher"): "STAR AI DATABASE: Prof. U.S. Hon (USH) teaches Electronics and Computer Networks (CN).",
    ("aware", "ada", "python teacher"): "STAR AI DATABASE: Prof. A.D. Aware (ADA) teaches Advanced Python.",
    ("aher", "mha", "english teacher"): "STAR AI DATABASE: Prof. M.H. Aher (MHA) teaches OE (English).",
    ("trusty",): "Star AI Database: The trusty of our college is **Mr. Sandeep Dada Rohmare**."   
}

def get_star_ai_response(user_input):
    user_input_lower = user_input.lower()
    
    # Security Check
    if "sanjivani" in user_input_lower or "ssgm" in user_input_lower:
        return "System Alert: Access Restricted. I am only authorized to access K.J. Somaiya Database."

    # 1. Local Database Match (High Priority)
    for keywords, answer in COLLEGE_DATA.items():
        if all(key in user_input_lower for key in keywords):
            return answer

    # 2. AI Fallback (Jab Local DB mein kuch na mile)
    if not api_key:
        return "⚠️ **SYSTEM ERROR:** Gemini API Key is missing. Check Render Settings."
    
    if not model:
        return "⚠️ **CONNECTION ERROR:** AI Brain is not connected. Please redeploy."

    try:
        # Prompt Engineering: AI ko batana ki wo kaun hai
        prompt = f"Act as Star AI, a helpful college assistant for K.J. Somaiya College. User Query: {user_input}. Keep answer short (max 2 lines)."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **AI ERROR:** Something went wrong. ({str(e)})"


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_data = request.json
    question = user_data.get('message', '')
    
    # Fake Thinking Time (Realism ke liye)
    time.sleep(0.5) 
    
    answer = get_star_ai_response(question)

    if answer:
        # Formatting for Chat
        answer = answer.replace("**", "").replace("\n", "<br>")
        
    return jsonify({"response": answer})

if __name__ == '__main__':
    app.run(debug=True)
