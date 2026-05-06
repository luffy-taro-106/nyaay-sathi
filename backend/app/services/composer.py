from app.models.schemas import CaseCategory, LegalSource, OrchestrateResponse, SupportedLanguage


DISCLAIMER_EN = "This is legal information, not legal advice."

DISCLAIMER_BY_LANG = {
    "en": DISCLAIMER_EN,
    "hi": "Yeh kanooni jankari hai, kanooni salaah nahi.",
    "mr": "ही कायदेशीर माहिती आहे, कायदेशीर सल्ला नाही.",
    "ta": "இது சட்ட தகவல் மட்டுமே; சட்ட ஆலோசனை அல்ல.",
    "bn": "এটি আইনি তথ্য, আইনি পরামর্শ নয়।",
}

TEXT_BY_LANG = {
    "en": {
        "out_scope": (
            "This query is outside the current pilot scope. "
            "Nyaay Sathi currently covers: employment & wages, property & tenancy, "
            "women's protection, consumer fraud, and police & FIR."
        ),
        "out_scope_limit": "Limitation depends on your issue; please verify with DLSA.",
        "out_scope_template": "Please describe your issue for manual complaint drafting support.",
        "clarify": "I need a few more details before giving precise forum, documents, and timeline guidance.",
        "clarify_hint": "Share details soon so we can provide accurate next legal steps quickly.",
        "clarify_template": "Will be generated after your answers.",
        "no_sources": "I could not find enough verified legal sources for this specific query. Please contact DLSA or NyayaBandhu for human legal assistance.",
        "no_sources_limit": "Please file early to avoid delay-related legal limitations.",
        "no_sources_template": "Please use assisted/manual drafting with legal aid support.",
        "emp_rights": "You may have a right to timely and fair wages, including minimum wage protections and lawful grievance channels.",
        "limitation": "File quickly after non-payment or unlawful termination; delays can weaken recovery and evidence.",
        "complaint_subject": "Subject: Complaint regarding non-payment of wages",
        "dlsa": "DLSA (district office)",
        "nyayabandhu": "NyayaBandhu portal",
        "id_proof": "Any ID proof",
        "complaint_papers": "Relevant complaint papers (if any)",
        "id_proof_simple": "ID proof",
        "any_docs": "Any available documents related to your issue",
        "dlsa_help": "District Legal Services Authority (DLSA) help desk",
        "category_template_body": (
            "I am submitting this complaint regarding the above issue. "
            "Please take necessary action as per applicable law.\n\n"
            "Attached: supporting documents and communication records."
        ),
        "free_aid_dlsa_in": "DLSA in {district}",
        "free_aid_nyayabandhu": "NyayaBandhu pro bono legal support",
        "fallback_intro": (
            "I've lined up a few ideas from general materials we keep on common issues. "
            "They are not a tailored read of your exact story, so please sense-check with DLSA or a lawyer."
        ),
        "fallback_limit": (
            "Deadlines depend on the exact facts—if something feels urgent, ask DLSA or a court help desk soon."
        ),
        "fallback_template": (
            "Draft outline: parties, dates, what happened, what relief you want, and key evidence. "
            "Legal aid clinics can help finalize wording."
        ),
        "illustrative_note": (
            "Some lines below are anonymized district-level patterns from our notes—not court judgments and not predictions."
        ),
        "meta_rights": (
            "I'm an AI assistant called Nyaay Sathi. I explain everyday Indian legal options in plain language—I'm not a "
            "lawyer and I don't decide who wins a case. I can help with wages and job issues, rent and eviction, women's "
            "safety laws, consumer or refund problems, and police or FIR trouble: sensible first steps, places like DLSA "
            "or the right office, papers people usually gather, and how complaints often begin. When you're ready, tell me "
            "your district and what happened in your own words—I'll ask a few gentle questions if I need more detail."
        ),
        "meta_limit": (
            "If someone is in danger or a deadline feels urgent, reach emergency services or DLSA—don't wait only on this chat."
        ),
        "meta_template": (
            "In your own words: who was involved, what happened, roughly when, your district, and what you want next."
        ),
    },
    "hi": {
        "out_scope": (
            "Yeh sawal abhi pilot scope ke bahar hai. Nyaay Sathi abhi cover karta hai: "
            "employment & wages, property & tenancy, women's protection, consumer fraud, aur police & FIR."
        ),
        "out_scope_limit": "Limitation aapke issue par nirbhar karta hai; kripya DLSA se verify karein.",
        "out_scope_template": "Manual complaint drafting ke liye apni samasya batayein.",
        "clarify": "Sahi forum, documents aur timeline batane ke liye mujhe kuch aur jaankari chahiye.",
        "clarify_hint": "Kripya details jaldi share karein taaki sahi kanooni agla kadam bataya ja sake.",
        "clarify_template": "Aapke jawab ke baad template banaya jayega.",
        "no_sources": "Is specific query ke liye paryapt verified legal sources nahi mile. Kripya DLSA ya NyayaBandhu se human madad lein.",
        "no_sources_limit": "Kripya jaldi file karein taaki deri ki wajah se kanooni limitation na lage.",
        "no_sources_template": "Kripya legal aid ki madad se manual drafting karein.",
        "emp_rights": "Aapko samay par aur uchit vetan ka adhikar ho sakta hai, jisme minimum wage suraksha aur kanooni grievance channels shamil hain.",
        "limitation": "Non-payment ya unlawful termination ke baad jaldi file karein; deri se evidence aur recovery weak ho sakti hai.",
        "complaint_subject": "Vishay: Vetan na milne ke sambandh mein shikayat",
        "dlsa": "DLSA (zila karyalay)",
        "nyayabandhu": "NyayaBandhu portal",
        "id_proof": "Koi bhi pehchan patra",
        "complaint_papers": "Sambandhit shikayat ke kagazat (agar hain)",
        "id_proof_simple": "Pehchan patra",
        "any_docs": "Aapke issue se sambandhit koi bhi available documents",
        "dlsa_help": "Zila Legal Services Authority (DLSA) help desk",
        "category_template_body": (
            "Main yeh shikayat upar diye gaye vishay ke sambandh mein prastut kar raha/rahi hoon. "
            "Kripya lagu kanoon ke anusar avashyak karyavahi karein.\n\n"
            "Sanlagn: sahayak documents aur communication records."
        ),
        "free_aid_dlsa_in": "{district} ka DLSA",
        "free_aid_nyayabandhu": "NyayaBandhu pro bono kanooni sahayata",
        "fallback_intro": (
            "Maine aam maslon ke saamanya notes se kuch points jode hain; yeh aapki poori sthiti ka "
            "personal jawab nahi—DLSA ya yogya vakil se zaroor sahi karein."
        ),
        "fallback_limit": (
            "Samay seema aapke tathyon par nirbhar karti hai—agar jaldi lage to DLSA ya court help desk se poochh lein."
        ),
        "fallback_template": (
            "Draft: paksh, tithiyan, kya hua, kya maang hai, aur mukhya saboot. Legal aid clinic wording finalize karne mein madad kar sakti hai."
        ),
        "illustrative_note": (
            "Kuch lines anonymized zila-level patterns hain hamare notes se—yeh court judgment ya bhavishyavani nahi hain."
        ),
        "meta_rights": (
            "Main ek AI assistant hoon, naam Nyaay Sathi. Main rozmarra ke Indian legal options ko seedhi bhasha mein samjhata/samjhati "
            "hoon—main vakil nahi hoon aur yeh tay nahi karta ki case kaun jeetega. Vetan/naukri, kiraya/bedkhali, mahila suraksha, "
            "consumer/refund, police/FIR jaise mamalon mein agla kadam, DLSA ya sahi daftar, kagazat aur shikayat shuru karne ka "
            "dhancha bata sakta hoon. Jab aap taiyyar hon, apna zila aur apni kahani apne shabdon mein batayein—zarurat ho to main "
            "kuch saaf sawal poochhunga."
        ),
        "meta_limit": (
            "Agar khatra lagta hai ya samay kam ho to turant emergency ya DLSA se sampark karein—sirf chat par bharosa na karein."
        ),
        "meta_template": (
            "Apne shabdon mein: kaun shamil tha, kya hua, kab tak, zila, aur aap kya chahte hain."
        ),
    },
    "mr": {
        "out_scope": (
            "हा प्रश्न सध्या पायलटच्या कक्षेबाहेर आहे. Nyaay Sathi सध्या कव्हर करते: "
            "employment & wages, property & tenancy, women's protection, consumer fraud आणि police & FIR."
        ),
        "out_scope_limit": "Limitation तुमच्या प्रश्नावर अवलंबून आहे; कृपया DLSA कडून पडताळा.",
        "out_scope_template": "Manual complaint drafting साठी तुमची समस्या सांगा.",
        "clarify": "अचूक forum, documents आणि timeline सांगण्यासाठी मला अजून काही माहिती हवी आहे.",
        "clarify_hint": "कृपया माहिती लवकर द्या, म्हणजे योग्य कायदेशीर पुढील पावले देता येतील.",
        "clarify_template": "तुमच्या उत्तरांनंतर template तयार होईल.",
        "no_sources": "या प्रश्नासाठी पुरेसे verified legal sources मिळाले नाहीत. कृपया DLSA किंवा NyayaBandhu कडून मानव मदत घ्या.",
        "no_sources_limit": "कृपया लवकर तक्रार दाखल करा, म्हणजे विलंबामुळे कायदेशीर limitation लागू होणार नाही.",
        "no_sources_template": "कृपया legal aid च्या मदतीने manual drafting करा.",
        "emp_rights": "तुम्हाला वेळेवर आणि योग्य वेतनाचा अधिकार असू शकतो, ज्यात minimum wage संरक्षण आणि कायदेशीर grievance channels समाविष्ट आहेत.",
        "limitation": "वेतन न मिळणे किंवा बेकायदेशीर सेवासमाप्तीनंतर लवकर तक्रार करा; उशीर झाल्यास पुरावे आणि recovery कमकुवत होऊ शकते.",
        "complaint_subject": "विषय: वेतन न मिळाल्याबाबत तक्रार",
        "dlsa": "DLSA (जिल्हा कार्यालय)",
        "nyayabandhu": "NyayaBandhu portal",
        "id_proof": "कोणताही ओळखपत्र",
        "complaint_papers": "संबंधित तक्रारीची कागदपत्रे (असल्यास)",
        "id_proof_simple": "ओळखपत्र",
        "any_docs": "तुमच्या प्रश्नाशी संबंधित उपलब्ध कागदपत्रे",
        "dlsa_help": "जिल्हा Legal Services Authority (DLSA) help desk",
        "category_template_body": (
            "मी ही तक्रार वरील विषयासंदर्भात सादर करत आहे. "
            "कृपया लागू कायद्यानुसार आवश्यक कारवाई करा.\n\n"
            "संलग्न: सहाय्यक कागदपत्रे आणि communication records."
        ),
        "free_aid_dlsa_in": "{district} मधील DLSA",
        "free_aid_nyayabandhu": "NyayaBandhu pro bono कायदेशीर सहाय्य",
        "fallback_intro": (
            "सामान्य विषयांसाठी आमच्याकडे असलेल्या साहित्यातून काही मुद्दे मी जोडले आहेत; "
            "हे तुमच्या नेमक्या प्रकरणाचे वैयक्तिक उत्तर नाही—DLSA किंवा पात्र वकीलाकडे खात्री करा."
        ),
        "fallback_limit": (
            "मुदती तुमच्या तथ्यांवर अवलंबून असतात—तातडी वाटल्यास लवकर DLSA किंवा न्यायालयीन मदतकेंद्राशी संपर्क करा."
        ),
        "fallback_template": (
            "मसुदा: पक्ष, तारखा, काय घडले, कोणती मागणी, मुख्य पुरावे. कायदेशीर मदत केंद्रे मजकूर अंतिम करण्यास मदत करू शकतात."
        ),
        "illustrative_note": (
            "काही ओळी अनामित जिल्हा-स्तरीय नमुने आहेत आमच्या नोंदींमधून—न्यायालयीन निकाल किंवा भाकित नाहीत."
        ),
        "meta_rights": (
            "मी Nyaay Sathi नावाची AI सहाय्यक आहे. रोजच्या भारतीय कायदेशीर पर्यायांबद्दल सोप्या भाषेत माहिती देतो—वकील नाही आणि "
            "कोण जिंकेल ते ठरवत नाही. वेतन/नोकरी, भाडे/बेदखली, महिला सुरक्षा, ग्राहक/परतावा, पोलीस/FIR यांसारख्या गोष्टींमध्ये पुढचे पाऊल, "
            "DLSA किंवा योग्य कार्यालय, कागदपत्रे आणि तक्रार कशी सुरू होते हे सांगू शकते. तुम्ही तयार असाल तेव्हा जिल्हा आणि घडलेले "
            "तुमच्या शब्दात सांगा—गरज असल्यास मी काही प्रश्न विचारेन."
        ),
        "meta_limit": (
            "धोका वाटत असेल किंवा वेळ कमी असेल तर त्वरित आपत्कालीन किंवा DLSA शी संपर्क करा—फक्त चॅटवर अवलंबून राहू नका."
        ),
        "meta_template": (
            "तुमच्या भाषेत: कोण होते, काय घडले, अंदाजे केव्हा, जिल्हा, आणि पुढे काय हवे आहे."
        ),
    },
    "ta": {
        "out_scope": (
            "இந்த கேள்வி தற்போதைய பைலட் வரம்பிற்கு வெளியே உள்ளது. Nyaay Sathi தற்போது: "
            "employment & wages, property & tenancy, women's protection, consumer fraud, police & FIR ஆகியவற்றை உள்ளடக்குகிறது."
        ),
        "out_scope_limit": "Limitation உங்கள் சிக்கலைப் பொறுத்தது; தயவுசெய்து DLSA-ஐ உறுதி செய்க.",
        "out_scope_template": "Manual complaint drafting-க்கு உங்கள் சிக்கலை விளக்குக.",
        "clarify": "சரியான forum, documents மற்றும் timeline சொல்ல நான் இன்னும் சில தகவல்கள் தேவைப்படுகிறது.",
        "clarify_hint": "தயவுசெய்து தகவலை விரைவில் பகிரவும்; சரியான சட்ட அடுத்த படிகளை சொல்ல முடியும்.",
        "clarify_template": "உங்கள் பதில்களுக்குப் பிறகு template உருவாக்கப்படும்.",
        "no_sources": "இந்த கேள்விக்கு போதுமான verified legal sources கிடைக்கவில்லை. தயவுசெய்து DLSA அல்லது NyayaBandhu மூலம் மனித உதவி பெறவும்.",
        "no_sources_limit": "தாமதத்தால் சட்ட limitation ஏற்படாதவாறு விரைவில் புகார் செய்யவும்.",
        "no_sources_template": "தயவுசெய்து legal aid உதவியுடன் manual drafting செய்யவும்.",
        "emp_rights": "காலத்திற்கு சம்பளம் மற்றும் நியாயமான கூலி பெறும் உரிமை உங்களுக்கு இருக்கலாம்; இதில் minimum wage பாதுகாப்பும் சட்ட grievance வாயில்களும் அடங்கும்.",
        "limitation": "சம்பளம் வழங்காதது அல்லது சட்டவிரோத பணிநீக்கம் ஏற்பட்டால் விரைவாக புகார் செய்யவும்; தாமதம் ஆதாரத்தையும் மீட்பையும் பலவீனப்படுத்தும்.",
        "complaint_subject": "பொருள்: சம்பளம் வழங்காதது குறித்த புகார்",
        "dlsa": "DLSA (மாவட்ட அலுவலகம்)",
        "nyayabandhu": "NyayaBandhu portal",
        "id_proof": "ஏதேனும் அடையாளச் சான்று",
        "complaint_papers": "தொடர்புடைய புகார் ஆவணங்கள் (இருந்தால்)",
        "id_proof_simple": "அடையாளச் சான்று",
        "any_docs": "உங்கள் சிக்கல் தொடர்பான கிடைக்கும் ஆவணங்கள்",
        "dlsa_help": "மாவட்ட Legal Services Authority (DLSA) help desk",
        "category_template_body": (
            "மேற்கண்ட பிரச்சினை குறித்து இந்த புகாரை சமர்ப்பிக்கிறேன். "
            "பொருந்தும் சட்டப்படி தேவையான நடவடிக்கை எடுக்கவும்.\n\n"
            "இணைப்பு: ஆதரவு ஆவணங்கள் மற்றும் communication records."
        ),
        "free_aid_dlsa_in": "{district}-ல் DLSA",
        "free_aid_nyayabandhu": "NyayaBandhu pro bono சட்ட உதவி",
        "fallback_intro": (
            "பொதுவான தலைப்புகளுக்கான எங்கள் பின்னணிப் பொருட்களிலிருந்து சில யோசனைகளை இணைத்துள்ளேன்; "
            "இது உங்கள் சூழலுக்கு தனிப்பயன் அல்ல—DLSA அல்லது தகுதியான வழக்கறிஞரிடம் சரிபார்க்கவும்."
        ),
        "fallback_limit": (
            "காலக்கெடுக்கள் உங்கள் உண்மைகளைப் பொறுத்தவை—அவசரமாகத் தோன்றினால் விரைவில் DLSA அல்லது நீதிமன்ற உதவி மையத்தை அணுகவும்."
        ),
        "fallback_template": (
            "வரைவு: தரப்பினர், தேதிகள், நடந்தது, என்ன நிவாரணம், முக்கிய ஆதாரங்கள். சட்ட உதவி மையங்கள் வாசகத்தை இறுதி செய்ய உதவும்."
        ),
        "illustrative_note": (
            "சில வரிகள் மாவட்ட-நிலை மாதிரிகள்—நீதிமன்ற தீர்ப்புகள் அல்ல; முடிவு உறுதியும் அல்ல."
        ),
        "meta_rights": (
            "நான் Nyaay Sathi என்ற AI உதவியாளர். இந்தியாவில் அன்றாட சட்டப் பாதைகளை எளிய மொழியில் விளக்குகிறேன்—வழக்கறிஞர் அல்ல; "
            "யார் வெல்வார்கள் என்று சொல்ல மாட்டேன். சம்பளம்/வேலை, வாடகை/காலி செய்தல், பெண்கள் பாதுகாப்பு, நுகர்வோர்/பணத்திரும்பப்பெறுதல், "
            "காவல்/FIR போன்றவற்றில் அடுத்த படி, DLSA அல்லது சரியான அலுவலகம், ஆவணங்கள், புகார் எப்படி தொடங்குவது என்று உதவுகிறேன். "
            "தயாராகும்போது மாவட்டமும் நடந்தது உங்கள் வார்த்தைகளிலும் சொல்லுங்கள்—தேவையானால் சில கேள்விகள் கேட்பேன்."
        ),
        "meta_limit": (
            "அபாயம் தோன்றினால் அல்லது காலக்கெடு அவசரமாக இருந்தால் உடனே அவசர உதவி அல்லது DLSA-ஐ அணுகுங்கள்—அரட்டையை மட்டும் நம்பாதீர்கள்."
        ),
        "meta_template": (
            "உங்கள் வார்த்தைகளில்: யார் யார், என்ன நடந்தது, ஏறக்குறைய எப்போது, மாவட்டம், அடுத்து என்ன வேண்டும்."
        ),
    },
    "bn": {
        "out_scope": (
            "এই প্রশ্নটি বর্তমান পাইলটের আওতার বাইরে। Nyaay Sathi এখন কভার করে: "
            "employment & wages, property & tenancy, women's protection, consumer fraud এবং police & FIR।"
        ),
        "out_scope_limit": "Limitation আপনার সমস্যার উপর নির্ভর করে; দয়া করে DLSA থেকে যাচাই করুন।",
        "out_scope_template": "Manual complaint drafting-এর জন্য আপনার সমস্যা বর্ণনা করুন।",
        "clarify": "সঠিক forum, documents এবং timeline জানাতে আমার আরও কিছু তথ্য দরকার।",
        "clarify_hint": "দয়া করে দ্রুত তথ্য শেয়ার করুন, তাহলে সঠিক আইনি পরবর্তী পদক্ষেপ জানাতে পারব।",
        "clarify_template": "আপনার উত্তরের পরে template তৈরি হবে।",
        "no_sources": "এই নির্দিষ্ট প্রশ্নের জন্য পর্যাপ্ত verified legal sources পাওয়া যায়নি। দয়া করে DLSA বা NyayaBandhu থেকে মানব সহায়তা নিন।",
        "no_sources_limit": "দয়া করে দ্রুত অভিযোগ দাখিল করুন, যাতে দেরির কারণে আইনি limitation না হয়।",
        "no_sources_template": "দয়া করে legal aid-এর সাহায্যে manual drafting করুন।",
        "emp_rights": "আপনার সময়মতো এবং ন্যায্য মজুরি পাওয়ার অধিকার থাকতে পারে, যার মধ্যে minimum wage সুরক্ষা এবং আইনি grievance চ্যানেল অন্তর্ভুক্ত।",
        "limitation": "মজুরি না পাওয়া বা বেআইনি চাকরিচ্যুতির পরে দ্রুত অভিযোগ করুন; দেরি হলে প্রমাণ ও recovery দুর্বল হতে পারে।",
        "complaint_subject": "বিষয়: মজুরি না পাওয়া সংক্রান্ত অভিযোগ",
        "dlsa": "DLSA (জেলা অফিস)",
        "nyayabandhu": "NyayaBandhu portal",
        "id_proof": "যেকোনো পরিচয়পত্র",
        "complaint_papers": "সংশ্লিষ্ট অভিযোগের কাগজপত্র (যদি থাকে)",
        "id_proof_simple": "পরিচয়পত্র",
        "any_docs": "আপনার সমস্যা সম্পর্কিত উপলব্ধ যেকোনো নথি",
        "dlsa_help": "জেলা Legal Services Authority (DLSA) help desk",
        "category_template_body": (
            "আমি উপরের সমস্যা সম্পর্কে এই অভিযোগটি দাখিল করছি। "
            "প্রযোজ্য আইন অনুযায়ী প্রয়োজনীয় ব্যবস্থা গ্রহণ করুন।\n\n"
            "সংযুক্ত: সহায়ক নথি এবং communication records."
        ),
        "free_aid_dlsa_in": "{district}-এ DLSA",
        "free_aid_nyayabandhu": "NyayaBandhu pro bono আইনি সহায়তা",
        "fallback_intro": (
            "সাধারণ বিষয়ের উপাদান থেকে কয়েকটি ধারণা আমি জুড়ে দিয়েছি; এটি আপনার নির্দিষ্ট অবস্থার জন্য "
            "ব্যক্তিগত পরামর্শ নয়—DLSA বা যোগ্য আইনজীবীর কাছে যাচাই করুন।"
        ),
        "fallback_limit": (
            "সময়সীমা আপনার ঘটনার উপর নির্ভর করে—জরুরি মনে হলে দ্রুত DLSA বা আদালত সহায়তা ডেস্কে জিজ্ঞাসা করুন।"
        ),
        "fallback_template": (
            "খসড়া: পক্ষ, তারিখ, কী ঘটেছে, কী প্রতিকার চান, মূল প্রমাণ। আইনি সহায়তা ক্লিনিক শব্দচয়ন চূড়ান্ত করতে সাহায্য করতে পারে।"
        ),
        "illustrative_note": (
            "কিছু লাইন জেলা-স্তরের নামহীন নমুনা—আদালতের রায় বা ভবিষ্যদ্বাণী নয়।"
        ),
        "meta_rights": (
            "আমি Nyaay Sathi নামে একটি AI সহকারী। আমি ভারতে প্রচলিত আইনি পথ সহজ ভাষায় ব্যাখ্যা করি—আমি আইনজীবী নই এবং কে জিতবে বলি না। "
            "বেতন/চাকরি, ভাড়া/উচ্ছেদ, নারীর নিরাপত্তা, ভোক্তা/ফেরত, পুলিশ/FIR—এসবে পরবর্তী পদক্ষেপ, DLSA বা সঠিক অফিস, কাগজপত্র ও অভিযোগ "
            "কীভাবে শুরু হয় তা বলতে পারি। প্রস্তুত হলে জেলা ও ঘটনাটি নিজের ভাষায় বলুন—প্রয়োজনে কয়েকটি প্রশ্ন করব।"
        ),
        "meta_limit": (
            "বিপদ বা সময়সীমা জরুরি মনে হলে দ্রুত জরুরি সেবা বা DLSA-তে যোগাযোগ করুন—শুধু চ্যাটের ওপর নির্ভর করবেন না।"
        ),
        "meta_template": (
            "নিজের ভাষায়: কারা জড়িত, কী হয়েছে, প্রায় কখন, জেলা, এবং আপনি কী চান।"
        ),
    },
}

CATEGORY_GUIDANCE: dict[str, dict[str, dict]] = {
    "en": {
        "employment_wages": {
            "rights_summary": "",
            "forums": [
                "Labour Commissioner office",
                "Labour Court (if unresolved after labour authority process)",
            ],
            "documents": [
                "Employment proof (offer letter/ID card/contract)",
                "Wage proof (bank statement/payslips/attendance)",
                "Communication evidence (emails/messages/notices)",
            ],
            "limitation_hint": "File quickly after non-payment or unlawful termination; delays can weaken recovery and evidence.",
            "template": (
                "Subject: Complaint regarding non-payment of wages\n\n"
                "I, [NAME], worked at [EMPLOYER] from [DATE] to [DATE/ONGOING]. "
                "My wages for [PERIOD] remain unpaid despite repeated requests. "
                "I request immediate recovery of dues and legal action under applicable wage laws.\n\n"
                "Attached: identity proof, employment proof, wage records, communication logs."
            ),
        },
        "property_tenancy": {
            "rights_summary": "You may have tenancy and property rights around fair notice, lawful eviction process, and dispute redressal.",
            "forums": ["Rent Controller", "RERA (if builder/project issue)", "Civil Court"],
            "documents": [
                "Rent agreement or ownership papers",
                "Rent payment proof / receipts",
                "Notices, messages, and photos of property condition",
            ],
            "limitation_hint": "Act quickly after notice, illegal eviction attempt, or possession dispute to preserve remedies.",
            "template": "Subject: Complaint regarding tenancy/property dispute",
        },
        "womens_protection": {
            "rights_summary": "You may seek immediate legal protection, safety orders, and formal complaint mechanisms under women protection laws.",
            "forums": ["Protection Officer", "Internal Complaints Committee (ICC)", "Mahila Police / Women Cell"],
            "documents": [
                "Incident timeline and written account",
                "Messages, call records, medical records, witness details (if available)",
                "Any prior complaint copy",
            ],
            "limitation_hint": "For safety-related incidents, seek help immediately and document events as early as possible.",
            "template": "Subject: Complaint seeking protection and legal action",
        },
        "consumer_fraud": {
            "rights_summary": "You may claim refund, replacement, compensation, and complaint redress in consumer fraud or defective service matters.",
            "forums": ["District Consumer Commission", "State/National Commission (as applicable)"],
            "documents": [
                "Invoice/order receipt/payment proof",
                "Product/service communication and screenshots",
                "Prior complaint and seller response (if any)",
            ],
            "limitation_hint": "File the complaint within limitation timelines under consumer law; avoid delay.",
            "template": "Subject: Consumer complaint for fraud/deficiency of service",
        },
        "police_fir": {
            "rights_summary": "You may escalate if FIR is not registered and seek lawful remedies before senior police or magistrate.",
            "forums": ["SP Office / Senior Police Officer", "Magistrate Court", "SC/ST Cell (if applicable)"],
            "documents": [
                "Written complaint copy",
                "Any refusal proof / station details / diary entry",
                "Evidence of incident and witnesses (if available)",
            ],
            "limitation_hint": "Escalate refusal promptly and preserve all written records and acknowledgments.",
            "template": "Subject: Request for FIR registration / escalation of non-registration",
        },
    },
    "hi": {
        "employment_wages": {
            "rights_summary": "",
            "forums": [
                "Shram Ayukta karyalay / Labour Commissioner office",
                "Labour Court (yadi shram adhikaran prakriya ke baad)",
            ],
            "documents": [
                "Naukri ka praman (offer letter/ID card/contract)",
                "Vetan praman (bank statement/payslips/hajri)",
                "Sanvaad praman (email/message/notice)",
            ],
            "limitation_hint": "Non-payment ya unlawful termination ke baad jaldi file karein; deri se evidence aur recovery weak ho sakti hai.",
            "template": (
                "Vishay: Vetan na milne ke sambandh mein shikayat\n\n"
                "Main, [NAAM], ne [DATE] se [DATE/CHALU] tak [EMPLOYER] mein kaam kiya. "
                "[AVADHI] ke vetan abhi tak nahi mile. Bar-bar nivedan ke baad bhi bhugtan nahi hua. "
                "Anurodh hai ki thaka vetan vasuli aur lagu kanoon ke anusar karyavahi ki jaye.\n\n"
                "Sanlagn: pehchan patra, naukri praman, vetan records, sanvaad ki niyantrakiyan."
            ),
        },
        "property_tenancy": {
            "rights_summary": "Aapko uchit notice, kanooni eviction process, aur vivad nivaran ke sambandh mein tenancy aur property adhikar ho sakte hain.",
            "forums": ["Rent Controller", "RERA (builder/project issue ke liye)", "Civil Court"],
            "documents": [
                "Rent agreement ya ownership ke kagazat",
                "Rent payment ka praman / receipts",
                "Notices, messages, aur property ki sthiti ke photos",
            ],
            "limitation_hint": "Notice, avaidh eviction prayas ya possession vivad ke baad jaldi karyavahi karein.",
            "template": "Vishay: Tenancy/property vivad ke sambandh mein shikayat",
        },
        "womens_protection": {
            "rights_summary": "Aap mahila suraksha kanoonon ke tahat turant kanooni suraksha, safety orders, aur aupcharik shikayat tantra prapt kar sakti hain.",
            "forums": ["Protection Officer", "Internal Complaints Committee (ICC)", "Mahila Police / Women Cell"],
            "documents": [
                "Ghatna ki timeline aur likhit vivran",
                "Messages, call records, medical records, gawah vivran (yadi uplabdh)",
                "Pichli shikayat ki copy (yadi koi)",
            ],
            "limitation_hint": "Suraksha sambandhi ghatnaon mein turant madad lein aur ghatnaon ko jaldi se jaldi document karein.",
            "template": "Vishay: Suraksha aur kanooni karyavahi ke liye shikayat",
        },
        "consumer_fraud": {
            "rights_summary": "Aap consumer fraud ya doshpurn seva ke maamlon mein refund, replacement, mukavja aur shikayat nivaran ki maang kar sakte hain.",
            "forums": ["District Consumer Commission", "State/National Commission (yatha lagu)"],
            "documents": [
                "Invoice/order receipt/payment praman",
                "Product/service ke messages aur screenshots",
                "Pichli shikayat aur seller ka jawab (yadi koi)",
            ],
            "limitation_hint": "Consumer law ke tahat limitation samay seema mein shikayat darj karein; deri se bachein.",
            "template": "Vishay: Fraud/seva mein doosh ke liye consumer shikayat",
        },
        "police_fir": {
            "rights_summary": "Yadi FIR darj nahi ki gayi to aap senior police ya magistrate ke samne escalate kar sakte hain aur kanooni upchar maang sakte hain.",
            "forums": ["SP karyalay / varishtha police adhikari", "Magistrate Court", "SC/ST Cell (yadi lagu)"],
            "documents": [
                "Likhit shikayat ki copy",
                "Inkaar ka praman / station vivran / diary entry",
                "Ghatna ke saboot aur gawah (yadi uplabdh)",
            ],
            "limitation_hint": "Inkaar ko turant escalate karein aur sabhi likhit records aur acknowledgments surakshit rakhein.",
            "template": "Vishay: FIR darj karne / non-registration escalate karne ki vinati",
        },
    },
    "mr": {
        "employment_wages": {
            "rights_summary": "",
            "forums": [
                "मजूर आयुक्त कार्यालय (Labour Commissioner)",
                "मजूर न्यायालय (प्राधिकरण प्रक्रियेनंतर लागू असल्यास)",
            ],
            "documents": [
                "नोकरीचा पुरावा (ऑफर लेटर/ओळखपत्र/करार)",
                "वेतन पुरावा (बँक स्टेटमेंट/पे-स्लिप/हजेरी)",
                "संवाद पुरावा (ईमेल/संदेश/नोटीस)",
            ],
            "limitation_hint": "वेतन न मिळणे किंवा बेकायदेशीर सेवासमाप्तीनंतर लवकर तक्रार करा; उशीर झाल्यास पुरावे आणि recovery कमकुवत होऊ शकते.",
            "template": (
                "विषय: वेतन न मिळाल्याबाबत तक्रार\n\n"
                "मी, [नाव], [तारखे] पासून [तारखे/सुरू] पर्यंत [नोकरीदार] येथे काम केले. "
                "[कालावधी] चे वेतन अद्याप मिळाले नाही. वारंवार विनंतीनंतरही भरणा झाला नाही. "
                "विनंती आहे की थकबाकी वेतन वसूल करण्यासाठी व लागू कायद्यानुसार कारवाई करावी.\n\n"
                "संलग्न: ओळखपत्र, नोकरीचा पुरावा, वेतनाचे रेकॉर्ड, संवादाची नोंद."
            ),
        },
        "property_tenancy": {
            "rights_summary": "तुम्हाला योग्य notice, कायदेशीर eviction प्रक्रिया, आणि वाद निवारण यासंदर्भात tenancy आणि property अधिकार असू शकतात.",
            "forums": ["Rent Controller", "RERA (builder/project issue असल्यास)", "Civil Court"],
            "documents": [
                "Rent agreement किंवा मालकी हक्काची कागदपत्रे",
                "Rent payment पुरावा / पावत्या",
                "Notices, messages, आणि property स्थितीचे फोटो",
            ],
            "limitation_hint": "Notice, बेकायदेशीर eviction प्रयत्न किंवा possession वाद नंतर लवकर कारवाई करा.",
            "template": "विषय: Tenancy/property वादाबाबत तक्रार",
        },
        "womens_protection": {
            "rights_summary": "तुम्ही महिला संरक्षण कायद्यांनुसार त्वरित कायदेशीर संरक्षण, safety orders आणि औपचारिक तक्रार यंत्रणा मिळवू शकता.",
            "forums": ["Protection Officer", "Internal Complaints Committee (ICC)", "Mahila Police / Women Cell"],
            "documents": [
                "घटनेची timeline आणि लिखित विवरण",
                "Messages, call records, वैद्यकीय records, साक्षीदार तपशील (उपलब्ध असल्यास)",
                "मागील तक्रारीची प्रत (असल्यास)",
            ],
            "limitation_hint": "सुरक्षा संबंधित घटनांमध्ये त्वरित मदत घ्या आणि घटना लवकरात लवकर document करा.",
            "template": "विषय: संरक्षण आणि कायदेशीर कारवाईसाठी तक्रार",
        },
        "consumer_fraud": {
            "rights_summary": "तुम्ही consumer fraud किंवा सेवेच्या त्रुटीच्या प्रकरणांमध्ये refund, replacement, मोबदला आणि तक्रार निवारणाची मागणी करू शकता.",
            "forums": ["District Consumer Commission", "State/National Commission (लागू असल्यास)"],
            "documents": [
                "Invoice/order receipt/payment पुरावा",
                "Product/service चे messages आणि screenshots",
                "मागील तक्रार आणि seller चे उत्तर (असल्यास)",
            ],
            "limitation_hint": "Consumer law नुसार limitation कालावधीत तक्रार दाखल करा; उशीर टाळा.",
            "template": "विषय: Fraud/सेवेतील त्रुटीसाठी consumer तक्रार",
        },
        "police_fir": {
            "rights_summary": "FIR दाखल न झाल्यास तुम्ही वरिष्ठ पोलीस किंवा magistrate कडे escalate करू शकता आणि कायदेशीर उपाय मागू शकता.",
            "forums": ["SP कार्यालय / वरिष्ठ पोलीस अधिकारी", "Magistrate Court", "SC/ST Cell (लागू असल्यास)"],
            "documents": [
                "लिखित तक्रारीची प्रत",
                "नकार पुरावा / station तपशील / diary entry",
                "घटनेचे पुरावे आणि साक्षीदार (उपलब्ध असल्यास)",
            ],
            "limitation_hint": "नकार त्वरित escalate करा आणि सर्व लिखित records आणि acknowledgments जतन करा.",
            "template": "विषय: FIR नोंदणी / non-registration escalate करण्याची विनंती",
        },
    },
    "ta": {
        "employment_wages": {
            "rights_summary": "",
            "forums": [
                "Labour Commissioner அலுவலகம்",
                "Labour Court (அதிகாரி நடைமுறைக்குப் பிறகு பொருந்தினால்)",
            ],
            "documents": [
                "வேலை ஆதாரம் (offer letter/ID/ஒப்பந்தம்)",
                "சம்பள ஆதாரம் (வங்கி அறிக்கை/payslip/வருகை)",
                "தொடர்பு ஆதாரம் (மின்னஞ்சல்/செய்தி/அறிவிப்பு)",
            ],
            "limitation_hint": "சம்பளம் வழங்காதது அல்லது சட்டவிரோத பணிநீக்கம் ஏற்பட்டால் விரைவாக புகார் செய்யவும்; தாமதம் ஆதாரத்தையும் மீட்பையும் பலவீனப்படுத்தும்.",
            "template": (
                "பொருள்: சம்பளம் வழங்காதது குறித்த புகார்\n\n"
                "நான், [பெயர்], [தேதி] முதல் [தேதி/தொடர்ந்து] வரை [முதலாளி] இல் பணிபுரிந்தேன். "
                "[காலம்] க்கான சம்பளம் இன்னும் வழங்கப்படவில்லை. மீண்டும் மீண்டும் கோரிக்கைகளுக்குப் பிறகும் பணம் வரவில்லை. "
                "தொகையை மீட்டெடுக்கவும் பொருந்தும் சட்டப்படி நடவடிக்கை எடுக்கவும் கோருகிறேன்.\n\n"
                "இணைப்பு: அடையாள ஆதாரம், வேலை ஆதாரம், சம்பள பதிவுகள், தொடர்பு பதிவுகள்."
            ),
        },
        "property_tenancy": {
            "rights_summary": "நியாயமான notice, சட்டபூர்வ eviction செயல்முறை, மற்றும் சர்ச்சை தீர்வு தொடர்பாக உங்களுக்கு tenancy மற்றும் property உரிமைகள் இருக்கலாம்.",
            "forums": ["Rent Controller", "RERA (builder/project issue என்றால்)", "Civil Court"],
            "documents": [
                "Rent agreement அல்லது உரிமை ஆவணங்கள்",
                "Rent payment ஆதாரம் / ரசீதுகள்",
                "Notices, messages, மற்றும் property நிலை புகைப்படங்கள்",
            ],
            "limitation_hint": "Notice, சட்டவிரோத eviction முயற்சி அல்லது possession சர்ச்சைக்குப் பிறகு விரைவாக நடவடிக்கை எடுக்கவும்.",
            "template": "பொருள்: Tenancy/property சர்ச்சை தொடர்பான புகார்",
        },
        "womens_protection": {
            "rights_summary": "பெண்கள் பாதுகாப்பு சட்டங்களின் கீழ் உடனடி சட்டப் பாதுகாப்பு, safety orders, மற்றும் முறையான புகார் வழிமுறைகளை நீங்கள் பெறலாம்.",
            "forums": ["Protection Officer", "Internal Complaints Committee (ICC)", "Mahila Police / Women Cell"],
            "documents": [
                "சம்பவத்தின் timeline மற்றும் எழுத்துப்பூர்வ விளக்கம்",
                "Messages, call records, மருத்துவ records, சாட்சி விவரங்கள் (கிடைத்தால்)",
                "முந்தைய புகாரின் நகல் (இருந்தால்)",
            ],
            "limitation_hint": "பாதுகாப்பு தொடர்பான சம்பவங்களில் உடனே உதவி பெறவும் மற்றும் நிகழ்வுகளை விரைவாக document செய்யவும்.",
            "template": "பொருள்: பாதுகாப்பு மற்றும் சட்ட நடவடிக்கைக்கான புகார்",
        },
        "consumer_fraud": {
            "rights_summary": "Consumer fraud அல்லது குறைபாடான சேவை விஷயங்களில் refund, replacement, இழப்பீடு மற்றும் புகார் தீர்வை நீங்கள் கோரலாம்.",
            "forums": ["District Consumer Commission", "State/National Commission (பொருந்தினால்)"],
            "documents": [
                "Invoice/order receipt/payment ஆதாரம்",
                "Product/service messages மற்றும் screenshots",
                "முந்தைய புகார் மற்றும் seller பதில் (இருந்தால்)",
            ],
            "limitation_hint": "Consumer law-ன் கீழ் limitation கால அளவில் புகார் செய்யவும்; தாமதத்தை தவிர்க்கவும்.",
            "template": "பொருள்: Fraud/சேவை குறைபாட்டிற்கான consumer புகார்",
        },
        "police_fir": {
            "rights_summary": "FIR பதிவு செய்யப்படவில்லை என்றால், மூத்த போலீஸ் அல்லது magistrate-க்கு escalate செய்து சட்ட தீர்வுகளை கோரலாம்.",
            "forums": ["SP அலுவலகம் / மூத்த போலீஸ் அதிகாரி", "Magistrate Court", "SC/ST Cell (பொருந்தினால்)"],
            "documents": [
                "எழுத்துப்பூர்வ புகாரின் நகல்",
                "மறுப்பு ஆதாரம் / station விவரங்கள் / diary entry",
                "சம்பவத்தின் ஆதாரங்கள் மற்றும் சாட்சிகள் (கிடைத்தால்)",
            ],
            "limitation_hint": "மறுப்பை உடனடியாக escalate செய்யவும் மற்றும் அனைத்து எழுத்துப்பூர்வ records மற்றும் acknowledgments-ஐ பாதுகாக்கவும்.",
            "template": "பொருள்: FIR பதிவு / non-registration escalate கோரிக்கை",
        },
    },
    "bn": {
        "employment_wages": {
            "rights_summary": "",
            "forums": [
                "Labour Commissioner অফিস",
                "Labour Court (কর্তৃপক্ষের প্রক্রিয়ার পর প্রযোজ্য হলে)",
            ],
            "documents": [
                "চাকরির প্রমাণ (offer letter/ID/চুক্তি)",
                "বেতনের প্রমাণ (ব্যাংক স্টেটমেন্ট/payslip/উপস্থিতি)",
                "যোগাযোগের প্রমাণ (ইমেইল/বার্তা/নোটিশ)",
            ],
            "limitation_hint": "বেতন না পাওয়া বা বেআইনি চাকরিচ্যুতির পরে দ্রুত অভিযোগ করুন; দেরি হলে প্রমাণ ও recovery দুর্বল হতে পারে।",
            "template": (
                "বিষয়: বেতন না পাওয়া সংক্রান্ত অভিযোগ\n\n"
                "আমি, [নাম], [তারিখ] থেকে [তারিখ/চলমান] পর্যন্ত [নিয়োগকর্তা]-এ কাজ করেছি। "
                "[সময়কাল]-এর বেতন এখনও বাকি। বারবার অনুরোধের পরেও পরিশোধ হয়নি। "
                "বকেয়া আদায় ও প্রযোজ্য আইন অনুযায়ী ব্যবস্থা গ্রহণের অনুরোধ করছি।\n\n"
                "সংযুক্ত: পরিচয়পত্র, চাকরির প্রমাণ, বেতনের রেকর্ড, যোগাযোগের রেকর্ড।"
            ),
        },
        "property_tenancy": {
            "rights_summary": "ন্যায্য notice, আইনসঙ্গত eviction প্রক্রিয়া এবং বিরোধ নিষ্পত্তির ক্ষেত্রে আপনার tenancy এবং property অধিকার থাকতে পারে।",
            "forums": ["Rent Controller", "RERA (builder/project issue হলে)", "Civil Court"],
            "documents": [
                "Rent agreement বা মালিকানার কাগজপত্র",
                "Rent payment প্রমাণ / রসিদ",
                "Notices, messages, এবং property অবস্থার ছবি",
            ],
            "limitation_hint": "Notice, বেআইনি eviction প্রচেষ্টা বা possession বিরোধের পরে দ্রুত পদক্ষেপ নিন।",
            "template": "বিষয়: Tenancy/property বিরোধ সংক্রান্ত অভিযোগ",
        },
        "womens_protection": {
            "rights_summary": "নারী সুরক্ষা আইনের অধীনে আপনি অবিলম্বে আইনি সুরক্ষা, safety orders এবং আনুষ্ঠানিক অভিযোগ ব্যবস্থা পেতে পারেন।",
            "forums": ["Protection Officer", "Internal Complaints Committee (ICC)", "Mahila Police / Women Cell"],
            "documents": [
                "ঘটনার timeline এবং লিখিত বিবরণ",
                "Messages, call records, চিকিৎসা records, সাক্ষীর বিবরণ (থাকলে)",
                "পূর্ববর্তী অভিযোগের কপি (থাকলে)",
            ],
            "limitation_hint": "সুরক্ষা সংক্রান্ত ঘটনায় অবিলম্বে সাহায্য নিন এবং ঘটনাগুলি যত দ্রুত সম্ভব document করুন।",
            "template": "বিষয়: সুরক্ষা এবং আইনি ব্যবস্থার জন্য অভিযোগ",
        },
        "consumer_fraud": {
            "rights_summary": "Consumer fraud বা ত্রুটিপূর্ণ পরিষেবার ক্ষেত্রে আপনি refund, replacement, ক্ষতিপূরণ এবং অভিযোগ নিষ্পত্তি দাবি করতে পারেন।",
            "forums": ["District Consumer Commission", "State/National Commission (প্রযোজ্য হলে)"],
            "documents": [
                "Invoice/order receipt/payment প্রমাণ",
                "Product/service messages এবং screenshots",
                "পূর্ববর্তী অভিযোগ এবং seller-এর উত্তর (থাকলে)",
            ],
            "limitation_hint": "Consumer law-এর অধীনে limitation সময়সীমার মধ্যে অভিযোগ দাখিল করুন; দেরি এড়িয়ে চলুন।",
            "template": "বিষয়: Fraud/পরিষেবা ত্রুটির জন্য consumer অভিযোগ",
        },
        "police_fir": {
            "rights_summary": "FIR নথিভুক্ত না হলে আপনি সিনিয়র পুলিশ বা magistrate-এর কাছে escalate করতে পারেন এবং আইনি প্রতিকার চাইতে পারেন।",
            "forums": ["SP অফিস / সিনিয়র পুলিশ অফিসার", "Magistrate Court", "SC/ST Cell (প্রযোজ্য হলে)"],
            "documents": [
                "লিখিত অভিযোগের কপি",
                "প্রত্যাখ্যান প্রমাণ / station বিবরণ / diary entry",
                "ঘটনার প্রমাণ এবং সাক্ষী (থাকলে)",
            ],
            "limitation_hint": "প্রত্যাখ্যান অবিলম্বে escalate করুন এবং সমস্ত লিখিত records এবং acknowledgments সংরক্ষণ করুন।",
            "template": "বিষয়: FIR নিবন্ধন / non-registration escalate-এর অনুরোধ",
        },
    },
}


_TOPIC_INTRO: dict[str, dict[CaseCategory, str]] = {
    "en": {
        "employment_wages": "Sounds like something with work or wages. I can help you think through unpaid salary, sudden termination, PF, or overtime.",
        "property_tenancy": "Got it—land, rent, or property questions. I can help you think through eviction notices, deposits, possession, mutation, or boundary trouble.",
        "womens_protection": "Thank you for trusting me. I can talk through protection orders, domestic violence support, dowry harassment, or workplace harassment.",
        "consumer_fraud": "I can help with consumer issues like refunds, defective products, online fraud, or unresponsive sellers.",
        "police_fir": "I can help with FIR-related troubles—if police are refusing to register a complaint or you're unsure how to escalate.",
        "general": "Happy to help. I focus on common Indian legal topics—wages and work, rent and property, women's safety, consumer fraud, and police/FIR matters.",
    },
    "hi": {
        "employment_wages": "Lagta hai naukri ya vetan ka mamla hai. Main unpaid salary, sudden termination, PF ya overtime samjhane mein madad kar sakta/sakti hoon.",
        "property_tenancy": "Theek hai—zameen, kiraya ya property ka vishay. Eviction notice, deposit, possession, mutation, ya boundary par baat kar sakte hain.",
        "womens_protection": "Aapne bharosa kiya—shukriya. Protection order, domestic violence madad, dahej utpidan, ya workplace harassment par baat ho sakti hai.",
        "consumer_fraud": "Refund, doshpurn samaan, online fraud, ya seller ka jawab na milne jaisi consumer dikkaton mein madad kar sakta/sakti hoon.",
        "police_fir": "FIR sambandhi dikkaton mein madad kar sakta/sakti hoon—agar police complaint nahi le rahi ya escalate karna hai.",
        "general": "Madad ke liye taiyyar hoon. Main rozmarra ke Indian legal topics dekhta/dekhti hoon—vetan/naukri, kiraya/property, mahila suraksha, consumer fraud, aur police/FIR.",
    },
    "mr": {
        "employment_wages": "नोकरी किंवा वेतनाशी संबंधित वाटतंय. न मिळालेला पगार, अचानक नोकरी सोडवणे, PF, किंवा overtime यांवर बोलू शकतो/शकते.",
        "property_tenancy": "ठीक—जमीन, भाडे किंवा मालमत्ता. Eviction notice, deposit, possession, mutation, किंवा सीमा वाद यावर बोलू शकतो.",
        "womens_protection": "विश्वास ठेवल्याबद्दल धन्यवाद. Protection order, घरगुती हिंसा मदत, हुंडा त्रास, किंवा कार्यस्थळ छळ यावर बोलू शकतो.",
        "consumer_fraud": "Refund, सदोष वस्तू, online fraud, किंवा विक्रेत्याचा प्रतिसाद नसणे यांत मदत करू शकतो.",
        "police_fir": "FIR संबंधित अडचणींमध्ये मदत करू शकतो—पोलीस तक्रार घेत नसल्यास किंवा escalate करायचे असल्यास.",
        "general": "मदतीसाठी तयार. मी रोजच्या भारतीय कायदेशीर विषयांवर बोलतो—वेतन/नोकरी, भाडे/मालमत्ता, महिला सुरक्षा, ग्राहक फसवणूक, पोलीस/FIR.",
    },
    "ta": {
        "employment_wages": "வேலை அல்லது சம்பளம் தொடர்பாக போல உள்ளது. சம்பளம் வராமை, திடீர் பணிநீக்கம், PF, overtime பற்றி பேசலாம்.",
        "property_tenancy": "சரி—நிலம், வாடகை, அல்லது சொத்து விஷயம். Eviction notice, deposit, possession, mutation, அல்லது எல்லைப் பிரச்சினை குறித்து பேசலாம்.",
        "womens_protection": "நம்பி பகிர்ந்ததற்கு நன்றி. Protection order, குடும்ப வன்முறை உதவி, வரதட்சணைத் தொல்லை, பணிஇட துன்புறுத்தல் பற்றி பேசலாம்.",
        "consumer_fraud": "Refund, குறைபாடான பொருள், online fraud, விற்பவர் பதில் இல்லாமை—இப்படிப்பட்ட நுகர்வோர் பிரச்சினைகளில் உதவ முடியும்.",
        "police_fir": "FIR தொடர்பான சிக்கல்களில் உதவ முடியும்—காவலர் புகார் வாங்க மறுத்தாலோ, escalate செய்ய வேண்டுமோ.",
        "general": "உதவ தயார். அன்றாட இந்திய சட்ட தலைப்புகளில் கவனம்—சம்பளம்/வேலை, வாடகை/சொத்து, பெண்கள் பாதுகாப்பு, நுகர்வோர் மோசடி, காவல்/FIR.",
    },
    "bn": {
        "employment_wages": "চাকরি বা বেতন সংক্রান্ত মনে হচ্ছে। অপ্রদত্ত বেতন, হঠাৎ চাকরিচ্যুতি, PF বা overtime নিয়ে আলোচনা করতে পারি।",
        "property_tenancy": "ঠিক আছে—জমি, ভাড়া বা সম্পত্তি। Eviction notice, deposit, possession, mutation, বা সীমানা সমস্যা নিয়ে আলোচনা করতে পারি।",
        "womens_protection": "বিশ্বাস করে শেয়ার করার জন্য ধন্যবাদ। Protection order, পারিবারিক সহিংসতা সহায়তা, যৌতুক হয়রানি, কর্মস্থলে হয়রানি নিয়ে কথা বলতে পারি।",
        "consumer_fraud": "Refund, ত্রুটিযুক্ত পণ্য, online fraud, বিক্রেতার সাড়া না মেলা—এমন ভোক্তা সমস্যায় সাহায্য করতে পারি।",
        "police_fir": "FIR সংক্রান্ত সমস্যায় সাহায্য করতে পারি—পুলিশ অভিযোগ না নিলে বা escalate করতে হলে।",
        "general": "সাহায্যের জন্য প্রস্তুত। আমি প্রতিদিনের ভারতীয় আইনি বিষয়গুলো দেখি—বেতন/চাকরি, ভাড়া/সম্পত্তি, নারীর নিরাপত্তা, ভোক্তা প্রতারণা, পুলিশ/FIR।",
    },
}

_OPEN_QUESTIONS: dict[str, list[str]] = {
    "en": [
        "Could you tell me what happened, in your own words?",
        "Roughly when did this start, and which district or state are you in?",
        "What outcome would feel right—recovery, action, protection, or something else?",
    ],
    "hi": [
        "Apne shabdon mein bata sakte hain ki kya hua?",
        "Yeh kab shuru hua, aur aap kis district/state mein hain?",
        "Aap kya chahte hain—recovery, karyavahi, suraksha, ya kuch aur?",
    ],
    "mr": [
        "तुमच्या शब्दांत सांगाल का काय घडले?",
        "हे साधारण केव्हा सुरू झाले, आणि तुम्ही कोणत्या जिल्ह्यात/राज्यात आहात?",
        "तुम्हाला नक्की काय हवे—recovery, कारवाई, संरक्षण, की दुसरे काही?",
    ],
    "ta": [
        "உங்கள் வார்த்தைகளில் என்ன நடந்தது சொல்வீர்களா?",
        "இது தோராயமாக எப்போது தொடங்கியது, எந்த மாவட்டம்/மாநிலத்தில் இருக்கிறீர்கள்?",
        "எந்த முடிவு சரியாக இருக்கும்—recovery, நடவடிக்கை, பாதுகாப்பு, அல்லது வேறொன்று?",
    ],
    "bn": [
        "নিজের ভাষায় কী হয়েছে বলবেন?",
        "এটি প্রায় কখন শুরু হলো, আপনি কোন জেলা/রাজ্যে আছেন?",
        "কী ফলাফল ঠিক মনে হবে—recovery, পদক্ষেপ, সুরক্ষা, না অন্য কিছু?",
    ],
}


def compose_topic_clarification(
    *,
    category: CaseCategory,
    language: SupportedLanguage,
    district: str | None,
) -> OrchestrateResponse:
    """Vague topic intros: acknowledge the area, then ask 2–3 natural follow-ups (no RAG dump)."""
    intros = _TOPIC_INTRO.get(language, _TOPIC_INTRO["en"])
    intro = intros.get(category) or intros["general"]
    questions = _OPEN_QUESTIONS.get(language, _OPEN_QUESTIONS["en"])
    lang = TEXT_BY_LANG[language]
    return OrchestrateResponse(
        disclaimer=DISCLAIMER_BY_LANG[language],
        category=category,
        crisis_detected=False,
        rights_summary=intro,
        suggested_forum=[],
        required_documents=[],
        limitation_hint=lang["fallback_limit"],
        free_legal_aid=_free_aid_localized(language, district),
        complaint_template=lang["fallback_template"],
        helplines=[],
        sources=[],
        model_used=None,
        needs_clarification=True,
        clarifying_questions=list(questions),
    )


def compose_meta_intro_fallback(
    *,
    language: SupportedLanguage,
    district: str | None,
) -> OrchestrateResponse:
    """Greeting / 'how can you help' — AI assistant first, no RAG corpus."""
    lang = TEXT_BY_LANG[language]
    return OrchestrateResponse(
        disclaimer=DISCLAIMER_BY_LANG[language],
        category="general",
        crisis_detected=False,
        rights_summary=lang["meta_rights"],
        suggested_forum=[lang["dlsa_help"], lang["nyayabandhu"]],
        required_documents=[],
        limitation_hint=lang["meta_limit"],
        free_legal_aid=_free_aid_localized(language, district),
        complaint_template=lang["meta_template"],
        helplines=[],
        sources=[],
        model_used=None,
        needs_clarification=False,
        clarifying_questions=[],
    )


def _free_aid_localized(language: SupportedLanguage, district: str | None) -> list[str]:
    lang = TEXT_BY_LANG[language]
    district_hint = district or {
        "en": "your district",
        "hi": "aapke zile",
        "mr": "तुमच्या जिल्ह्यात",
        "ta": "உங்கள் மாவட்டம்",
        "bn": "আপনার জেলা",
    }[language]
    return [
        lang["free_aid_dlsa_in"].format(district=district_hint),
        lang["free_aid_nyayabandhu"],
    ]


def _statute_lead(category: CaseCategory, language: SupportedLanguage, district: str | None) -> str:
    """A short, advisor-voice opener tied to the category—no statute dump."""
    place = (district or "").strip()
    if language == "hi":
        if category == "employment_wages":
            return f"Aapne {place + ' mein ' if place else ''}vetan ki problem batayi—samay par poora vetan paana aapka adhikar hai aur iski shikayat ki ja sakti hai."
        if category == "property_tenancy":
            return f"Aapne {place + ' mein ' if place else ''}makaan/jameen ki samasya batayi—uchit notice aur kanooni prakriya ke bina bedakhli generally nahi ho sakti."
        if category == "womens_protection":
            return f"Aapne ek sanvedansheel mahila-suraksha mamla bataya{(' (' + place + ')') if place else ''}—aapko turant suraksha aur kanooni rahat lene ka adhikar hai."
        if category == "consumer_fraud":
            return f"Aapne consumer/refund ki problem batayi{(' ' + place + ' mein') if place else ''}—deficient saamaan ya seva ke khilaf consumer adalat mein shikayat ki ja sakti hai."
        if category == "police_fir":
            return f"Aapne FIR/police ki dikkat batayi{(' ' + place + ' mein') if place else ''}—cognizable mamle mein police ko information darj karni hoti hai aur na karne par hierarchical remedies hain."
        return "Main aapki baat dhyaan se sun raha hoon."
    if language == "mr":
        if category == "employment_wages":
            return (
                f"तुम्ही {place + ' मध्ये ' if place else ''}वेतनाबाबत सांगितले—वेळेवर पूर्ण वेतन मिळणे हा तुमचा अधिकार आहे आणि त्यासाठी तक्रार दाखल करता येते."
            )
        if category == "property_tenancy":
            return (
                f"तुम्ही {place + ' मध्ये ' if place else ''}भाडे किंवा मालमत्तेबाबत बोललात—योग्य नोटीस आणि कायदेशीर प्रक्रियेशिवाय बेदखली सहसा शक्य नाही."
            )
        if category == "womens_protection":
            return (
                f"ही गंभीर बाब आहे{(' (' + place + ')') if place else ''}—संरक्षण कायद्यांतर्गत तुम्हाला त्वरित कायदेशीर संरक्षण आणि दिलासा मिळू शकतो."
            )
        if category == "consumer_fraud":
            return (
                f"तुम्ही ग्राहक/परतावा संबंधी अडचण सांगितली{(' ' + place + ' मध्ये') if place else ''}—दोषयुक्त वस्तू किंवा सेवेबाबत तक्रार निवारणाचे मार्ग आहेत."
            )
        if category == "police_fir":
            return (
                f"तुम्ही FIR किंवा पोलिसांबाबत अडचण सांगितली{(' ' + place + ' मध्ये') if place else ''}—गंभीर गुन्ह्यांमध्ये माहिती नोंदवणे अपेक्षित असते; नकार झाल्यास पुढचे पर्याय आहेत."
            )
        return "मी तुमचे म्हणणे ऐकत आहे."
    if category == "employment_wages":
        return f"It sounds like a wages or job issue{(' in ' + place) if place else ''}. Workers do have a right to timely, full wages, and there are clear places to push back when that breaks down."
    if category == "property_tenancy":
        return f"From what you’ve said{(' (' + place + ')') if place else ''}, this looks like a rent or property matter. Tenants and owners both have protections—eviction or deposit disputes usually need notice and a proper forum."
    if category == "womens_protection":
        return f"This sounds serious{(' (' + place + ')') if place else ''}. There are protective laws and quick-relief options designed exactly for situations like this, and you don’t have to handle it alone."
    if category == "consumer_fraud":
        return f"It sounds like a consumer or fraud complaint{(' from ' + place) if place else ''}. Buyers do have remedies for defects, refund denials, and online scams—both consumer commissions and the cyber portal can help."
    if category == "police_fir":
        return f"It sounds like trouble with getting an FIR registered{(' in ' + place) if place else ''}. The law actually requires the police to record information about a cognizable offence, and there are next steps if they don’t."
    return "Tell me a bit more and I can sketch out where to start."


def _phrase_outcome(outcome: str | None, language: SupportedLanguage) -> str:
    if language == "hi":
        return {
            "won": "kaafi had tak rahat mili",
            "lost": "khaas rahat nahi mili",
            "settled": "settle ho gaya",
            "partial": "kuch had tak rahat mili",
        }.get(outcome or "", "")
    if language == "mr":
        return {
            "won": "त्यांना अनुकूल परिणाम मिळाला",
            "lost": "त्यांना अपेक्षित दिलासा मिळाला नाही",
            "settled": "प्रकरण तडजोडीने मिटले",
            "partial": "अंशतः दिलासा मिळाला",
        }.get(outcome or "", "")
    return {
        "won": "things worked out for them",
        "lost": "things didn’t go their way",
        "settled": "the matter ended in a settlement",
        "partial": "they got partial relief",
    }.get(outcome or "", "")


def _illustrative_paragraph(
    sources: list[LegalSource],
    *,
    district: str | None,
    language: SupportedLanguage,
    category: CaseCategory,
) -> str:
    """Pick at most one won + one lost district pattern for THIS topic only—never mix wage and consumer stories."""
    if not district or category == "general":
        return ""
    dn = district.strip().casefold()
    won: LegalSource | None = None
    lost: LegalSource | None = None
    for s in sources:
        if s.entry_type != "illustrative_case":
            continue
        if (s.corpus_category or "") != category:
            continue
        if (s.district or "").strip().casefold() != dn:
            continue
        if s.outcome == "won" and won is None:
            won = s
        elif s.outcome in ("lost", "partial") and lost is None:
            lost = s
        if won and lost:
            break
    if not (won or lost):
        return ""

    def _phrase_en(s: LegalSource, *, subject: str) -> str:
        docs = ", ".join((s.documents_used or [])[:3]) if s.documents_used else ""
        forum = (s.forum_visited or "").strip().lower()
        outcome_phrase = _phrase_outcome(s.outcome, language)
        clauses: list[str] = []
        if docs:
            clauses.append(f"kept things like {docs}")
        if forum:
            clauses.append(f"approached the {forum}")
        if not clauses and not outcome_phrase:
            return ""
        action = " and ".join(clauses) if clauses else ""
        if action and outcome_phrase:
            return f"{subject} {action}, and {outcome_phrase}"
        if action:
            return f"{subject} {action}"
        return f"{subject} {outcome_phrase}"

    def _phrase_mr(s: LegalSource, *, subject: str) -> str:
        docs = ", ".join((s.documents_used or [])[:3]) if s.documents_used else ""
        forum = (s.forum_visited or "").strip()
        outcome_phrase = _phrase_outcome(s.outcome, language)
        clauses: list[str] = []
        if docs:
            clauses.append(f"{docs} अशा कागदपत्रांसह तयारी केली")
        if forum:
            clauses.append(f"{forum} येथे संपर्क केला")
        if not clauses and not outcome_phrase:
            return ""
        action = " आणि ".join(clauses) if clauses else ""
        if action and outcome_phrase:
            return f"{subject} ने {action}, आणि {outcome_phrase}"
        if action:
            return f"{subject} ने {action}"
        return f"{subject} ला {outcome_phrase}"

    def _phrase_hi(s: LegalSource, *, subject: str) -> str:
        docs = ", ".join((s.documents_used or [])[:3]) if s.documents_used else ""
        forum = (s.forum_visited or "").strip()
        outcome_phrase = _phrase_outcome(s.outcome, language)
        clauses: list[str] = []
        if docs:
            clauses.append(f"{docs} jaisi cheezen tayyar rakhi")
        if forum:
            clauses.append(f"{forum} se sampark kiya")
        if not clauses and not outcome_phrase:
            return ""
        action = " aur ".join(clauses) if clauses else ""
        if action and outcome_phrase:
            return f"{subject} ne {action}, aur {outcome_phrase}"
        if action:
            return f"{subject} ne {action}"
        return f"{subject} ko {outcome_phrase}"

    if language == "hi":
        head = f"{district.strip()} ke hamare anonymized notes mein"
        bits: list[str] = []
        if won:
            p = _phrase_hi(won, subject="ek vyakti")
            if p:
                bits.append(p)
        if lost:
            p = _phrase_hi(lost, subject="doosre vyakti—jinke paas kam paperwork ya zyada deri thi")
            if p:
                bits.append(p)
        if not bits:
            return ""
        joined = "; jabki ".join(bits)
        return f" {head} {joined}. Yeh sirf patterns hain—aapke tathyon par natija badal sakta hai."

    if language == "mr":
        head = f"आमच्या अनामित नोंदींमधून {district.strip()} बद्दल"
        bits_mr: list[str] = []
        if won:
            p = _phrase_mr(won, subject="एक व्यक्ती")
            if p:
                bits_mr.append(p)
        if lost:
            p = _phrase_mr(lost, subject="दुसरी व्यक्ती—कमी कागदपत्रे किंवा उशीर असलेली")
            if p:
                bits_mr.append(p)
        if not bits_mr:
            return ""
        joined_mr = "; तर ".join(bits_mr)
        return f" {head} {joined_mr}. हे फक्त नमुने आहेत, भाकित नाही—तुमच्या तथ्यांवर निकाल अवलंबून असतो."

    head = f"From our anonymized notes around {district.strip()},"
    bits = []
    if won:
        p = _phrase_en(won, subject="one person")
        if p:
            bits.append(p)
    if lost:
        p = _phrase_en(lost, subject="another person, with thinner paperwork or more delay,")
        if p:
            bits.append(p)
    if not bits:
        return ""
    joined = "; while ".join(bits)
    return f" {head} {joined}. These are just patterns, not predictions—your facts can change the picture."


def compose_fallback_unified(
    *,
    category: CaseCategory,
    language: SupportedLanguage,
    district: str | None,
    sources: list[LegalSource],
) -> OrchestrateResponse:
    """LLM-down fallback: still warm and conversational, never a snippet dump."""
    lang = TEXT_BY_LANG[language]

    lead = _statute_lead(category, language, district)
    illustrative = _illustrative_paragraph(sources, district=district, language=language, category=category)
    closer_en = " I can suggest where people usually start and what papers help—want me to walk you through that?"
    closer_hi = " Main bata sakta hoon log aam taur par kahan se shuru karte hain aur kaunse kagazat madad karte hain—chaaliye saath chalte hain?"
    closer_mr = (
        " मी सांगू शकतो लोक सहसा कुठून सुरुवात करतात आणि कोणती कागदपत्रे उपयोगी असतात—पुढे एकत्र चालू का?"
    )
    if language == "hi":
        closer = closer_hi
    elif language == "mr":
        closer = closer_mr
    elif language == "en":
        closer = closer_en
    else:
        closer = ""

    if lead or illustrative:
        rights_summary = f"{lead}{illustrative}{closer}".strip()
    else:
        rights_summary = lang["fallback_intro"]
    guidance = CATEGORY_GUIDANCE.get(language, CATEGORY_GUIDANCE["en"])
    if category != "general" and category in guidance:
        g = guidance[category]
        suggested_forum = list(g["forums"])
        required_documents = list(g["documents"])
        limitation_hint = g["limitation_hint"]
        complaint_template = f"{g['template']}\n\n{lang['category_template_body']}"
    else:
        suggested_forum = [lang["dlsa_help"]]
        required_documents = [lang["id_proof_simple"], lang["any_docs"]]
        limitation_hint = lang["fallback_limit"]
        complaint_template = lang["fallback_template"]
    return OrchestrateResponse(
        disclaimer=DISCLAIMER_BY_LANG[language],
        category=category,
        crisis_detected=False,
        rights_summary=rights_summary,
        suggested_forum=suggested_forum,
        required_documents=required_documents,
        limitation_hint=limitation_hint,
        free_legal_aid=_free_aid_localized(language, district),
        complaint_template=complaint_template,
        helplines=[],
        sources=sources,
        model_used=None,
    )
