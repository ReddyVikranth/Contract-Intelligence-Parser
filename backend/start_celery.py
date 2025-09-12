#!/usr/bin/env python3
"""
Script to start Celery worker for development
"""
import os
import sys
from app.celery_app import celery_app

if __name__ == "__main__":
    # Start Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--queues=contract_processing',
        '--concurrency=2'
    ])