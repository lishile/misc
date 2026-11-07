#!/usr/bin/env python3
"""将 sing-box 出站配置转换为 v2rayN/Shadowrocket Base64 订阅。"""

from __future__ import annotations

import argparse
import base64
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, urlencode, urlsplit

SUPPORTED_TYPES = {"vless", "hysteria2"}
EXCLUDED_TAGS = {"empty-for-hold-reality"}


class SubscriptionError(ValueError):
    """订阅配置或输出不符合预期。"""


def _require(mapping: dict[str, Any], key: str, tag: str) -> Any:
    value = mapping.get(key)
    if value is None or value == "":
        raise SubscriptionError(f"节点 {tag!r} 缺少字段 {key!r}")
    return value


def _host_for_uri(server: str) -> str:
    return f"[{server}]" if ":" in server and not server.startswith("[") else server


def _query(items: Iterable[tuple[str, Any]]) -> str:
    normalized = [(key, str(value)) for key, value in items if value is not None and value != ""]
    return urlencode(normalized, doseq=True, quote_via=quote, safe="")


def vless_uri(outbound: dict[str, Any]) -> str:
    tag = str(_require(outbound, "tag", "<unknown>"))
    server = _host_for_uri(str(_require(outbound, "server", tag)))
    port = int(_require(outbound, "server_port", tag))
    uuid = quote(str(_require(outbound, "uuid", tag)), safe="")
    tls = outbound.get("tls") or {}
    transport = outbound.get("transport") or {}
    reality = tls.get("reality") or {}
    utls = tls.get("utls") or {}

    query: list[tuple[str, Any]] = [("encryption", "none")]
    flow = outbound.get("flow")
    if flow:
        query.append(("flow", flow))

    if reality.get("enabled"):
        query.extend(
            [
                ("security", "reality"),
                ("sni", tls.get("server_name")),
                ("fp", utls.get("fingerprint")),
                ("pbk", _require(reality, "public_key", tag)),
                ("sid", reality.get("short_id")),
            ]
        )
    elif tls.get("enabled"):
        query.extend(
            [
                ("security", "tls"),
                ("sni", tls.get("server_name")),
                ("fp", utls.get("fingerprint")),
            ]
        )
    else:
        query.append(("security", "none"))

    transport_type = transport.get("type", "tcp")
    query.append(("type", transport_type))
    if transport_type == "ws":
        headers = transport.get("headers") or {}
        query.extend(
            [
                ("host", headers.get("Host") or headers.get("host")),
                ("path", transport.get("path", "/")),
            ]
        )

    if outbound.get("packet_encoding"):
        query.append(("packetEncoding", outbound["packet_encoding"]))

    return f"vless://{uuid}@{server}:{port}?{_query(query)}#{quote(tag, safe='')}"


def _hysteria_ports(outbound: dict[str, Any], tag: str) -> tuple[int, str | None]:
    raw_ports = outbound.get("server_ports")
    if raw_ports:
        # 原始分片通常是数组；sing-box merge 会把单元素数组规范化成字符串。
        if isinstance(raw_ports, (str, int)):
            port_specs = [str(raw_ports).strip()]
        elif isinstance(raw_ports, list):
            port_specs = [str(item).strip() for item in raw_ports if str(item).strip()]
        else:
            raise SubscriptionError(
                f"节点 {tag!r} 的 server_ports 类型无效: {type(raw_ports).__name__}"
            )
        if not port_specs or not port_specs[0]:
            raise SubscriptionError(f"节点 {tag!r} 的 server_ports 为空")
        first = port_specs[0].replace("-", ":").split(":", 1)[0]
        try:
            primary_port = int(first)
        except ValueError as exc:
            raise SubscriptionError(f"节点 {tag!r} 的端口格式无效: {port_specs[0]!r}") from exc
        # 分享链接常用 mport 的连字符表示范围；主端口供忽略 mport 的客户端使用。
        mport = ",".join(spec.replace(":", "-") for spec in port_specs)
        return primary_port, mport

    return int(_require(outbound, "server_port", tag)), None


def hysteria2_uri(outbound: dict[str, Any]) -> str:
    tag = str(_require(outbound, "tag", "<unknown>"))
    server = _host_for_uri(str(_require(outbound, "server", tag)))
    port, mport = _hysteria_ports(outbound, tag)
    password = quote(str(_require(outbound, "password", tag)), safe="")
    tls = outbound.get("tls") or {}
    obfs = outbound.get("obfs") or {}

    query: list[tuple[str, Any]] = [
        ("sni", None if tls.get("disable_sni") else tls.get("server_name")),
        ("insecure", "1" if tls.get("insecure") else "0"),
        ("mport", mport),
        ("obfs", obfs.get("type")),
        ("obfs-password", obfs.get("password")),
        ("upmbps", outbound.get("up_mbps")),
        ("downmbps", outbound.get("down_mbps")),
    ]

    return f"hysteria2://{password}@{server}:{port}?{_query(query)}#{quote(tag, safe='')}"


def outbound_uri(outbound: dict[str, Any]) -> str:
    outbound_type = outbound.get("type")
    if outbound_type == "vless":
        return vless_uri(outbound)
    if outbound_type == "hysteria2":
        return hysteria2_uri(outbound)
    raise SubscriptionError(f"不支持的出站类型: {outbound_type!r}")


def select_outbounds(config: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_tags: set[str] = set()
    for outbound in config.get("outbounds", []):
        tag = outbound.get("tag")
        if outbound.get("type") not in SUPPORTED_TYPES or tag in EXCLUDED_TAGS:
            continue
        if not tag:
            raise SubscriptionError("存在缺少 tag 的代理节点")
        if tag in seen_tags:
            raise SubscriptionError(f"节点 tag 重复: {tag!r}")
        seen_tags.add(tag)
        selected.append(outbound)
    return selected


def build_subscription(config: dict[str, Any], expected_count: int | None = None) -> str:
    outbounds = select_outbounds(config)
    if not outbounds:
        raise SubscriptionError("没有找到可发布的 VLESS 或 Hysteria2 节点")
    if expected_count is not None and len(outbounds) != expected_count:
        raise SubscriptionError(
            f"节点数量不符合预期: 实际 {len(outbounds)}，预期 {expected_count}"
        )
    payload = "\n".join(outbound_uri(outbound) for outbound in outbounds) + "\n"
    return base64.b64encode(payload.encode("utf-8")).decode("ascii") + "\n"


def decode_subscription(encoded: str, expected_count: int | None = None) -> list[str]:
    compact = "".join(encoded.split())
    try:
        decoded = base64.b64decode(compact, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise SubscriptionError("订阅不是有效的 UTF-8 Base64 内容") from exc

    links = [line.strip() for line in decoded.splitlines() if line.strip()]
    if not links:
        raise SubscriptionError("订阅中没有节点")
    if expected_count is not None and len(links) != expected_count:
        raise SubscriptionError(
            f"订阅节点数量不符合预期: 实际 {len(links)}，预期 {expected_count}"
        )

    seen_names: set[str] = set()
    for link in links:
        parsed = urlsplit(link)
        if parsed.scheme not in {"vless", "hysteria2"}:
            raise SubscriptionError(f"订阅包含不支持的链接: {link[:40]!r}")
        name = parsed.fragment
        if not name:
            raise SubscriptionError("订阅链接缺少节点名称")
        if name in seen_names:
            raise SubscriptionError(f"订阅节点名称重复: {name!r}")
        seen_names.add(name)
    return links


def _read_text(path: str) -> str:
    if path == "-":
        return os.sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary_path = Path(handle.name)
    temporary_path.replace(path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="生成 Base64 订阅")
    generate.add_argument("--input", default="-", help="合并后的 sing-box JSON，- 表示 stdin")
    generate.add_argument("--output", required=True, help="订阅输出文件")
    generate.add_argument(
        "--expected-count", type=int, help="可选：要求节点数严格等于此值"
    )

    verify = subparsers.add_parser("verify", help="验证 Base64 订阅")
    verify.add_argument("--input", required=True, help="订阅文件，- 表示 stdin")
    verify.add_argument(
        "--expected-count", type=int, help="可选：要求节点数严格等于此值"
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "generate":
            config = json.loads(_read_text(args.input))
            encoded = build_subscription(config, args.expected_count)
            _write_atomic(Path(args.output), encoded)
            links = decode_subscription(encoded, args.expected_count)
            print(f"已生成 {len(links)} 个节点: {args.output}")
        else:
            links = decode_subscription(_read_text(args.input), args.expected_count)
            print(f"订阅验证通过，共 {len(links)} 个节点")
    except (OSError, json.JSONDecodeError, SubscriptionError) as exc:
        print(f"错误: {exc}", file=os.sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
