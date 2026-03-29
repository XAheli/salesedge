#!/usr/bin/env bash
# SalesEdge — API Key Rotation Helper
# Safely rotates API keys in the .env file with backup and validation.
#
# Usage:
#   ./scripts/rotate-keys.sh SE_OGD_API_KEY         # Rotate a specific key
#   ./scripts/rotate-keys.sh --list                  # List all rotatable keys
#   ./scripts/rotate-keys.sh --check                 # Verify all keys are valid

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
BACKUP_DIR="$PROJECT_ROOT/.env-backups"

ROTATABLE_KEYS=(
    "SE_OGD_API_KEY"
    "SE_LLM_API_KEY"
    "SE_JWT_SECRET_KEY"
    "SE_FINNHUB_API_KEY"
    "SE_ALPHA_VANTAGE_KEY"
    "SE_FMP_API_KEY"
    "SE_COINGECKO_API_KEY"
    "SE_EXCHANGERATE_KEY"
    "SE_OPENEXCHANGE_APP_ID"
)

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found at $ENV_FILE"
    echo "Run 'make bootstrap' to create it."
    exit 1
fi

list_keys() {
    echo "Rotatable API keys:"
    echo ""
    for key in "${ROTATABLE_KEYS[@]}"; do
        current=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
        if [ -n "$current" ] && [ "$current" != "" ]; then
            masked="${current:0:4}...${current: -4}"
            echo "  $key = $masked"
        else
            echo "  $key = (not set)"
        fi
    done
}

check_keys() {
    echo "Checking API key validity..."
    echo ""
    local all_ok=true

    ogd_key=$(grep "^SE_OGD_API_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
    if [ -n "$ogd_key" ] && [ "$ogd_key" != "your-ogd-api-key-here" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://api.data.gov.in/resource/server-lookup?api-key=${ogd_key}&format=json&limit=1" 2>/dev/null || echo "000")
        if [ "$status" = "200" ]; then
            echo "  SE_OGD_API_KEY: VALID (HTTP $status)"
        else
            echo "  SE_OGD_API_KEY: INVALID or UNREACHABLE (HTTP $status)"
            all_ok=false
        fi
    else
        echo "  SE_OGD_API_KEY: NOT SET"
        all_ok=false
    fi

    jwt_key=$(grep "^SE_JWT_SECRET_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
    if [ -n "$jwt_key" ] && [ ${#jwt_key} -ge 32 ]; then
        echo "  SE_JWT_SECRET_KEY: SET (${#jwt_key} chars)"
    else
        echo "  SE_JWT_SECRET_KEY: WEAK or NOT SET (min 32 chars recommended)"
        all_ok=false
    fi

    if $all_ok; then
        echo ""
        echo "All checked keys are valid."
    else
        echo ""
        echo "Some keys need attention. See above."
        exit 1
    fi
}

rotate_key() {
    local key_name="$1"

    local valid=false
    for k in "${ROTATABLE_KEYS[@]}"; do
        if [ "$k" = "$key_name" ]; then valid=true; break; fi
    done

    if ! $valid; then
        echo "ERROR: '$key_name' is not a recognized rotatable key."
        echo "Run '$0 --list' to see valid keys."
        exit 1
    fi

    mkdir -p "$BACKUP_DIR"
    local backup="$BACKUP_DIR/.env.$(date +%Y%m%d_%H%M%S)"
    cp "$ENV_FILE" "$backup"
    echo "Backed up .env to $backup"

    read -rp "Enter new value for $key_name: " new_value

    if [ -z "$new_value" ]; then
        echo "ERROR: Empty value not allowed."
        exit 1
    fi

    if grep -q "^${key_name}=" "$ENV_FILE"; then
        local tmp_file
        tmp_file=$(mktemp)
        while IFS= read -r line; do
            if [[ "$line" =~ ^${key_name}= ]]; then
                echo "${key_name}=${new_value}"
            else
                echo "$line"
            fi
        done < "$ENV_FILE" > "$tmp_file"
        mv "$tmp_file" "$ENV_FILE"
        echo "Updated $key_name in .env"
    else
        echo "${key_name}=${new_value}" >> "$ENV_FILE"
        echo "Added $key_name to .env"
    fi

    echo ""
    echo "Key rotated. Restart services to apply:"
    echo "  make dev-backend   # restart backend"
}

case "${1:-}" in
    --list)  list_keys ;;
    --check) check_keys ;;
    --help|-h)
        echo "Usage:"
        echo "  $0 KEY_NAME    Rotate a specific API key"
        echo "  $0 --list      List all rotatable keys and their status"
        echo "  $0 --check     Validate key connectivity"
        echo "  $0 --help      Show this help"
        ;;
    "")
        echo "ERROR: Specify a key name or use --list / --check"
        echo "Run '$0 --help' for usage."
        exit 1
        ;;
    *)
        rotate_key "$1"
        ;;
esac
