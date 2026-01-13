set -euo pipefail

echo "=== Ubuntu Server Baseline (Lenovo) ==="

# --- Preconditions ---
if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo -i" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

# --- Timezone / time sync ---
timedatectl set-timezone Europe/Berlin
systemctl enable --now systemd-timesyncd >/dev/null 2>&1 || true

# --- Update system ---
apt-get update -y
apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg lsb-release ufw fail2ban unattended-upgrades jq

# --- User to grant docker access and SSH hardening ---
read -r -p "Enter your existing admin username (created during install): " ADMIN_USER
if ! id "$ADMIN_USER" >/dev/null 2>&1; then
  echo "User does not exist: $ADMIN_USER" >&2
  exit 1
fi

# --- SSH key-based auth setup ---
echo "Paste your SSH PUBLIC KEY (single line). It will be installed for $ADMIN_USER:"
read -r SSH_PUBKEY
install -d -m 0700 -o "$ADMIN_USER" -g "$ADMIN_USER" "/home/$ADMIN_USER/.ssh"
touch "/home/$ADMIN_USER/.ssh/authorized_keys"
chmod 0600 "/home/$ADMIN_USER/.ssh/authorized_keys"
chown "$ADMIN_USER:$ADMIN_USER" "/home/$ADMIN_USER/.ssh/authorized_keys"
grep -qxF "$SSH_PUBKEY" "/home/$ADMIN_USER/.ssh/authorized_keys" || echo "$SSH_PUBKEY" >> "/home/$ADMIN_USER/.ssh/authorized_keys"

# --- Harden SSH (no password login, no root login) ---
SSHD_CFG="/etc/ssh/sshd_config"
cp -a "$SSHD_CFG" "${SSHD_CFG}.bak.$(date +%Y%m%d%H%M%S)"

# Ensure settings exist and are enforced
sed -i 's/^\s*#\?\s*PasswordAuthentication\s\+.*/PasswordAuthentication no/g' "$SSHD_CFG"
grep -q '^PasswordAuthentication ' "$SSHD_CFG" || echo 'PasswordAuthentication no' >> "$SSHD_CFG"

sed -i 's/^\s*#\?\s*PermitRootLogin\s\+.*/PermitRootLogin no/g' "$SSHD_CFG"
grep -q '^PermitRootLogin ' "$SSHD_CFG" || echo 'PermitRootLogin no' >> "$SSHD_CFG"

sed -i 's/^\s*#\?\s*PubkeyAuthentication\s\+.*/PubkeyAuthentication yes/g' "$SSHD_CFG"
grep -q '^PubkeyAuthentication ' "$SSHD_CFG" || echo 'PubkeyAuthentication yes' >> "$SSHD_CFG"

systemctl restart ssh

# --- Firewall (UFW) ---
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw --force enable

# --- Fail2ban for SSH ---
cat >/etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
mode = aggressive
port = ssh
logpath = %(sshd_log)s
maxretry = 5
findtime = 10m
bantime  = 1h
EOF
systemctl enable --now fail2ban

# --- Unattended upgrades (security) ---
dpkg-reconfigure -f noninteractive unattended-upgrades || true
systemctl enable --now unattended-upgrades || true

# --- Static IP (Netplan) ---
echo "=== Network: Static IP via Netplan ==="
echo "If you prefer DHCP reservation in your router, answer 'no' to skip and do that instead."
read -r -p "Configure static IP now? (yes/no): " DO_STATIC
if [[ "${DO_STATIC,,}" == "yes" ]]; then
  echo "Available interfaces:"
  ip -br link | awk '{print " - "$1" ("$2")"}'
  read -r -p "Enter interface name to configure (exact, e.g. eno1/wlp2s0): " IFACE
  read -r -p "Enter static IP with CIDR (e.g. 192.168.1.50/24): " IP_CIDR
  read -r -p "Enter default gateway IP: " GW
  read -r -p "Enter DNS servers comma-separated (e.g. 1.1.1.1,8.8.8.8): " DNSCSV
  DNS1="$(echo "$DNSCSV" | cut -d, -f1 | xargs)"
  DNS2="$(echo "$DNSCSV" | cut -d, -f2 | xargs)"

  NETPLAN_FILE="/etc/netplan/01-lenovo-server.yaml"
  cat >"$NETPLAN_FILE" <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    ${IFACE}:
      dhcp4: false
      addresses: [${IP_CIDR}]
      routes:
        - to: default
          via: ${GW}
      nameservers:
        addresses: [${DNS1},${DNS2}]
EOF

  netplan generate
  netplan apply
fi

# --- Docker Engine + Compose plugin (official repo) ---
echo "=== Installing Docker Engine + Compose plugin ==="
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

ARCH="$(dpkg --print-architecture)"
CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" >/etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker
usermod -aG docker "$ADMIN_USER"

# --- Server directories ---
install -d -m 0750 -o root -g root /srv
install -d -m 0750 -o root -g root /srv/stacks
install -d -m 0750 -o root -g root /srv/data
install -d -m 0750 -o root -g root /srv/backups

echo
echo "=== DONE ==="
echo "1) IMPORTANT: open a NEW SSH session now and confirm key login works."
echo "2) Then you may logout and rely on SSH key auth only."
echo "3) Docker installed. Your user must re-login for docker group to apply."
