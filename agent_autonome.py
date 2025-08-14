# ===================================================================
# AGENT AUTONOME DE CONTENU V2.0 - PUBLICATION BLOGGER
#
# Rôle :
# 1. Détecte les tendances (Google Trends, Reddit).
# 2. Génère un article de qualité avec l'IA.
# 3. Publie automatiquement l'article sur Blogger.
# ===================================================================

import os
import time
import logging
import re
import requests
import threading
import json
from typing import List, Dict, Optional
from flask import Flask

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Configuration du Logging ---
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AgentAutonome')

# --- Vérification des outils ---
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logger.warning("Outil 'pytrends' non trouvé. (pip install pytrends)")

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("Outil 'praw' non trouvé. (pip install praw)")

# ===================================================================
# MODULE 1 : Le "Radar" (TrendRadar) - INCHANGÉ
# ===================================================================
class TrendRadar:
    def __init__(self):
        self.logger = logging.getLogger('TrendRadar')
        self.commercial_keywords = ['achat', 'prix', 'test', 'avis', 'meilleur', 'guide']
        self.trends_client = self._init_google_trends()
        self.reddit_client = self._init_reddit()
        self.logger.info("🎯 Radar à tendances initialisé.")

    def _init_google_trends(self) -> Optional[TrendReq]:
        if not PYTRENDS_AVAILABLE: return None
        try:
            return TrendReq(hl=os.getenv('GTRENDS_HL', 'fr-FR'), tz=int(os.getenv('GTRENDS_TZ', '60')))
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion Google Trends: {e}")
            return None
    
    def _init_reddit(self) -> Optional[praw.Reddit]:
        if not PRAW_AVAILABLE: return None
        try:
            client = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='AgentAutonome/1.5'
            )
            assert client.read_only
            self.logger.info("✅ Connecté à l'API Reddit.")
            return client
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion Reddit: {e}")
            return None
    
    def detect_trends(self) -> List[Dict]:
        trends = []
        google_trends_pn = os.getenv('GTRENDS_PN', 'france')
        reddit_subreddit = os.getenv('REDDIT_SUBREDDIT', 'france+technologie')

        if self.trends_client:
            try:
                df = self.trends_client.trending_searches(pn=google_trends_pn)
                for i, trend in enumerate(df[0].head(5)):
                    trends.append({"title": trend, "source": "Google", "score": 100 - i*10})
            except Exception: pass
        if self.reddit_client:
            try:
                for post in self.reddit_client.subreddit(reddit_subreddit).hot(limit=5):
                    if not post.stickied:
                        trends.append({"title": post.title, "source": "Reddit", "score": post.score / 5})
            except Exception: pass
        self.logger.info(f"📈 {len(trends)} tendances détectées.")
        return trends

    def select_best_topic(self, trends: List[Dict]) -> Optional[Dict]:
        if not trends: return None
        for trend in trends:
            trend['score'] += sum(1 for kw in self.commercial_keywords if kw in trend['title'].lower()) * 20
        best_topic = sorted(trends, key=lambda x: x['score'], reverse=True)[0]
        self.logger.info(f"🎯 Sujet choisi: '{best_topic['title']}' (Score: {best_topic['score']:.0f})")
        return best_topic

# ===================================================================
# MODULE 2 : Le "Moteur" (ContentEngine) - MODIFIÉ POUR BLOGGER
# ===================================================================
class ContentEngine:
    def __init__(self):
        self.logger = logging.getLogger('ContentEngine')
        self.logger.info("⚙️ Moteur de contenu initialisé.")
        self.blogger_service = self._get_blogger_service()

    def _get_blogger_service(self):
        creds = None
        
        # Les informations d'identification sont stockées dans des variables d'environnement
        token_json_str = os.getenv('GOOGLE_TOKEN_JSON')
        client_secret_json_str = os.getenv('GOOGLE_CLIENT_SECRET_JSON')

        if not token_json_str or not client_secret_json_str:
            self.logger.error("❌ Variables d'environnement GOOGLE_TOKEN_JSON ou GOOGLE_CLIENT_SECRET_JSON non trouvées.")
            return None

        try:
            token_info = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_info)
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du chargement de GOOGLE_TOKEN_JSON: {e}")
            return None

        # Si les identifiants ont expiré, nous essayons de les rafraîchir.
        if creds and creds.expired and creds.refresh_token:
            try:
                client_config = json.loads(client_secret_json_str)
                creds.refresh(Request(client_config=client_config))
                # Après un rafraîchissement, nous devrions mettre à jour la variable d'environnement, mais c'est complexe sur Render.
                # Pour l'instant, cela fonctionnera pour la durée de vie du processus.
                self.logger.info("✅ Token d'accès rafraîchi.")
            except Exception as e:
                self.logger.error(f"❌ Impossible de rafraîchir le token: {e}")
                self.logger.error("Veuillez ré-exécuter 'authorize_blogger.py' localement pour obtenir un nouveau token.")
                return None
        
        if not creds or not creds.valid:
            self.logger.error("❌ Identifiants Google non valides.")
            return None

        try:
            service = build('blogger', 'v3', credentials=creds)
            self.logger.info("✅ Service Blogger initialisé avec succès.")
            return service
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la création du service Blogger: {e}")
            return None

    def generate_content(self, prompt: str) -> Optional[str]:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        ai_model = os.getenv('AI_MODEL', 'deepseek/deepseek-r1-0528:free')
        if not api_key:
            self.logger.error("❌ Clé API DEEPSEEK_API_KEY non trouvée.")
            return None
        self.logger.info(f"✍️ Envoi de la demande à l'IA (Modèle: {ai_model})...")
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": ai_model, "messages": [{"role": "user", "content": prompt}]},
                timeout=180
            )
            response.raise_for_status()
            self.logger.info("✅ L'IA a terminé d'écrire l'article.")
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"❌ Erreur pendant l'écriture par l'IA: {e}")
            return None

    def publish_to_blogger(self, title: str, content: str) -> bool:
        """Publie l'article sur Blogger via l'API."""
        if not self.blogger_service:
            self.logger.error("❌ Le service Blogger n'est pas disponible. Publication annulée.")
            return False
            
        blog_id = os.getenv('BLOGGER_BLOG_ID')
        if not blog_id:
            self.logger.error("❌ Variable d'environnement BLOGGER_BLOG_ID non trouvée.")
            return False

        body = {
            "kind": "blogger#post",
            "blog": {
                "id": blog_id
            },
            "title": title,
            "content": content
        }

        self.logger.info(f"📤 Publication de l'article sur le blog ID {blog_id}...")
        try:
            posts = self.blogger_service.posts()
            req = posts.insert(blogId=blog_id, body=body, isDraft=False)
            post = req.execute()
            self.logger.info(f"✅ Article publié avec succès ! URL : {post.get('url')}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur de publication Blogger : {e}")
            return False

# ===================================================================
# MODULE 3 : Le "Chef d'Orchestre" (AutonomousAgent) - MODIFIÉ
# ===================================================================
class AutonomousAgent:
    def __init__(self, cycle_hours: int = 12):
        self.trend_radar = TrendRadar()
        self.content_engine = ContentEngine()
        self.cycle_interval_seconds = cycle_hours * 3600
        self.logger = logging.getLogger('AutonomousAgent')
        self.logger.info(f"🤖 Agent V2.0 (Blogger) prêt. Cycle de {cycle_hours} heures.")

    def create_prompt_from_topic(self, topic: Dict) -> str:
        return (
            f"Rédige un article de blog détaillé et bien structuré sur le sujet suivant : '{topic['title']}'. "
            "Le ton doit être informatif et engageant. Longueur : environ 800 mots."
        )

    def run_single_cycle(self):
        self.logger.info("--- Lancement d'un nouveau cycle ---")
        trends = self.trend_radar.detect_trends()
        best_topic = self.trend_radar.select_best_topic(trends)
        if not best_topic:
            self.logger.warning("Aucun sujet intéressant trouvé.")
            return

        prompt = self.create_prompt_from_topic(best_topic)
        article_content = self.content_engine.generate_content(prompt)
        if article_content:
            success = self.content_engine.publish_to_blogger(best_topic['title'], article_content)
            if not success:
                self.logger.error("Échec de la publication, l'article n'est pas en ligne.")
        else:
            self.logger.error("Échec de la création de l'article.")
        
        self.logger.info("--- Fin du cycle ---")

    def start(self):
        while True:
            self.run_single_cycle()
            self.logger.info(f"En pause pour {self.cycle_interval_seconds / 3600:.0f} heures...")
            time.sleep(self.cycle_interval_seconds)

# ===================================================================
# SECTION SERVEUR WEB POUR RENDER
# ===================================================================
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'L\'agent est en cours d\'exécution en arrière-plan.'

def run_agent():
    """Charge l'environnement et démarre l'agent."""
    try:
        from dotenv import load_dotenv
        if load_dotenv():
            logger.info("Fichier de configuration .env chargé.")
        else:
            logger.info("Fichier .env non trouvé, utilisation des variables d'environnement système.")
    except ImportError:
        logger.warning("Outil 'python-dotenv' non trouvé.")
    
    cycle_hours = int(os.getenv('CYCLE_HOURS', '12'))
    agent = AutonomousAgent(cycle_hours=cycle_hours)
    agent.start()

# ===================================================================
# POINT DE DÉPART DU PROGRAMME
# ===================================================================

# Démarrer l'agent dans un thread séparé pour qu'il ne bloque pas le serveur web
logger.info("Démarrage du thread de l'agent en arrière-plan.")
agent_thread = threading.Thread(target=run_agent, daemon=True)
agent_thread.start()

if __name__ == "__main__":
    # Cette partie est principalement pour les tests locaux.
    logger.info("Démarrage du serveur web Flask pour les tests locaux.")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


