#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

cd "${repo_root}"

if [[ ! -d .git ]]; then
  echo "This script must run inside a git clone of oracle-apex-ai-skills-apexlang." >&2
  exit 1
fi

git pull --ff-only

install_codex="false"
if [[ -d "${HOME}/.agents" ]]; then
  install_codex="true"
else
  for skill in oracle-apex-ai-skills-apexlang oracle-apexlang-dev oracle-apexlang-export oracle-apexlang-object-lock; do
    if [[ -e "${CODEX_HOME:-${HOME}/.codex}/skills/${skill}" || -L "${CODEX_HOME:-${HOME}/.codex}/skills/${skill}" ]]; then
      install_codex="true"
      break
    fi
  done
fi

if [[ "${install_codex}" == "true" ]]; then
  if [[ "${1:-}" == "--replace-existing" ]]; then
    bash scripts/install_codex.sh --replace-existing
  else
    bash scripts/install_codex.sh
  fi
fi

if [[ -d "${HOME}/.claude" ]]; then
  bash scripts/install_claude_code.sh
fi

echo
echo "Core skills updated. Project profiles under .oracle-apexlang/ were not modified."
