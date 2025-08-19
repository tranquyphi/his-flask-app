#!/bin/bash
# Service management script for HIS application
# Usage: ./service_manager.sh [flask|fastapi|status]

case "$1" in
    flask)
        echo "Switching to Flask mode..."
        sudo systemctl stop hisFastAPI.service 2>/dev/null || true
        sudo systemctl start his.service
        echo "Flask service started on 127.0.0.1:8000"
        ;;
    fastapi)
        echo "Switching to FastAPI mode..." 
        sudo systemctl stop his.service 2>/dev/null || true
        # Create FastAPI systemd service if it doesn't exist
        if [ ! -f /etc/systemd/system/hisFastAPI.service ]; then
            echo "Creating FastAPI service..."
            cat > /tmp/hisFastAPI.service << 'EOF'
[Unit]
Description=FastAPI HIS application
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/his
Environment=PATH=/root/his/venv/bin
ExecStart=/root/his/venv/bin/python -c "import uvicorn; import his_fastapi; uvicorn.run(his_fastapi.app, host='127.0.0.1', port=8000, workers=4)"
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
            sudo cp /tmp/hisFastAPI.service /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable hisFastAPI.service
        fi
        sudo systemctl start hisFastAPI.service
        echo "FastAPI service started on 127.0.0.1:8000"
        ;;
    status)
        echo "=== Service Status ==="
        echo "Flask service (his.service):"
        sudo systemctl is-active his.service 2>/dev/null || echo "inactive"
        echo "FastAPI service (hisFastAPI.service):"
        sudo systemctl is-active hisFastAPI.service 2>/dev/null || echo "inactive"
        echo "Current active service on port 8000:"
        lsof -i :8000 | grep LISTEN || echo "No service listening on port 8000"
        ;;
    *)
        echo "Usage: $0 [flask|fastapi|status]"
        echo "  flask   - Switch to Flask backend"
        echo "  fastapi - Switch to FastAPI backend" 
        echo "  status  - Show current service status"
        exit 1
        ;;
esac
