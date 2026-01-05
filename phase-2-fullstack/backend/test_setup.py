"""
Quick test script to verify backend setup.
Run this after setting up DATABASE_URL in .env
"""

import sys

def test_imports():
    """Test that all required modules can be imported."""
    print("✓ Testing imports...")
    try:
        import fastapi
        import sqlmodel
        import jwt
        import bcrypt
        from src.config import settings
        from src.models.user import User
        from src.models.task import Task
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\n✓ Testing configuration...")
    try:
        from src.config import settings
        print(f"  ✓ Environment: {settings.ENVIRONMENT}")
        print(f"  ✓ App Name: {settings.APP_NAME}")
        print(f"  ✓ Database URL: {settings.DATABASE_URL[:30]}...")
        print(f"  ✓ CORS Origins: {settings.cors_origins_list}")
        
        if "YOURPASSWORD" in settings.DATABASE_URL:
            print("\n  ⚠ WARNING: DATABASE_URL still has placeholder!")
            print("  → Update .env with your actual Neon database URL")
            return False
        
        if len(settings.BETTER_AUTH_SECRET) < 32:
            print("\n  ⚠ WARNING: BETTER_AUTH_SECRET should be at least 32 characters")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration failed: {e}")
        return False


def test_database_connection():
    """Test database connection."""
    print("\n✓ Testing database connection...")
    try:
        from src.database import engine
        from sqlmodel import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✓ Database connection successful!")
        return True
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        print("\n  → Make sure to:")
        print("     1. Create a Neon database at https://console.neon.tech/")
        print("     2. Copy the connection string")
        print("     3. Update DATABASE_URL in .env file")
        return False


def test_security():
    """Test security utilities."""
    print("\n✓ Testing security utilities...")
    try:
        from src.utils.security import hash_password, verify_password, create_access_token
        from uuid import uuid4
        
        # Test password hashing
        password = "test123"
        hashed = hash_password(password)
        assert verify_password(password, hashed), "Password verification failed"
        assert not verify_password("wrong", hashed), "Wrong password should fail"
        print("  ✓ Password hashing works")
        
        # Test JWT
        from src.config import settings
        token = create_access_token(
            user_id=uuid4(),
            email="test@example.com",
            secret_key=settings.BETTER_AUTH_SECRET
        )
        assert len(token) > 0, "Token generation failed"
        print("  ✓ JWT token generation works")
        
        return True
    except Exception as e:
        print(f"  ✗ Security test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Backend Setup Verification")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database_connection()))
    results.append(("Security", test_security()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Backend is ready.")
        print("\nNext steps:")
        print("  1. Start server: uvicorn src.main:app --reload --port 8000")
        print("  2. Open Swagger UI: http://localhost:8000/docs")
        print("  3. Test endpoints in Swagger UI")
    else:
        print("\n⚠ Some tests failed. Fix the issues above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
