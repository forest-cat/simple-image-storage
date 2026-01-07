# SIS (Simple-Image-Storage) API
## Description
This project is a simple API writen in Python with Fast-API to store and serve images, featuring a simple authentication.
## Installation
### Docker Compose (recommended)
1. Ensure your docker is set up correctly
2. Clone this repository: `git clone https://github.com/forest-cat/simple-image-storage.git`
3. Navigate into it: `cd simple-image-storage`
4. Configure a Token via the `SIS_ACCESS_TOKEN` environment variable in the `docker-compose.yml`
5. Build the container with: `docker compose build`
6. Run the application using: `docker compose up -d`
### Manual Installation using uv
1. Ensure you have access to a working `uv` installation
2. Clone this repository: `git clone https://github.com/forest-cat/simple-image-storage.git`
3. Navigate into it: `cd simple-image-storage`
4. Run `uv sync` to ensure all packages are installed
5. Copy the `example_config.yml` from this repository and set a token, you can change all other values or remove them because they're the default values and don't change anything
6. Start the application using `uv run app/main.py`

## Usage
To use the application i recommend using curl or by using any request library in your favorite language
### Upload Image
To upload an use the following curl command:
```bash
curl -F 'file=@<filepath>' -H "Authorization: Bearer <token>" <endpoint-root-url>/upload/<integer-id>
```
The `integer-id` can be any given id you want the image to be accessible on later.
The `endpoint-root-url` is the endpoint for the api, it could look like this: `https://example.com`
### Download Image
To download an image use the following curl command:
```bash
curl -o output.webp <endpoint-root-url>/image/<integer-id>
```
> Note: The output file here has the .webp extension because all images uploaded to the api will be automatically converted to a webp file and only served as such to save bandwith.