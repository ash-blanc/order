"""CLI entry point"""
import asyncio

import uvicorn

from .api import app


def main():
    """Run the server"""
    uvicorn.run(
        "order.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()