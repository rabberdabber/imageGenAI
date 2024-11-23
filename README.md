# ImageGenAI

A FastAPI-based asynchronous image generation API that leverages AI models to create images from text prompts.

## Features

- 🎨 Text-to-Image Generation
- ⚡ Asynchronous Processing
- 🔒 Built-in Content Moderation
- 🎯 Customizable Image Parameters
- 🚀 FastAPI Backend
- 🐳 Docker Support

## Tech Stack

- Python 3.11+
- FastAPI
- Docker & Docker Compose
- Poetry for dependency management
- Ruff for code formatting and linting

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry package manager
- Docker and Docker Compose (optional)

### Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/imageGenAI.git
cd imageGenAI
```

2. Create a `.env` file in the `src` directory with the following variables:

```env
APP_NAME="ImageGenAI"
APP_DESCRIPTION="An Async FastAPI Image Generation API"
APP_VERSION="0.1.0"
ENVIRONMENT="local"
FLUX_API_KEY="your_flux_api_key"
```

### Installation

#### Using Poetry (Recommended)

1. Install dependencies:

```bash
poetry install
```

2. Activate the virtual environment:

```bash
poetry shell
```

#### Using Docker

1. Build and run the containers:

```bash
docker-compose up --build
```

## API Usage

### Generate Image Endpoint

```bash
POST /api/v1/generate-image
```

Request body:

```json
{
  "prompt": "A beautiful sunset over mountains",
  "width": 1024,
  "height": 768,
  "prompt_upsampling": false,
  "seed": null,
  "safety_tolerance": 2,
  "output_format": "jpeg"
}
```

Parameters:

- `prompt`: Text description of the desired image
- `width`: Image width (64-2048 pixels)
- `height`: Image height (64-2048 pixels)
- `prompt_upsampling`: Enable/disable prompt upsampling
- `seed`: Optional seed for reproducible generations
- `safety_tolerance`: Content moderation level (0-3)
- `output_format`: Output format ("jpeg" or "png")

## Development

### Code Quality

The project uses pre-commit hooks for code quality. Install them with:

```bash
pre-commit install
```

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
ruff check --fix
ruff format
```

## Acknowledgments

This project structure is inspired by the [FastAPI-boilerplate](https://github.com/igorbenav/FastAPI-boilerplate) - an excellent template for building scalable FastAPI applications with modern best practices.
