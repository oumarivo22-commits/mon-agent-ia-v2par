# site_builder_agent.py
#
# This agent is designed to automatically generate a landing page
# for a given product idea. It will take product information as input
# and output a complete HTML file.

def get_landing_page_template():
    """
    Returns a string containing a modern, self-contained
    HTML and CSS template for a product landing page.
    """
    html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PRODUCT_NAME}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f9; color: #333; line-height: 1.6; }
        .container { max-width: 960px; margin: 0 auto; padding: 20px; }
        header { background-color: #fff; padding: 20px; text-align: center; border-bottom: 1px solid #ddd; }
        header h1 { margin: 0; color: #2c3e50; font-size: 2.5em; }
        .hero { background-color: #3498db; color: #fff; padding: 60px 20px; text-align: center; }
        .hero h2 { font-size: 2.2em; margin-top: 0; }
        .hero p { font-size: 1.2em; max-width: 600px; margin: 10px auto; }
        .features { padding: 40px 20px; background-color: #fff; }
        .features h3 { text-align: center; font-size: 2em; color: #2c3e50; margin-bottom: 40px; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
        .feature-card { background-color: #f9f9f9; padding: 25px; border-radius: 8px; text-align: center; border: 1px solid #eee; }
        .feature-card h4 { font-size: 1.2em; color: #3498db; margin-top: 0; }
        .cta { background-color: #2c3e50; color: #fff; padding: 60px 20px; text-align: center; }
        .cta h3 { font-size: 2em; margin-top: 0; }
        .cta form { margin-top: 20px; display: flex; justify-content: center; align-items: center; }
        .cta input[type="email"] { padding: 15px; font-size: 1em; width: 300px; max-width: 70%; border: none; border-radius: 5px 0 0 5px; }
        .cta button { padding: 15px 30px; font-size: 1em; border: none; background-color: #3498db; color: #fff; cursor: pointer; border-radius: 0 5px 5px 0; white-space: nowrap; }
        footer { text-align: center; padding: 20px; font-size: 0.9em; color: #777; }
    </style>
</head>
<body>
    <header class="container">
        <h1>{PRODUCT_NAME}</h1>
    </header>

    <main>
        <section class="hero">
            <h2>{TAGLINE}</h2>
            <p>{HERO_DESCRIPTION}</p>
        </section>

        <section class="features">
            <div class="container">
                <h3>Nos fonctionnalités</h3>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h4>{FEATURE_1_TITLE}</h4>
                        <p>{FEATURE_1_TEXT}</p>
                    </div>
                    <div class="feature-card">
                        <h4>{FEATURE_2_TITLE}</h4>
                        <p>{FEATURE_2_TEXT}</p>
                    </div>
                    <div class="feature-card">
                        <h4>{FEATURE_3_TITLE}</h4>
                        <p>{FEATURE_3_TEXT}</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="cta">
            <h3>Prêt à essayer ?</h3>
            <p>Inscrivez-vous pour être le premier informé de notre lancement officiel !</p>
            <form>
                <input type="email" placeholder="Votre adresse email" required>
                <button type="submit">Accès anticipé</button>
            </form>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 {PRODUCT_NAME}. Tous droits réservés.</p>
        </div>
    </footer>
</body>
</html>
    """
    return html_template

def generate_landing_page(product_data):
    """
    Generates an index.html file from a template and product data.
    """
    print("Generating landing page...")
    template = get_landing_page_template()

    # Replace placeholders with actual data
    filled_html = template
    for key, value in product_data.items():
        filled_html = filled_html.replace(f"{{{key}}}", value)

    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(filled_html)
        print("Successfully generated index.html")
    except IOError as e:
        print(f"Error writing to file: {e}")

def main():
    """
    Main function to generate a landing page for a specific product.
    """
    print("Site Builder Agent is running...")

    # Define the product data for our test case: DownMark.fr
    downmark_data = {
        "PRODUCT_NAME": "DownMark.fr",
        "TAGLINE": "Convertissez n'importe quelle page web en Markdown propre, en un seul clic.",
        "HERO_DESCRIPTION": "Fatigué de copier-coller du texte mal formaté ? DownMark est un outil simple qui préserve la structure de votre contenu et vous fait gagner du temps.",
        "FEATURE_1_TITLE": "Conversion Rapide",
        "FEATURE_1_TEXT": "Obtenez un fichier Markdown propre et bien structuré à partir de n'importe quel article ou page web en quelques secondes.",
        "FEATURE_2_TITLE": "Open Source & Respectueux",
        "FEATURE_2_TEXT": "Notre code est transparent et nous ne conservons aucune de vos données. Votre vie privée est notre priorité.",
        "FEATURE_3_TITLE": "Simple d'Utilisation",
        "FEATURE_3_TEXT": "Pas de configuration compliquée. Installez notre extension de navigateur et commencez à convertir immédiatement."
    }

    generate_landing_page(downmark_data)

if __name__ == "__main__":
    main()
