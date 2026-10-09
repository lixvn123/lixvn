import os
import json
import re

KIT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_index_html_structure():
    path = os.path.join(KIT_DIR, "index.html")
    assert os.path.isfile(path), "index.html must exist"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "<!DOCTYPE html>" in content
    assert "<html" in content and "</html>" in content
    assert "<head>" in content and "</head>" in content
    assert "<body" in content and "</body>" in content
    
    # Semantic elements
    for tag in ["<header", "<main", "<section", "<footer", "<nav"]:
        assert tag in content, f"Semantic tag {tag} should be present in index.html"
        
    # Meta tags
    assert 'meta name="viewport"' in content
    assert 'meta charset="UTF-8"' in content
    assert 'property="og:title"' in content
    
    # Claude & AI positioning
    assert "Claude" in content
    assert "AgentPulse" in content
    assert "Anthropic" in content

def test_application_pitch_completeness():
    path = os.path.join(KIT_DIR, "APPLICATION_PITCH.md")
    assert os.path.isfile(path), "APPLICATION_PITCH.md must exist"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "2-Sentence Pitch" in content
    assert "Claude 3.5 Sonnet" in content
    assert "Website URL" in content
    assert "Work Email" in content
    assert "GitHub Repo Link" in content
    assert "Checklist Agar Lolos Verifikasi" in content

def test_setup_guide_completeness():
    path = os.path.join(KIT_DIR, "SETUP_GUIDE.md")
    assert os.path.isfile(path), "SETUP_GUIDE.md must exist"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "Cloudflare Email Routing" in content
    assert "Vercel" in content
    assert "console.anthropic.com" in content
    assert "$1,000" in content

def test_vercel_json_validity():
    path = os.path.join(KIT_DIR, "vercel.json")
    assert os.path.isfile(path), "vercel.json must exist"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "headers" in data
    assert isinstance(data["headers"], list)
    assert len(data["headers"]) > 0

def test_readme_and_license():
    readme_path = os.path.join(KIT_DIR, "README.md")
    license_path = os.path.join(KIT_DIR, "LICENSE")
    
    assert os.path.isfile(readme_path), "README.md must exist"
    assert os.path.isfile(license_path), "LICENSE must exist"
    
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()
    assert "AgentPulse" in readme
    assert "Apache-2.0" in readme
    assert "Quickstart" in readme
