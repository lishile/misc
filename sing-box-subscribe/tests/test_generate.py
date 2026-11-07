import base64
import unittest
from urllib.parse import parse_qs, urlsplit

from generate import (
    SubscriptionError,
    build_subscription,
    decode_subscription,
    hysteria2_uri,
    select_outbounds,
    vless_uri,
)


class GenerateSubscriptionTests(unittest.TestCase):
    def test_vless_websocket_tls(self) -> None:
        link = vless_uri(
            {
                "type": "vless",
                "tag": "ws-node",
                "server": "edge.example.com",
                "server_port": 443,
                "uuid": "00000000-0000-0000-0000-000000000001",
                "tls": {
                    "enabled": True,
                    "server_name": "origin.example.com",
                    "utls": {"fingerprint": "chrome"},
                },
                "transport": {
                    "type": "ws",
                    "path": "/proxy path",
                    "headers": {"Host": "origin.example.com"},
                },
                "packet_encoding": "xudp",
            }
        )

        parsed = urlsplit(link)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, "vless")
        self.assertEqual(parsed.hostname, "edge.example.com")
        self.assertEqual(parsed.port, 443)
        self.assertEqual(query["security"], ["tls"])
        self.assertEqual(query["type"], ["ws"])
        self.assertEqual(query["host"], ["origin.example.com"])
        self.assertEqual(query["path"], ["/proxy path"])
        self.assertEqual(query["packetEncoding"], ["xudp"])
        self.assertEqual(parsed.fragment, "ws-node")

    def test_vless_reality(self) -> None:
        link = vless_uri(
            {
                "type": "vless",
                "tag": "reality-node",
                "server": "192.0.2.1",
                "server_port": 443,
                "uuid": "00000000-0000-0000-0000-000000000002",
                "flow": "xtls-rprx-vision",
                "tls": {
                    "enabled": True,
                    "server_name": "www.example.com",
                    "utls": {"fingerprint": "chrome"},
                    "reality": {
                        "enabled": True,
                        "public_key": "public-key",
                        "short_id": "abcd",
                    },
                },
            }
        )

        query = parse_qs(urlsplit(link).query)
        self.assertEqual(query["security"], ["reality"])
        self.assertEqual(query["flow"], ["xtls-rprx-vision"])
        self.assertEqual(query["pbk"], ["public-key"])
        self.assertEqual(query["sid"], ["abcd"])
        self.assertEqual(query["type"], ["tcp"])

    def test_hysteria2_port_hopping(self) -> None:
        link = hysteria2_uri(
            {
                "type": "hysteria2",
                "tag": "hy2-node",
                "server": "hy2.example.com",
                "server_ports": ["44123:45123"],
                "password": "password:with symbols",
                "up_mbps": 20,
                "down_mbps": 200,
                "obfs": {"type": "salamander", "password": "obfs password"},
                "tls": {"server_name": "hy2.example.com", "insecure": False},
            }
        )

        parsed = urlsplit(link)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, "hysteria2")
        self.assertEqual(parsed.port, 44123)
        self.assertEqual(query["mport"], ["44123-45123"])
        self.assertEqual(query["obfs"], ["salamander"])
        self.assertEqual(query["obfs-password"], ["obfs password"])
        self.assertEqual(query["insecure"], ["0"])

    def test_hysteria2_port_hopping_after_sing_box_merge(self) -> None:
        link = hysteria2_uri(
            {
                "type": "hysteria2",
                "tag": "merged-hy2-node",
                "server": "hy2.example.com",
                # sing-box merge 会把单元素 server_ports 数组规范化成字符串。
                "server_ports": "44123:45123",
                "password": "password",
                "tls": {"server_name": "hy2.example.com"},
            }
        )

        parsed = urlsplit(link)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.port, 44123)
        self.assertEqual(query["mport"], ["44123-45123"])

    def test_build_filters_placeholder_and_round_trips(self) -> None:
        config = {
            "outbounds": [
                {"type": "direct", "tag": "direct"},
                {
                    "type": "vless",
                    "tag": "empty-for-hold-reality",
                    "server": "placeholder.invalid",
                    "server_port": 443,
                    "uuid": "placeholder",
                },
                {
                    "type": "vless",
                    "tag": "real-node",
                    "server": "example.com",
                    "server_port": 443,
                    "uuid": "00000000-0000-0000-0000-000000000003",
                },
            ]
        }

        selected = select_outbounds(config)
        self.assertEqual([item["tag"] for item in selected], ["real-node"])
        encoded = build_subscription(config, expected_count=1)
        links = decode_subscription(encoded, expected_count=1)
        self.assertEqual(len(links), 1)
        self.assertIn("#real-node", links[0])
        self.assertTrue(base64.b64decode(encoded).decode().endswith("\n"))

    def test_empty_subscription_is_rejected(self) -> None:
        with self.assertRaisesRegex(SubscriptionError, "没有找到可发布"):
            build_subscription({"outbounds": []})

        encoded_empty = base64.b64encode(b"\n").decode()
        with self.assertRaisesRegex(SubscriptionError, "没有节点"):
            decode_subscription(encoded_empty)

    def test_optional_expected_count_is_enforced(self) -> None:
        config = {
            "outbounds": [
                {
                    "type": "vless",
                    "tag": "real-node",
                    "server": "example.com",
                    "server_port": 443,
                    "uuid": "00000000-0000-0000-0000-000000000004",
                }
            ]
        }
        with self.assertRaisesRegex(SubscriptionError, "节点数量不符合预期"):
            build_subscription(config, expected_count=2)


if __name__ == "__main__":
    unittest.main()
