"""
Main farming orchestrator
"""
import time
from typing import List, Dict, Any
from datetime import datetime

from .wallet_manager import WalletManager
from .database import Database
from .notion_logger import NotionLogger
from .modules.megaeth import MegaETHModule
from .modules.lighter import LighterModule
from .modules.polymarket import PolymarketModule
from .utils.encryption import Encryptor
from .utils.logger import setup_logger
from .config import config

logger = setup_logger()


class AirdropFarmer:
    """Main orchestrator for airdrop farming activities"""

    def __init__(self):
        """Initialize the farmer with all necessary components"""
        logger.info("Initializing AirdropFarmer...")

        # Initialize encryption
        self.encryptor = Encryptor(config.MASTER_PASSWORD)

        # Initialize wallet manager
        self.wallet_manager = WalletManager(self.encryptor)

        # Initialize database
        self.database = Database()

        # Initialize Notion logger
        self.notion_logger = NotionLogger()

        # Initialize platform modules
        self.megaeth = MegaETHModule()
        self.lighter = LighterModule()
        self.polymarket = PolymarketModule()

        logger.info("AirdropFarmer initialized successfully")

    def setup_wallets(self, count: int = None) -> List[str]:
        """
        Setup wallets for farming

        Args:
            count: Number of wallets to create (uses config if not specified)

        Returns:
            List of wallet addresses
        """
        count = count or config.NUM_WALLETS

        existing_wallets = self.wallet_manager.get_wallets()

        if existing_wallets:
            logger.info(f"Found {len(existing_wallets)} existing wallets")
            return self.wallet_manager.get_wallet_addresses()

        logger.info(f"Creating {count} new wallets...")
        new_wallets = self.wallet_manager.create_multiple_wallets(count)

        addresses = [w.address for w in new_wallets]
        logger.info(f"Created {len(addresses)} wallets: {addresses}")

        return addresses

    def run_farming_activities(self) -> Dict[str, Any]:
        """
        Run all farming activities for all wallets

        Returns:
            Summary of farming run
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("Starting farming activities...")
        logger.info("=" * 80)

        wallets = self.wallet_manager.get_wallets()

        if not wallets:
            logger.warning("No wallets found. Please run setup_wallets() first.")
            return {
                "status": "failed",
                "error": "No wallets configured",
                "wallets_processed": 0,
                "activities_completed": 0
            }

        results = {
            "start_time": datetime.utcnow().isoformat(),
            "wallets_processed": 0,
            "activities_completed": 0,
            "errors": [],
            "wallet_results": []
        }

        # Process each wallet
        for wallet in wallets:
            logger.info(f"\n--- Processing wallet: {wallet.address} ---")

            wallet_result = {
                "address": wallet.address,
                "platforms": {}
            }

            # MegaETH testnet interactions
            try:
                logger.info("Running MegaETH testnet interactions...")
                megaeth_result = self.megaeth.interact_with_testnet(wallet)
                wallet_result["platforms"]["megaeth"] = megaeth_result

                # Log to database
                self.database.log_activity(
                    wallet_address=wallet.address,
                    activity_type="testnet_interaction",
                    platform="MegaETH",
                    status="success" if megaeth_result["success"] else "failed",
                    details=megaeth_result
                )

                # Log to Notion
                self.notion_logger.log_activity(
                    wallet_address=wallet.address,
                    platform="MegaETH",
                    activity_type="Testnet Interaction",
                    status="success" if megaeth_result["success"] else "failed",
                    details=megaeth_result
                )

                # Update wallet state
                self.database.update_wallet_state(wallet.address, {
                    "last_megaeth_activity": datetime.utcnow().isoformat(),
                    "megaeth_tx_count": megaeth_result.get("successful_count", 0)
                })

                # Update platform stats
                self.database.update_platform_stats("MegaETH", megaeth_result["success"])

                if megaeth_result["success"]:
                    results["activities_completed"] += megaeth_result.get("successful_count", 0)

            except Exception as e:
                logger.error(f"MegaETH interaction failed: {e}")
                results["errors"].append(f"MegaETH - {wallet.address}: {str(e)}")
                wallet_result["platforms"]["megaeth"] = {"error": str(e), "success": False}

            # Lighter DEX farming
            try:
                logger.info("Running Lighter DEX farming...")
                lighter_result = self.lighter.farm_points(wallet.address)
                wallet_result["platforms"]["lighter"] = lighter_result

                # Log to database
                self.database.log_activity(
                    wallet_address=wallet.address,
                    activity_type="points_farming",
                    platform="Lighter",
                    status="success" if lighter_result["success"] else "failed",
                    details=lighter_result
                )

                # Log to Notion
                self.notion_logger.log_activity(
                    wallet_address=wallet.address,
                    platform="Lighter",
                    activity_type="Points Farming",
                    status="success" if lighter_result["success"] else "failed",
                    details=lighter_result
                )

                # Update wallet state
                self.database.update_wallet_state(wallet.address, {
                    "last_lighter_activity": datetime.utcnow().isoformat(),
                    "lighter_points": lighter_result.get("current_points", 0)
                })

                # Update platform stats
                self.database.update_platform_stats("Lighter", lighter_result["success"])

                if lighter_result["success"]:
                    results["activities_completed"] += lighter_result.get("successful_count", 0)

            except Exception as e:
                logger.error(f"Lighter DEX farming failed: {e}")
                results["errors"].append(f"Lighter - {wallet.address}: {str(e)}")
                wallet_result["platforms"]["lighter"] = {"error": str(e), "success": False}

            # Polymarket tracking
            try:
                logger.info("Running Polymarket tracking...")
                polymarket_result = self.polymarket.track_interactions(wallet.address)
                wallet_result["platforms"]["polymarket"] = polymarket_result

                # Log to database
                self.database.log_activity(
                    wallet_address=wallet.address,
                    activity_type="interaction_tracking",
                    platform="Polymarket",
                    status="success" if polymarket_result["success"] else "failed",
                    details=polymarket_result
                )

                # Log to Notion
                self.notion_logger.log_activity(
                    wallet_address=wallet.address,
                    platform="Polymarket",
                    activity_type="Interaction Tracking",
                    status="success" if polymarket_result["success"] else "failed",
                    details=polymarket_result
                )

                # Update wallet state
                self.database.update_wallet_state(wallet.address, {
                    "last_polymarket_activity": datetime.utcnow().isoformat(),
                    "polymarket_trades": polymarket_result.get("trades_count", 0)
                })

                # Update platform stats
                self.database.update_platform_stats("Polymarket", polymarket_result["success"])

                if polymarket_result["success"]:
                    results["activities_completed"] += polymarket_result.get("successful_count", 0)

            except Exception as e:
                logger.error(f"Polymarket tracking failed: {e}")
                results["errors"].append(f"Polymarket - {wallet.address}: {str(e)}")
                wallet_result["platforms"]["polymarket"] = {"error": str(e), "success": False}

            results["wallet_results"].append(wallet_result)
            results["wallets_processed"] += 1

            logger.info(f"Completed processing wallet: {wallet.address}")

        # Calculate duration
        duration = time.time() - start_time
        results["duration_seconds"] = duration
        results["end_time"] = datetime.utcnow().isoformat()

        # Determine overall status
        results["status"] = "success" if results["activities_completed"] > 0 else "failed"

        # Log scheduler run to database
        self.database.log_scheduler_run(
            status=results["status"],
            wallets_processed=results["wallets_processed"],
            activities_completed=results["activities_completed"],
            errors=results["errors"] if results["errors"] else None,
            duration=duration
        )

        # Log scheduler run to Notion
        self.notion_logger.log_scheduler_run(
            run_status=results["status"],
            wallets_processed=results["wallets_processed"],
            activities_completed=results["activities_completed"],
            errors=results["errors"],
            duration=duration
        )

        logger.info("=" * 80)
        logger.info(f"Farming activities completed!")
        logger.info(f"Wallets processed: {results['wallets_processed']}")
        logger.info(f"Activities completed: {results['activities_completed']}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Errors: {len(results['errors'])}")
        logger.info("=" * 80)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get farming statistics

        Returns:
            Statistics dictionary
        """
        wallets = self.wallet_manager.get_wallet_addresses()
        platform_stats = self.database.get_platform_stats()
        recent_activities = self.database.get_recent_activities(limit=50)

        stats = {
            "total_wallets": len(wallets),
            "wallets": wallets,
            "platform_stats": platform_stats,
            "recent_activities_count": len(recent_activities),
            "generated_at": datetime.utcnow().isoformat()
        }

        return stats

    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        self.database.close()
        logger.info("Cleanup completed")
