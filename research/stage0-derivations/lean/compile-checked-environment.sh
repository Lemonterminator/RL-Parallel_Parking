#!/usr/bin/env bash
set -u
export PATH="$HOME/.elan/bin:$PATH"
cd /home/linan/stage0-mathlib || exit 1
proof_dir=/mnt/c/Users/Jiang/Documents/RL/stage0-derivations/lean
log="$proof_dir/COMPILE.log"
{
  date -u '+UTC %Y-%m-%d %H:%M:%S'
  lean --version
  git rev-parse HEAD
  for filename in D06ThreeCircleCover.lean D07RigidDisplacement.lean D08HeadingPotential.lean; do
    printf '\nCHECK %s\n' "$filename"
    lake env lean "$proof_dir/$filename"
    result=$?
    printf 'EXIT_STATUS %s\n' "$result"
    if [ "$result" -ne 0 ]; then exit "$result"; fi
  done
} > "$log" 2>&1
cat "$log"
