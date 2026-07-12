#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: transcribe.sh <audio-file> [output.txt]

Uses ElevenLabs Scribe v1. Requires ELEVENLABS_API_KEY.
USAGE
}

if [[ $# -eq 1 && ( "$1" == "-h" || "$1" == "--help" ) ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 64
fi

case "$1" in
  -*)
    echo "ERROR: unknown option: $1" >&2
    usage
    exit 64
    ;;
esac

AUDIO_FILE="${1/#\~/$HOME}"
OUTPUT_FILE="${2:-${AUDIO_FILE%.*}.transcript.txt}"

if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "ERROR: audio file not found: $AUDIO_FILE" >&2
  exit 66
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl is required for transcription requests." >&2
  exit 69
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/post-walk-transcribe.XXXXXX")"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

strip_assignment_value() {
  local line="$1"
  line="$(printf '%s' "$line" | sed -E 's/^[[:space:]]*export[[:space:]]+//; s/^[[:space:]]*//')"
  local value="${line#*=}"
  value="${value%%#*}"
  value="$(printf '%s' "$value" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  printf '%s' "$value"
}

load_key_from_known_files() {
  local key="$1"
  [[ -n "${!key:-}" ]] && return 0
  [[ "${POST_WALK_TRANSCRIBE_NO_ENV_FILES:-}" == "1" ]] && return 1

  local files=(
    "$PWD/.env"
    "$PWD/.env.local"
    "$HOME/.zshenv"
    "$HOME/.zprofile"
    "$HOME/.zshrc"
  )

  local file line value
  for file in "${files[@]}"; do
    [[ -r "$file" ]] || continue
    line="$(grep -E "^[[:space:]]*(export[[:space:]]+)?${key}=" "$file" | tail -n 1 || true)"
    [[ -n "$line" ]] || continue
    value="$(strip_assignment_value "$line")"
    if [[ -n "$value" ]]; then
      export "$key=$value"
      return 0
    fi
  done

  return 1
}

require_key() {
  local key="$1"
  if ! load_key_from_known_files "$key"; then
    cat >&2 <<ERR
ERROR: $key is required.
Export $key, or define it in one of:
  - $PWD/.env
  - $PWD/.env.local
  - $HOME/.zshenv
  - $HOME/.zprofile
  - $HOME/.zshrc
ERR
    exit 78
  fi
}

ensure_output_dir() {
  local dir
  dir="$(dirname "$OUTPUT_FILE")"
  mkdir -p "$dir"
}

print_failure_details() {
  local body="$1"
  local err="$2"
  echo "ERROR: ElevenLabs Scribe transcription request failed." >&2
  if [[ -s "$err" ]]; then
    sed 's/^/curl: /' "$err" >&2
  fi
  if [[ -s "$body" ]]; then
    sed 's/^/response: /' "$body" >&2
  fi
}

extract_elevenlabs_text() {
  local response_file="$1"
  local output_file="$2"

  if command -v python3 >/dev/null 2>&1; then
    python3 - "$response_file" "$output_file" <<'PY'
import json
import sys

response_path, output_path = sys.argv[1:3]
with open(response_path, "r", encoding="utf-8") as f:
    data = json.load(f)

text = data.get("text", "")
if not isinstance(text, str) or not text.strip():
    raise SystemExit("ElevenLabs response did not contain a non-empty text field")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text.strip() + "\n")
PY
    return
  fi

  if command -v jq >/dev/null 2>&1; then
    local text
    text="$(jq -r '.text // empty' "$response_file")"
    if [[ -z "$text" ]]; then
      echo "ERROR: ElevenLabs response did not contain a non-empty text field." >&2
      return 1
    fi
    printf '%s\n' "$text" > "$output_file"
    return
  fi

  echo "ERROR: python3 or jq is required to parse ElevenLabs JSON responses." >&2
  return 69
}

transcribe_elevenlabs() {
  require_key "ELEVENLABS_API_KEY"

  local response="$TMP_DIR/elevenlabs-response.json"
  local error="$TMP_DIR/elevenlabs-error.txt"
  : > "$response"
  : > "$error"

  # Fireworks audio inference was deprecated on 2026-06-10, so use ElevenLabs
  # Scribe: about $0.40/hr, best-in-class accuracy, and native m4a support.
  if ! curl --silent --show-error --fail-with-body \
    -X POST "https://api.elevenlabs.io/v1/speech-to-text" \
    -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
    -F "model_id=scribe_v1" \
    -F "file=@${AUDIO_FILE}" \
    -o "$response" \
    2> "$error"; then
    print_failure_details "$response" "$error"
    exit 1
  fi

  ensure_output_dir
  extract_elevenlabs_text "$response" "$OUTPUT_FILE"
}

transcribe_elevenlabs
printf '%s\n' "$OUTPUT_FILE"
