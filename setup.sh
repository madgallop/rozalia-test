#!/bin/bash
# Create the hidden folder if it doesn't exist
mkdir -p .streamlit

# Take the GitHub secret environment variable and print it into the file
echo "$MY_SECRETS_BLOCK" > .streamlit/secrets.toml

echo "Database secrets successfully injected by GitHub!"