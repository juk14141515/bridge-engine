# VPS Automation Setup

## Goal
Run Bridge Engine continuously on the VPS even when your laptop is off.

---

# 1. Pull Latest Repo

```bash
cd ~/bridge-engine
git pull
```

---

# 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

---

# 3. Test Main Brain

```bash
python scripts/bridge_brain.py
```

This runs:
- automation runner
- reward loop engine
- context intelligence
- adaptive learning engine
- path effectiveness engine

---

# 4. Install Cron Automation

Open cron:

```bash
crontab -e
```

Add:

```cron
*/30 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/bridge_brain.py >> /home/ubuntu/bridge-engine/data/bridge_brain.log 2>&1
```

Save:
- CTRL + O
- ENTER
- CTRL + X

Verify:

```bash
crontab -l
```

---

# 5. Verify Logs

```bash
cat /home/ubuntu/bridge-engine/data/bridge_brain.log
```

---

# 6. Future Improvements

Later replace cron with:
- systemd workers
- Celery
- Redis queues
- async orchestration

---

# 7. Long-Term Automation Vision

The VPS eventually:
- analyzes user behavior
- scores learning paths
- adapts recommendations
- generates reports
- schedules tasks
- updates reward systems
- learns context patterns
- creates recovery plans
- builds personalized execution paths
- scans resources
- ranks modalities
- orchestrates AI assistants

continuously in the background.
