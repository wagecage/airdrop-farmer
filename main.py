#!/usr/bin/env python3
"""
AirdropFarmer - Main entry point
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from airdrop_farmer.scheduler import FarmingScheduler
from airdrop_farmer.farmer import AirdropFarmer
from airdrop_farmer.utils.logger import setup_logger
from airdrop_farmer.config import config

logger = setup_logger(log_file=config.LOG_FILE, log_level=config.LOG_LEVEL)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AirdropFarmer - Crypto Airdrop Farming Automation Bot"
    )
    parser.add_argument(
        "command",
        choices=["run", "schedule", "setup", "stats"],
        help="Command to execute"
    )
    parser.add_argument(
        "--wallets",
        type=int,
        help="Number of wallets to create (for setup command)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Interval in hours between scheduled runs"
    )
    parser.add_argument(
        "--no-immediate",
        action="store_true",
        help="Don't run immediately when starting scheduler"
    )

    args = parser.parse_args()

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        config.validate()

        if args.command == "setup":
            # Setup wallets
            logger.info("Setting up wallets...")
            farmer = AirdropFarmer()
            addresses = farmer.setup_wallets(count=args.wallets)
            logger.info(f"Setup complete! Created {len(addresses)} wallets:")
            for i, addr in enumerate(addresses, 1):
                logger.info(f"  {i}. {addr}")

        elif args.command == "run":
            # Run once
            logger.info("Running farming activities (single run)...")
            scheduler = FarmingScheduler()
            results = scheduler.run_once()
            logger.info(f"Run completed: {results['status']}")

        elif args.command == "schedule":
            # Start scheduler
            logger.info("Starting scheduler...")
            scheduler = FarmingScheduler(interval_hours=args.interval)
            scheduler.start(run_immediately=not args.no_immediate)

        elif args.command == "stats":
            # Show statistics
            logger.info("Fetching statistics...")
            farmer = AirdropFarmer()
            stats = farmer.get_stats()

            print("\n" + "=" * 80)
            print("AIRDROP FARMER STATISTICS")
            print("=" * 80)
            print(f"\nTotal Wallets: {stats['total_wallets']}")
            print(f"\nWallet Addresses:")
            for i, addr in enumerate(stats['wallets'], 1):
                print(f"  {i}. {addr}")

            print(f"\nPlatform Statistics:")
            for platform_stat in stats['platform_stats']:
                print(f"\n  {platform_stat['platform']}:")
                print(f"    Total Activities: {platform_stat['total_activities']}")
                print(f"    Successful: {platform_stat['successful_activities']}")
                print(f"    Failed: {platform_stat['failed_activities']}")
                print(f"    Last Activity: {platform_stat.get('last_activity_time', 'N/A')}")

            print(f"\nRecent Activities: {stats['recent_activities_count']}")
            print(f"\nGenerated at: {stats['generated_at']}")
            print("=" * 80 + "\n")

            farmer.cleanup()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nStopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
