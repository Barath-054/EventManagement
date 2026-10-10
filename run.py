import uvicorn
import os
import sys

def main():
    print("=" * 70)
    print(" EVENTMATE AI – SMART EVENT PLANNING & BUDGET MANAGEMENT PLATFORM")
    print(" Tailored for Coimbatore, Tamil Nadu, India")
    print("=" * 70)
    print(" Server URL:        http://127.0.0.1:8000")
    print(" API Documentation: http://127.0.0.1:8000/docs")
    print("-" * 70)
    print(" Sample Test Accounts:")
    print("   Customer: client@eventmate.ai  /  Client@123")
    print("   Admin:    admin@eventmate.ai   /  Admin@123")
    print("=" * 70)
    
    # Run Uvicorn server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
