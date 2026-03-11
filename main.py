import asyncio

from app.main import main as app_main

__all__ = ["main"]


def main() -> None:
    asyncio.run(app_main())


if __name__ == "__main__":
    main()
