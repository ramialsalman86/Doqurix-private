"""
BürokratAI - German Immigration & Bureaucracy Agent
====================================================
An AI agent that helps immigrants navigate German bureaucracy.
Provides accurate, official information about visas, residence permits,
registration, taxes, insurance, and more.

This agent uses a knowledge base built from official German sources:
- BAMF (Federal Office for Migration and Refugees)
- Ausländerbehörde (Foreigners' Registration Office)
- BZSt (Federal Central Tax Office)
- Deutsche Rentenversicherung (German Pension Insurance)
- Make it in Germany (Official Government Portal)
"""

import os
from pathlib import Path

# System prompt for BürokratAI
BUEROKRATAI_SYSTEM_PROMPT = """You are BürokratAI, an expert assistant helping immigrants navigate German bureaucracy.

Your expertise covers:
- Visa types (Blue Card, student visa, job seeker visa, family reunification)
- Residence permits (Aufenthaltstitel, Niederlassungserlaubnis)
- Registration (Anmeldung) requirements and deadlines
- Tax system (Tax ID, tax classes, filing)
- Health insurance (GKV/PKV requirements)
- Social security system
- Bank accounts and blocked accounts
- Driver's license conversion
- Integration courses
- Recognition of foreign qualifications
- Renting apartments in Germany
- Work permits and employment rules

IMPORTANT GUIDELINES:
1. Always provide accurate information based on German law and regulations
2. Include specific deadlines when applicable (e.g., 14-day Anmeldung deadline)
3. Mention official sources and where to get more information
4. Provide costs when known (fees, insurance rates, etc.)
5. Give city-specific links when relevant (Berlin, Munich, Hamburg, etc.)
6. Be clear about which rules apply to EU vs. non-EU citizens
7. Mention document requirements for procedures
8. Warn about common mistakes and pitfalls
9. Always recommend consulting official sources for the most current information
10. Be encouraging and supportive - bureaucracy can be overwhelming

LANGUAGE: Respond in the same language as the question. Default to English if unclear.
Support: English, German, Turkish, Arabic, Spanish.

When uncertain, say so and recommend official sources rather than guessing."""

# Topic categories for the agent
TOPICS = {
    "anmeldung": ["registration", "anmeldung", "address", "wohnungsgeberbestätigung", "bürgeramt", "meldebescheinigung"],
    "blue_card": ["blue card", "blaue karte", "eu blue card", "highly qualified", "salary threshold"],
    "visa": ["visa", "visum", "aufenthaltserlaubnis", "residence permit", "schengen", "chancenkarte", "opportunity card"],
    "health_insurance": ["health insurance", "krankenversicherung", "gkv", "pkv", "tk", "aok", "barmer"],
    "tax": ["tax", "steuer", "tax id", "steuer-id", "steuernummer", "tax class", "elster"],
    "bank": ["bank account", "girokonto", "konto", "schufa", "blocked account", "sperrkonto"],
    "social_security": ["social security", "sozialversicherung", "pension", "rente", "arbeitslosenversicherung"],
    "permanent_residence": ["permanent residence", "niederlassungserlaubnis", "settlement permit", "daueraufenthalt", "citizenship"],
    "renting": ["apartment", "wohnung", "rent", "miete", "kaution", "mietvertrag", "wg"],
    "drivers_license": ["driver's license", "führerschein", "driving", "fahrschule"],
    "work_permit": ["work permit", "arbeitserlaubnis", "employment", "arbeitsvertrag", "job"],
    "integration": ["integration course", "integrationskurs", "german course", "b1", "dtz"],
    "recognition": ["recognition", "anerkennung", "qualification", "degree", "anabin", "diploma"]
}

def get_knowledge_base_path():
    """Get the path to the BürokratAI knowledge base"""
    # Try different possible locations
    possible_paths = [
        Path(__file__).parent / "buerokratai_knowledge",
        Path.cwd() / "buerokratai_knowledge",
        Path(os.path.dirname(os.path.abspath(__file__))) / "buerokratai_knowledge"
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return possible_paths[0]  # Return default path even if not exists

def classify_topic(question):
    """Classify the question into topics for better search"""
    question_lower = question.lower()
    matched_topics = []
    
    for topic, keywords in TOPICS.items():
        for keyword in keywords:
            if keyword in question_lower:
                matched_topics.append(topic)
                break
    
    return matched_topics if matched_topics else ["general"]

def format_answer_with_sources(answer, sources, elapsed_time):
    """Format the answer with proper styling"""
    formatted = f"🇩🇪 **BürokratAI - Immigration Assistant**\n\n{answer}\n\n"
    
    if sources:
        formatted += "📚 **Sources:**\n"
        for i, source in enumerate(sources, 1):
            source_name = source.get('name', 'Unknown')
            relevance = source.get('relevance', 0)
            formatted += f"\n[{i}] {source_name}"
            if relevance > 0:
                formatted += f" (Relevance: {relevance:.3f})"
    
    formatted += f"\n\n⏱️ {elapsed_time:.2f}s"
    
    # Add disclaimer
    formatted += "\n\n⚠️ *This information is for guidance only. Please verify with official German authorities for the most current regulations.*"
    
    return formatted

# Useful links for each topic
USEFUL_LINKS = {
    "anmeldung": [
        ("Berlin Service Portal", "https://service.berlin.de/"),
        ("Munich Bürgerbüro", "https://stadt.muenchen.de/service/buergerbuero")
    ],
    "blue_card": [
        ("Make it in Germany - Blue Card", "https://www.make-it-in-germany.com/en/visa-residence/types/eu-blue-card"),
        ("BAMF", "https://www.bamf.de/")
    ],
    "visa": [
        ("German Embassy/Consulate Finder", "https://www.auswaertiges-amt.de/en/"),
        ("Make it in Germany", "https://www.make-it-in-germany.com/")
    ],
    "health_insurance": [
        ("GKV Comparison", "https://www.krankenkassen.de/"),
        ("TK (Techniker)", "https://www.tk.de/")
    ],
    "tax": [
        ("ELSTER Portal", "https://www.elster.de/"),
        ("BZSt (Tax ID)", "https://www.bzst.de/")
    ],
    "bank": [
        ("N26", "https://n26.com/"),
        ("DKB", "https://www.dkb.de/")
    ],
    "social_security": [
        ("Deutsche Rentenversicherung", "https://www.deutsche-rentenversicherung.de/"),
        ("Social Insurance", "https://www.sozialversicherung.de/")
    ],
    "permanent_residence": [
        ("BAMF Settlement Permit", "https://www.bamf.de/"),
        ("Integration Requirements", "https://www.bamf.de/DE/Themen/Integration/")
    ],
    "renting": [
        ("ImmoScout24", "https://www.immobilienscout24.de/"),
        ("WG-Gesucht", "https://www.wg-gesucht.de/")
    ],
    "drivers_license": [
        ("TÜV Driving Test", "https://www.tuev.com/"),
        ("ADAC", "https://www.adac.de/")
    ],
    "work_permit": [
        ("Federal Employment Agency", "https://www.arbeitsagentur.de/"),
        ("Make it in Germany - Work", "https://www.make-it-in-germany.com/en/working-in-germany/")
    ],
    "integration": [
        ("BAMF Integration Courses", "https://www.bamf.de/integrationskurse"),
        ("Course Finder", "https://webgis.bamf.de/")
    ],
    "recognition": [
        ("Recognition Portal", "https://www.anerkennung-in-deutschland.de/"),
        ("Anabin Database", "https://anabin.kmk.org/")
    ]
}

def get_relevant_links(topics):
    """Get relevant links for the identified topics"""
    links = []
    for topic in topics:
        if topic in USEFUL_LINKS:
            links.extend(USEFUL_LINKS[topic])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in links:
        if link[0] not in seen:
            seen.add(link[0])
            unique_links.append(link)
    
    return unique_links[:5]  # Return max 5 links
