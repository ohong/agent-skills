#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: transcribe.sh <audio-file> [output.txt]

Uses fal.ai Wizper (fal-ai/wizper). Requires FAL_KEY.
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

for cmd in curl python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: $cmd is required." >&2
    exit 69
  fi
done

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

fail() {
  echo "ERROR: $1" >&2
  [[ -n "${2:-}" && -s "${2:-}" ]] && sed 's/^/response: /' "$2" >&2
  exit 1
}

json_field() {
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); v=d.get(sys.argv[2], ""); sys.exit(1) if not isinstance(v,str) or not v else print(v)' "$1" "$2"
}

require_key "FAL_KEY"

content_type="audio/mp4"
case "${AUDIO_FILE##*.}" in
  mp3|mpga) content_type="audio/mpeg" ;;
  wav) content_type="audio/wav" ;;
  webm) content_type="audio/webm" ;;
esac

# 1. Upload the local file to fal storage (Wizper only accepts URLs).
init="$TMP_DIR/initiate.json"
curl --silent --show-error --fail-with-body \
  -X POST "https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3" \
  -H "Authorization: Key ${FAL_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"content_type\": \"${content_type}\", \"file_name\": \"$(basename "$AUDIO_FILE")\"}" \
  -o "$init" || fail "fal storage initiate failed." "$init"

upload_url="$(json_field "$init" upload_url)" || fail "no upload_url in initiate response." "$init"
file_url="$(json_field "$init" file_url)" || fail "no file_url in initiate response." "$init"

curl --silent --show-error --fail \
  -X PUT "$upload_url" \
  -H "Content-Type: ${content_type}" \
  --upload-file "$AUDIO_FILE" \
  -o /dev/null || fail "fal storage upload PUT failed."

# 2. Queue the transcription and poll (long memos exceed sync timeouts).
submit="$TMP_DIR/submit.json"
curl --silent --show-error --fail-with-body \
  -X POST "https://queue.fal.run/fal-ai/wizper" \
  -H "Authorization: Key ${FAL_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"audio_url\": \"${file_url}\", \"task\": \"transcribe\"}" \
  -o "$submit" || fail "Wizper submit failed." "$submit"

status_url="$(json_field "$submit" status_url)" || fail "no status_url in submit response." "$submit"
response_url="$(json_field "$submit" response_url)" || fail "no response_url in submit response." "$submit"

status="$TMP_DIR/status.json"
deadline=$((SECONDS + 1800))
while :; do
  curl --silent --show-error --fail-with-body \
    -H "Authorization: Key ${FAL_KEY}" \
    "$status_url" -o "$status" || fail "Wizper status poll failed." "$status"
  state="$(json_field "$status" status || true)"
  [[ "$state" == "COMPLETED" ]] && break
  [[ "$state" == "IN_QUEUE" || "$state" == "IN_PROGRESS" ]] || fail "Wizper request ended in state: ${state:-unknown}" "$status"
  (( SECONDS < deadline )) || fail "Wizper transcription timed out after 30 minutes."
  sleep 5
done

result="$TMP_DIR/result.json"
curl --silent --show-error --fail-with-body \
  -H "Authorization: Key ${FAL_KEY}" \
  "$response_url" -o "$result" || fail "Wizper result fetch failed." "$result"

mkdir -p "$(dirname "$OUTPUT_FILE")"
python3 - "$result" "$OUTPUT_FILE" <<'PY'
import json, sys
result_path, output_path = sys.argv[1:3]
with open(result_path, encoding="utf-8") as f:
    data = json.load(f)
text = data.get("text", "")
if not isinstance(text, str) or not text.strip():
    raise SystemExit("Wizper response did not contain a non-empty text field")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(text.strip() + "\n")
PY

printf '%s\n' "$OUTPUT_FILE"
