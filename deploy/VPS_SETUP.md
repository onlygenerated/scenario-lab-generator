# Labwright VPS Deployment — Step-by-Step

Goal: get Labwright running at **https://labwright.com** on your Hostinger VPS, gated by a username/password, so you can share the link with a friend.

This guide assumes you're new to the command line. Every step has:
- **Do this** — the exact commands to copy/paste
- **You should see** — how to know it worked
- **If stuck** — what to try

Work through it top to bottom. Each phase takes ~5–15 minutes.

---

## Before you begin — what to gather

- [ ] **VPS IP address** — find it in Hostinger hPanel → your VPS → Overview (labeled "IPv4 Address")
- [ ] **VPS root password** — you set this when you created the VPS (resettable in hPanel)
- [ ] **Anthropic API key** — get one at https://console.anthropic.com/settings/keys
- [ ] **A terminal on your Windows machine** — press `Win+X`, pick **Terminal** or **PowerShell**. Either works.

---

## Phase 1 — Point labwright.com at your VPS (DNS)

You do this in the Hostinger web panel. No SSH yet.

**Do this:**
1. Log into https://hpanel.hostinger.com
2. Go to **Domains** → click **labwright.com**. Leave the nameservers alone — Hostinger's normal nameservers are `ns1.dns-parking.com` / `ns2.dns-parking.com` (that naming is confusing but correct).
3. **If the domain is parked as a website,** delete the website first. In hPanel → **Websites** → find `labwright.com` → **Manage** → "Delete website" or "Remove hosting." This clears the CDN binding that otherwise blocks A records with `Cannot add A/AAAA record when CDN is enabled`. (Only delete the **website**, not the **domain** — the domain stays registered.)
4. Open **DNS / Nameservers** → delete any existing A records at `@` and `www`
5. Add a new **A record**:
   - Type: `A`
   - Name: `@`
   - Points to: `<your-VPS-IP>`
   - TTL: `300`
6. Add another **A record**:
   - Name: `www`
   - Points to: `<your-VPS-IP>`
   - TTL: `300`
7. Add a **wildcard A record** (needed for lab subdomains like `lab-8923.labwright.com`):
   - Name: `*`
   - Points to: `<your-VPS-IP>`
   - TTL: `300`

**You should see:** Three A records listed (`@`, `www`, `*`), all pointing to your VPS IP.

**Then wait ~5 minutes**, and verify at https://dnschecker.org — type `labwright.com`, pick type A. Your VPS IP should show up in most locations. If half the map is still showing old IPs, wait another 5 min.

---

## Phase 2 — Connect to your VPS

**Do this** (open PowerShell/Terminal, replace the IP):

```
ssh root@<your-VPS-IP>
```

First time only: it asks "Are you sure you want to continue connecting?" — type `yes` and Enter.

Then paste your root password (right-click to paste; the cursor won't move, that's normal — passwords are hidden).

**You should see:** A prompt that looks like `root@srv-xxxxx:~#`. You're now on the server.

**If stuck:** Double-check the IP. If you see "Connection refused," the VPS isn't running — check Hostinger hPanel.

---

## Phase 3 — Create a regular user (don't stay as root)

Running as root is dangerous. We'll make a regular user.

**Do this** (replace `phil` with whatever you want):

```
adduser phil
```

Enter a password twice. For the "Full Name" etc. prompts, just press Enter to skip.

Give that user admin powers:

```
usermod -aG sudo phil
```

Also add them to the docker group now so it's ready later:

```
usermod -aG docker phil 2>/dev/null || true
```

(That line may say "docker: group does not exist" — ignore; we'll create it in Phase 5.)

Switch to the new user:

```
su - phil
```

**You should see:** Prompt changes to `phil@srv-xxxxx:~$` — the `$` means you're no longer root.

From here on, **when you need admin rights, prefix the command with `sudo`**. It'll ask for your password the first time, then remember for a few minutes.

---

## Phase 4 — Firewall

Only let through SSH and web traffic. Labs are reached via Caddy on port 443, not directly on their Jupyter ports, so the 8888–8988 range does **not** need to be open to the public internet.

**Do this:**

```
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

**You should see:** `Firewall is active and enabled on system startup.`

**Check it:** `sudo ufw status` — should list ALLOW rules for 22 (SSH), 80, and 443.

---

## Phase 5 — Install Docker

Docker runs the backend and each lab.

**Do this:**

```
curl -fsSL https://get.docker.com | sudo sh
```

Takes 1–2 minutes of scrolling output.

Add yourself to the docker group (so you don't need `sudo` for docker commands):

```
sudo usermod -aG docker $USER
```

**Important:** Log out and back in for the group to take effect.

```
exit
exit
```

Then reconnect:

```
ssh phil@<your-VPS-IP>
```

**Test it:**

```
docker run hello-world
```

**You should see:** A "Hello from Docker!" message. That proves Docker is working and you don't need `sudo` for it.

---

## Phase 6 — Install Node.js (for the frontend build)

**Do this:**

```
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs
```

**Verify:**

```
node --version
npm --version
```

Both should print a version number (node ~20.x, npm ~10.x).

---

## Phase 7 — Get the code

**Do this:**

```
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www
cd /var/www
git clone https://github.com/onlygenerated/scenario-lab-generator.git labwright
cd labwright
```

**You should see:** `ls` shows `backend/`, `frontend/`, `templates/`, `docker-compose.yml`, and a `deploy/` directory with this file.

**If the repo is private** and it asks for credentials: use your GitHub username and a Personal Access Token (not your password). Create a token at https://github.com/settings/tokens with "repo" scope.

---

## Phase 8 — Create the `.env` file

**Do this:**

```
nano .env
```

Paste this (right-click in PowerShell to paste), replacing the API key with your real one:

```
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
DEMO_MODE=true
CORS_ORIGINS=["https://labwright.com"]
LAB_URL_TEMPLATE=https://lab-{port}.labwright.com/lab/tree/1_INSTRUCTIONS.md?token=labtoken
LAB_BASE_DIR=/var/www/labwright/lab_workspaces
```

`LAB_URL_TEMPLATE` is the full URL pattern handed to the browser for each launched lab. `{port}` gets substituted with the Jupyter container's host port. Caddy fronts these subdomains with Let's Encrypt TLS on demand (see Phase 11 Caddyfile).

Save: press `Ctrl+O`, then Enter, then `Ctrl+X`.

**Why `DEMO_MODE=true`?** It uses a pre-made sample blueprint instead of calling Claude. Lets you validate the deploy without burning API credits. Flip to `false` once everything works.

---

## Phase 9 — Pre-build the Jupyter image

This is a one-time step. Each lab reuses this pre-built image, so launches drop from ~60 seconds to a few.

**Do this:**

```
docker build -t labwright-jupyter:base templates/jupyter/
```

Takes 2–3 minutes. Lots of pip install output.

**You should see:** `Successfully tagged labwright-jupyter:base` near the end.

---

## Phase 10 — Build the frontend

**Do this:**

```
cd frontend
npm ci
npm run build
cd ..
```

`npm ci` installs dependencies (~1 min); `npm run build` produces the production files.

**You should see:** A new `frontend/dist/` directory with `index.html` and an `assets/` folder.

---

## Phase 11 — Install Caddy

Caddy is the web server — it handles HTTPS automatically, serves the frontend, and proxies API calls to the backend.

**Do this:**

```
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

**Verify:** `caddy version` should print a version number.

---

## Phase 12 — Configure Caddy

First, generate a bcrypt hash of the password you want your friend to use.

**Do this:**

```
caddy hash-password
```

It prompts for your password twice. Copy the output — it starts with `$2a$14$...`. That's the hash.

Now install the Caddyfile that ships with the repo:

```
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile
```

In the file, find `REPLACE_WITH_BCRYPT_HASH` and paste your hash in its place. The username is `demo` — change it in the file if you want something different.

Save: `Ctrl+O`, Enter, `Ctrl+X`.

Start Caddy:

```
sudo systemctl reload caddy
```

**Check Caddy is healthy:**

```
sudo systemctl status caddy
```

It should say `active (running)`. Press `q` to exit the status view.

**Test in your browser:** Open **https://labwright.com**.

**You should see:**
- Your browser prompts for a username and password (from Caddy's basic auth)
- Enter `demo` and the password you chose
- You see the Labwright SPA load (empty, because the backend isn't running yet — Phase 13)

**If the site doesn't load:**
- DNS may still be propagating — wait 5 more minutes, try again
- Check Caddy logs: `sudo journalctl -u caddy -n 50`
- The very first load takes 10–30 seconds while Caddy fetches a TLS cert from Let's Encrypt

---

## Phase 13 — Start the backend

**Do this:**

```
cd /var/www/labwright
docker compose up -d backend
```

We only start `backend` (not `frontend`) because Caddy is already serving the built frontend from `frontend/dist/`.

Wait ~15 seconds, then check:

```
docker compose ps
curl http://localhost:8000/health
```

**You should see:**
- `backend` listed with STATE `running`
- `/health` returns something like `{"status":"ok"}`

**Reload https://labwright.com in your browser** — the SPA should now be fully functional. You can:
- Click through to generate a blueprint (demo mode serves the sample)
- Launch a lab — wait ~15 seconds for containers to come up
- Click the Jupyter link that appears

**If "Launch Lab" shows an error:** Check backend logs with `docker compose logs -f backend` (Ctrl+C to exit).

---

## Phase 14 — Give it to your friend

Share:
- **URL:** https://labwright.com
- **Username:** `demo`
- **Password:** the one you chose in Phase 12

Tell them: "You'll see a browser login prompt first. After you log in, click 'Generate' then 'Launch Lab' — it takes ~15 seconds to spin up."

---

## Phase 15 — Going off demo mode

Once you've confirmed everything works:

```
cd /var/www/labwright
nano .env
```

Change `DEMO_MODE=true` to `DEMO_MODE=false`. Save.

```
docker compose restart backend
```

Now blueprint generation will call Claude for real. Monitor your spend at https://console.anthropic.com and set a budget limit there as a safety net.

---

## Ongoing maintenance

### Update to a newer version of Labwright

```
cd /var/www/labwright
git pull
cd frontend && npm ci && npm run build && cd ..
docker compose up -d --build backend
```

### See what's running

```
docker compose ps        # backend
docker ps                # backend + all running labs
```

### Clean up old Docker images (monthly is fine)

```
docker system prune -f
```

### View logs live

- Backend: `docker compose logs -f backend`
- Caddy: `sudo journalctl -u caddy -f`
- Exit log view with `Ctrl+C`

### If the VPS reboots

Everything comes back automatically (thanks to `restart: unless-stopped` on containers and Caddy being a systemd service). But if something doesn't:

```
cd /var/www/labwright && docker compose up -d backend
sudo systemctl start caddy
```

---

## Troubleshooting quick-reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Browser can't reach labwright.com | DNS not propagated yet | Wait 10 min; re-check dnschecker.org |
| "Your connection is not private" | Caddy still getting TLS cert | Wait 30s after first reload, refresh |
| Site loads but shows browser login loop | Wrong bcrypt hash in Caddyfile | Re-run `caddy hash-password`, re-paste, `sudo systemctl reload caddy` |
| `docker compose ps` shows backend restarting | Usually `.env` error | `docker compose logs backend` to see the error |
| "Launch Lab" button spins forever | Out of memory, or Jupyter image missing | `docker stats` to check; re-run Phase 9 if `labwright-jupyter:base` isn't listed in `docker image ls` |
| Lab URL shows `localhost` | `LAB_URL_TEMPLATE` not set in `.env` | Add the line, `docker compose up -d --force-recreate backend` |
| First click on a fresh lab is slow (1–3s) | Caddy fetching Let's Encrypt cert on demand | Expected; subsequent loads on that port are fast (cert cached 90 days) |
| Lab tab shows "Your connection is not private" | Caddy's `ask` endpoint rejected the cert request — check backend is up and reachable at `http://localhost:8000/api/internal/cert-ok?domain=lab-8900.labwright.com` (should return 200) | `curl` the URL locally on the VPS; fix backend if it errors |
| Everything broken after `apt upgrade` | Docker or Caddy got replaced | `sudo systemctl restart docker caddy` |

---

## What's running where (so you can visualize it)

```
Browser
   │  https://labwright.com
   ▼
Caddy (port 443)  ──► serves frontend/dist/ (SPA)
   │
   ├─ /api/*   ──► localhost:8000  (FastAPI backend, in Docker)
   └─ /health  ──► localhost:8000

Backend (port 8000)
   │  talks to /var/run/docker.sock
   ▼
Lab containers (each a compose project):
   lab-abc123-jupyter     (port 8912 on host)
   lab-abc123-source-db   (internal only)
   lab-abc123-target-db   (internal only)
```

Browser reaches the lab via `https://labwright.com:<port>/?token=labtoken` (Phase 8's `LAB_URL_BASE` controls that URL). Lab ports are in 8888–8988, exposed by the firewall in Phase 4.
