from flask import Flask, request, jsonify, render_template
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import socket
import urllib.parse

app = Flask(__name__)

def scrape_domains(prompt):
    formatted_prompt = prompt.replace(" ", "+")
    url = f"https://www.design.com/ai-domain-name-generator/search?text={formatted_prompt}&textChanged=true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Use Playwright's wait function instead of sleep
        page.wait_for_selector("div.tw-text-lg.tw-grow.tw-font-bold.tw-break-all")

        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")
    domain_elements = soup.find_all("div", class_="tw-text-lg tw-grow tw-font-bold tw-break-all")

    domains = [element.text.strip() for element in domain_elements]
    return domains

def is_domain_available(domain):
    # A dummy check to simulate domain availability; you can replace this with actual domain checking logic.
    try:
        socket.gethostbyname(domain)
        return False  # Domain is not available
    except socket.gaierror:
        return True  # Domain is available

@app.route('/api', methods=['GET'])
def api():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Missing 'prompt' query parameter"}), 400

    try:
        decoded_prompt = urllib.parse.unquote(prompt)
        domains = scrape_domains(decoded_prompt)
        
        if not domains:
            return jsonify({"error": "No domains found"}), 404
        
        # Return domains as JSON
        return jsonify({"domains": domains})
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500
    
@app.route('/check', methods=['GET'])
def check_domain():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Domain parameter is missing"}), 400

    # Check if the domain is available
    available = is_domain_available(domain)

    # Respond with JSON format
    return jsonify({
        "domain": domain,
        "available": available
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)