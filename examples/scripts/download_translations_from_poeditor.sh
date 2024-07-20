#!/bin/bash

set -euo pipefail

echo "Fetching all languages from the project..."

# Set the API token and project ID from parameters or default to environment variables
POEDITOR__API_TOKEN="${1:-$POEDITOR__API_TOKEN}"
POEDITOR__PROJECT_ID="${2:-$POEDITOR__PROJECT_ID}"

# Set the sources directory. The `locales` directory should be in it.
SOURCES_DIR="${3:-$SOURCES_DIR}"

if [ -z "$POEDITOR__API_TOKEN" ]; then
  echo "Error: POEDITOR__API_TOKEN is not set."
  exit 1
fi

if [ -z "$POEDITOR__PROJECT_ID" ]; then
  echo "Error: POEDITOR__PROJECT_ID is not set."
  exit 1
fi

if [ -z "$SOURCES_DIR" ]; then
  SOURCES_DIR="."
fi

# Get all languages from the project
LANGUAGES=$(curl -s -X POST https://api.poeditor.com/v2/languages/list \
  -d api_token="$POEDITOR__API_TOKEN" \
  -d id="$POEDITOR__PROJECT_ID" | jq -r '.result.languages[].code')

echo "Languages fetched. Starting to export translations..."

# For each language, export the translations
for LANGUAGE in $LANGUAGES
do
  echo "Processing language: $LANGUAGE"

  echo "$POEDITOR__PROJECT_ID"

  # Request export
  EXPORT=$(curl -s -X POST https://api.poeditor.com/v2/projects/export \
    -d api_token="$POEDITOR__API_TOKEN" \
    -d id="$POEDITOR__PROJECT_ID" \
    -d language="$LANGUAGE" \
    -d type="po")

  # Get export URL
  URL=$(echo "$EXPORT" | jq -r '.result.url')

  # Create directory if not exists
  echo "Creating directory for $LANGUAGE if not exists..."
  mkdir -p "./$SOURCES_DIR/locales/$LANGUAGE/LC_MESSAGES/"

  echo "Downloading translations file for $LANGUAGE..."

  # Download the file
  curl -s -o "./$SOURCES_DIR/locales/$LANGUAGE/LC_MESSAGES/messages.po" "$URL"

  echo "Translations for $LANGUAGE have been downloaded and saved!"
done

echo "All translations have been exported successfully."
