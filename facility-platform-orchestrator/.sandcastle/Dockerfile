FROM node:22-bookworm

# System dependencies
RUN apt-get update && apt-get install -y \
  git \
  curl \
  jq \
  && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && apt-get update && apt-get install -y gh \
  && rm -rf /var/lib/apt/lists/*

# Codex CLI
RUN npm install -g @openai/codex

# Rename node user to agent (keeps UID 1000 so mounts align)
RUN usermod -d /home/agent -m -l agent node
RUN chown -R 1000:1000 /home/agent
RUN rm -f /home/agent/.gitconfig /home/agent/.gitconfig.lock
RUN chmod 1777 /home/agent
USER agent

WORKDIR /home/agent

# Sandcastle bind-mounts the git worktree at /home/agent/workspace
# and overrides the working directory to /home/agent/workspace at container start.
ENTRYPOINT ["sleep", "infinity"]
