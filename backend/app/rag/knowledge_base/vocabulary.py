"""German vocabulary knowledge base for RAG."""

VOCABULARY_CHUNKS = [
    {
        "content": """Essential A1 Vocabulary - Greetings and Basic Phrases
Hallo / Guten Tag / Guten Morgen / Guten Abend / Gute Nacht
Tschüss / Auf Wiedersehen / Bis bald / Bis später
Bitte (please/you're welcome) / Danke (thank you) / Danke schön (thank you very much)
Entschuldigung (excuse me/sorry) / Es tut mir leid (I'm sorry)
Wie heißen Sie? / Ich heiße... (What is your name? / My name is...)
Wie geht es Ihnen? / Mir geht es gut. (How are you? / I am fine.)
Woher kommen Sie? / Ich komme aus... (Where are you from? / I'm from...)
Sprechen Sie Deutsch? / Ein bisschen. (Do you speak German? / A little.)""",
        "source": "vocabulary_a1",
        "cefr_level": "A1",
        "topic": "greetings",
    },
    {
        "content": """German Numbers (Zahlen) - A1
0-10: null, eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun, zehn
11-19: elf, zwölf, dreizehn, vierzehn, fünfzehn, sechzehn, siebzehn, achtzehn, neunzehn
20-100: zwanzig, dreißig, vierzig, fünfzig, sechzig, siebzig, achtzig, neunzig, hundert
Compound numbers: einundzwanzig (21), zweiunddreißig (32) — units before tens, connected with "und"
Large numbers: tausend (1,000), zehntausend (10,000), hunderttausend (100,000), eine Million (1,000,000)
Ordinal numbers: erste, zweite, dritte, vierte, fünfte (1st, 2nd, 3rd, 4th, 5th)""",
        "source": "vocabulary_a1",
        "cefr_level": "A1",
        "topic": "numbers",
    },
    {
        "content": """German Workplace Vocabulary (Arbeitsplatz) - B1/B2
die Stelle / die Arbeitsstelle - job position
der Arbeitgeber / der Arbeitnehmer - employer / employee
die Bewerbung - job application
das Vorstellungsgespräch - job interview
der Lebenslauf (CV/resume)
das Gehalt / der Lohn - salary / wage
die Gehaltsvorstellung - salary expectation
die Probezeit - probationary period
der Arbeitsvertrag - employment contract
die Kündigung - termination / resignation
die Überstunden - overtime
das Homeoffice - home office / remote work
der Betriebsrat - works council (Germany-specific)
die Urlaubstage - vacation days (German standard: 24-30 days)
die Krankmeldung - sick note (Krankenschein)""",
        "source": "vocabulary_workplace",
        "cefr_level": "B1",
        "topic": "workplace",
    },
    {
        "content": """German IT/Tech Vocabulary for Job Seekers
die Softwareentwicklung - software development
der Entwickler / die Entwicklerin - developer
das Projekt - project
die Anforderungen - requirements
die Schnittstelle - interface / API
die Datenbank - database
die Cloud - cloud
die künstliche Intelligenz (KI) - artificial intelligence (AI)
maschinelles Lernen - machine learning
die Agile Methodik - agile methodology
der Sprint - sprint
das Scrum - scrum
die Codeüberprüfung - code review
das Debugging - debugging
die Versionskontrolle - version control
die Continuous Integration - CI/CD
der Tech Stack - tech stack
die Skalierbarkeit - scalability""",
        "source": "vocabulary_tech",
        "cefr_level": "B2",
        "topic": "technology",
    },
    {
        "content": """German Housing Vocabulary (Wohnen)
die Wohnung - apartment
das Haus - house / home
das Zimmer - room
die Miete - rent
der Vermieter / die Vermieterin - landlord / landlady
der Mieter / die Mieterin - tenant
die Kaution - security deposit (usually 2-3 months rent)
die Nebenkosten - additional costs (utilities)
der Mietvertrag - rental contract
die Wohngemeinschaft (WG) - shared apartment
die Besichtigung - viewing appointment
die Betriebskosten - operating costs
die Heizkosten - heating costs
der Energieausweis - energy certificate (required by law)
die Abmeldung / Anmeldung - deregistration / registration at Bürgeramt""",
        "source": "vocabulary_housing",
        "cefr_level": "B1",
        "topic": "housing",
    },
    {
        "content": """German Bureaucracy Vocabulary (Behörden)
das Bürgeramt - citizen's office (for registration, ID)
die Anmeldung - registration of residence (required within 2 weeks of moving)
der Personalausweis - German ID card
der Reisepass - passport
die Aufenthaltserlaubnis - residence permit
das Visum - visa
die Arbeitserlaubnis - work permit
das Finanzamt - tax office
die Steuernummer - tax number
die Steuerklasse - tax class (I-VI in Germany)
die Krankenversicherung - health insurance (mandatory in Germany)
die gesetzliche / private KV - public / private health insurance
die Rentenversicherung - pension insurance
die Sozialversicherungsnummer - social security number
die SCHUFA - credit bureau (important for renting)""",
        "source": "vocabulary_bureaucracy",
        "cefr_level": "B1",
        "topic": "bureaucracy",
    },
    {
        "content": """German Cultural Notes and Idioms
Das ist mir Wurst. - I don't care. (Literally: That is sausage to me.)
Ich drücke dir die Daumen. - I'm keeping my fingers crossed. (Literally: I press the thumbs for you.)
Alles hat ein Ende, nur die Wurst hat zwei. - Everything has an end, only the sausage has two. (Things come to an end.)
Das ist nicht mein Bier. - That's not my problem. (Literally: That's not my beer.)
Auf dem Holzweg sein - To be on the wrong track (Literally: to be on the logging road)
Schwein haben - To be lucky (Literally: to have pig)
Ich verstehe nur Bahnhof. - It's all Greek to me. (Literally: I only understand train station.)
German directness: Germans value directness (Direktheit). "Nein" is not rude — it's clear communication.
Feierabend: The sacred end-of-workday — a time to disconnect from work completely.""",
        "source": "vocabulary_culture",
        "cefr_level": "B2",
        "topic": "culture_idioms",
    },
]
