from app.models.schemas import SupportedLanguage


QUESTION_BANK = {
    "en": {
        "employment_type": "Are you a full-time employee, contract worker, or gig worker?",
        "dues_period": "For which months or dates were wages not paid?",
        "amount_due": "Approximately how much amount is unpaid?",
        "proof_docs": "Do you have payslips, bank statements, attendance records, or messages from employer?",
        "location": "In which district/state is your workplace located?",
    },
    "hi": {
        "employment_type": "Aap full-time employee, contract worker, ya gig worker hain?",
        "dues_period": "Kin mahino ya dates ka vetan nahi mila?",
        "amount_due": "Lagbhag kitni raashi bachi hui hai?",
        "proof_docs": "Kya aapke paas payslip, bank statement, attendance record, ya employer ke messages hain?",
        "location": "Aapka kaam kis district/state mein hai?",
    },
    "mr": {
        "employment_type": "तुम्ही full-time कर्मचारी, contract worker की gig worker आहात?",
        "dues_period": "कोणत्या महिन्यांचे/दिनांकांचे वेतन मिळाले नाही?",
        "amount_due": "अंदाजे किती रक्कम बाकी आहे?",
        "proof_docs": "तुमच्याकडे payslip, bank statement, attendance record किंवा employer messages आहेत का?",
        "location": "तुमचे काम कोणत्या district/state मध्ये आहे?",
    },
    "ta": {
        "employment_type": "நீங்கள் full-time employee, contract worker, அல்லது gig worker ஆவீர்களா?",
        "dues_period": "எந்த மாதம்/தேதிக்கான சம்பளம் வரவில்லை?",
        "amount_due": "சுமார் எவ்வளவு தொகை நிலுவையில் உள்ளது?",
        "proof_docs": "உங்களிடம் payslip, bank statement, attendance record, அல்லது employer message உள்ளதா?",
        "location": "உங்கள் வேலை எந்த district/state-ல் உள்ளது?",
    },
    "bn": {
        "employment_type": "আপনি কি full-time employee, contract worker, নাকি gig worker?",
        "dues_period": "কোন মাস/তারিখের মজুরি পাননি?",
        "amount_due": "প্রায় কত টাকা বকেয়া আছে?",
        "proof_docs": "আপনার কাছে payslip, bank statement, attendance record, বা employer message আছে কি?",
        "location": "আপনার কর্মস্থল কোন district/state-এ?",
    },
}


def _missing_signals(message: str, district: str | None, state: str | None) -> list[str]:
    text = message.lower()
    missing: list[str] = []
    employment_tokens = {
        "full-time",
        "contract",
        "gig",
        "employee",
        "worker",
        "कर्मचारी",
        "कामगार",
        "नौकरी",
        "रोजगार",
        "ஊழியர்",
        "employee",
        "কর্মী",
        "চাকরি",
    }
    period_tokens = {
        "month",
        "months",
        "date",
        "since",
        "from",
        "period",
        "महिना",
        "महीने",
        "दिनांक",
        "மாதம்",
        "தேதி",
        "মাস",
        "তারিখ",
    }
    proof_tokens = {
        "payslip",
        "bank",
        "statement",
        "attendance",
        "message",
        "email",
        "स्लिप",
        "बैंक",
        "मेसेज",
        "उपस्थिति",
        "बँक",
        "संदेश",
        "வருகை",
        "வங்கி",
        "বার্তা",
        "ব্যাংক",
    }

    if not any(token in text for token in employment_tokens):
        missing.append("employment_type")
    if not any(token in text for token in period_tokens):
        missing.append("dues_period")
    if not any(char.isdigit() for char in text):
        missing.append("amount_due")
    if not any(token in text for token in proof_tokens):
        missing.append("proof_docs")
    if not district and not state:
        missing.append("location")

    return missing


def build_clarifying_questions(
    *,
    message: str,
    language: SupportedLanguage,
    district: str | None,
    state: str | None,
    max_questions: int = 5,
) -> list[str]:
    keys = _missing_signals(message=message, district=district, state=state)
    if not keys:
        return []

    lang_bank = QUESTION_BANK.get(language, QUESTION_BANK["en"])
    questions = [lang_bank[key] for key in keys if key in lang_bank]
    return questions[:max_questions]
