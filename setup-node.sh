#!/bin/bash

# Install deps
sudo apt-get -qq update
sudo apt-get -q install -y iperf3 protobuf-compiler sshpass nload

# Configure zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
sudo -k chsh -s "$(which zsh)" "${USER}"

# Install Rust
curl https://sh.rustup.rs -sSf | sh -s -- -y

# Install zsh plugins
curl --proto '=https' -fLsS https://rossmacarthur.github.io/install/crate.sh |
    bash -s -- --repo rossmacarthur/sheldon --to ~/.cargo/bin
mkdir -p ~/.config/sheldon
cat <<EOF >~/.config/sheldon/plugins.toml
shell = "zsh"

[plugins.zsh-autosuggestions]
github = "zsh-users/zsh-autosuggestions"

[plugins.zsh-syntax-highlighting]
github = "zsh-users/zsh-syntax-highlighting"

[plugins.zsh-vi-mode]
github = "jeffreytse/zsh-vi-mode"
EOF

echo "eval '$(~/.cargo/bin/sheldon source)'" >>~/.zshrc
echo "ZVM_VI_INSERT_ESCAPE_BINDKEY=jk" >>~/.zshrc

# Configure to allow large numbers of connections
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535"

exit 0
