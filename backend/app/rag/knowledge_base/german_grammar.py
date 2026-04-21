"""Core German grammar knowledge base chunks for RAG indexing."""

GRAMMAR_CHUNKS = [
    {
        "content": """German Cases (Fälle) - Overview
German has four grammatical cases: Nominativ (subject), Akkusativ (direct object), Dativ (indirect object), Genitiv (possession).
The case determines the article form:
- Nominativ: der/die/das/die (m/f/n/pl)
- Akkusativ: den/die/das/die (m/f/n/pl)
- Dativ: dem/der/dem/den (m/f/n/pl)
- Genitiv: des/der/des/der (m/f/n/pl)
Example: Der Mann (Nom) gibt der Frau (Dat) den Ball (Akk).""",
        "source": "german_grammar_core",
        "cefr_level": "A2",
        "topic": "cases",
    },
    {
        "content": """German Verb Conjugation - Present Tense (Präsens)
Regular verbs follow the pattern: stem + ending
machen (to do/make): ich mache, du machst, er/sie/es macht, wir machen, ihr macht, sie/Sie machen
Strong verbs often have vowel change for du/er forms:
fahren (to drive): ich fahre, du fährst, er fährt, wir fahren, ihr fahrt, sie fahren
lesen (to read): ich lese, du liest, er liest, wir lesen, ihr lest, sie lesen""",
        "source": "german_grammar_core",
        "cefr_level": "A1",
        "topic": "conjugation",
    },
    {
        "content": """German Modal Verbs (Modalverben)
The six modal verbs: können (can), müssen (must), dürfen (may/allowed), wollen (want), sollen (should), mögen (like)
In a modal verb sentence, the main verb goes to the END in infinitive form:
Ich kann Deutsch sprechen. (I can speak German.)
Er muss heute arbeiten. (He must work today.)
Sie darf nicht rauchen. (She is not allowed to smoke.)
Wir wollen nach Berlin fahren. (We want to go to Berlin.)""",
        "source": "german_grammar_core",
        "cefr_level": "A2",
        "topic": "modal_verbs",
    },
    {
        "content": """German Word Order (Wortstellung)
Main clause: Subject + Verb + (Objects/Adverbials)
Key rule: The finite verb is ALWAYS in position 2.
If another element starts the sentence, verb and subject swap (inversion):
Gestern habe ich Kaffee getrunken. (Yesterday I drank coffee.)
In subordinate clauses (with conjunctions weil, dass, obwohl, wenn), the verb goes to the END:
Ich lerne Deutsch, weil es interessant ist.
Ich weiß, dass er morgen kommt.""",
        "source": "german_grammar_core",
        "cefr_level": "A2",
        "topic": "word_order",
    },
    {
        "content": """German Perfect Tense (Perfekt) - Past Events
Perfekt = haben/sein + past participle (Partizip II)
Most verbs use HABEN: Ich habe gegessen. (I have eaten / I ate.)
Motion/state-change verbs use SEIN: Ich bin gefahren. (I drove.) Er ist eingeschlafen. (He fell asleep.)
Regular participle: ge- + stem + -t: machen → gemacht, spielen → gespielt
Irregular participle: ge- + irregular stem + -en: essen → gegessen, fahren → gefahren, gehen → gegangen
Separable verbs: eingekauft (einkaufen), aufgestanden (aufstehen)
Verbs ending in -ieren: no ge- prefix: studiert, telefoniert""",
        "source": "german_grammar_core",
        "cefr_level": "A2",
        "topic": "perfect_tense",
    },
    {
        "content": """German Articles and Gender (Artikel und Genus)
Every German noun has a gender: masculine (der), feminine (die), or neuter (das).
Helpful patterns:
- Words ending in -ung, -heit, -keit, -schaft, -tion → feminine (die)
- Words ending in -er (agent nouns), -ismus → masculine (der)
- Words ending in -chen, -lein (diminutives), -um → neuter (das)
- Compound nouns take the gender of the LAST word: das Handy + die Nummer = die Handynummer
Indefinite articles: ein (m/n), eine (f) — kein/keine for negation""",
        "source": "german_grammar_core",
        "cefr_level": "A1",
        "topic": "articles_gender",
    },
    {
        "content": """German Subordinating Conjunctions (Subjunktionen)
Common subordinating conjunctions that send the verb to the end:
weil (because): Ich bleibe, weil es regnet.
obwohl (although): Er kommt, obwohl er müde ist.
wenn (when/if): Wenn ich Zeit habe, lese ich.
dass (that): Ich weiß, dass du recht hast.
damit (so that): Sie lernt, damit sie die Prüfung besteht.
bevor (before): Bevor ich schlafe, putze ich die Zähne.
nachdem (after): Nachdem er gegessen hatte, schlief er.
Note: In spoken German, "weil" is sometimes used with verb-2nd position informally.""",
        "source": "german_grammar_core",
        "cefr_level": "B1",
        "topic": "conjunctions",
    },
    {
        "content": """German Konjunktiv II - Subjunctive Mood
Used for: wishes, polite requests, hypotheticals, indirect speech
Formation for common verbs:
sein → wäre: Ich wäre gern Arzt. (I would like to be a doctor.)
haben → hätte: Ich hätte gern mehr Zeit. (I would like to have more time.)
werden → würde + infinitive: Ich würde das gerne machen. (I would like to do that.)
können → könnte: Könnten Sie mir helfen? (Could you help me?)
müssen → müsste: Er müsste das wissen. (He should know that.)
Polite requests: Würden Sie bitte... / Könnten Sie bitte...""",
        "source": "german_grammar_core",
        "cefr_level": "B2",
        "topic": "konjunktiv_ii",
    },
    {
        "content": """German Passive Voice (Passiv)
Vorgangspassiv (process): werden + Partizip II
Das Buch wird gelesen. (The book is being read.)
Das Buch wurde gelesen. (The book was read.)
Das Buch ist gelesen worden. (The book has been read.) - Perfekt passive
Zustandspassiv (state): sein + Partizip II
Die Tür ist geöffnet. (The door is open.)
Agent expressed with "von + Dativ": Das Buch wurde von Goethe geschrieben.
Passive with modal: Das muss getan werden. (That must be done.)""",
        "source": "german_grammar_core",
        "cefr_level": "B1",
        "topic": "passive",
    },
    {
        "content": """German Adjective Endings (Adjektivdeklinationen)
Three declension patterns depending on article type:
1. Strong (no article): kalter Kaffee, frisches Wasser
2. Weak (after definite article der/die/das): der kalte Kaffee, die schöne Frau
3. Mixed (after indefinite article ein): ein kalter Kaffee, eine schöne Frau
Key patterns for Nominativ/Akkusativ:
- der Mann → den alten Mann (Akk m: -en ending)
- die Frau → der schönen Frau (Dat f: -en ending)
Memory trick: The article must show the case somehow — if the article does it, adjective gets -en; if not, adjective carries the marker.""",
        "source": "german_grammar_core",
        "cefr_level": "B1",
        "topic": "adjective_endings",
    },
]
