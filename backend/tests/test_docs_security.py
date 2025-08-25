# backend/tests/test_docs_security.py

"""
Test script to demonstrate API docs security configurations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import security_config

def test_docs_security_scenarios():
    """Test different API docs security configurations"""
    print("=== API Documentation Security Test ===")
    print()
    
    print("Current Configuration:")
    print(f"  ENABLE_API_DOCS: {security_config.ENABLE_API_DOCS}")
    print(f"  PROTECT_API_DOCS: {security_config.PROTECT_API_DOCS}")
    print(f"  DEV_MODE: {security_config.DEV_MODE}")
    print()
    
    # Simulate different configuration scenarios
    scenarios = [
        {
            'name': 'Development (Open Docs)',
            'enable_docs': True,
            'protect_docs': False,
            'dev_mode': True,
            'description': 'Docs accessible without restrictions - DEVELOPMENT ONLY'
        },
        {
            'name': 'Production (Protected Docs)',
            'enable_docs': True,
            'protect_docs': True,
            'dev_mode': False,
            'description': 'Docs require API key and origin validation'
        },
        {
            'name': 'Production (No Docs)',
            'enable_docs': False,
            'protect_docs': True,
            'dev_mode': False,
            'description': 'Docs completely disabled (404 responses) - MOST SECURE'
        },
        {
            'name': 'Staging (Protected Docs)',
            'enable_docs': True,
            'protect_docs': True,
            'dev_mode': True,
            'description': 'Docs available but protected - good for staging'
        }
    ]
    
    print("Configuration Scenarios:")
    print("-" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   ENABLE_API_DOCS={scenario['enable_docs']}")
        print(f"   PROTECT_API_DOCS={scenario['protect_docs']}")
        print(f"   DEV_MODE={scenario['dev_mode']}")
        print(f"   Result: {scenario['description']}")
        
        # Determine access level
        if not scenario['enable_docs']:
            access = "❌ 404 Not Found"
        elif not scenario['protect_docs']:
            access = "⚠️  Open Access (DEV ONLY!)"
        else:
            access = "🔒 API Key Required"
        
        print(f"   Access: {access}")
        print()
    
    print("Security Recommendations:")
    print("-" * 30)
    print("✅ Development: ENABLE_API_DOCS=true, PROTECT_API_DOCS=false")
    print("✅ Staging: ENABLE_API_DOCS=true, PROTECT_API_DOCS=true")
    print("✅ Production: ENABLE_API_DOCS=false (most secure)")
    print("⚠️  Production Alt: ENABLE_API_DOCS=true, PROTECT_API_DOCS=true (if docs needed)")
    print()
    
    print("API Docs URLs (when enabled):")
    print("- http://localhost:8000/docs (Swagger UI)")
    print("- http://localhost:8000/redoc (ReDoc)")
    print("- http://localhost:8000/openapi.json (OpenAPI Schema)")
    print()
    
    if scenario['protect_docs'] and scenario['enable_docs']:
        print("To access protected docs, include header:")
        print(f"X-API-Key: {security_config.ADMIN_API_KEY}")

if __name__ == "__main__":
    print("CertAlert API Documentation Security Test")
    print("=" * 50)
    print()
    
    test_docs_security_scenarios()
