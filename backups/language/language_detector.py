"""Indonesian Regional Language Detection"""

JAVANESE_PATTERNS = {
    'greetings': ['kabare', 'pripun', 'matur nuwun', 'sugeng', 'monggo'],
    'numbers': ['siji', 'loro', 'telu', 'papat', 'limo', 'enem', 'pitu', 'wolu', 'songo', 'sepuluh'],
    'common': ['sampun', 'dereng', 'pinten', 'niku', 'napa', 'punapa', 'wonten', 'mboten']
}

SUNDANESE_PATTERNS = {
    'greetings': ['kumaha', 'damang', 'hatur nuhun', 'wilujeng', 'mangga'],
    'common': ['parantos', 'teu acan', 'sabaraha', 'naon', 'dimana', 'iraha']
}

BETAWI_PATTERNS = {
    'greetings': ['ape kabar', 'gimane', 'makasih ye'],
    'common': ['udah', 'belom', 'berape', 'apaan', 'dimane']
}

def detect_language(text: str) -> str:
    """Detect Indonesian regional language"""
    text_lower = text.lower()
    
    # Count matches
    jawa_score = sum(1 for patterns in JAVANESE_PATTERNS.values() 
                     for word in patterns if word in text_lower)
    sunda_score = sum(1 for patterns in SUNDANESE_PATTERNS.values() 
                      for word in patterns if word in text_lower)
    betawi_score = sum(1 for patterns in BETAWI_PATTERNS.values() 
                       for word in patterns if word in text_lower)
    
    if jawa_score > 0 and jawa_score >= sunda_score and jawa_score >= betawi_score:
        return 'javanese'
    elif sunda_score > 0 and sunda_score >= betawi_score:
        return 'sundanese'
    elif betawi_score > 0:
        return 'betawi'
    
    return 'indonesian'

def enhance_prompt_with_language(prompt: str, detected_lang: str) -> str:
    """Add language context to prompt"""
    if detected_lang == 'javanese':
        prefix = "[User using Javanese] "
    elif detected_lang == 'sundanese':
        prefix = "[User using Sundanese] "
    elif detected_lang == 'betawi':
        prefix = "[User using Betawi] "
    else:
        prefix = ""
    
    return prefix + prompt
