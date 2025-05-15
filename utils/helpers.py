import re
info={}
def extract_info(text):
    print(text,"text")
    # Simply extracting the raw values entered by the user
    # These are the fields we expect to be filled by the user input
    info['name'] = ''
    info['email'] = ''
    info['phone'] = ''
    info['experience'] = ''
    info['position'] = ''
    info['location'] = ''
    info['tech_stack'] = []

    # Add basic keywords and split to match the user-entered data
    text = text.lower()  # Make the input lowercase for uniformity

    # Find and store the name, email, phone, etc. as they appear
    if 'name' in text:
        info['name'] = text.split("name")[-1].strip()

    if 'email' in text:
        info['email'] = text.split("email")[-1].strip()

    if 'phone' in text:
        info['phone'] = text.split("phone")[-1].strip()

    if 'experience' in text:
        info['experience'] = text.split("experience")[-1].strip()

    if 'position' in text:
        info['position'] = text.split("position")[-1].strip()

    if 'location' in text:
        info['location'] = text.split("location")[-1].strip()

    if 'tech_stack' in text or 'skills' in text:
        tech_stack_start = text.split("skills")[-1] if 'skills' in text else text.split("tech_stack")[-1]
        info['tech_stack'] = [tech.strip() for tech in tech_stack_start.split(',')]

    return info



def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", email))



def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\+?\d[\d\s()\-]{7,}\d", phone))


