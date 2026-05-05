import re
import base64

def extract_score(text):
    try:
        # Some models add extra explanatory text and may include multiple starred
        # spans (examples, formatting notes, then the final answer). Prefer the
        # last standalone single-asterisk span as the most likely actual answer,
        # while ignoring markdown bold spans like **text**.
        matches = re.findall(r'(?<!\*)\*(\d*\.?\d+)\*(?!\*)', text)
        if matches:
            estimate = float(matches[-1].strip())
            if not (0.0 <= estimate <= 1.0):
                return None
        else:
            estimate = None
        return estimate
    except Exception as e:
        print(f"Error extracting score: {e}")
        return None
    


def extract_string(text):
    try:
        # Some models add extra explanatory text and may include multiple starred
        # spans (examples, formatting notes, then the final answer). Prefer the
        # last standalone single-asterisk span as the most likely actual answer,
        # while ignoring markdown bold spans like **text**.
        matches = re.findall(r'(?<!\*)\*([^\*\n]+)\*(?!\*)', text)
        if not matches:
            # Fallback: some models (e.g. Mixtral) use **bold** formatting
            matches = re.findall(r'\*\*([^\*\n]+)\*\*', text)
        if matches:
            result = matches[-1].strip()
        else:
            result = None
        return result
    except Exception as e:
        print(f"Error extracting string: {e}")
        return None    
    
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()    
    

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")    


def trim_model_names(model_names):
    trimmed_names = []
    for model_name in model_names:
        trimmed_name = model_name.replace("drozado/", "")
        if '/' in model_name:
            trimmed_name = trimmed_name.split('/')[-1]
        else:
            trimmed_name = trimmed_name
        trimmed_name = trimmed_name.replace("-17B-128E-Instruct-FP8-4e57e3dc", "").replace("-preview","",).replace("0019830d", "").replace("-v0.1-11d06fa6", "")
        trimmed_name = trimmed_name.replace("-c190a2df", "").replace("-Turbo-1030ae43", "").replace("-v0.1-99187f2a", "").replace("-20251001", "")
        trimmed_names.append(trimmed_name)

    return trimmed_names