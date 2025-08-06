# Troubleshooting Guide - Userbot

## Masalah Umum dan Solusi

### 1. Userbot Tidak Jalan / Tidak Ada Log

#### Kemungkinan Penyebab:
- Session file corrupt atau tidak valid
- API credentials salah
- Docker container crash saat startup
- Tidak ada akses ke target group

#### Solusi:

**A. Cek Status Container:**
```bash
# Lihat semua container
docker ps -a

# Lihat logs container
docker logs pencepu

# Lihat logs real-time
docker logs -f pencepu
```

**B. Test Koneksi Lokal:**
```bash
# Jalankan test script
python test_userbot.py

# Atau dengan environment variables
API_ID=your_api_id API_HASH=your_api_hash python test_userbot.py
```

**C. Rebuild Container:**
```bash
# Stop dan remove container lama
docker-compose down

# Rebuild image
docker-compose build --no-cache

# Start ulang
docker-compose up -d

# Monitor logs
docker-compose logs -f
```

### 2. Session File Issues

#### Gejala:
- Error "Session file is corrupted"
- Diminta login terus menerus
- API errors saat startup

#### Solusi:
```bash
# Backup session lama
cp userbot.session userbot.session.backup

# Hapus session dan login ulang
rm userbot.session

# Jalankan userbot untuk login ulang
python Main.py
```

### 3. Docker Logs Tidak Muncul

#### Penyebab:
- Volume mapping tidak benar
- Container crash sebelum menulis log
- Logging configuration salah

#### Solusi:
```bash
# Pastikan directory logs ada
mkdir -p logs

# Check volume mapping
docker inspect pencepu | grep -A 10 "Mounts"

# Lihat logs langsung dari Docker
docker logs pencepu --details --timestamps

# Check container status
docker inspect pencepu | grep -A 5 "State"
```

### 4. Permission Issues

#### Gejala:
- "Permission denied" errors
- Cannot write to log files
- Session file cannot be created

#### Solusi:
```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod 644 userbot.session
chmod 755 logs/

# Atau run container sebagai current user
docker-compose run --user $(id -u):$(id -g) pencepu
```

### 5. Network/Connection Issues

#### Gejala:
- "Connection timeout"
- "Cannot reach Telegram servers"
- API errors

#### Solusi:
```bash
# Test koneksi internet
ping telegram.org

# Check DNS
nslookup api.telegram.org

# Test dengan proxy jika perlu
export HTTP_PROXY=your_proxy
export HTTPS_PROXY=your_proxy
```

## Debug Commands

### Useful Docker Commands:
```bash
# Enter running container
docker exec -it pencepu bash

# Run container interactively
docker run -it --rm userbot-image python Main.py

# Check container resource usage
docker stats pencepu

# View container configuration
docker inspect pencepu
```

### Environment Variables:
```bash
# Create .env file dari .env.example
cp .env.example .env

# Edit dengan credentials yang benar
nano .env

# Load environment variables
source .env
```

### Log Analysis:
```bash
# Search for specific errors
docker logs pencepu 2>&1 | grep -i error

# Check last 100 lines
docker logs --tail 100 pencepu

# Follow logs with timestamps
docker logs -f -t pencepu
```

## Konfigurasi Optimal

### Docker Compose untuk Production:
```yaml
services:
  pencepu:
    build: .
    container_name: pencepu
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - ./userbot.session:/app/userbot.session:ro
    environment:
      - TZ=Asia/Jakarta
      - API_ID=${API_ID}
      - API_HASH=${API_HASH}
      - TARGET_GROUP=${TARGET_GROUP}
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Monitoring Script:
```bash
#!/bin/bash
# monitor.sh - Check userbot health

while true; do
    if ! docker ps | grep -q pencepu; then
        echo "$(date): Container pencepu is not running!"
        docker-compose up -d
    fi
    
    # Check if logs are being written
    if [ ! -f logs/userbot.log ]; then
        echo "$(date): No log file found!"
    else
        last_log=$(tail -1 logs/userbot.log | cut -d' ' -f1-2)
        current_time=$(date "+%Y-%m-%d %H:%M")
        # Add your monitoring logic here
    fi
    
    sleep 60
done
```

## Kontak untuk Bantuan

Jika masih ada masalah setelah mengikuti guide ini:

1. **Collect logs:**
   ```bash
   # Kumpulkan semua info debug
   docker logs pencepu > userbot_debug.log 2>&1
   docker inspect pencepu > container_info.json
   ```

2. **Check system resources:**
   ```bash
   df -h  # Disk space
   free -m  # Memory
   docker system df  # Docker space usage
   ```

3. **Provide information:**
   - OS version
   - Docker version
   - Error messages
   - Steps to reproduce
   - Log files