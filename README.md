DevAI

To start backend server: `uvicorn dev_ai.asgi:application --reload`  
To start code-server: `cd backend; docker run -p 8080:8080 -v $(pwd)/code-environment:/tmp/code-environment code-server-update`  
To start image-library `docker pull miranfirdausi/image-library:latest; docker run -d -p 8001:8000 --name image_library_container image-library`