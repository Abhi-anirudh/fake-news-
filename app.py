import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from google import genai
from PIL import Image


app = Flask(__name__)

UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    client = genai.Client()
except Exception as e:
    print("FATAL ERROR: Could not initialize Gemini Client.")
    print(f"Details: {e}")
    print("Please ensure your GEMINI_API_KEY environment variable is set correctly.")
    client = None
    
MODEL_NAME = 'gemini-2.5-flash' 


def create_gemini_prompt(text: str, language: str, mode: str) -> str:
    """Creates the detailed, structured prompt for the Gemini model based on detection mode."""
    
    if mode == 'image':
        prompt_instruction = (
            "You are an expert deepfake detection AI. Analyze the provided 'IMAGE' exclusively. "
            "Determine if the image is an authentic photograph or a computer-generated/manipulated deepfake. "
            "Ignore any missing text input or language selection. Your verdict MUST be based ONLY on the visual analysis."
        )
    elif language == 'hi':
        prompt_instruction = (
            "आप एक विशेषज्ञ तथ्य-जांचकर्ता (fact-checker) हैं। दिए गए 'न्यूज़ टेक्स्ट' और 'इमेज' का विश्लेषण करें। "
            "सटीकता की पुष्टि के लिए Google Search का उपयोग करें। यदि टेक्स्ट झूठा है, भ्रामक है, या इमेज डीपफेक/छेड़छाड़ "
            "की गई है, तो स्पष्ट रूप से 'FALSE' घोषित करें। अन्यथा 'REAL' घोषित करें। अपना जवाब ONLY JSON फॉर्मेट में दें, "
            "जैसा कि 'RESPONSE FORMAT' में परिभाषित है।"
        )
    elif language == 'mr':
        prompt_instruction = (
            "तुम्ही तज्ञ फॅक्ट-चेकर आहात. 'न्यूज टेक्स्ट' आणि 'इमेज'चे विश्लेषण करा. सत्यता तपासण्यासाठी Google Search वापरा. "
            "जर टेक्स्ट खोटा किंवा दिशाभूल करणारा असेल किंवा इमेज डीपफेक/बदललेली असेल, तर स्पष्टपणे 'FALSE' सांगा. "
            "अन्यथा 'REAL' सांगा. फक्त JSON फॉरमॅटमध्ये उत्तर द्या."
        )
    elif language == 'te':
        prompt_instruction = (
            "మీరు నిపుణుడైన ఫ్యాక్ట్-చెకర్. ఇచ్చిన 'న్యూస్ టెక్స్ట్' మరియు 'ఇమేజ్'ను విశ్లేషించండి. ఖచ్చితత్వాన్ని నిర్ధారించడానికి "
            "Google Search ఉపయోగించండి. టెక్స్ట్ తప్పుగా ఉంటే లేదా ఇమేజ్ డీప్‌ఫేక్ అయితే, స్పష్టంగా 'FALSE' అని ప్రకటించండి. "
            "లేదంటే 'REAL' అని ప్రకటించండి. 'RESPONSE FORMAT'లో నిర్వచించినట్లుగా మీ సమాధానాన్ని ONLY JSON ఫార్మాట్‌లో ఇవ్వండి."
        )
    else:
        prompt_instruction = (
            "You are an expert, unbiased fact-checker and deepfake detection AI. Analyze the provided 'NEWS TEXT' "
            "and 'IMAGE' (if provided). Use the Google Search tool to find supporting or refuting evidence for the claims. "
            "Your verdict MUST be based on factual verification and image manipulation analysis. If the text is false/misleading "
            "OR the image is a deepfake/manipulated, declare 'FALSE'. Otherwise, declare 'REAL'. Give your answer ONLY in the "
            "JSON format defined in 'RESPONSE FORMAT'."
        )
        
    text_content = f"--- NEWS TEXT ---\n{text or 'NONE PROVIDED'}"
        
    prompt = f"""
{prompt_instruction}

{text_content}

--- RESPONSE FORMAT ---
{{
  "verdict": "REAL/FALSE",
  "confidence_score": "XX%",
  "reasoning": "A concise summary of why the content is real or fake/deepfake, citing evidence found via Google Search or internal analysis.",
  "claims_status": [
    {{"claim": "Claim 1 extracted from text (if available)", "status": "TRUE/FALSE/UNVERIFIABLE"}}
  ]
}}
"""
    return prompt


@app.route('/predict', methods=['POST'])
def predict():
    """Handles the form submission and calls the Gemini API."""
    if client is None:
        return jsonify({"error": "Gemini API Client failed to initialize. Check API key."}), 500

    news_text = request.form.get('news_text', '')
    language = request.form.get('language')
    image_file = request.files.get('news_image')
    detection_mode = request.form.get('detection_mode')

    
    if detection_mode == 'text' and not news_text.strip():
        return jsonify({"error": "Text input is required for Text Only mode."}), 400
    if detection_mode == 'image' and (not image_file or not image_file.filename):
        return jsonify({"error": "An image file is required for Image Only mode."}), 400
    if detection_mode == 'both' and not news_text.strip():
        return jsonify({"error": "Text input is required for Both mode."}), 400

    contents = []
    temp_image_path = None
    
   
    if image_file and image_file.filename:
        try:
            temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(temp_image_path)
            img = Image.open(temp_image_path)
            contents.append(img)
        except Exception as e:
            return jsonify({"error": f"Error processing image file: {str(e)}"}), 500

   
    if detection_mode == 'image':
        text_for_prompt = "Perform deepfake analysis only. No text verification is needed."
    else:
        text_for_prompt = news_text
        
    prompt = create_gemini_prompt(text_for_prompt, language, detection_mode) 
    contents.append(prompt)

    try:
        tools_config = [{"google_search": {}}] if detection_mode != 'image' else []
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config={"tools": tools_config}
        )

        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        try:
            json_response = json.loads(response.text.strip())
            return jsonify(json_response), 200

        except json.JSONDecodeError:
            match = re.search(r"```json\s*([\s\S]*?)\s*```", response.text)
            if match:
                json_string = match.group(1)
                json_response = json.loads(json_string)
                return jsonify(json_response), 200
            else:
                return jsonify({
                    "error": "Model returned text that could not be parsed as JSON.",
                    "raw_output": response.text
                }), 500

    except Exception as e:
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        error_message = f"Gemini API Error: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500


@app.route('/')
def index_page():
    return send_from_directory('.', 'index.html')

@app.route('/detect.html')
def detect_page():
    return send_from_directory('.', 'detect.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)


if __name__ == '__main__':
    print("\n🚀 Running Flask server. Access at http://127.0.0.1:5000/")
    print("NOTE: Ensure 'GEMINI_API_KEY' is set in your environment variables.")
    app.run(debug=True)
