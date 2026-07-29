#!/bin/bash
cd "$(dirname "$0")"
PATH="/Users/henry/Library/Python/3.9/bin:$PATH"
uvicorn app.main:app --host 0.0.0.0 --port 9121