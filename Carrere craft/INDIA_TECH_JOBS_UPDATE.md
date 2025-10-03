# India Tech Jobs Configuration - UPDATED!

## Changes Made:

### 1. ✅ Country Changed to India
**File**: `fetch_jobs.py` (Line 12)
```python
self.country = "in"  # Now fetches jobs from India
```

### 2. ✅ Default Search Set to Tech Jobs
**File**: `templates/jobs.html` (Line 373)
- Page now loads with "software developer" as default search
- Shows tech-related jobs immediately on page load

### 3. ✅ Location Placeholders Updated
**File**: `templates/jobs.html`
- Changed from "New York" to "Bangalore, Mumbai, Delhi"
- Label updated to "Location (India)"

### 4. ✅ Salary Currency Changed to INR (₹)
**Files**: `fetch_jobs.py` & `templates/jobs.html`
- Salary filters now show ₹ (Indian Rupees) instead of $
- Placeholders updated: ₹500,000 - ₹2,000,000
- Salary display in job cards shows ₹ symbol

---

## How to Use:

### 1. Restart Your Flask App
```bash
python app.py
```

### 2. Navigate to Jobs Section
- Login to your account
- Click "Jobs" in navigation

### 3. You'll See:
- **Default**: Tech jobs (Software Developer) from India
- **Location Filter**: Indian cities (Bangalore, Mumbai, Delhi, etc.)
- **Salary**: Displayed in ₹ (INR)

---

## Popular Tech Job Searches in India:

### Job Titles to Try:
- Software Developer
- Python Developer
- Java Developer
- Full Stack Developer
- Data Scientist
- DevOps Engineer
- Frontend Developer
- Backend Developer
- React Developer
- Node.js Developer
- Machine Learning Engineer
- Cloud Engineer
- Mobile App Developer
- QA Engineer
- UI/UX Designer

### Popular Tech Cities in India:
- Bangalore (Bengaluru)
- Hyderabad
- Pune
- Mumbai
- Delhi NCR (Gurgaon, Noida)
- Chennai
- Kolkata
- Ahmedabad

### Salary Ranges (Annual in INR):
- **Entry Level**: ₹300,000 - ₹600,000
- **Mid Level**: ₹600,000 - ₹1,500,000
- **Senior Level**: ₹1,500,000 - ₹3,000,000+

---

## Example Searches:

1. **Python Developer in Bangalore**
   - Title: `Python Developer`
   - Location: `Bangalore`
   - Min Salary: `800000`
   - Max Salary: `1500000`

2. **Full Stack Developer in Hyderabad**
   - Title: `Full Stack Developer`
   - Location: `Hyderabad`
   - Min Salary: `600000`
   - Max Salary: `1200000`

3. **Data Scientist in Mumbai**
   - Title: `Data Scientist`
   - Location: `Mumbai`
   - Min Salary: `1000000`
   - Max Salary: `2000000`

---

## Features:
✅ Jobs from India only
✅ Tech jobs by default
✅ Salary in Indian Rupees (₹)
✅ Indian city suggestions
✅ Real-time job listings
✅ Save/bookmark jobs
✅ Apply directly to jobs

---

**Your job system is now optimized for tech jobs in India!** 🇮🇳 🚀
