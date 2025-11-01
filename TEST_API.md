# Testing Soosh Backend API

## 1. Start the Backend

```bash
cd /Users/vivekkumar/Soosh/SooshAI/backend
uvicorn main:app --reload
```

## 2. Open API Documentation

**Interactive Swagger Docs**: http://localhost:8000/api/docs

## 3. Test Endpoints (Using curl or Swagger UI)

### Health Check
```bash
curl http://localhost:8000/health
```

### 1. Create Account (Signup)
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "first_name": "John",
    "last_name": "Doe",
    "age": 25,
    "age_group": "young_adult",
    "user_type": "beginner"
  }'
```

**Copy the `access_token` from the response!**

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

### 3. Get Current User (Protected Route)
```bash
# Replace YOUR_TOKEN with the access_token from signup/login
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Update Profile
```bash
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Aspiring developer learning to code",
    "city": "San Francisco"
  }'
```

### 5. Create AI Profile
```bash
curl -X POST http://localhost:8000/api/v1/ai-profiling/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["programming", "web development", "AI"],
    "skills": ["Python", "JavaScript"],
    "goals": ["Become a full-stack developer", "Learn machine learning"],
    "learning_style": "visual",
    "available_time_per_week": 20
  }'
```

### 6. Get AI Recommendations
```bash
curl http://localhost:8000/api/v1/ai-profiling/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. List Categories
```bash
curl http://localhost:8000/api/v1/categories/with-subcategories
```

### 8. Search Users
```bash
curl -X POST http://localhost:8000/api/v1/users/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "john",
    "limit": 10
  }'
```

### 9. Check Voice AI Provider
```bash
curl http://localhost:8000/api/v1/voice/provider
```

## 4. Test with Swagger UI (Easier!)

1. Go to http://localhost:8000/api/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

### To Test Protected Endpoints:
1. First call `/auth/signup` or `/auth/login`
2. Copy the `access_token` from response
3. Click the green "Authorize" button at top right
4. Enter: `Bearer YOUR_TOKEN`
5. Click "Authorize"
6. Now all protected endpoints will work!

## 5. Expected Results

✅ **Signup**: Should return tokens + user object
✅ **Login**: Should return tokens + user object
✅ **Get User**: Should return user profile
✅ **Update Profile**: Should update and return user
✅ **AI Profile**: Should create profile with recommendations
✅ **Categories**: Should return 22 categories with subcategories
✅ **Voice Provider**: Should show current AI provider (local or openai)

## Common Issues

### "Role postgres does not exist"
- Fixed! Using `vivekkumar` user instead

### "Token expired"
- Login again to get a new token

### "Unauthorized"
- Make sure you're using `Bearer YOUR_TOKEN` format
- Token might be expired, login again

### "404 Not Found"
- Check the URL is correct
- Backend must be running

## Next Steps

After testing these endpoints, we can:
1. Continue building remaining endpoints (opportunities, mentors, bookings, etc.)
2. Connect the frontend React Native app
3. Test the complete user journey

