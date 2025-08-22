#!/bin/bash
# Backup script for FeedForward Docker deployment

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="feedforward-app"

echo "🔄 Starting FeedForward backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "⚠️  Warning: Container $CONTAINER_NAME is not running"
    echo "Attempting backup anyway..."
fi

# Backup database
echo "💾 Backing up database..."
docker cp "$CONTAINER_NAME:/app/data/users.db" "$BACKUP_DIR/users_${TIMESTAMP}.db" 2>/dev/null || {
    echo "⚠️  Could not backup database from container"
    if [ -f "./data/users.db" ]; then
        echo "📁 Backing up local database instead..."
        cp "./data/users.db" "$BACKUP_DIR/users_${TIMESTAMP}.db"
    fi
}

# Backup uploads directory
echo "📁 Backing up uploads..."
docker cp "$CONTAINER_NAME:/app/data/uploads" "$BACKUP_DIR/uploads_${TIMESTAMP}" 2>/dev/null || {
    echo "⚠️  Could not backup uploads from container"
    if [ -d "./data/uploads" ]; then
        echo "📁 Backing up local uploads instead..."
        cp -r "./data/uploads" "$BACKUP_DIR/uploads_${TIMESTAMP}"
    fi
}

# Backup environment file (without sensitive data)
echo "📋 Backing up configuration..."
if [ -f ".env" ]; then
    # Create sanitized version without API keys
    grep -v "API_KEY\|PASSWORD\|SECRET" .env > "$BACKUP_DIR/config_${TIMESTAMP}.env" || true
fi

# Create backup manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_DIR/manifest_${TIMESTAMP}.txt" <<EOF
FeedForward Backup Manifest
Generated: $(date)
Database: users_${TIMESTAMP}.db
Uploads: uploads_${TIMESTAMP}/
Config: config_${TIMESTAMP}.env

Container: $CONTAINER_NAME
Docker Image: $(docker inspect --format='{{.Config.Image}}' $CONTAINER_NAME 2>/dev/null || echo "N/A")

Backup Location: $BACKUP_DIR
EOF

# Compress backup
echo "🗜️  Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "feedforward_backup_${TIMESTAMP}.tar.gz" \
    "users_${TIMESTAMP}.db" \
    "uploads_${TIMESTAMP}" \
    "config_${TIMESTAMP}.env" \
    "manifest_${TIMESTAMP}.txt" 2>/dev/null || true

# Clean up uncompressed files
rm -rf "uploads_${TIMESTAMP}"
rm -f "users_${TIMESTAMP}.db" "config_${TIMESTAMP}.env" "manifest_${TIMESTAMP}.txt"

cd - > /dev/null

# Show backup info
BACKUP_SIZE=$(du -h "$BACKUP_DIR/feedforward_backup_${TIMESTAMP}.tar.gz" | cut -f1)
echo ""
echo "✅ Backup completed successfully!"
echo "📦 Backup file: $BACKUP_DIR/feedforward_backup_${TIMESTAMP}.tar.gz"
echo "📏 Size: $BACKUP_SIZE"

# Clean old backups (keep last 7)
echo "🧹 Cleaning old backups (keeping last 7)..."
cd "$BACKUP_DIR"
ls -t feedforward_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
cd - > /dev/null

echo "✨ Backup process complete!"