def get_domain_from_email(email):
    """Имэйлээс домайн хаягийг гаргах функц"""
    return email.split('@')[-1]
