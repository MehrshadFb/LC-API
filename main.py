import datetime
import json
import os
from collections import defaultdict

import requests
from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import redis
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["*"])

# Connect to Redis (Upstash)
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True,
)


def get_user_profile(username):
    """Fetch comprehensive user profile data from LeetCode."""
    url = "https://leetcode.com/graphql"

    # Query for user profile information
    # Note: To view all available variables and queries, open a user's LeetCode profile page,
    #       then inspect the Network tab in your browser's developer tools.
    #       Filter by XHR requests and look for GraphQL queries to see the structure and fields used.
    profile_query = {
        "query": """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            username
            profile {
              realName
              aboutMe
              school
              websites
              countryName
              company
              jobTitle
              skillTags
              userAvatar
              ranking
            }
            githubUrl
            twitterUrl
            linkedinUrl
            submitStats {
              acSubmissionNum {
                difficulty
                count
                submissions
              }
              totalSubmissionNum {
                difficulty
                count
                submissions
              }
            }
            userCalendar {
              submissionCalendar
            }
          }
          allQuestionsCount {
            difficulty
            count
          }
        }
        """,
        "variables": {"username": username},
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "LeetCode-API/1.0",  # Avoid being blocked by LeetCode
    }

    response = requests.post(url, json=profile_query, headers=headers)
    return response.json()


def process_progress_by_year(submission_calendar):
    """Process submission calendar to get progress by year with daily breakdowns."""
    progress = {}
    today = datetime.date.today()
    one_year_ago = today - datetime.timedelta(days=365)

    # Initialize data structures
    yearly_data = defaultdict(lambda: {"daily": {}, "total": 0})
    current_data = {"daily": {}, "total": 0}

    # Process each submission entry
    for timestamp_str, count in submission_calendar.items():
        timestamp = int(timestamp_str)
        date = datetime.date.fromtimestamp(timestamp)  # Convert timestamp to date
        year = date.year
        date_str = date.isoformat()  # Format date as YYYY-MM-DD

        # Add to yearly data
        yearly_data[year]["daily"][date_str] = count
        yearly_data[year]["total"] += count

        # Current logic - last past year
        if one_year_ago <= date <= today:
            current_data["daily"][date_str] = count
            current_data["total"] += count

    # Add current progress (last 365 days) with daily breakdown
    progress["current"] = current_data

    # Add yearly progress with daily breakdowns
    for year in sorted(
        yearly_data.keys(), reverse=True
    ):  # Sort years in descending order
        progress[str(year)] = {
            "daily": yearly_data[year]["daily"],
            "total": yearly_data[year]["total"],
        }

    return progress


@app.route("/api/user/<username>", methods=["GET"])
def get_user_data(username):
    """Get comprehensive user data including profile, progress, and problem statistics."""
    try:
        # Check Redis cache first
        cache_key = f"leetcode_user:{username}"
        cached_data = r.get(cache_key)
        if cached_data:
            return jsonify(json.loads(cached_data))

        # If not in cache, fetch user data from LeetCode
        data = get_user_profile(username)

        # Safety checks
        if (
            "data" not in data
            or not data["data"]
            or data["data"]["matchedUser"] is None
        ):
            return jsonify(
                {
                    "error": "Could not fetch user data. Maybe invalid username or blocked request."
                }
            )

        user_data = data["data"]["matchedUser"]
        all_questions = data["data"]["allQuestionsCount"]

        # Extract profile information
        profile = user_data.get("profile", {})

        # Process submission calendar
        submission_calendar_str = user_data["userCalendar"]["submissionCalendar"]
        submission_calendar = json.loads(
            submission_calendar_str
        )  # Convert string to dictionary

        # Process progress by year
        progress = process_progress_by_year(submission_calendar)

        # Process problem statistics
        problems = {
            "easy": {"solved": 0, "total": 0},
            "medium": {"solved": 0, "total": 0},
            "hard": {"solved": 0, "total": 0},
        }

        # Get total questions count for each difficulty
        for question_stat in all_questions:
            difficulty = question_stat["difficulty"].lower()
            if difficulty in problems:  # Ignore 'All'
                problems[difficulty]["total"] = question_stat["count"]

        # Get solved questions count for each difficulty
        for submission_stat in user_data["submitStats"]["acSubmissionNum"]:
            difficulty = submission_stat["difficulty"].lower()
            if difficulty in problems:  # Do we need this guard?
                problems[difficulty]["solved"] = submission_stat["count"]

        # Build the response according to the specified format
        result = {
            "username": user_data.get("username"),
            "github": user_data.get("githubUrl"),
            "twitter": user_data.get("twitterUrl"),
            "linkedin": user_data.get("linkedinUrl"),
            "ranking": profile.get("ranking"),
            "realname": profile.get("realName"),
            "aboutme": profile.get("aboutMe"),
            "school": profile.get("school"),
            "website": profile.get("websites", []),
            "country_name": profile.get("countryName"),
            "company": profile.get("company"),
            "job_title": profile.get("jobTitle"),
            "skill": profile.get("skillTags", []),
            "progress": progress,
            "problem": problems,
        }

        # Store in Redis cache for 1 hour (3600 seconds)
        # LeetCode data doesn't change frequently, so 1 hour is reasonable
        r.setex(cache_key, 3600, json.dumps(result))

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})


# Swagger UI setup
SWAGGER_URL = "/docs"  # URL for exposing Swagger UI
API_URL = "/swagger.yaml"  # URL for Swagger YAML file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "LeetCode Profile API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/swagger.yaml")
def swagger_yaml():
    return send_from_directory(".", "swagger.yaml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
