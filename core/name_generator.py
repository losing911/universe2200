"""
Cyberpunk Name Generator
Generates realistic modern handles, display names, and avatars for Universe 2200.
"""
import random

class NameGenerator:
    # Modern, cool, but not cliché cyberpunk prefixes/suffixes for handles
    HANDLE_PREFIXES = [
        "real", "its", "the", "official", "just", "meta", "crypto", "async", 
        "hyper", "neon", "lux", "zen", "nova", "echo", "flux", "velvet",
        "urban", "night", "solar", "lunar", "wild", "free", "pure"
    ]
    
    HANDLE_SUFFIXES = [
        "verse", "flow", "wave", "mode", "zone", "mind", "soul", "vibe",
        "live", "now", "sys", "net", "xyz", "bot", "haze", "mist",
        "dreams", "truth", "zero", "one", "pro", "max"
    ]
    
    # Modern First Names (Mix of English/Euro/Turkish - Global vibe)
    MALE_NAMES = [
        "Alex", "Ryan", "Leo", "Kai", "Jax", "Owen", "Ezra", "Luca", "Noah", 
        "Liam", "Ethan", "Mason", "Logan", "Aiden", "Caleb", "Gabriel", "Luke", 
        "Emir", "Can", "Aras", "Kaan", "Atlas", "Mars", "Orion", "Chase", "Cole",
        "Dante", "Enzo", "Finn", "Hugo", "Ivan", "Jett", "Kobe", "Luis", "Milo",
        "Nico", "Omar", "Paul", "Quinn", "Ravi", "Seth", "Troy", "Umar", "Vito"
    ]
    
    FEMALE_NAMES = [
        "Ava", "Mia", "Zoe", "Ivy", "Lia", "Sky", "Luna", "Maya", "Nora", 
        "Ella", "Ruby", "Rose", "Jade", "Hope", "Lily", "Iris", "Cleo",
        "Ada", "Ela", "Nil", "Su", "Lara", "Mina", "Peri", "Sera", "Aria",
        "Bella", "Cara", "Demi", "Elsa", "Faye", "Gia", "Hana", "Ines", 
        "Joy", "Kira", "Leia", "Mara", "Nina", "Olga", "Pia", "Ria", "Sia", 
        "Tara", "Uma", "Vera", "Willa", "Xena", "Yara", "Zara"
    ]
    
    LAST_NAMES = [
        "Vance", "Cross", "Steel", "Wolf", "Moon", "Sun", "Fox", "West", "North",
        "River", "Stone", "Storm", "Frost", "Rain", "Snow", "Woods", "Brooks",
        "Hayes", "Ford", "Gray", "Black", "White", "Blue", "Green", "Red",
        "King", "Knight", "Prince", "Duke", "Earl", "Baron", "Lord", "Stark",
        "Wayne", "Kent", "Lane", "Drake", "Cole", "Hart", "Bond", "Hunt",
        "Yilmaz", "Demir", "Kaya", "Celik", "Sahin", "Yildiz", "Ozturk", "Aydin"
    ]

    @staticmethod
    def generate_name(seed=None) -> dict:
        rng = random.Random(seed) if seed else random.Random()
        
        # 1. Determine Gender (approx 50/50)
        gender = "male" if rng.random() > 0.5 else "female"
        
        # 2. Pick Name
        first_name = rng.choice(NameGenerator.MALE_NAMES if gender == "male" else NameGenerator.FEMALE_NAMES)
        last_name = rng.choice(NameGenerator.LAST_NAMES)
        
        display_name = f"{first_name} {last_name}"
        
        # 3. Generate Handle
        style = rng.choice(["classic", "underscore", "period", "prefix", "suffix"])
        if style == "classic":
            handle = f"{first_name}{last_name}".lower()
        elif style == "underscore":
            handle = f"{first_name}_{last_name}".lower()
        elif style == "period":
            handle = f"{first_name}.{last_name}".lower()
        elif style == "prefix":
            prefix = rng.choice(NameGenerator.HANDLE_PREFIXES)
            handle = f"{prefix}{first_name}".lower()
        else: # suffix
            suffix = rng.choice(NameGenerator.HANDLE_SUFFIXES)
            handle = f"{first_name}{suffix}".lower()
        
        # Add random numbers if handle likely taken (simulated)
        if rng.random() > 0.7:
            handle += str(rng.randint(1, 99))
            
        # 4. Generate Avatar
        # Using randomuser.me for realistic placeholders mapped to seed/gender
        # Map a seed-based index (0-99) to the photo ID
        photo_id = rng.randint(0, 99)
        # randomuser.me uses 'men' and 'women' in path
        gender_path = "men" if gender == "male" else "women"
        avatar_url = f"https://randomuser.me/api/portraits/{gender_path}/{photo_id}.jpg"
        
        return {
            "gender": gender,
            "handle": "@" + handle,
            "display_name": display_name,
            "avatar": avatar_url
        }
