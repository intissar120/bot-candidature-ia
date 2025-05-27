from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def analyser_offre_avec_groq(offre_emploi, nom_candidat, competences_candidat):
    """
    cette fonctioon analyse une offre d'emploi avec l'API Groq
    """

    groq_api_key = os.getenv('GROQ_API_KEY')

    if not groq_api_key:
        return {
            "competences_cles": ["⚠️ Clé API Groq manquante"],
            "lettre_motivation": "Veuillez configurer votre clé API Groq dans le fichier .env",
            "points_entretien": ["Ajoutez GROQ_API_KEY=votre_clé dans .env"],
            "score_compatibilite": 0,
            "conseils": ["Obtenez une clé gratuite sur https://console.groq.com"]
        }

    prompt = f"""
    Tu es un assistant RH expert. Analyse cette offre d'emploi et génère une réponse complète.

    OFFRE D'EMPLOI:
    {offre_emploi}

    PROFIL DU CANDIDAT:
    - Nom: {nom_candidat}
    - Compétences: {competences_candidat}

    Génère une réponse au format JSON avec:
    1. "competences_cles": liste des 5 compétences les plus importantes de l'offre
    2. "lettre_motivation": lettre de motivation personnalisée (150-200 mots)
    3. "points_entretien": 5 points clés à mentionner en entretien
    4. "score_compatibilite": score sur 100 de compatibilité du profil
    5. "conseils": 3 conseils pour améliorer la candidature

    Réponds uniquement en JSON valide.
    """

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "Tu es un expert RH qui analyse les offres d'emploi et génère des réponses au format JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }

        print("🚀 Analyse en cours avec Groq...")
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content']
            print("✅ Analyse terminée avec succès")

            # Extraction du JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text

            return json.loads(json_text)

        else:
            print(f"❌ Erreur API Groq: {response.status_code}")
            return {
                "competences_cles": ["Erreur de connexion à l'API"],
                "lettre_motivation": "Service temporairement indisponible",
                "points_entretien": ["Réessayez dans quelques minutes"],
                "score_compatibilite": 0,
                "conseils": ["Vérifiez votre connexion internet"]
            }

    except requests.exceptions.Timeout:
        print("⏱️ Timeout de l'API")
        return {
            "competences_cles": ["Délai d'attente dépassé"],
            "lettre_motivation": "L'analyse a pris trop de temps",
            "points_entretien": ["Réessayez avec une offre plus courte"],
            "score_compatibilite": 0,
            "conseils": ["Simplifiez votre demande"]
        }
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {
            "competences_cles": ["Erreur lors de l'analyse"],
            "lettre_motivation": "Une erreur s'est produite",
            "points_entretien": ["Veuillez réessayer"],
            "score_compatibilite": 0,
            "conseils": ["Contactez le support si le problème persiste"]
        }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyser', methods=['POST'])
def analyser():
    try:
        data = request.json
        offre = data.get('offre_emploi', '').strip()
        nom = data.get('nom_candidat', '').strip()
        competences = data.get('competences_candidat', '').strip()

        print(f"📝 Nouvelle analyse pour: {nom}")

        if not all([offre, nom, competences]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400

        resultat = analyser_offre_avec_groq(offre, nom, competences)

        resultat['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultat['nom_candidat'] = nom
        resultat['powered_by'] = "Groq AI"

        return jsonify(resultat)

    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500


@app.route('/historique')
def historique():
    return render_template('historique.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/health')
def health():
    """Point de contrôle pour vérifier que l'app fonctionne"""
    return jsonify({
        'status': 'OK',
        'service': 'Bot de Candidature IA',
        'powered_by': 'Groq',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("⚠️  ATTENTION: Clé API Groq non trouvée!")
        print("📝 Ajoutez GROQ_API_KEY=votre_clé dans le fichier .env")
        print("🔗 Obtenez une clé gratuite: https://console.groq.com")
    else:
        print("✅ Clé API Groq configurée")

    print("🚀 Bot de Candidature IA démarré!")
    print("⚡ Propulsé par Groq (gratuit et rapide)")
    print("📱 Interface: http://localhost:5000")
    print("🔍 Santé: http://localhost:5000/health")

    app.run(debug=True, port=5000)