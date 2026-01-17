from flask import Flask, render_template, request, jsonify
import os
import time
import google.generativeai as genai

app = Flask(__name__)
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

active_model = None

def configure_genai():
    global active_model
    try:
        genai.configure(api_key=GENAI_API_KEY)
        print("Checking available AI models...")
        
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        priority_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-001', 'models/gemini-pro']
        selected_model_name = next((m for m in priority_models if m in available_models), None)
        
        if not selected_model_name and available_models:
            selected_model_name = available_models[0]
            
        if selected_model_name:
            print(f"✅ SUCCESS: Connected to model '{selected_model_name}'")
            active_model = genai.GenerativeModel(selected_model_name)
        else:
            print("⚠️ WARNING: No compatible Gemini models found.")
            
    except Exception as e:
        print(f"❌ SETUP ERROR: {e}")


configure_genai()


COLLEGE_DATA = {
    ("principle",): "Star AI Database: The Principal of K.J. Somaiya College is **DR. Vijay Thange Sir**.",
    
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
    ("monday", "monday schedule", "mon lectures"): "STAR AI DATABASE: **Monday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-B, Math: Batch-A, Python: Batch-C, CN: Batch-D)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: AEC (Hindi)<br>• 01:00-02:00 PM: DS-II (Prof. K.D. Nirmal)<br>• 02:00-03:00 PM: CC",

    # --- TUESDAY ---
    ("tuesday", "tuesday schedule", "tue lectures"): "STAR AI DATABASE: **Tuesday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-C, Math: Batch-B, Python: Batch-D, CN: Batch-E)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: AEC (Hindi)<br>• 01:00-02:00 PM: DS-II (Prof. K.D. Nirmal)<br>• 02:00-03:00 PM: CC",

    # --- WEDNESDAY ---
    ("wednesday", "wednesday schedule", "wed lectures"): "STAR AI DATABASE: **Wednesday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-D, Elec: Batch-C, Python: Batch-E, CN: Batch-F)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: Math (JLK) / Electronics (USH)<br>• 01:00-02:00 PM: DBMS-II (Prof. K.D. Nirmal)",

    # --- THURSDAY ---
    ("thursday", "thursday schedule", "thu lectures"): "STAR AI DATABASE: **Thursday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-E, Elec: Batch-D, Python: Batch-F, CN: Batch-A)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: Math (JLK) / Electronics (USH)<br>• 01:00-02:00 PM: DBMS-II (Prof. K.D. Nirmal)",

    # --- FRIDAY ---
    ("friday", "friday schedule", "fri lectures"): "STAR AI DATABASE: **Friday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-F, Elec: Batch-E, Python: Batch-A, CN: Batch-B)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: OE English (Prof. M.H. Aher)<br>• 01:00-02:00 PM: CN (Prof. U.S. Hon)",

    # --- SATURDAY ---
    ("saturday", "saturday schedule", "sat lectures"): "STAR AI DATABASE: **Saturday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS: Batch-A, Elec: Batch-F, Python: Batch-B, CN: Batch-C)<br>• 11:30-12:00 PM: Lunch Break<br>• 12:00-01:00 PM: OE English (Prof. M.H. Aher)<br>• 01:00-02:00 PM: Adv. Python (Prof. A.D. Aware)",

    # --- PRACTICAL BATCHES LOGIC ---
    ("practical batches", "batch details", "practicals"): "STAR AI DATABASE: **Practical Batches (8:30-11:30 AM):**<br>• Mon: DS(B), Math(A), Py(C), CN(D)<br>• Tue: DS(C), Math(B), Py(D), CN(E)<br>• Wed: DS(D), Elec(C), Py(E), CN(F)<br>• Thu: DS(E), Elec(D), Py(F), CN(A)<br>• Fri: DS(F), Elec(E), Py(A), CN(B)<br>• Sat: DS(A), Elec(F), Py(B), CN(C)",

    # --- TEACHERS / FACULTY ---
    ("nirmal", "kdn", "ds teacher", "dbms teacher"): "STAR AI DATABASE: Prof. K.D. Nirmal (KDN) teaches Data Structures (DS) and DBMS.",
    ("kadam", "jlk", "math teacher"): "STAR AI DATABASE: Prof. J.L. Kadam (JLK) teaches Mathematics.",
    ("hon", "ush", "electronics teacher", "cn teacher"): "STAR AI DATABASE: Prof. U.S. Hon (USH) teaches Electronics and Computer Networks (CN).",
    ("aware", "ada", "python teacher"): "STAR AI DATABASE: Prof. A.D. Aware (ADA) teaches Advanced Python.",
    ("aher", "mha", "english teacher"): "STAR AI DATABASE: Prof. M.H. Aher (MHA) teaches OE (English).",

    ("trusty",): "Star AI Database: The trusty of our college is **MR.Sandeep Dada Rohmare**."   
}


def get_star_ai_response(user_input):
    user_input_lower = user_input.lower()
    
   
    if "sanjivani" in user_input_lower or "ssgm" in user_input_lower:
        return "System Alert: Access Restricted. I am only authorized to access K.J. Somaiya Database."

  
    for keywords, answer in COLLEGE_DATA.items():
        
        if all(key in user_input_lower for key in keywords):
            return answer

 
    if active_model:
        try:
            prompt = f"Act as Star AI, a smart college assistant. User asks: {user_input}. Answer briefly in 2 lines."
            response = active_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"
    else:
        return "Star AI System Error: Connection to Cloud Brain failed."


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_data = request.json
    question = user_data.get('message')
    time.sleep(1) # Thinking effect
    answer = get_star_ai_response(question)
    

    if answer:
        answer = answer.replace("**", "").replace("\n", "<br>")
        
    return jsonify({"response": answer})

if __name__ == '__main__':

    app.run(debug=True)

