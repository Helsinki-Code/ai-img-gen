Universal Image Generation API Gateway
This is a high-performance, production-ready API gateway that provides a single, unified endpoint for generating images from multiple AI providers, including OpenAI's DALL-E 3 and Black Forest Labs' FLUX models.

Features
Multi-Provider Support: Seamlessly switch between DALL-E and BFL FLUX models in a single API call.

Unified API: A consistent and predictable request/response format, regardless of the backend provider.

Extensible by Design: Easily add new image generation providers by creating a new "adapter" module.

Production Ready: Includes API key authentication, centralized configuration, and deployment guides for Vercel and Docker.

Asynchronous Processing: Built with FastAPI and httpx for high-performance, non-blocking I/O, essential for handling long-running AI generation tasks.

Getting Started
1. Prerequisites
Python 3.9+

Git

2. Setup (Local Development)
Clone the repository:

git clone <your-repo-url>
cd image-api-gateway

Create and configure your environment file:
Copy the example file and fill in your API keys.

cp .env.example .env

Edit the .env file:

# Your secret keys for the gateway itself. Comma-separated for multiple keys.
GATEWAY_API_KEYS=my-secret-key-1,my-super-secret-key-2

# API Keys for the downstream providers
OPENAI_API_KEY="sk-..."
BFL_API_KEY="bf..."

Install dependencies:

pip install -r requirements.txt

3. Running the Application Locally
To run the server in a local development environment:

uvicorn main:app --reload

The API will be available at http://127.0.0.1:8000 and the interactive documentation (Swagger UI) can be found at http://127.0.0.1:8000/docs.

Deploying to Production with Vercel
Vercel is an excellent platform for deploying this serverless FastAPI application.

1. Prerequisites
A free Vercel account.

Vercel CLI (optional, but recommended): npm install -g vercel

2. Deployment Steps
Push your code to a Git repository (GitHub, GitLab, Bitbucket). Vercel uses this to deploy your project.

Import Project in Vercel:

Log in to your Vercel dashboard.

Click "Add New..." -> "Project".

Select the Git repository you just created. Vercel will automatically detect that it is a Python project because of the requirements.txt and vercel.json files.

Configure Environment Variables:
This is the most critical step for security. Do not commit your .env file. Instead, add the keys in the Vercel project settings:

In the "Configure Project" screen, expand the "Environment Variables" section.

Add the following three secrets, copying the values from your .env file:

GATEWAY_API_KEYS

OPENAI_API_KEY

BFL_API_KEY

Deploy:

Click the "Deploy" button.

Vercel will handle the entire process: installing dependencies, building the serverless function, and deploying it to their global network.

Your API gateway will now be live on a Vercel URL!

Vercel Configuration
Vercel needs a configuration file named vercel.json in the root of your project. This file tells its build system that this is a Python project and how to handle incoming requests, routing them all to your FastAPI application.

Create a file named vercel.json with the following content:

{
    "version": 2,
    "builds": [
        {
            "src": "main.py",
            "use": "@vercel/python",
            "config": { "maxLambdaSize": "15mb" }
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "main.py"
        }
    ]
}

Making a Request
You can use curl or any API client to make requests. Make sure to include your gateway API key in the X-API-Key header.

Example: Generate an image with BFL FLUX

# NOTE: Replace the URL with your Vercel deployment URL
curl -X 'POST' \
  '[https://your-project-name.vercel.app/v1/images/generations](https://your-project-name.vercel.app/v1/images/generations)' \
  -H 'accept: application/json' \
  -H 'X-API-Key: my-secret-key-1' \
  -H 'Content-Type: application/json' \
  -d '{
  "provider": "bfl-flux",
  "prompt": "An epic photograph of a Bengaluru auto-rickshaw navigating a futuristic, neon-lit street in the rain",
  "n": 1,
  "user_id": "user-test-123",
  "provider_params": {
    "model": "flux-kontext-pro",
    "aspect_ratio": "16:9"
  }
}'

Appendix: Docker Deployment
A Dockerfile is included for containerization if you prefer to deploy to other platforms like AWS, Google Cloud Run, or a private server.

Build the Docker image:

docker build -t image-gateway .

Run the Docker container:
Make sure to pass your .env file to the container.

docker run -d --env-file .env -p 8000:8000 image-gateway


