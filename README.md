# LeetCode Profile API

A Flask-based REST API that fetches and processes comprehensive LeetCode user data including user profiles, submission statistics, and progress tracking by year.

## Features

- 🔍 **Comprehensive User Profiles**: Fetch detailed user information including bio, company, education, and social links
- 📊 **Problem Statistics**: Get solving statistics categorized by difficulty (Easy, Medium, Hard)
- 📅 **Progress Tracking**: View submission progress with yearly breakdowns and daily activity
- 🎯 **Current Year Analysis**: Special focus on the last 365 days of activity
- 🔗 **Social Integration**: Access to GitHub, Twitter, and LinkedIn profiles
- 🏆 **Ranking Information**: LeetCode ranking and skill tags
- ⚡ **Redis Caching**: Fast response times with 1-hour cache for user data
- 🌐 **CORS Enabled**: Cross-origin requests supported for web applications

## API Endpoint

### Get User Data

**Endpoint:** `GET /api/user/{username}`

**Description:** Retrieves comprehensive LeetCode user data for the specified username.

**Parameters:**

- `username` (path parameter, required): LeetCode username

**Example Request:**

```bash
curl -X GET "http://127.0.0.1:5000/api/user/john_doe"
```

**Example Response:**

```json
{
  "username": "john_doe",
  "github": "https://github.com/johndoe",
  "twitter": "https://twitter.com/johndoe",
  "linkedin": "https://linkedin.com/in/johndoe",
  "ranking": 12345,
  "realname": "John Doe",
  "aboutme": "Software Engineer passionate about algorithms",
  "school": "MIT",
  "website": ["https://johndoe.dev"],
  "country_name": "United States",
  "company": "Tech Corp",
  "job_title": "Senior Software Engineer",
  "skill": ["Python", "JavaScript", "Algorithms"],
  "progress": {
    "current": {
      "daily": {
        "2024-01-15": 3,
        "2024-01-16": 5
      },
      "total": 180
    },
    "2024": {
      "daily": {
        "2024-01-01": 2,
        "2024-01-02": 1
      },
      "total": 365
    },
    "2023": {
      "daily": {
        "2023-12-31": 4
      },
      "total": 200
    }
  },
  "problem": {
    "easy": {
      "solved": 150,
      "total": 800
    },
    "medium": {
      "solved": 100,
      "total": 1600
    },
    "hard": {
      "solved": 25,
      "total": 700
    }
  }
}
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd LC-API
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   Copy the example environment file and configure your Redis credentials:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Redis (Upstash) credentials:

   ```bash
   REDIS_HOST=your-redis-host.upstash.io
   REDIS_PORT=your-redis-port
   REDIS_PASSWORD=your-redis-password
   ```

## Usage

1. **Start the server:**

   ```bash
   python main.py
   ```

2. **Access the API:**
   The server will start on `http://127.0.0.1:5000` by default.

3. **Make requests:**
   ```bash
   # Get user data for a specific LeetCode username
   curl http://127.0.0.1:5000/api/user/your_leetcode_username
   ```

## Response Format

### Success Response (200)

The API returns a JSON object with the following structure:

| Field          | Type         | Description                |
| -------------- | ------------ | -------------------------- |
| `username`     | string       | LeetCode username          |
| `github`       | string/null  | GitHub profile URL         |
| `twitter`      | string/null  | Twitter profile URL        |
| `linkedin`     | string/null  | LinkedIn profile URL       |
| `ranking`      | integer/null | LeetCode ranking           |
| `realname`     | string/null  | User's real name           |
| `aboutme`      | string/null  | User's bio/about section   |
| `school`       | string/null  | Educational institution    |
| `website`      | array        | List of personal websites  |
| `country_name` | string/null  | User's country             |
| `company`      | string/null  | Current company            |
| `job_title`    | string/null  | Current job title          |
| `skill`        | array        | List of skill tags         |
| `progress`     | object       | Submission progress data   |
| `problem`      | object       | Problem solving statistics |

#### Progress Object Structure

The `progress` object contains:

- `current`: Last 365 days of activity
- `YYYY`: Yearly breakdowns (e.g., "2024", "2023")

Each period contains:

- `daily`: Object with date strings as keys and submission counts as values
- `total`: Total submissions for that period

#### Problem Object Structure

The `problem` object contains statistics for each difficulty:

- `easy`: { solved: number, total: number }
- `medium`: { solved: number, total: number }
- `hard`: { solved: number, total: number }

### Error Response (400/500)

```json
{
  "error": "Error message describing what went wrong"
}
```

Common error scenarios:

- Invalid username
- User profile is private or doesn't exist
- LeetCode API blocking requests
- Network connectivity issues

## Technical Details

### Dependencies

- **Flask**: Web framework for creating the REST API
- **flask-cors**: Enable CORS for cross-origin requests from web applications
- **flask-swagger-ui**: Interactive API documentation interface
- **requests**: HTTP library for making requests to LeetCode's GraphQL API
- **redis**: Redis client for caching user data and improving performance
- **python-dotenv**: Load environment variables from .env file for configuration
- **datetime**: For date/time manipulation and progress calculations
- **json**: For parsing LeetCode's submission calendar data
- **collections.defaultdict**: For efficient data structure management

### Data Processing

1. **GraphQL Query**: The API uses LeetCode's GraphQL endpoint to fetch comprehensive user data
2. **Redis Caching**: User data is cached for 1 hour to improve performance and reduce API calls
3. **Calendar Processing**: Submission calendar data is processed to create yearly and current (365-day) breakdowns
4. **Statistics Aggregation**: Problem statistics are calculated by difficulty level
5. **Data Transformation**: Raw LeetCode data is transformed into a clean, structured format

### Caching Strategy

- **Cache Duration**: 1 hour (3600 seconds) for user data
- **Cache Key Format**: `leetcode_user:{username}`
- **Cache Benefits**: Faster response times, reduced LeetCode API calls, better rate limit compliance
- **Cache Provider**: Redis (Upstash) for reliable cloud-based caching

### Rate Limiting Considerations

- The API includes a custom User-Agent header to reduce the likelihood of being blocked
- Redis caching significantly reduces calls to LeetCode's API
- Be mindful of LeetCode's rate limiting policies

## Error Handling

The API includes comprehensive error handling for:

- Invalid usernames
- Network timeouts
- Malformed responses from LeetCode
- Missing or null data fields

## Development

### Project Structure

```
LC-API/
├── main.py           # Main application file
├── swagger.yaml      # OpenAPI/Swagger specification
└── README.md         # This file
```

### Key Functions

- `get_user_profile(username)`: Fetches raw user data from LeetCode's GraphQL API
- `process_progress_by_year(submission_calendar)`: Processes submission calendar into yearly breakdowns
- `get_user_data(username)`: Main API endpoint handler

### Development Setup

1. Enable debug mode (already enabled in the code)
2. The server will automatically reload on code changes
3. Access detailed error messages in debug mode

## API Documentation

For detailed API documentation with interactive testing capabilities, refer to the `swagger.yaml` file which provides:

- Complete endpoint specifications
- Request/response schemas
- Example payloads
- Error response formats

You can view the Swagger documentation using tools like:

- [Swagger Editor](https://editor.swagger.io/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redoc.ly/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This API is for educational and personal use only. Please respect LeetCode's terms of service and rate limiting policies. The API fetches publicly available user data and does not access private information.

## Support

If you encounter any issues or have questions:

1. Check the error response for detailed information
2. Ensure the LeetCode username is correct and the profile is public
3. Verify network connectivity
4. Check if LeetCode's API is accessible from your location
