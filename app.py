from flask import Flask, render_template, request, jsonify
import os
import time
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURATION ---
api_key = os.getenv("GEMINI_API_KEY")

# --- MODEL SETUP ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ CONNECTED TO GEMINI AI")
    except Exception as e:
        model = None
        print(f"❌ API ERROR: {e}")
else:
    model = None

# --- COLLEGE DATABASE (LOCAL DATA) ---
COLLEGE_DATA = {
    # --- 1. FULL PRACTICAL CHART (Sabse Important) ---
    ("practical", "batch", "lab"): """STAR AI DATABASE: **SYBCS Practical Batches (8:30 AM - 11:30 AM):**<br>
    • **Mon:** DS(B), Math(A), Python(C), CN(D)<br>
    • **Tue:** DS(C), Math(B), Python(D), CN(E)<br>
    • **Wed:** DS(D), Elec(C), Python(E), CN(F)<br>
    • **Thu:** DS(E), Elec(D), Python(F), CN(A)<br>
    • **Fri:** DS(F), Elec(E), Python(A), CN(B)<br>
    • **Sat:** DS(A), Elec(F), Python(B), CN(C)""",

    # --- 2. DAILY PRACTICALS (Specific Day Queries) ---
    ("monday", "practical"): "STAR AI DATABASE: **Monday Practicals (8:30-11:30 AM):**<br>• Data Struct: Batch B<br>• Maths: Batch A<br>• Adv Python: Batch C<br>• CN: Batch D",
    
    ("tuesday", "practical"): "STAR AI DATABASE: **Tuesday Practicals (8:30-11:30 AM):**<br>• Data Struct: Batch C<br>• Maths: Batch B<br>• Adv Python: Batch D<br>• CN: Batch E",
    
    ("wednesday", "practical"): "STAR AI DATABASE: **Wednesday Practicals (8:30-11:30 AM):**<br>• Data Struct: Batch D<br>• Electronics: Batch C<br>• Adv Python: Batch E<br>• CN: Batch F",
    
    ("thursday", "practical"): "STAR AI DATABASE: **Thursday Practicals (8:30-11:30 AM):**<br>• Data Struct: Batch E<br>• Electronics: Batch D<br>• Adv Python: Batch F<br>• CN: Batch A",
    
    ("friday", "practical"): "STAR AI DATABASE: **Friday Practicals (8:30-11:30 AM):**<br>• Data Struct: Batch F<br>• Electronics: Batch E<br>• Adv Python: Batch A<br>• CN: Batch B",
    
    ("saturday", "practical"): "STAR AI DATABASE: **Saturday Practicals (8:30-11:30 AM):**<br>• Data Struct: Batch A<br>• Electronics: Batch F<br>• Adv Python: Batch B<br>• CN: Batch C",

    # --- 3. DAILY LECTURE SCHEDULE (Based on Image) ---
    ("monday",): "STAR AI DATABASE: **Monday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS-B, Math-A, Py-C, CN-D)<br>• 12:00-01:00 PM: AEC (Hindi)<br>• 01:00-02:00 PM: DS-II (Prof. Nirmal)<br>• 02:00-03:00 PM: CC",
    
    ("tuesday",): "STAR AI DATABASE: **Tuesday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS-C, Math-B, Py-D, CN-E)<br>• 12:00-01:00 PM: AEC (Hindi)<br>• 01:00-02:00 PM: DS-II (Prof. Nirmal)<br>• 02:00-03:00 PM: CC",
    
    ("wednesday",): "STAR AI DATABASE: **Wednesday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS-D, Elec-C, Py-E, CN-F)<br>• 12:00-01:00 PM: Math (JLK) / Electronics (USH)<br>• 01:00-02:00 PM: DBMS-II (Prof. Nirmal)",
    
    ("thursday",): "STAR AI DATABASE: **Thursday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS-E, Elec-D, Py-F, CN-A)<br>• 12:00-01:00 PM: Math (JLK) / Electronics (USH)<br>• 01:00-02:00 PM: DBMS-II (Prof. Nirmal)",
    
    ("friday",): "STAR AI DATABASE: **Friday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS-F, Elec-E, Py-A, CN-B)<br>• 12:00-01:00 PM: OE English (Prof. Aher)<br>• 01:00-02:00 PM: CN (Prof. Hon)",
    
    ("saturday",): "STAR AI DATABASE: **Saturday Schedule:**<br>• 08:30-11:30 AM: Practicals (DS-A, Elec-F, Py-B, CN-C)<br>• 12:00-01:00 PM: OE English (Prof. Aher)<br>• 01:00-02:00 PM: Adv. Python (Prof. Aware)",

    # --- 4. GENERAL QUERIES ---
    ("timetable", "schedule"): "STAR AI DATABASE: S.Y.B.Sc.(CS) Sem-II Timetable is active (w.e.f 29/12/2025). Ask for any day like 'Monday' or 'Practical Batches'.",
    ("teacher", "faculty"): "STAR AI DATABASE: **Teachers:**<br>• DS/DBMS: Prof. K.D. Nirmal<br>• Math: Prof. J.L. Kadam<br>• Electronics/CN: Prof. U.S. Hon<br>• Python: Prof. A.D. Aware<br>• English: Prof. M.H. Aher",
    ("principle", "principal"): "Star AI DATABASE: The Principal is **Dr. Vijay Thange Sir**.",
    ("library",): "Star AI DATABASE: Library timings: **9:00 AM to 4:15 PM**.",
    ("canteen",): "Star AI DATABASE: Canteen Menu: Vadapav (₹15), Samosa (₹15), Chai (₹5)."
}

def get_star_ai_response(user_input):
    user_input_lower = user_input.lower()
    
    if "sanjivani" in user_input_lower or "ssgm" in user_input_lower:
        return "System Alert: Access Restricted. I am only authorized for K.J. Somaiya."

    # 1. LOCAL DATABASE MATCH
    for keywords, answer in COLLEGE_DATA.items():
        if len(keywords) == 1:
            if keywords[0] in user_input_lower:
                return answer
        else:
            if all(key in user_input_lower for key in keywords):
                return answer

    # 2. AI FALLBACK
    if not api_key:
        return "⚠️ **SYSTEM NOTE:** Local Database se match nahi mila aur API Key missing hai. (Monday/Tuesday try karein)."
    
    if not model:
        return "⚠️ **API ERROR:** Google Gemini API Key Expire ho gayi hai. Nayi Key lagayein."

    try:
        prompt = f"Act as Star AI. Keep it short. User: {user_input}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "⚠️ **API EXPIRED:** Please update GEMINI_API_KEY in Render Dashboard."

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
