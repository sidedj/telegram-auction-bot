#!/usr/bin/env python3
import requests

def test_health():
    """Тестирует health check endpoint"""
    url = "https://telegabot-production-3c68.up.railway.app/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Health check статус: {response.status_code}")
        print(f"Health check ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health check работает!")
        else:
            print("❌ Health check не работает!")
            
    except Exception as e:
        print(f"❌ Ошибка health check: {e}")

if __name__ == "__main__":
    test_health()
