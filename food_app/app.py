from flask import Flask, render_template_string, redirect, url_for, request, session
import json
import math
import urllib.parse
import re
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# --- DATA HANDLING ---
def load_all_data():
    try:
        with open("recipes_db.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

weekly_box = []

# --- GOOGLE OAUTH HELPER FUNCTIONS ---
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def get_google_auth_url():
    """Generate Google OAuth authorization URL"""
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"].__str__().replace("'", "").replace(",", "+"),
        state=os.urandom(16).hex(),
    )
    return request_uri

# Simple client for OAuth flow
class OAuthClient:
    @staticmethod
    def prepare_request_uri(endpoint, **kwargs):
        params = []
        for key, value in kwargs.items():
            if key == 'scope':
                params.append(f"scope={value}")
            elif key == 'redirect_uri':
                params.append(f"redirect_uri={urllib.parse.quote(value)}")
            elif key == 'state':
                params.append(f"state={value}")
            elif key == 'client_id':
                params.append(f"client_id={value}")
            elif key == 'response_type':
                params.append(f"response_type={value}")
        return f"{endpoint}?{'&'.join(params)}"

client = OAuthClient()

# --- BLUE APRON DESIGN SYSTEM ---
MAIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PersonalFresh | Food</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Source Sans Pro', sans-serif; background-color: #ffffff; }
        h1, h2, h3, .serif { font-family: 'Lora', serif; }
        .ba-navy { color: #002657; }
        .ba-bg-navy { background-color: #002657; }
        .ba-bg-google { background-color: #4285F4; }
        .sidebar-icon { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #e5e7eb; transition: all 0.2s; padding: 2px; }
        
        #filterModal { display: none; }
        .protein-btn { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; display: flex; align-items: center; gap: 10px; font-weight: 600; }
        .protein-btn.active { border-color: #002657; background: #f0f4ff; color: #002657; border-width: 2px; }
        
        /* Video Overlay Styles */
        .video-trigger:hover .play-overlay { opacity: 1; }
        .play-overlay { background: rgba(0, 38, 87, 0.4); transition: opacity 0.3s; opacity: 0; }

        /* Login Modal */
        .modal-backdrop { background: rgba(0, 0, 0, 0.5); }
    </style>
</head>
<body class="text-gray-800">

    <nav class="border-b border-gray-200 py-4 px-6 sticky top-0 bg-white z-50">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div class="flex items-center gap-4">
                <button class="text-2xl ba-navy">☰</button>
                <h1 class="text-3xl font-bold ba-navy tracking-tight">Food</h1>
            </div>
            <div class="flex items-center gap-4">
                {% if user %}
                <div class="flex items-center gap-3">
                    <img src="{{ user.picture }}" alt="Profile" class="w-10 h-10 rounded-full border-2 border-gray-200">
                    <span class="text-sm font-bold ba-navy hidden sm:inline">{{ user.name }}</span>
                    <a href="/logout" class="text-sm text-gray-500 hover:text-gray-700 font-bold">Logout</a>
                </div>
                {% else %}
                <span class="text-sm font-bold ba-navy hidden sm:inline">My Box: {{ box|length }}</span>
                <button onclick="openLoginModal()" class="ba-bg-google text-white px-6 py-2 rounded-full font-bold text-sm flex items-center gap-2 hover:bg-blue-600 transition">
                    <svg class="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                    Sign in with Google
                </button>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Login Modal -->
    <div id="loginModal" class="fixed inset-0 z-[200] hidden">
        <div class="modal-backdrop absolute inset-0" onclick="closeLoginModal()"></div>
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4">
            <div class="text-center">
                <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg class="w-10 h-10 text-blue-600" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                </div>
                <h2 class="text-2xl font-bold ba-navy mb-2">Welcome Back</h2>
                <p class="text-gray-500 mb-8">Sign in to access your personalized meal planning</p>
                <a href="/login" class="ba-bg-google text-white px-8 py-3 rounded-full font-bold text-sm inline-flex items-center gap-2 hover:bg-blue-600 transition shadow-lg">
                    <svg class="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                    Sign in with Google
                </a>
                <p class="text-xs text-gray-400 mt-6">
                    By continuing, you agree to our Terms of Service and Privacy Policy
                </p>
            </div>
        </div>
    </div>

    <div class="max-w-7xl mx-auto flex">
        <aside class="w-32 flex-shrink-0 flex flex-col items-center gap-8 pt-12 sticky top-24 h-screen border-r border-gray-100">
            {% for item in [('15 MINUTE MEALS', 'https://cdn-icons-png.flaticon.com/512/3563/3563457.png'), ('MEAL KITS', 'https://cdn-icons-png.flaticon.com/512/3081/3081918.png'), ('ASSEMBLE & BAKE', 'https://cdn-icons-png.flaticon.com/512/2917/2917633.png'), ('DISH BY BLUE APRON', 'https://cdn-icons-png.flaticon.com/512/1046/1046771.png'), ('BREAKFAST', 'https://cdn-icons-png.flaticon.com/512/2102/2102793.png'), ('LUNCH', 'https://cdn-icons-png.flaticon.com/512/2102/2102796.png'), ('DINNER', 'https://cdn-icons-png.flaticon.com/512/2102/2102795.png')] %}
            <div class="flex flex-col items-center gap-1 group cursor-pointer px-2">
                <div class="sidebar-icon bg-gray-50"><img src="{{ item[1] }}" class="p-2 opacity-60"></div>
                <span class="text-[9px] font-black uppercase text-center text-gray-400 leading-tight group-hover:text-blue-900">{{ item[0] }}</span>
            </div>
            {% endfor %}
        </aside>

        <main class="flex-1 px-10 pt-12">
            <div class="flex justify-between items-center mb-12">
                <h2 class="text-5xl font-light ba-navy">Your Menu</h2>
                <button onclick="toggleFilters()" class="border border-gray-200 rounded-full px-8 py-3 font-bold text-gray-600">Filters</button>
            </div>

            {% for category, data in sections.items() %}
                {% if data.recipes %}
                <section class="mb-20">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                        {% for r in data.recipes %}
                        <div class="group">
                            <div class="relative rounded-2xl overflow-hidden aspect-[4/3] mb-6 shadow-sm">
                                <img src="{{ r.image_url }}" class="w-full h-full object-cover">
                            </div>
                            <div class="flex justify-between items-start">
                                <div class="flex-1">
                                    <h4 class="text-2xl font-bold ba-navy leading-tight">{{ r.title }}</h4>
                                    <p class="text-gray-400 italic mt-1">with {{ r.ingredients[:2]|join(' & ') }}</p>
                                </div>
                                <div class="flex flex-col gap-2">
                                    <a href="/add/{{ r.id }}" class="ba-bg-navy text-white text-center py-2 px-6 rounded-full font-bold text-sm">Add</a>
                                    <a href="/recipe/{{ r.id }}" class="text-center text-blue-600 font-bold text-xs uppercase">Details</a>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </section>
                {% endif %}
            {% endfor %}
        </main>
    </div>

    <script>
        function toggleFilters() {
            const modal = document.getElementById('filterModal');
            modal.style.display = (modal.style.display === 'flex') ? 'none' : 'flex';
        }

        function openLoginModal() {
            document.getElementById('loginModal').classList.remove('hidden');
        }

        function closeLoginModal() {
            document.getElementById('loginModal').classList.add('hidden');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    all_recipes = load_all_data()
    search_query = request.args.get('search', '').lower()
    
    safe_recipes = [r for r in all_recipes if search_query in r.get('title', '').lower()]
    
    organized = {"Dinner": [], "Lunch": [], "Other": []}
    for r in safe_recipes:
        cat = r.get('category', 'Other')
        if cat in organized: organized[cat].append(r)
        else: organized["Other"].append(r)

    final_sections = {}
    for cat, recipes in organized.items():
        final_sections[cat] = {"recipes": recipes[:6], "total": len(recipes)}

    user = session.get('user')
    return render_template_string(MAIN_HTML, sections=final_sections, box=weekly_box, current_search=search_query, user=user)

# --- GOOGLE OAUTH ROUTES ---
@app.route('/login')
def login():
    """Redirect to Google OAuth authorization endpoint"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return "Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.", 500
    
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.rstrip('/') + "/callback",
        scope="openid email profile",
        state=os.urandom(16).hex(),
        client_id=GOOGLE_CLIENT_ID,
        response_type="code",
    )
    return redirect(request_uri)

@app.route('/login/callback')
def callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return "Google OAuth not configured.", 500
    
    # Get authorization code
    code = request.args.get("code")
    state = request.args.get("state")
    
    if not code:
        return "Authorization code not found", 400
    
    # Get token endpoint
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Prepare token request
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url.rstrip('/'),
        code=code,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    
    # Exchange code for token
    token_response = requests.post(token_url, headers=headers, data=body)
    
    if token_response.status_code != 200:
        return f"Failed to get token: {token_response.text}", 400
    
    # Parse token
    token_data = token_response.json()
    
    # Get user info
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    
    if userinfo_response.status_code != 200:
        return f"Failed to get user info: {userinfo_response.text}", 400
    
    user_info = userinfo_response.json()
    
    # Store user in session
    session['user'] = {
        'id': user_info.get('sub'),
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'picture': user_info.get('picture'),
        'given_name': user_info.get('given_name'),
        'family_name': user_info.get('family_name'),
    }
    
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    """Clear session and log out user"""
    session.pop('user', None)
    return redirect(url_for('home'))

# Helper for OAuth token request (simplified)
def prepare_token_request(token_url, **kwargs):
    """Prepare OAuth token request parameters"""
    import urllib.parse
    data = {
        'code': kwargs.get('code'),
        'client_id': kwargs.get('client_id'),
        'client_secret': kwargs.get('client_secret'),
        'redirect_uri': kwargs.get('redirect_url'),
        'grant_type': 'authorization_code',
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = urllib.parse.urlencode(data)
    return token_url, headers, body

# Monkey-patch the client
client.prepare_token_request = prepare_token_request

@app.route('/add/<recipe_id>')
def add_to_box(recipe_id):
    all_recipes = load_all_data()
    recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    if recipe and recipe not in weekly_box: weekly_box.append(recipe)
    return redirect(url_for('home'))

@app.route('/recipe/<recipe_id>')
def view_recipe(recipe_id):
    all_recipes = load_all_data()
    recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    if not recipe: return "Not Found", 404
    
    # Process ingredients for retail links
    retail_ingredients = []
    for ing in recipe.get('ingredients', []):
        retail_ingredients.append({
            'original': ing,
            'clean': clean_ingredient(ing),
            'walmart': f"https://www.walmart.com/search?q={urllib.parse.quote(clean_ingredient(ing))}",
            'target': f"https://www.target.com/s?searchTerm={urllib.parse.quote(clean_ingredient(ing))}",
            'sams': f"https://www.samsclub.com/s/{urllib.parse.quote(clean_ingredient(ing))}"
        })
    
    DETAIL_HTML = """
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@700&display=swap" rel="stylesheet">
    <style>
        h1 { font-family: 'Lora', serif; color: #002657; }
        .video-trigger:hover .play-btn { transform: scale(1.1); }
        .retail-icon { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 900; color: white; transition: transform 0.2s; }
        .retail-icon:hover { transform: scale(1.2); }
        .bg-walmart { background-color: #0071ce; }
        .bg-target { background-color: #cc0000; }
        .bg-sams { background-color: #004a99; }
        #videoModal { display: none; }
    </style>

    <div id="videoModal" class="fixed inset-0 bg-black/90 z-[200] flex items-center justify-center p-4">
        <div class="relative w-full max-w-4xl aspect-video bg-black rounded-2xl overflow-hidden">
            <button onclick="closeVideo()" class="absolute top-4 right-4 text-white text-4xl z-50">&times;</button>
            <iframe id="videoPlayer" class="w-full h-full" src="" frameborder="0" allowfullscreen></iframe>
        </div>
    </div>

    <div class="max-w-4xl mx-auto p-12">
        <a href="/" class="text-blue-600 font-bold mb-8 block">&larr; Back to Menu</a>
        
        <h1 class="text-5xl mb-8">{{ r.title }}</h1>
        
        <div class="relative group video-trigger cursor-pointer mb-12" onclick="openVideo('https://www.youtube.com/embed/dQw4w9WgXcQ')">
            <img src="{{ r.image_url }}" class="w-full h-[500px] object-cover rounded-3xl shadow-2xl">
            <div class="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/40 transition-all rounded-3xl">
                <div class="play-btn w-20 h-20 bg-white/90 rounded-full flex items-center justify-center pl-2 shadow-xl transition-transform">
                    <div class="w-0 h-0 border-y-[15px] border-y-transparent border-l-[25px] border-l-[#002657]"></div>
                </div>
            </div>
            <div class="absolute bottom-6 left-6 text-white font-bold uppercase tracking-widest text-sm bg-black/40 px-4 py-2 rounded-full">Click to Play Tutorial</div>
        </div>

        <div class="grid grid-cols-3 gap-16">
            <div class="col-span-1">
                <h3 class="font-bold text-xs uppercase tracking-widest border-b pb-4 mb-4">Ingredients</h3>
                <ul class="space-y-4">
                    {% for item in retail_data %}
                    <li class="group">
                        <div class="text-sm text-gray-800 mb-2">{{ item.original }}</div>
                        <div class="flex gap-2 opacity-60 group-hover:opacity-100 transition-opacity">
                            <a href="{{ item.walmart }}" target="_blank" class="retail-icon bg-walmart" title="Search Walmart">W</a>
                            <a href="{{ item.target }}" target="_blank" class="retail-icon bg-target" title="Search Target">T</a>
                            <a href="{{ item.sams }}" target="_blank" class="retail-icon bg-sams" title="Search Sam's Club">S</a>
                        </div>
                        <div class="h-[1px] bg-gray-100 mt-3"></div>
                    </li>
                    {% endfor %}
                </ul>
            </div>

            <div class="col-span-2">
                <h3 class="font-bold text-xs uppercase tracking-widest border-b pb-4 mb-4">Cooking Steps</h3>
                <div class="whitespace-pre-line text-gray-600 leading-loose">{{ r.instructions }}</div>
            </div>
        </div>
    </div>

    <script>
        function openVideo(url) {
            document.getElementById('videoPlayer').src = url;
            document.getElementById('videoModal').style.display = 'flex';
        }
        function closeVideo() {
            document.getElementById('videoModal').style.display = 'none';
            document.getElementById('videoPlayer').src = '';
        }
    </script>
    """
    user = session.get('user')
    return render_template_string(DETAIL_HTML, r=recipe, retail_data=retail_ingredients, user=user)

if __name__ == '__main__':
    app.run(debug=True)