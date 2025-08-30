from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime, timedelta
import random
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# NASA API endpoints (most are free, no API key required)
NASA_APOD_API = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
NASA_NEO_API = "https://api.nasa.gov/neo/rest/v1/feed?api_key=DEMO_KEY"
NASA_MARS_API = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key=DEMO_KEY"
NASA_EARTH_API = "https://api.nasa.gov/planetary/earth/assets?lon=-95.33&lat=29.78&dim=0.10&api_key=DEMO_KEY"

# ISRO-related news and info (using general space news APIs since ISRO doesn't have open APIs)
SPACE_NEWS_API = "https://api.spacexdata.com/v4/launches/latest"

# Initialize Google Gemini with your API key
try:
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    if google_api_key:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("🤖 Google Gemini AI integrated successfully with your API key!")
    else:
        print("⚠️ No Google API key found, using basic responses")
        model = None
except Exception as e:
    print(f"⚠️ Gemini setup error: {e}")
    model = None

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/space-chat', methods=['POST'])
def space_chat():
    """
    Handle chat messages and return space-related responses from NASA/ISRO data
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        
        # Determine what type of space information to fetch based on user message
        if 'apod' in user_message or 'picture' in user_message or 'photo' in user_message or 'image' in user_message:
            response = get_nasa_apod()
        elif 'asteroid' in user_message or 'neo' in user_message or 'near earth' in user_message:
            response = get_nasa_neo_data()
        elif 'mars' in user_message or 'rover' in user_message or 'curiosity' in user_message:
            response = get_mars_rover_data()
        elif 'spacex' in user_message or 'launch' in user_message or 'rocket' in user_message:
            response = get_spacex_launch_data()
        elif 'isro' in user_message or 'indian space' in user_message or 'india' in user_message:
            response = get_isro_info()
        elif any(constellation in user_message for constellation in ['ursa major', 'ursa minor', 'orion', 'cassiopeia', 'andromeda', 'constellation', 'big dipper', 'little dipper']):
            response = get_constellation_info(user_message)
        elif any(planet in user_message for planet in ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'planet']):
            response = get_planet_info(user_message)
        elif any(term in user_message for term in ['star', 'sun', 'supernova', 'neutron star', 'white dwarf', 'black hole']):
            response = get_stellar_info(user_message)
        elif any(term in user_message for term in ['galaxy', 'milky way', 'andromeda galaxy', 'spiral galaxy']):
            response = get_galaxy_info(user_message)
        else:
            # Use AI to answer any space question intelligently
            response = get_smart_space_answer(user_message)
            
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'response': f"I'm having trouble connecting to space agencies right now, but here's an interesting space fact: The universe is about 13.8 billion years old and contains over 2 trillion galaxies! 🌌 Error details: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 200

def get_nasa_apod():
    """Get NASA Astronomy Picture of the Day"""
    try:
        response = requests.get(NASA_APOD_API, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"🌟 **NASA's Astronomy Picture of the Day**: {data.get('title', 'Amazing Space Image')}\n\n{data.get('explanation', 'A beautiful view from space!')}\n\n📅 Date: {data.get('date', 'Today')}\n🔗 You can view it at: {data.get('url', 'NASA APOD website')}"
        else:
            return get_fallback_apod_info()
    except:
        return get_fallback_apod_info()

def get_fallback_apod_info():
    """Fallback APOD information when API fails"""
    apod_facts = [
        "🌟 **NASA's APOD Program**: Every day since 1995, NASA has featured a different image or photograph of our fascinating universe, along with a brief explanation written by a professional astronomer!",
        "📸 **Did you know?** NASA's Astronomy Picture of the Day has featured over 10,000 stunning images of space, from distant galaxies to planets in our solar system!",
        "🔭 **APOD Archive**: The NASA APOD archive contains decades of the most beautiful space images ever captured, each with detailed explanations from astronomers!"
    ]
    return random.choice(apod_facts)

def get_nasa_neo_data():
    """Get NASA Near Earth Objects data"""
    try:
        # Use today's date for NEO feed
        today = datetime.now().strftime('%Y-%m-%d')
        neo_url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key=DEMO_KEY"
        
        response = requests.get(neo_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            element_count = data.get('element_count', 0)
            if element_count > 0:
                neo_objects = data.get('near_earth_objects', {}).get(today, [])
                if neo_objects:
                    neo = neo_objects[0]  # Get first NEO
                    name = neo.get('name', 'Unknown asteroid')
                    diameter = neo.get('estimated_diameter', {}).get('meters', {})
                    min_diameter = diameter.get('estimated_diameter_min', 0)
                    max_diameter = diameter.get('estimated_diameter_max', 0)
                    
                    return f"🌌 **NASA NEO Update**: Today, there are {element_count} Near Earth Objects being tracked!\n\n🪨 **Featured Asteroid**: {name}\n📏 **Estimated Size**: {min_diameter:.1f} - {max_diameter:.1f} meters\n\n⚠️ NASA continuously monitors these objects to ensure Earth's safety! All current NEOs pose no threat to our planet."
                    
        return get_fallback_neo_info()
    except:
        return get_fallback_neo_info()

def get_fallback_neo_info():
    """Fallback NEO information"""
    neo_facts = [
        "🪨 **NASA NEO Program**: NASA tracks over 90% of near-Earth asteroids larger than 1 km. None of the known objects pose a threat to Earth for the next 100+ years!",
        "🌌 **Asteroid Facts**: There are currently over 28,000 known near-Earth asteroids. NASA discovers about 3,000 new ones each year using ground and space-based telescopes!",
        "🛡️ **Planetary Defense**: NASA's DART mission successfully changed an asteroid's orbit in 2022, proving we can defend Earth if needed!"
    ]
    return random.choice(neo_facts)

def get_mars_rover_data():
    """Get Mars rover information"""
    mars_facts = [
        "🔴 **Mars Rover Update**: NASA's Perseverance rover is currently exploring Jezero Crater, searching for signs of ancient microbial life and collecting samples for future return to Earth!",
        "🤖 **Rover Fleet**: NASA has successfully operated 5 rovers on Mars: Sojourner, Spirit, Opportunity, Curiosity, and Perseverance. Ingenuity helicopter made the first powered flight on another planet!",
        "🧪 **Mars Discovery**: NASA's rovers have confirmed that Mars once had flowing water, a thicker atmosphere, and conditions that could have supported life billions of years ago!",
        "📡 **Current Mission**: Perseverance has collected over 20 rock samples and Ingenuity has completed over 50 flights, far exceeding its planned 5 flights!"
    ]
    return random.choice(mars_facts)

def get_spacex_launch_data():
    """Get SpaceX launch information"""
    try:
        response = requests.get(SPACE_NEWS_API, timeout=10)
        if response.status_code == 200:
            data = response.json()
            mission_name = data.get('name', 'Unknown Mission')
            launch_date = data.get('date_utc', 'Unknown Date')
            details = data.get('details', 'No details available')
            success = data.get('success', False)
            
            status = "✅ Successful" if success else "❌ Failed" if success is False else "⏳ Scheduled"
            
            return f"🚀 **Latest SpaceX Mission**: {mission_name}\n\n📅 **Launch Date**: {launch_date}\n🎯 **Status**: {status}\n\n📝 **Details**: {details or 'This mission represents SpaceX continued efforts to advance space exploration and make life multiplanetary!'}"
    except:
        pass
    
    spacex_facts = [
        "🚀 **SpaceX Achievements**: SpaceX has revolutionized space travel with reusable rockets, reducing launch costs by 90% and making space more accessible than ever before!",
        "🌌 **Starship Program**: SpaceX is developing Starship, the most powerful rocket ever built, designed to carry humans to Mars and make life multiplanetary!",
        "🛰️ **Starlink Network**: SpaceX has deployed over 5,000 Starlink satellites, providing high-speed internet to remote areas worldwide and supporting global connectivity!"
    ]
    return random.choice(spacex_facts)

def get_isro_info():
    """Get ISRO (Indian Space Research Organization) information"""
    isro_facts = [
        "🇮🇳 **ISRO Achievements**: India's Mars Orbiter Mission (Mangalyaan) made India the first country to reach Mars orbit in its first attempt, and the most cost-effective Mars mission ever at just $74 million!",
        "🚀 **Chandrayaan Program**: ISRO's Chandrayaan-3 successfully landed on the Moon's south pole in 2023, making India the 4th country to land on the Moon and the first to reach the lunar south pole!",
        "🛰️ **PSLV Success**: ISRO's Polar Satellite Launch Vehicle has achieved over 95% success rate and holds the record for launching 104 satellites in a single mission!",
        "🌍 **Global Impact**: ISRO provides crucial Earth observation data for disaster management, weather forecasting, and agricultural monitoring, serving not just India but the entire world!",
        "💫 **Future Missions**: ISRO is planning Gaganyaan (human spaceflight program), Shukrayaan-1 (Venus mission), and Chandrayaan-4 (Moon sample return mission)!"
    ]
    return random.choice(isro_facts)

def get_random_space_fact():
    """Get random space facts with data context"""
    space_facts = [
        "🌌 **NASA Discovery**: The James Webb Space Telescope has detected galaxies that formed just 400 million years after the Big Bang, giving us unprecedented views of the early universe!",
        "⭐ **Stellar Facts**: According to NASA data, there are more stars in the observable universe than grains of sand on all Earth's beaches - approximately 10^24 stars!",
        "🌍 **Earth Science**: NASA Earth observing satellites have shown that Earth's ice sheets are losing mass at an accelerating rate, with critical implications for sea level rise!",
        "🪐 **Solar System**: NASA's Juno mission revealed that Jupiter has a 'fuzzy' core and produces auroras 1000 times brighter than Earth's!",
        "🚀 **ISS Updates**: The International Space Station travels at 17,500 mph, completing an orbit around Earth every 90 minutes. Astronauts see 16 sunrises and sunsets daily!",
        "🌟 **Exoplanet Hunt**: NASA has confirmed over 5,000 exoplanets so far, with many potentially habitable worlds in the 'Goldilocks zone' of their stars!"
    ]
    return random.choice(space_facts)

def get_constellation_info(user_message):
    """Get information about constellations"""
    constellation_data = {
        'ursa major': "🐻 **Ursa Major (The Great Bear)**: One of the most recognizable constellations! It contains the famous Big Dipper asterism - 7 bright stars that form a ladle shape. Located in the northern sky, it's visible year-round from most northern latitudes. The Big Dipper's pointer stars (Merak and Dubhe) help locate Polaris, the North Star. In mythology, it represents a great bear being hunted across the sky.",
        'big dipper': "✨ **The Big Dipper**: This isn't actually a constellation but an asterism (star pattern) within Ursa Major! The seven stars - Alkaid, Mizar, Alioth, Megrez, Phecda, Merak, and Dubhe - form the famous ladle shape. Interestingly, 5 of these stars are part of the Ursa Major Moving Group, traveling through space together.",
        'ursa minor': "🐻 **Ursa Minor (The Little Bear)**: Home to Polaris, the North Star! This constellation contains the Little Dipper asterism. Polaris sits nearly at the north celestial pole, making it appear stationary while other stars rotate around it. Ancient navigators have used Polaris for centuries to find true north.",
        'orion': "⭐ **Orion (The Hunter)**: Perhaps the most famous constellation! Visible worldwide, it features the iconic three stars of Orion's Belt (Alnitak, Alnilam, Mintaka). The red supergiant Betelgeuse marks his shoulder, while blue-white Rigel marks his foot. The Orion Nebula (M42) is a stellar nursery where new stars are born!",
        'cassiopeia': "👑 **Cassiopeia (The Queen)**: This distinctive W-shaped constellation is easy to spot in the northern sky! It's circumpolar from most northern latitudes, meaning it never sets. In mythology, Cassiopeia was a vain queen. The constellation helps locate Polaris and is opposite the Big Dipper across the north celestial pole.",
        'andromeda': "🌌 **Andromeda (The Princess)**: This constellation is famous for containing the Andromeda Galaxy (M31), our nearest major galactic neighbor! The galaxy is visible to the naked eye as a fuzzy patch. In mythology, Andromeda was a princess chained to a rock as sacrifice to a sea monster, but was saved by Perseus.",
        'scorpio': "🦂 **Scorpio (The Scorpion)**: A spectacular zodiac constellation visible in summer! Its brightest star is Antares, a red supergiant 700 times the size of our Sun. The constellation looks like a scorpion with a curved tail and claws. In mythology, it's the scorpion that killed Orion the Hunter. Best viewed in July and August in the southern sky!",
        'scorpius': "🦂 **Scorpio (The Scorpion)**: A spectacular zodiac constellation visible in summer! Its brightest star is Antares, a red supergiant 700 times the size of our Sun. The constellation looks like a scorpion with a curved tail and claws. In mythology, it's the scorpion that killed Orion the Hunter. Best viewed in July and August in the southern sky!",
        'leo': "🦁 **Leo (The Lion)**: A bright zodiac constellation that really looks like a lion! Its brightest star Regulus marks the lion's heart. The 'Sickle' asterism forms the lion's mane and head. Leo is home to many galaxies and the annual Leonid meteor shower in November. Best seen in spring evenings!",
        'virgo': "♍ **Virgo (The Virgin)**: The second-largest constellation in the sky! Its brightest star Spica is actually a binary star system. Virgo contains over 1,300 galaxies in the Virgo Cluster. In mythology, Virgo represents the goddess of harvest. Best visible in late spring and early summer!",
        'gemini': "♊ **Gemini (The Twins)**: Features the bright stars Castor and Pollux, representing the twin brothers in Greek mythology! Gemini is a zodiac constellation best seen in winter. It's home to the beautiful open star cluster M35 and was the radiant point for the 2020 SpaceX mission naming!",
        'cancer': "🦀 **Cancer (The Crab)**: The faintest zodiac constellation, but it contains the beautiful Beehive Cluster (M44)! In mythology, it's the crab that pinched Hercules during his battle with the Hydra. Cancer is best seen in late winter and early spring between Gemini and Leo!",
        'aquarius': "🏺 **Aquarius (The Water Bearer)**: A large zodiac constellation known for meteor showers! Home to the radiant points of several meteor showers including the Aquarids. Its brightest star is Sadalsuud. Best viewed in autumn evenings in the southern sky!",
        'pisces': "🐟 **Pisces (The Fishes)**: A large but faint zodiac constellation representing two fish tied together! Contains the vernal equinox point where the Sun crosses the celestial equator in spring. Best seen in autumn evenings, though it requires dark skies due to its faint stars!"
    }
    
    for constellation, info in constellation_data.items():
        if constellation in user_message:
            return info
    
    # General constellation information
    return "✨ **Constellations**: Star patterns that have guided humanity for thousands of years! There are 88 official constellations covering the entire sky. They help us navigate, tell time, and share stories across cultures. Popular northern constellations include Ursa Major (Big Dipper), Orion, and Cassiopeia. Which constellation interests you?"

def get_planet_info(user_message):
    """Get information about planets"""
    planet_data = {
        'mercury': "☿️ **Mercury**: The closest planet to the Sun and the smallest in our solar system! It has extreme temperature swings from 800°F (430°C) during the day to -290°F (-180°C) at night. A year on Mercury (88 Earth days) is shorter than its day (176 Earth days)! NASA's MESSENGER mission mapped its entire surface.",
        'venus': "♀️ **Venus**: Earth's 'evil twin' and the hottest planet in our solar system! Its thick atmosphere of carbon dioxide creates a runaway greenhouse effect, reaching 900°F (480°C) - hot enough to melt lead. It rotates backwards and a day is longer than a year there! Often called the 'Morning Star' or 'Evening Star.'",
        'earth': "🌍 **Earth**: Our beautiful blue marble and the only known planet with life! 71% covered by oceans, with a perfect distance from the Sun for liquid water. Protected by a magnetic field and ozone layer, it's home to millions of species. NASA monitors Earth's climate and changes from space with dozens of satellites!",
        'mars': "🔴 **Mars**: The Red Planet, our most explored neighbor! It gets its color from iron oxide (rust) on its surface. Mars has the largest volcano (Olympus Mons) and canyon (Valles Marineris) in the solar system. NASA's rovers have found evidence of ancient rivers and lakes - it may have harbored life billions of years ago!",
        'jupiter': "🪐 **Jupiter**: The king of planets! This gas giant is so massive it could fit all other planets inside it. Jupiter acts as our cosmic protector, attracting asteroids and comets with its powerful gravity. It has over 80 moons, including the four Galilean moons discovered in 1610. The Great Red Spot is a storm larger than Earth!",
        'saturn': "🪐 **Saturn**: The jewel of our solar system with its stunning rings! These rings are made of billions of ice and rock particles. Saturn is so light it would float in water! It has 146 known moons, including Titan with its thick atmosphere and liquid methane lakes. NASA's Cassini mission revealed incredible details about Saturn's system.",
        'uranus': "🌀 **Uranus**: The tilted ice giant! It rotates on its side at a 98-degree angle, possibly due to an ancient collision. Composed mainly of water, methane, and ammonia ices, it appears blue-green due to methane in its atmosphere. It has faint rings and 27 known moons named after Shakespeare characters!",
        'neptune': "💙 **Neptune**: The windiest planet with speeds up to 1,200 mph (2,000 km/h)! This deep blue ice giant is the farthest known planet from the Sun. It takes 165 Earth years to complete one orbit! Neptune has 16 known moons, with Triton being the largest and orbiting backwards, suggesting it's a captured Kuiper Belt object."
    }
    
    for planet, info in planet_data.items():
        if planet in user_message:
            return info
    
    return "🪐 **Our Solar System**: Contains 8 amazing planets, each unique! From scorching Mercury to icy Neptune, they show incredible diversity. NASA missions have visited all planets, revolutionizing our understanding. Which planet would you like to explore?"

def get_stellar_info(user_message):
    """Get information about stars and stellar objects"""
    stellar_data = {
        'star': "⭐ **Stars**: Massive nuclear fusion reactors that light up the universe! They fuse hydrogen into helium in their cores, releasing enormous energy. Stars are born in nebulae, live for millions to billions of years, and end as white dwarfs, neutron stars, or black holes depending on their mass.",
        'sun': "☀️ **Our Sun**: A middle-aged yellow dwarf star that's been shining for 4.6 billion years! Every second, it converts 600 million tons of hydrogen into helium, powering all life on Earth. The Sun's core reaches 27 million°F (15 million°C). Solar activity follows an 11-year cycle monitored by NASA's Solar Dynamics Observatory.",
        'supernova': "💥 **Supernovae**: The explosive death of massive stars! These cosmic explosions are so bright they can outshine entire galaxies. They create and scatter heavy elements like iron and gold throughout the universe - we are literally made of star stuff! NASA telescopes regularly discover supernovae in distant galaxies.",
        'neutron star': "⚡ **Neutron Stars**: The ultra-dense remnants of massive stars! A sugar-cube sized piece would weigh 6 billion tons on Earth. They can spin 700 times per second and have magnetic fields trillions of times stronger than Earth's. Some emit radio beams (pulsars) that sweep across space like cosmic lighthouses.",
        'white dwarf': "💎 **White Dwarfs**: The hot, dense cores left behind when Sun-like stars die! About the size of Earth but with the mass of the Sun. They slowly cool over billions of years, eventually becoming cold, dark objects. Our Sun will become a white dwarf in about 5 billion years.",
        'black hole': "🕳️ **Black Holes**: Regions of spacetime where gravity is so strong that nothing, not even light, can escape! They form when massive stars collapse. NASA's Event Horizon Telescope captured the first image of a black hole in 2019. The supermassive black hole in our galaxy's center, Sagittarius A*, is 4 million times the Sun's mass!"
    }
    
    for term, info in stellar_data.items():
        if term in user_message:
            return info
    
    return "⭐ **Stars and Stellar Objects**: The universe is filled with incredible stellar phenomena! From main sequence stars like our Sun to exotic objects like neutron stars and black holes. NASA's space telescopes study these cosmic powerhouses. What stellar object interests you?"

def get_galaxy_info(user_message):
    """Get information about galaxies"""
    galaxy_data = {
        'milky way': "🌌 **The Milky Way**: Our home galaxy containing over 100 billion stars! It's a barred spiral galaxy about 100,000 light-years across. We're located in the Orion Arm, about 26,000 light-years from the galactic center. Our entire solar system orbits the galaxy once every 225-250 million years!",
        'andromeda galaxy': "🌌 **Andromeda Galaxy (M31)**: Our nearest major galactic neighbor, 2.5 million light-years away! It's approaching us at 250,000 mph and will collide with the Milky Way in about 4.5 billion years, creating a new galaxy astronomers call 'Milkomeda.' You can see it with the naked eye as a fuzzy patch!",
        'galaxy': "🌌 **Galaxies**: Massive collections of stars, gas, dust, and dark matter! There are over 2 trillion galaxies in the observable universe. They come in three main types: spiral (like the Milky Way), elliptical, and irregular. NASA's Hubble and James Webb telescopes have revealed galaxies from when the universe was young!"
    }
    
    for term, info in galaxy_data.items():
        if term in user_message:
            return info
    
    return "🌌 **Galaxies**: Island universes containing billions to trillions of stars! Our Milky Way is just one of countless galaxies in the universe. NASA telescopes study galaxy formation and evolution across cosmic time. Which galaxy interests you?"

def get_smart_space_answer(user_message):
    """Use Google Gemini AI to provide intelligent answers to any space question"""
    try:
        if model is None:
            return get_random_space_fact()
        
        # Create a space-expert prompt for Gemini
        prompt = f"""You are VyomNetra, an expert space and astronomy chatbot. Answer this question about space, astronomy, constellations, planets, or any space-related topic with accurate, engaging information. Keep your response informative but friendly, include relevant emojis, and make it educational.

User question: {user_message}

Please provide a detailed, accurate answer about the space topic they're asking about. If it's about a constellation, include information about its stars, mythology, and how to find it. If it's about planets, include facts about their characteristics and any NASA missions. Make it interesting and educational!"""

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini AI error: {e}")
        # Fallback to random space facts if AI fails
        return get_random_space_fact()

if __name__ == '__main__':
    print("🚀 Starting VyomNetra Space Chat Backend...")
    print("🌌 Connecting to NASA and space agency APIs...")
    app.run(host='0.0.0.0', port=5000, debug=True)