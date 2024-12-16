import dns.resolver
import re
import ipaddress

"""dns.resolver.resolve(domain, 'MX'): Энэ функц нь өгөгдсөн домайнаас MX (Mail Exchanger) бичиглэлийг шалгаж авдаг. MX бичиглэл нь имэйл хүлээн авах серверийг зааж өгдөг.
   Тайлбар:
   MX бичиглэл нь домайн имэйл хүлээн авах серверүүдийн талаарх мэдээллийг агуулдаг. Хэрэв MX бичиглэл олдвол домайн зөв, бол зөв домайн гэж үзэгдэнэ.
   Хэрэв домайн зөвшөөрөгдсөн MX бичиглэлтэй бол "Valid domain with MX records" гэж буцаана.
   Хэрэв алдаа гарвал, тухайлбал, DNS-сервер хариу өгөхгүй бол Exception авдаг. Тэгэхээр "Domain check error: ..." гэж буцаадаг."""
def check_sender_domain(domain):
    """Имэйл илгээгчийн домайн шалгах функц"""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX') # DNS-ээс MX бичиглэлийг шалгаж байна
        return "Valid domain with MX records" if mx_records else "Invalid domain"
    except Exception as e:
        return f"Domain check error: {e}"
        
        
"""dns.resolver.resolve(domain, 'TXT'): Энэ функц нь өгөгдсөн домайнтай холбоотой TXT бичиглэлийг шалгаж авдаг. TXT бичиглэлүүд нь тухайн домайнтай холбогдсон төрлүүд, өөрийн тохиргоонууд болон нэмэлт мэдээллийг агуулдаг.
   if 'v=spf1' in record.to_text(): Энэ шалгалт нь SPF бичиглэлийг агуулсан эсэхийг шалгадаг. SPF бичиглэл нь "v=spf1" гэж эхэлдэг бөгөөд энэ нь тухайн домайн зөвшөөрсөн имэйл серверүүдийг тодорхойлдог.
   Тайлбар:
   Хэрэв SPF бичиглэл олдвол SPF record found: ... гэж буцаана.
   Хэрэв олдохгүй бол "No SPF record found" гэж буцаана.
   Алдаа гарсан тохиолдолд, Exception хүлээж авч "SPF check error: ..." гэж буцаадаг."""
def check_spf(domain):
    """SPF бичиглэл шалгах функц"""
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for record in txt_records:
            if 'v=spf1' in record.to_text():
                return f"SPF record found: {record.to_text()}"
        return "No SPF record found"
    except Exception as e:
        return f"SPF check error: {e}"


"""default._domainkey.{domain}: Энэ нь DKIM бичиглэлд зориулсан selector хаяг юм. DKIM бол имэйл үйлдлийн бүртгэлтэй холбоотой аюулгүй байдлын бичиглэл бөгөөд тухайн домайнаас гарсан имэйлийн аюулгүй байдлыг баталгаажуулдаг.
   dns.resolver.resolve(dkim_selector, 'TXT'): Энэ функц нь домайны DKIM бичиглэлд зориулсан TXT бичиглэлийг шалгаж авдаг.
   Тайлбар:
   Хэрэв DKIM бичиглэл олдвол "DKIM record found: ..." гэж буцаана.
   Хэрэв DKIM бичиглэл байхгүй бол "No DKIM record found" гэж буцаана.
   Алдаа гарсан тохиолдолд, "DKIM check error: ..." гэж буцаана."""
def check_dkim(domain):
    """DKIM бичиглэл шалгах функц"""
    try:
        dkim_selector = f"default._domainkey.{domain}"
        dkim_record = dns.resolver.resolve(dkim_selector, 'TXT')
        return f"DKIM record found: {dkim_record[0].to_text()}"
    except dns.resolver.NXDOMAIN:
        return "No DKIM record found"
    except Exception as e:
        return f"DKIM check error: {e}"


"""re.search(r"Received: from .* \[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", email_headers): Энэ хэсэг нь имэйлийн headers доторх "Received" мөрөөс IP хаягийг хайж байна. IP хаяг нь [...] тэмдэгтээр хязгаарлагдсан байдаг.
   ipaddress.ip_address(ip): Энэ нь олдсон IP хаягийг шалгаж, түүнийг зөв эсэхийг баталгаажуулдаг. Хэрвээ IP хаяг буруу бол алдаа үүсгэнэ.
   Тайлбар:
   Хэрэв олдсон IP хаяг зөв бол "Valid sender IP: {ip}" гэж буцаана.
   Хэрэв хаяг олоогүй бол "No valid sender IP found" гэж буцаана.
   Алдаа гарсан тохиолдолд "IP extraction error: ..." гэж буцаана."""
def extract_sender_ip(email_headers):
    """Имэйл илгээгчийн IP хаягийг шалгах функц"""
    try:
        match = re.search(r"Received: from .* \[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", email_headers)
        if match:
            ip = match.group(1)
            ipaddress.ip_address(ip)  # Validate IP
            return f"Valid sender IP: {ip}"
        return "No valid sender IP found"
    except Exception as e:
        return f"IP extraction error: {e}"
