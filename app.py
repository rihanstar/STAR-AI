from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# --- COLLEGE DATABASE (OFFLINE BRAIN) ---
COLLEGE_DATA = {
    # --- TEACHERS (Synonyms handled smartly now) ---
    ("nirmal", "kdn", "ds teacher", "dbms teacher"): "STAR AI DATABASE: **Prof. K.D. Nirmal** teaches Data Structures (DS) and DBMS.",
    ("kadam", "jlk", "math teacher"): "STAR AI DATABASE: **Prof. J.L. Kadam** teaches Mathematics.",
    ("hon", "ush", "electronics teacher"): "STAR AI DATABASE: **Prof. U.S. Hon** teaches Electronics and Computer Networks (CN).",
    ("aware", "ada", "python teacher"): "STAR AI DATABASE: **Prof. A.D. Aware** teaches Advanced Python.",
    ("aher", "mha", "english teacher"): "STAR AI DATABASE: **Prof. M.H. Aher** teaches OE (English).",
    ("jadhav", "hod"): "STAR AI DATABASE: The HOD of Computer Science (BCS) is **Prof. B.S. Jadhav Sir**.",
    ("thange", "principal"): "STAR AI DATABASE: The Principal of K.J. Somaiya College is **Dr. Vijay Thange Sir**.",
    ("trusty", "trustee"): "STAR AI DATABASE: The Trusty of our college is **Hon. Mr. Sandeep Dada Rohmare**.",

    # --- INFO ---
    ("topper", "rank"): "STAR AI DATABASE: **FYBCS Toppers (2024-25):**<br>• Sem-1: Rihan Pathan (9.45 CGPA)<br>• Sem-2: Srushti Ashtekar (9.73 CGPA)",
    ("admission",): "STAR AI DATABASE: **Admissions Closed.** Usually open from June to August.",
    ("canteen", "food"): "STAR AI DATABASE: **Canteen Menu:**<br>• Vadapav: ₹15<br>• Samosa: ₹15<br>• Tea/Coffee: ₹10",
    ("library",): "STAR AI DATABASE: **Library Timings:** 09:00 AM to 05:00 PM (Mon-Sat).",
    ("cr", "representative", "126"): "STAR AI DATABASE: The Class Representative (CR) is **Rihan Pathan** (Roll No 126).",

    # --- PRACTICAL BATCHES ---
    ("practical", "batch"): """STAR AI DATABASE: **SYBCS Practical Batches (8:30-11:30 AM):**<br>
    • **Mon:** DS(B), Math(A), Py(C), CN(D)<br>
    • **Tue:** DS(C), Math(B), Py(D), CN(E)<br>
    • **Wed:** DS(D), Elec(C), Py(E), CN(F)<br>
    • **Thu:** DS(E), Elec(D), Py(F), CN(A)<br>
    • **Fri:** DS(F), Elec(E), Py(A), CN(B)<br>
    • **Sat:** DS(A), Elec(F), Py(B), CN(C)""",

    # --- DAILY SCHEDULE ---
    ("monday",): "STAR AI DATABASE: **Monday Schedule:**<br>• 08:30-11:30: Practicals (DS-B, Math-A, Py-C, CN-D)<br>• 12:00-01:00: AEC (Hindi)<br>• 01:00-02:00: DS-II (Nirmal Mam)<br>• 02:00-03:00: CC",
    ("tuesday",): "STAR AI DATABASE: **Tuesday Schedule:**<br>• 08:30-11:30: Practicals (DS-C, Math-B, Py-D, CN-E)<br>• 12:00-01:00: AEC (Hindi)<br>• 01:00-02:00: DS-II (Nirmal Mam)<br>• 02:00-03:00: CC",
    ("wednesday",): "STAR AI DATABASE: **Wednesday Schedule:**<br>• 08:30-11:30: Practicals (DS-D, Elec-C, Py-E, CN-F)<br>• 12:00-01:00: Math (JLK) / Elec (USH)<br>• 01:00-02:00: DBMS-II (Nirmal Mam)",
    ("thursday",): "STAR AI DATABASE: **Thursday Schedule:**<br>• 08:30-11:30: Practicals (DS-E, Elec-D, Py-F, CN-A)<br>• 12:00-01:00: Math (JLK) / Elec (USH)<br>• 01:00-02:00: DBMS-II (Nirmal Mam)",
    ("friday",): "STAR AI DATABASE: **Friday Schedule:**<br>• 08:30-11:30: Practicals (DS-F, Elec-E, Py-A, CN-B)<br>• 12:00-01:00: OE English (Aher Mam)<br>• 01:00-02:00: CN (Hon Sir)",
    ("saturday",): "STAR AI DATABASE: **Saturday Schedule:**<br>• 08:30-11:30: Practicals (DS-A, Elec-F, Py-B, CN-C)<br>• 12:00-01:00: OE English (Aher Mam)<br>• 01:00-02:00: Adv. Python (Aware Sir)",
    
    ("timetable", "schedule"): "STAR AI DATABASE: **Timetable Active.** Ask for any day (e.g., 'Monday') or 'Practical Batches'."
}

def get_star_ai_response(user_input):
    user_input_lower = user_input.lower()
    
    # Security Check
    if "sanjivani" in user_input_lower or "ssgm" in user_input_lower:
        return "System Alert: Access Restricted. I am only authorized for K.J. Somaiya."

    # --- SMART MATCHING ALGORITHM ---
    
    # LEVEL 1: STRICT MATCH (Agar user specific question puche)
    # Example: "Monday Practical" -> Dono words match hone chahiye
    for keywords, answer in COLLEGE_DATA.items():
        if len(keywords) > 1: # Only for multi-word keys
            if all(key in user_input_lower for key in keywords):
                return answer

    # LEVEL 2: LOOSE MATCH (Agar user sirf ek naam le)
    # Example: "Nirmal" -> Match ho jayega (KDN ki zaroorat nahi)
    for keywords, answer in COLLEGE_DATA.items():
        if any(key in user_input_lower for key in keywords):
            return answer

    # FALLBACK
    return "⚠️ **OFFLINE MODE:** I can only answer questions about K.J. Somaiya College (Time Table, Teachers, HOD, Fees, etc.). Please check your spelling."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_data = request.json
    question = user_data.get('message', '')
    time.sleep(0.5) 
    answer = get_star_ai_response(question)
    
    if answer:
        answer = answer.replace("**", "").replace("\n", "<br>")
        
    return jsonify({"response": answer})

if __name__ == '__main__':
    app.run(debug=True)

