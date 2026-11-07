#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
config_file=${SUBSCRIPTION_DEPLOY_CONFIG:-$script_dir/deploy.env}

if [[ ! -f $config_file ]]; then
    echo "找不到部署配置: $config_file" >&2
    echo "请复制 deploy.env.example 为 deploy.env 并填写订阅文件名。" >&2
    exit 2
fi

# shellcheck disable=SC1090
source "$config_file"

: "${SING_BOX_BIN:?deploy.env 缺少 SING_BOX_BIN}"
: "${SOURCE_CONFIG_DIR:?deploy.env 缺少 SOURCE_CONFIG_DIR}"
: "${REMOTE_HOST:?deploy.env 缺少 REMOTE_HOST}"
: "${PUBLIC_BASE_URL:?deploy.env 缺少 PUBLIC_BASE_URL}"
: "${ORIGIN_IP:?deploy.env 缺少 ORIGIN_IP}"
: "${SUBSCRIPTION_FILENAME:?deploy.env 缺少 SUBSCRIPTION_FILENAME}"

if [[ ! $SUBSCRIPTION_FILENAME =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "SUBSCRIPTION_FILENAME 只能包含字母、数字、点、下划线和连字符" >&2
    exit 2
fi

work_dir=$(mktemp -d /tmp/sing-box-subscribe.XXXXXX)
remote_subscription="/tmp/sing-box-subscribe-${SUBSCRIPTION_FILENAME}.$$"
remote_installer="/tmp/sing-box-subscribe-install.$$.sh"
cleanup() {
    rm -rf "$work_dir"
    ssh -o BatchMode=yes "$REMOTE_HOST" \
        "rm -f '$remote_subscription' '$remote_installer'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

merged_config=$work_dir/merged.json
subscription=$work_dir/$SUBSCRIPTION_FILENAME

printf '%s\n' '1/5 校验生成器测试……'
PYTHONPATH="$script_dir" python3 -m unittest discover -s "$script_dir/tests" -p 'test_*.py'

printf '%s\n' '2/5 合并 sing-box 配置……'
sudo "$SING_BOX_BIN" -C "$SOURCE_CONFIG_DIR" merge /dev/stdout >"$merged_config"

printf '%s\n' '3/5 生成并验证 Base64 订阅……'
python3 "$script_dir/generate.py" generate \
    --input "$merged_config" \
    --output "$subscription"
python3 "$script_dir/generate.py" verify \
    --input "$subscription"

printf '%s\n' '4/5 上传并配置远程 Nginx……'
scp -q "$subscription" "$REMOTE_HOST:$remote_subscription"
scp -q "$script_dir/remote_install.sh" "$REMOTE_HOST:$remote_installer"
ssh -o BatchMode=yes "$REMOTE_HOST" \
    "chmod 0700 '$remote_installer' && '$remote_installer' '$remote_subscription' '$SUBSCRIPTION_FILENAME'"

url="${PUBLIC_BASE_URL%/}/v2ray/$SUBSCRIPTION_FILENAME"
authority=${PUBLIC_BASE_URL#*://}
authority=${authority%%/*}
origin_host=${authority%%:*}
origin_port=${authority##*:}
if [[ $origin_port == "$origin_host" ]]; then
    origin_port=443
fi

printf '%s\n' '5/5 验证源站与公网 HTTPS 地址……'
origin_copy=$work_dir/origin-subscription.txt
curl -fsS --connect-timeout 5 --max-time 20 \
    --resolve "$origin_host:$origin_port:$ORIGIN_IP" \
    --output "$origin_copy" "$url"
python3 "$script_dir/generate.py" verify \
    --input "$origin_copy"
if ! cmp -s "$subscription" "$origin_copy"; then
    echo "源站订阅与本地生成结果不一致" >&2
    exit 1
fi

# Cloudflare 2096 边缘连接偶有短暂 TLS 超时；只接受完整下载并通过解码校验的结果。
public_copy=$work_dir/public-subscription.txt
public_verified=false
for attempt in $(seq 1 10); do
    rm -f "$public_copy"
    if curl -4 -fsS --connect-timeout 5 --max-time 15 \
        --output "$public_copy" "$url" \
        && python3 "$script_dir/generate.py" verify --input "$public_copy" \
        && cmp -s "$subscription" "$public_copy"; then
        public_verified=true
        break
    fi
    echo "公网验证第 $attempt 次失败，2 秒后重试……" >&2
    sleep 2
done
if [[ $public_verified != true ]]; then
    echo "源站验证成功，但 Cloudflare 公网地址连续验证失败" >&2
    exit 1
fi

printf '\n发布完成：\n%s\n' "$url"
