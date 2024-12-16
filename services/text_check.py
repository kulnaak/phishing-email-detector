# import language_tool_python

def detect_keywords(email_text):
    phishing_keywords = ["дансаа баталгаажуул", "энд дарна уу", "яаралтай"]
    detected_keywords = [keyword for keyword in phishing_keywords if keyword.lower() in email_text.lower()]
    if detected_keywords:
        return f"Suspicious keywords detected: {', '.join(detected_keywords)}"
    return "No suspicious keywords found."

# def check_grammar_errors(email_text):
#     tool = language_tool_python.LanguageTool('en-US')
#     matches = tool.check(email_text)
#     if matches:
#         return f"Grammar issues detected: {len(matches)} issues found."
#     return "No grammar issues detected."

def detect_urgent_tone(email_text):
    urgency_phrases = ["таны данс хаагдана", "шуурхай арга хэмжээ авах", "24 цагийн дотор хариу илгээнэ үү", "эцсийн сануулга"]
    detected_phrases = [phrase for phrase in urgency_phrases if phrase.lower() in email_text.lower()]
    if detected_phrases:
        return f"Urgent tone detected: {', '.join(detected_phrases)}"
    return "No urgent tone detected."

def analyze_text(email_text):
    keyword_check = detect_keywords(email_text)
    # grammar_check = check_grammar_errors(email_text)
    urgency_check = detect_urgent_tone(email_text)
    
    results = {
        "keyword_check": keyword_check,
        # "grammar_check": grammar_check,
        "urgency_check": urgency_check
    }
    
    return results


