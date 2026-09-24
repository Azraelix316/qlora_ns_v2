#!/usr/bin/env bash
# agent.sh — minimal helper for the cross-node agent protocol (see PROTOCOL.md)
#
#   agent.sh start   <me>                  fetch + merge origin/main, print board + inbox
#   agent.sh inbox   <me>                  print messages addressed to <me>
#   agent.sh send    <me> <to> <text...>   append a dated message to <me>'s outbox for <to>
#   agent.sh finish  <me>                  commit all changes + push current branch to agent/<me>
set -euo pipefail

AGENTS="theoretical-research coder writer reviewer writing-research"

cmd="${1:-}"
me=""
case "$cmd" in
  start|inbox|finish)
    me="${2:?usage: agent.sh $cmd <agent>}"
    case " $AGENTS " in
      *" $me "*) ;;
      *) echo "error: unknown agent '$me' (known: $AGENTS)" >&2; exit 1 ;;
    esac
    ;;
  send)
    me="${2:?usage: agent.sh send <me> <to> <text...>}"
    to="${3:?usage: agent.sh send <me> <to> <text...>}"
    case " $AGENTS " in
      *" $me "*) ;;
      *) echo "error: unknown agent '$me' (known: $AGENTS)" >&2; exit 1 ;;
    esac
    case " $AGENTS " in
      *" $to "*) ;;
      *) echo "error: unknown agent '$to' (known: $AGENTS)" >&2; exit 1 ;;
    esac
    ;;
  *)
    echo "usage: agent.sh {start|inbox|send|finish} ..." >&2
    exit 1
    ;;
esac

branch="agent/$me"
if [ "$cmd" != "send" ] && [ "$(git rev-parse --abbrev-ref HEAD)" != "$branch" ]; then
  echo "error: on branch '$(git rev-parse --abbrev-ref HEAD)', expected '$branch'" >&2
  echo "hint: run this from the $me worktree (see PROTOCOL.md, new node setup)" >&2
  exit 1
fi

case "$cmd" in
  start)
    git fetch origin
    git merge origin/main --no-edit
    echo
    echo "=== board (state after merge) ==="
    for a in $AGENTS; do
      f="state/$a/NOTES.md"
      if [ -f "$f" ]; then
        status=$(grep -m1 '^> Status:' "$f" 2>/dev/null | sed 's/^> Status: *//' || true)
        echo "--- $a: ${status:-no status line}"
      fi
    done
    echo
    echo "=== your inbox ($me) ==="
    found=0
    for f in state/*/outbox/"to-$me.md"; do
      [ -e "$f" ] || continue
      found=1
      echo "--- from $(basename "$(dirname "$(dirname "$f")")"): $f"
      cat "$f"
      echo
    done
    [ "$found" = 1 ] || echo "(empty)"
    ;;
  inbox)
    found=0
    for f in state/*/outbox/"to-$me.md"; do
      [ -e "$f" ] || continue
      found=1
      echo "--- from $(basename "$(dirname "$(dirname "$f")")"): $f"
      cat "$f"
      echo
    done
    [ "$found" = 1 ] || echo "(empty)"
    ;;
  send)
    shift 3
    msg="$*"
    f="state/$me/outbox/to-$to.md"
    mkdir -p "$(dirname "$f")"
    {
      echo ""
      echo "## $(date -Is) — from $me"
      echo ""
      echo "$msg"
    } >> "$f"
    echo "appended to $f — run 'scripts/agent.sh finish $me' to push it"
    ;;
  finish)
    git add -A
    if git diff --cached --quiet; then
      echo "nothing to commit"
    else
      git commit -m "[$me] $(date -Is) session update"
    fi
    git push origin "HEAD:refs/heads/$branch"
    ;;
esac
