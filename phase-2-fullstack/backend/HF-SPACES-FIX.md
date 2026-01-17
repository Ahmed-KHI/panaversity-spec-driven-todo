# HF Spaces Configuration Fix

## Problem
Chat endpoint returns 500 error:
```
'Settings' object has no attribute 'OPENAI_API_KEY'
```

## Solution
Update `config.py` on HF Spaces to include the OPENAI_API_KEY field.

---

## Step-by-Step Instructions

### 1. Go to HF Spaces
https://huggingface.co/spaces/AhmedKHI/todo-api-phase2/tree/main

### 2. Edit config.py
Click on `config.py` → Click "Edit file"

### 3. Replace the Settings class
Find this section (around line 12-26):

```python
class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Security
    BETTER_AUTH_SECRET: str
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Application
    APP_NAME: str = "Todo Management API"
    APP_VERSION: str = "1.0.0"
```

**Replace with** (add the OPENAI_API_KEY lines):

```python
class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Security
    BETTER_AUTH_SECRET: str
    
    # Phase III: OpenAI
    OPENAI_API_KEY: str
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Application
    APP_NAME: str = "Todo Management API"
    APP_VERSION: str = "1.0.0"
```

### 4. Commit Changes
- Commit message: `Add OPENAI_API_KEY to Settings class`
- Click "Commit changes to main"

### 5. Wait for Rebuild
HF Spaces will automatically rebuild (2-3 minutes)

### 6. Test Chat Endpoint
Once rebuild completes, test again:
```bash
curl -X 'POST' \
  'https://ahmedkhi-todo-api-phase2.hf.space/api/7c29987e-25ea-48f7-8a13-ceff2369d1b8/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Add task to buy milk"}'
```

---

## Complete Updated config.py

Here's the full file for reference:

```python
"""
Application configuration.
[Task]: T-003 (Configuration)
[From]: spec.md §11, plan.md §4
[Updated]: T-014 (Phase III - Add OpenAI API key)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Security
    BETTER_AUTH_SECRET: str
    
    # Phase III: OpenAI
    OPENAI_API_KEY: str
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Application
    APP_NAME: str = "Todo Management API"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
```

---

## Why This Fixes It

1. **Environment Variable Exists**: OPENAI_API_KEY is set in HF Spaces secrets
2. **Pydantic Validation**: `BaseSettings` automatically loads from environment
3. **Type Declaration Required**: Pydantic needs `OPENAI_API_KEY: str` field defined
4. **Agent Code Works**: Once Settings has the field, `settings.OPENAI_API_KEY` works

---

## Expected Result

After the fix:
- ✅ Chat endpoint returns 200 status
- ✅ AI agent processes message
- ✅ Task operations work via natural language
- ✅ Response includes conversation_id and tool_calls

Example successful response:
```json
{
  "conversation_id": 1,
  "response": "✅ I've added a new task: 'Buy milk'",
  "tool_calls": [
    {
      "add_task": {
        "title": "Buy milk",
        "status": "pending"
      }
    }
  ]
}
```
