# ⚡ Quick Start Guide - Webconnex AI Text-to-SQL

Get up and running in **2 minutes**.

## Prerequisites Checklist

- [ ] Docker Desktop installed and running
- [ ] AWS credentials configured (with Okta)
- [ ] Access to AWS Bedrock (Nova Pro + Titan V2)

## 🚀 Launch in 3 Commands

```bash
# 1. Get AWS credentials
export AWS_PROFILE=049101138630-okta-admin-user
gimme-aws-creds --profile 049101138630-okta-admin-user

# 2. Launch the stack
docker compose up -d

# 3. Verify everything works
./verify.sh
```

## 🌐 Access the System

Once running, open your browser:

- **Frontend UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

## ✅ Verification

The `verify.sh` script checks:

```
✅ Docker is running
✅ All containers are healthy (backend, frontend, redis)
✅ API endpoints responding
✅ AWS credentials valid
✅ Bedrock access configured
✅ S3 buckets accessible
```

If all checks pass, you'll see:

```
╔══════════════════════════════════════════════════════════╗
║          ✅ All checks passed! System ready.             ║
╚══════════════════════════════════════════════════════════╝
```

## 🎯 Try Your First Query

1. Open the frontend: http://localhost:8501
2. Type a question: **"How many customers do we have?"**
3. Hit Enter and watch the AI generate SQL + results!

## 📊 Example Queries

Try these to get started:

```
"What's our total revenue this month?"
"Show me the top 10 customers by revenue"
"How many registrations did we have yesterday?"
"What's the average invoice amount?"
"Compare this month's revenue to last month"
```

## 🔧 Common Issues

### Issue: Containers not healthy

```bash
# Check logs
docker compose logs -f backend

# Restart
docker compose restart backend
```

### Issue: AWS credentials expired

```bash
# Refresh credentials
gimme-aws-creds --profile 049101138630-okta-admin-user

# Restart containers
docker compose restart backend frontend
```

### Issue: Port already in use

```bash
# Stop everything
docker compose down

# Start again
docker compose up -d
```

### Issue: "Module not found" errors

```bash
# Rebuild with no cache
docker compose build --no-cache
docker compose up -d
```

## 🛑 Stop the System

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## 📖 Want More Details?

- **Full Documentation**: [README.md](README.md)
- **Docker Guide**: [docs/DOCKER.md](docs/DOCKER.md)
- **Development Guide**: [CLAUDE.md](CLAUDE.md)
- **API Documentation**: http://localhost:8000/docs (when running)

## 🆘 Need Help?

1. Run `./verify.sh` to diagnose issues
2. Check logs: `docker compose logs -f`
3. See full troubleshooting: [README.md#troubleshooting](README.md#troubleshooting)
4. Slack: #text-to-sql-dev

---

**Status**: Production Ready ✅
**Version**: 2.1.0
**Powered by**: Amazon Nova Pro + Titan Embeddings V2
