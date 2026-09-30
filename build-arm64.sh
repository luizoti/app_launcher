#!/usr/bin/env bash
# Cross build the ARM64 (Raspberry Pi) binary from an x86_64 host using
# Docker + QEMU. The heavy work happens while the image is built, so the
# result is a plain layer that can simply be copied out.
#
# Usage:
#   ./build-arm64.sh              # build and extract dist/app_launcher
#   ./build-arm64.sh --no-cache   # force a full rebuild
set -euo pipefail

cd "$(dirname "$0")"

IMAGE="${IMAGE:-app-launcher-builder-arm64}"
PLATFORM="linux/arm64"
DOCKER_BUILD_ARGS=()

if [[ "${1:-}" == "--no-cache" ]]; then
    DOCKER_BUILD_ARGS+=(--no-cache)
fi

# .git fica de fora do contexto de build (ver .dockerignore), então a versão
# derivada da contagem de commits é calculada aqui e passada como build arg.
# Fórmula: 0.{n // 100}.{n % 100} — 1 commit = 0.0.1, 100 = 0.1.0, 250 = 0.2.50.
APP_VERSION=""
COMMIT_COUNT="$(git rev-list --count HEAD 2>/dev/null || true)"
if [[ -n "$COMMIT_COUNT" && "$COMMIT_COUNT" =~ ^[0-9]+$ ]]; then
    MINOR=$((COMMIT_COUNT / 100))
    PATCH=$((COMMIT_COUNT % 100))
    APP_VERSION="0.${MINOR}.${PATCH}"
    if git status --porcelain 2>/dev/null | grep -q .; then
        APP_VERSION="${APP_VERSION}-dirty"
    fi
    echo "==> Versao do build: $APP_VERSION ($COMMIT_COUNT commits)"
    DOCKER_BUILD_ARGS+=(--build-arg "APP_LAUNCHER_VERSION=$APP_VERSION")
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "docker nao encontrado no PATH" >&2
    exit 1
fi

# Register the QEMU binfmt handlers so Docker can run arm64 containers
# transparently on this x86_64 host. Needs --privileged once per boot.
if ! grep -qs 'aarch64' /proc/sys/fs/binfmt_misc/qemu-aarch64 2>/dev/null; then
    echo "==> Registrando handlers binfmt para arm64 (QEMU)"
    docker run --privileged --rm tonistiigi/binfmt --install arm64 >/dev/null
fi

echo "==> Construindo a imagem $IMAGE ($PLATFORM)"
docker build \
    --platform "$PLATFORM" \
    --file Dockerfile.build \
    --tag "$IMAGE" \
    "${DOCKER_BUILD_ARGS[@]}" \
    .

echo "==> Extraindo dist/app_launcher"
mkdir -p dist
container_id="$(docker create "$IMAGE")"
trap 'docker rm -f "$container_id" >/dev/null 2>&1 || true' EXIT
docker cp "$container_id:/app/dist/app_launcher" ./dist/app_launcher
docker rm "$container_id" >/dev/null
trap - EXIT

echo
echo "==> Resultado"
file ./dist/app_launcher
du -h ./dist/app_launcher

if ! file ./dist/app_launcher | grep -q 'ARM aarch64'; then
    echo "ERRO: o binario gerado nao e ARM aarch64" >&2
    exit 1
fi

echo
echo "==> Copie para o Pi:"
echo "    scp ./dist/app_launcher home:~/.local/bin/app_launcher"
