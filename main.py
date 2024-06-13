import json
import subprocess

CONFIG_FILE = 'config.json'
REDSOCKS_CONFIG_FILE = '/etc/redsocks.conf'
IPTABLES_CHAIN = 'REDSOCKS'


def pad_with_zero(num):
    return str(num).zfill(2)


def generate_redsocks_config(config):
    lines = [
        "base {\n",
        "\tlog_debug = off;\n",
        "\tlog_info = on;\n",
        "\tlog = \"stderr\";\n",
        "\tdaemon = on;\n",
        "\tredirector = iptables;\n",
        "}\n"
    ]

    for idx, entry in enumerate(config):
        proxy = entry['proxy']
        ip, port = proxy.split('://')[1].split(':')
        lines.append(f"redsocks {{\n")
        lines.append(f"\ttype = socks5;\n")
        lines.append(f"\tip = {ip};\n")
        lines.append(f"\tport = {port};\n")
        lines.append(f"\tlocal_ip = 127.0.0.1;\n")
        lines.append(f"\tlocal_port = 123{pad_with_zero(idx)};\n")
        lines.append(f"}}\n")

    with open(REDSOCKS_CONFIG_FILE, 'w') as f:
        f.writelines(lines)


def setup_iptables(config):
    # Flush and delete custom chain if it exists
    subprocess.run(['iptables', '-t', 'nat', '-F', IPTABLES_CHAIN])
    subprocess.run(['iptables', '-t', 'nat', '-X', IPTABLES_CHAIN])

    # Create a new chain
    subprocess.run(['iptables', '-t', 'nat', '-N', IPTABLES_CHAIN])

    for idx, entry in enumerate(config):
        local_port = f"123{pad_with_zero(idx)}"
        for target in entry['targets']:
            target_ip = target.split(':')[0]
            target_port = target.split(':')[1] if ':' in target else None
            if target_port:
                subprocess.run(
                    ['iptables', '-t', 'nat', '-A', IPTABLES_CHAIN, '-p', 'tcp', '--dport', target_port, '-d',
                     target_ip, '-j', 'REDIRECT', '--to-ports', local_port])
            else:
                subprocess.run(
                    ['iptables', '-t', 'nat', '-A', IPTABLES_CHAIN, '-d', target_ip, '-p', 'tcp', '-j', 'REDIRECT', '--to-ports',
                     local_port])

    # Redirect OUTPUT chain to our custom chain
    subprocess.run(['iptables', '-t', 'nat', '-A', 'OUTPUT', '-j', IPTABLES_CHAIN])


def cleanup_iptables():
    # Flush and delete custom chain
    subprocess.run(['iptables', '-t', 'nat', '-F', IPTABLES_CHAIN])
    subprocess.run(['iptables', '-t', 'nat', '-X', IPTABLES_CHAIN])
    # Remove redirection from OUTPUT chain
    subprocess.run(['iptables', '-t', 'nat', '-D', 'OUTPUT', '-j', IPTABLES_CHAIN])


def main(action):
    if action == 'start':
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        generate_redsocks_config(config)
        setup_iptables(config)
        # Restart redsocks to apply the new configuration
        subprocess.run(['systemctl', 'restart', 'redsocks'])
    elif action == 'stop':
        cleanup_iptables()
        # Stop redsocks service
        subprocess.run(['systemctl', 'stop', 'redsocks'])


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in ['start', 'stop']:
        print("Usage: python3 script.py [start|stop]")
        sys.exit(1)
    main(sys.argv[1])
