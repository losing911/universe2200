"""
Cyberpunk Name Generator
Generates realistic handles, display names, and avatars for Universe 2200.
"""
import random

class NameGenerator:
    PREFIXES = [
        "Neo", "Cyber", "Dark", "Light", "Shadow", "Iron", "Steel", "Chrome", 
        "Data", "Net", "Web", "Sync", "Null", "Void", "Glitch", "Flux", 
        "Pulse", "Wave", "Vector", "Prime", "Zero", "One", "Binary", "Hex",
        "Neu", "Syn", "Mech", "Bio", "Techno", "Vapor", "Retro", "Hyper"
    ]
    
    SUFFIXES = [
        "Runner", "Stalker", "Walker", "Coder", "Hacker", "Phreak", "Ghost", 
        "Soul", "Mind", "Core", "Link", "Nexus", "Node", "Grid", "Matrix", 
        "Viper", "Wolf", "Raven", "Hawk", "Eagle", "Rat", "Punk", "Junkie", 
        "Head", "Brain", "Face", "Eyes", "Hand", "Fist", "Blade", "Edge"
    ]
    
    FIRST_NAMES = [
        "Kael", "Ryx", "Jace", "Nyx", "Zane", "Vera", "Xon", "Mira", "Tyrell", 
        "Deckard", "Motoko", "Bato", "Case", "Molly", "Hiro", "Y.T.", "Korben", 
        "Leeloo", "Trinity", "Neo", "Morpheus", "Cypher", "Tank", "Dozer", 
        "Switch", "Apoc", "Mouse", "Revy", "Rock", "Benny", "Dutch", "Spike"
    ]
    
    LAST_NAMES = [
        "Vance", "Sterling", "Gibson", "Stephenson", "Dick", "Asimov", "Clarke", 
        "Herbert", "Orwell", "Huxley", "Bradbury", "Sagan", "Tyson", "Nye", 
        "Musk", "Gates", "Jobs", "Wozniak", "Torvalds", "Berners", "Lee", 
        "Lovelace", "Turing", "Hopper", "Hamilton", "Johnson", "Jackson", "Vaughan"
    ]

    AVATAR_BASES = [
        "https://api.dicebear.com/7.x/bottts/svg?seed=",
        "https://api.dicebear.com/7.x/avataaars/svg?seed=",
        "https://api.dicebear.com/7.x/identicon/svg?seed=",
        "https://api.dicebear.com/7.x/shapes/svg?seed="
    ]
    
    @staticmethod
    def generate_name(seed=None) -> dict:
        rng = random.Random(seed) if seed else random.Random()
        
        style = rng.choice(["handle", "real", "code"])
        
        if style == "handle":
            p = rng.choice(NameGenerator.PREFIXES)
            s = rng.choice(NameGenerator.SUFFIXES)
            n = 0
            if rng.random() > 0.5:
                n = rng.randint(0, 9999)
                handle = f"{p}{s}_{n}"
            else:
                handle = f"{p}_{s}"
            display_name = handle
            
        elif style == "real":
            f = rng.choice(NameGenerator.FIRST_NAMES)
            l = rng.choice(NameGenerator.LAST_NAMES)
            display_name = f"{f} {l}"
            handle = f"{f}.{l}".lower()
            if rng.random() > 0.5:
                handle += str(rng.randint(0, 99))
                
        else: # code
            p = rng.choice(NameGenerator.PREFIXES)
            code = rng.randint(100, 999)
            handle = f"{p}-{code}"
            display_name = handle
            
        # Generate Avatar
        avatar_type = rng.choice(NameGenerator.AVATAR_BASES)
        avatar_url = f"{avatar_type}{handle}"
        
        return {
            "handle": "@" + handle,
            "display_name": display_name,
            "avatar": avatar_url
        }
