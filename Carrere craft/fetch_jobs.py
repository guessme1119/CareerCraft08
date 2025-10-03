import os
import requests
from datetime import datetime, timedelta

class JobFetcher:
    """Fetch jobs from Adzuna API"""
    
    def __init__(self):
        self.app_id = os.environ.get('ADZUNA_APP_ID')
        self.api_key = os.environ.get('ADZUNA_API_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.country = "in"  # India - Change to your country code (us, gb, in, etc.)
    
    def fetch_jobs(self, query="", location="", page=1, results_per_page=30, salary_min=None, salary_max=None):
        """
        Fetch jobs from Adzuna API
        
        Args:
            query: Job title or keywords
            location: Location to search
            page: Page number (starts at 1)
            results_per_page: Number of results per page (max 50)
            salary_min: Minimum salary
            salary_max: Maximum salary
        
        Returns:
            dict: Job results with metadata
        """
        if not self.app_id or not self.api_key:
            return {
                'success': False,
                'error': 'API credentials not configured',
                'jobs': []
            }
        
        # Build API endpoint
        endpoint = f"{self.base_url}/{self.country}/search/{page}"
        
        # Build query parameters
        params = {
            'app_id': self.app_id,
            'app_key': self.api_key,
            'results_per_page': min(results_per_page, 50),
            'what': query,
            'where': location,
            'content-type': 'application/json'
        }
        
        # Add salary filters if provided
        if salary_min:
            params['salary_min'] = salary_min
        if salary_max:
            params['salary_max'] = salary_max
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and format job results
            jobs = []
            for job in data.get('results', []):
                jobs.append({
                    'id': job.get('id'),
                    'title': job.get('title'),
                    'company': job.get('company', {}).get('display_name', 'Company Not Listed'),
                    'location': job.get('location', {}).get('display_name', 'Location Not Specified'),
                    'description': job.get('description', '')[:300] + '...' if len(job.get('description', '')) > 300 else job.get('description', ''),
                    'salary_min': job.get('salary_min'),
                    'salary_max': job.get('salary_max'),
                    'salary_is_predicted': job.get('salary_is_predicted', False),
                    'contract_type': job.get('contract_type', 'Not Specified'),
                    'contract_time': job.get('contract_time', 'Full Time'),
                    'created': job.get('created'),
                    'redirect_url': job.get('redirect_url'),
                    'category': job.get('category', {}).get('label', 'Other')
                })
            
            return {
                'success': True,
                'jobs': jobs,
                'total_results': data.get('count', 0),
                'page': page,
                'results_per_page': results_per_page
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}',
                'jobs': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing jobs: {str(e)}',
                'jobs': []
            }
    
    def format_salary(self, salary_min, salary_max, is_predicted=False):
        """Format salary range for display"""
        if not salary_min and not salary_max:
            return "Salary Not Specified"
        
        prefix = "Est. " if is_predicted else ""
        
        # For India, show in INR (₹)
        if self.country == "in":
            if salary_min and salary_max:
                return f"{prefix}₹{salary_min:,.0f} - ₹{salary_max:,.0f}"
            elif salary_min:
                return f"{prefix}₹{salary_min:,.0f}+"
            else:
                return f"{prefix}Up to ₹{salary_max:,.0f}"
        else:
            # For other countries, show in USD ($)
            if salary_min and salary_max:
                return f"{prefix}${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min:
                return f"{prefix}${salary_min:,.0f}+"
            else:
                return f"{prefix}Up to ${salary_max:,.0f}"
    
    def calculate_days_ago(self, created_date):
        """Calculate how many days ago the job was posted"""
        try:
            job_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            now = datetime.now(job_date.tzinfo)
            delta = now - job_date
            
            if delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Yesterday"
            elif delta.days < 7:
                return f"{delta.days} days ago"
            elif delta.days < 30:
                weeks = delta.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            else:
                months = delta.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
        except:
            return "Recently"
