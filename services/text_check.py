def detect_keywords(email_text):
    phishing_keywords = [
        "дансаа баталгаажуул", "энд дарна уу", "яаралтай", "таны данс", "нууц үг", 
        "картын мэдээлэл", "мөнгө шилжүүлэх", "худалдан авалт", "таны аккаунт", 
        "сугалааны шагнал", "шилжүүлсэн мөнгө", "танд зөвшөөрөл", "хариу илгээх", 
        "таны төлбөр"
    ]
    detected_keywords = [keyword for keyword in phishing_keywords if keyword.lower() in email_text.lower()]
    if detected_keywords:
        return f"Сэжигтэй дараах үгсийг агуулсан: {', '.join(detected_keywords)}"
    return "Сэжигтэй үг олдоогүй."

def detect_urgent_tone(email_text):
    urgency_phrases = [
        "таны данс хаагдана", "шуурхай арга хэмжээ авах", "24 цагийн дотор хариу илгээнэ үү", 
        "эцсийн сануулга", "ямар нэгэн алдаа", "таны мэдээлэл устгах", "зөвшөөрөл өгөх",
        "өөрчлөлт хийгдсэн", "таны шууд хариу шаардлагатай", "таны нэр дээр буруу зүйл боллоо",
        "шалгагдсан"
    ]
    detected_phrases = [phrase for phrase in urgency_phrases if phrase.lower() in email_text.lower()]
    if detected_phrases:
        return f"Яаралтай хэмээх дараах утгыг агуулсан: {', '.join(detected_phrases)}"
    return "Яаралтай хэмээх утга агуулаагүй."

def analyze_text(email_text):
    keyword_check = detect_keywords(email_text)
    urgency_check = detect_urgent_tone(email_text)
    
    results = {
        "keyword_check": keyword_check,
        "urgency_check": urgency_check
    }
    
    return results
