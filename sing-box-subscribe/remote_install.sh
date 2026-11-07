#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "用法: $0 <远程临时订阅文件> <最终文件名>" >&2
    exit 2
fi

staged_file=$1
filename=$2
publish_dir=/var/www/sing-box-subscribe
nginx_conf=/etc/nginx/conf.d/sing-box-subscribe.conf
snippet_dir=/etc/nginx/snippets
snippet=$snippet_dir/sing-box-subscribe-managed.conf
include_line="    include $snippet;"

if [[ ! $filename =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "非法订阅文件名: $filename" >&2
    exit 2
fi
if [[ ! -f $staged_file ]]; then
    echo "找不到上传的临时文件: $staged_file" >&2
    exit 2
fi
if [[ ! -f $nginx_conf ]]; then
    echo "找不到 Nginx 配置: $nginx_conf" >&2
    exit 2
fi

install -d -o root -g www-data -m 0750 "$publish_dir"
install -d -o root -g root -m 0755 "$snippet_dir"
install -o root -g www-data -m 0640 "$staged_file" "$publish_dir/$filename.new"
mv -f "$publish_dir/$filename.new" "$publish_dir/$filename"
rm -f "$staged_file"

backup_dir=$(mktemp -d /tmp/sing-box-subscribe-nginx.XXXXXX)
trap 'rm -rf "$backup_dir"' EXIT
cp -a "$nginx_conf" "$backup_dir/main.conf"
if [[ -f $snippet ]]; then
    cp -a "$snippet" "$backup_dir/snippet.conf"
fi

cat >"$snippet.new" <<EOF
# 此文件由 sing-box-subscribe/publish.sh 管理。
location = /v2ray/$filename {
    if (\$request_method !~ ^(GET|HEAD)\$) {
        return 405;
    }

    alias $publish_dir/$filename;
    default_type text/plain;
    charset off;
    add_header Cache-Control "no-store" always;
    add_header X-Content-Type-Options "nosniff" always;
}
EOF
chmod 0644 "$snippet.new"
mv -f "$snippet.new" "$snippet"

if ! grep -Fqx "$include_line" "$nginx_conf"; then
    python3 - "$nginx_conf" "$include_line" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
include_line = sys.argv[2]
text = path.read_text(encoding="utf-8")
closing = text.rfind("\n}")
if closing < 0:
    raise SystemExit(f"无法定位 {path} 中 server 块的结束位置")
updated = text[:closing].rstrip() + "\n\n" + include_line + text[closing:] + "\n"
path.write_text(updated, encoding="utf-8")
PY
fi

if ! nginx -t; then
    cp -a "$backup_dir/main.conf" "$nginx_conf"
    if [[ -f $backup_dir/snippet.conf ]]; then
        cp -a "$backup_dir/snippet.conf" "$snippet"
    else
        rm -f "$snippet"
    fi
    echo "Nginx 校验失败，配置已回滚" >&2
    exit 1
fi

if command -v systemctl >/dev/null 2>&1; then
    systemctl reload nginx
else
    nginx -s reload
fi

echo "远程订阅已发布到 $publish_dir/$filename"
