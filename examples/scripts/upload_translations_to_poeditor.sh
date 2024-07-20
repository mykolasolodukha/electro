#!/bin/bash

set -euo pipefail

echo "Uploading terms to POEditor..."


# Set the API token and project ID from parameters or default to environment variables
POEDITOR__API_TOKEN="${1:-$POEDITOR__API_TOKEN}"
POEDITOR__PROJECT_ID="${2:-$POEDITOR__PROJECT_ID}"

if [ -z "$POEDITOR__API_TOKEN" ]; then
  echo "Error: POEDITOR__API_TOKEN is not set."
  exit 1
fi

if [ -z "$POEDITOR__PROJECT_ID" ]; then
  echo "Error: POEDITOR__PROJECT_ID is not set."
  exit 1
fi

# Set the sources directory. The `locales` directory should be in it.
SOURCES_DIR="${3:-$SOURCES_DIR}"

# File to be uploaded
FILE_PATH="./$SOURCES_DIR/locales/messages.pot"

# Check if the file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File $FILE_PATH does not exist."
    exit 1
fi

# Default locale
DEFAULT_LOCALE="${DEFAULT_LOCALE:-en}"

# Function to get language value
get_language_value() {
    local locale="$1"
    case "$locale" in
        "en")
            echo "189"
            ;;
        "fr")
            echo "50"
            ;;
        *)
            echo "Unknown locale $locale. Cannot get its ID for POEditor."
            exit 1
    esac
}


echo "Starting upload of terms to POEditor from $FILE_PATH..."

# Updating terms using the API
RESPONSE=$(curl -s -X POST https://api.poeditor.com/v2/projects/upload \
  -F api_token="$POEDITOR__API_TOKEN" \
  -F id="$POEDITOR__PROJECT_ID" \
  -F updating=terms \
  -F file=@"$FILE_PATH")

# Checking if the request was successful
SUCCESS=$(echo "$RESPONSE" | jq -r '.response.status')

if [[ "$SUCCESS" == "success" ]]; then
    echo "Upload successful!"

    # Open the web page with untranslated terms
    echo "Opening web page with untranslated terms for $DEFAULT_LOCALE..."
    open "https://poeditor.com/projects/po_edit?id=$POEDITOR__PROJECT_ID&per_page=100&id_language=$(get_language_value "$DEFAULT_LOCALE")&filter=ut"
else
    echo "Upload failed. Response from POEditor API: $RESPONSE"
fi
