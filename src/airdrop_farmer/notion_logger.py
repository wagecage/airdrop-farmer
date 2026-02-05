"""
Notion API logger for activity tracking
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from notion_client import Client

from .utils.logger import setup_logger
from .config import config

logger = setup_logger()


class NotionLogger:
    """Log activities to Notion database"""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize Notion logger

        Args:
            api_key: Notion API key
            database_id: Notion database ID
        """
        self.api_key = api_key or config.NOTION_API_KEY
        self.database_id = database_id or config.NOTION_DATABASE_ID

        if not self.api_key or not self.database_id:
            logger.warning("Notion API credentials not configured")
            self.client = None
        else:
            try:
                self.client = Client(auth=self.api_key)
                logger.info("Notion client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Notion client: {e}")
                self.client = None

    def log_activity(
        self,
        wallet_address: str,
        platform: str,
        activity_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        tx_hash: Optional[str] = None
    ) -> Optional[str]:
        """
        Log activity to Notion database

        Args:
            wallet_address: Wallet address
            platform: Platform name (MegaETH, Lighter, Polymarket)
            activity_type: Type of activity
            status: Status (success/failed)
            details: Additional details
            tx_hash: Transaction hash if applicable

        Returns:
            Notion page ID or None
        """
        if not self.client:
            logger.warning("Notion client not initialized - skipping log")
            return None

        try:
            # Format details as string
            details_str = ""
            if details:
                details_str = "\n".join([f"{k}: {v}" for k, v in details.items()])

            # Create Notion page properties
            properties = {
                "Wallet": {
                    "title": [
                        {
                            "text": {
                                "content": wallet_address
                            }
                        }
                    ]
                },
                "Platform": {
                    "select": {
                        "name": platform
                    }
                },
                "Activity": {
                    "rich_text": [
                        {
                            "text": {
                                "content": activity_type
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": status
                    }
                },
                "Timestamp": {
                    "date": {
                        "start": datetime.utcnow().isoformat()
                    }
                }
            }

            # Add optional fields if present
            if tx_hash:
                properties["TX Hash"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": tx_hash
                            }
                        }
                    ]
                }

            if details_str:
                properties["Details"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": details_str[:2000]  # Notion limit
                            }
                        }
                    ]
                }

            # Create page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )

            page_id = response["id"]
            logger.info(f"Logged activity to Notion: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to log activity to Notion: {e}")
            return None

    def log_batch_activities(self, activities: List[Dict[str, Any]]) -> List[Optional[str]]:
        """
        Log multiple activities to Notion

        Args:
            activities: List of activity dictionaries

        Returns:
            List of Notion page IDs
        """
        page_ids = []

        for activity in activities:
            page_id = self.log_activity(
                wallet_address=activity.get("wallet_address", ""),
                platform=activity.get("platform", ""),
                activity_type=activity.get("activity_type", ""),
                status=activity.get("status", ""),
                details=activity.get("details"),
                tx_hash=activity.get("tx_hash")
            )
            page_ids.append(page_id)

        logger.info(f"Logged {len(page_ids)} activities to Notion")
        return page_ids

    def log_scheduler_run(
        self,
        run_status: str,
        wallets_processed: int,
        activities_completed: int,
        errors: Optional[List[str]] = None,
        duration: Optional[float] = None
    ) -> Optional[str]:
        """
        Log scheduler run summary to Notion

        Args:
            run_status: Run status
            wallets_processed: Number of wallets processed
            activities_completed: Number of activities completed
            errors: List of errors
            duration: Duration in seconds

        Returns:
            Notion page ID or None
        """
        if not self.client:
            return None

        try:
            details = {
                "Wallets Processed": wallets_processed,
                "Activities Completed": activities_completed,
                "Duration": f"{duration:.2f}s" if duration else "N/A",
                "Errors": ", ".join(errors) if errors else "None"
            }

            return self.log_activity(
                wallet_address="SCHEDULER",
                platform="System",
                activity_type="Scheduled Run",
                status=run_status,
                details=details
            )

        except Exception as e:
            logger.error(f"Failed to log scheduler run to Notion: {e}")
            return None

    def create_database_if_needed(self, parent_page_id: str) -> Optional[str]:
        """
        Create Notion database if it doesn't exist

        Args:
            parent_page_id: Parent page ID to create database in

        Returns:
            Database ID or None
        """
        if not self.client:
            return None

        try:
            # Define database schema
            database = self.client.databases.create(
                parent={"page_id": parent_page_id},
                title=[
                    {
                        "type": "text",
                        "text": {
                            "content": "AirdropFarmer Activity Log"
                        }
                    }
                ],
                properties={
                    "Wallet": {
                        "title": {}
                    },
                    "Platform": {
                        "select": {
                            "options": [
                                {"name": "MegaETH", "color": "blue"},
                                {"name": "Lighter", "color": "green"},
                                {"name": "Polymarket", "color": "purple"},
                                {"name": "System", "color": "gray"}
                            ]
                        }
                    },
                    "Activity": {
                        "rich_text": {}
                    },
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "success", "color": "green"},
                                {"name": "failed", "color": "red"},
                                {"name": "pending", "color": "yellow"}
                            ]
                        }
                    },
                    "Timestamp": {
                        "date": {}
                    },
                    "TX Hash": {
                        "rich_text": {}
                    },
                    "Details": {
                        "rich_text": {}
                    }
                }
            )

            database_id = database["id"]
            logger.info(f"Created Notion database: {database_id}")
            return database_id

        except Exception as e:
            logger.error(f"Failed to create Notion database: {e}")
            return None

    def query_recent_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query recent activities from Notion

        Args:
            limit: Maximum number of activities to retrieve

        Returns:
            List of activity dictionaries
        """
        if not self.client:
            return []

        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                page_size=limit,
                sorts=[
                    {
                        "property": "Timestamp",
                        "direction": "descending"
                    }
                ]
            )

            activities = []
            for page in response["results"]:
                properties = page["properties"]

                activity = {
                    "wallet": self._extract_text(properties.get("Wallet")),
                    "platform": self._extract_select(properties.get("Platform")),
                    "activity_type": self._extract_text(properties.get("Activity")),
                    "status": self._extract_select(properties.get("Status")),
                    "timestamp": self._extract_date(properties.get("Timestamp")),
                    "tx_hash": self._extract_text(properties.get("TX Hash")),
                    "details": self._extract_text(properties.get("Details"))
                }

                activities.append(activity)

            logger.info(f"Retrieved {len(activities)} activities from Notion")
            return activities

        except Exception as e:
            logger.error(f"Failed to query Notion activities: {e}")
            return []

    @staticmethod
    def _extract_text(prop: Optional[Dict]) -> str:
        """Extract text from Notion property"""
        if not prop:
            return ""
        if prop["type"] == "title" and prop.get("title"):
            return prop["title"][0]["text"]["content"]
        if prop["type"] == "rich_text" and prop.get("rich_text"):
            return prop["rich_text"][0]["text"]["content"]
        return ""

    @staticmethod
    def _extract_select(prop: Optional[Dict]) -> str:
        """Extract select value from Notion property"""
        if not prop or prop["type"] != "select":
            return ""
        select = prop.get("select")
        return select["name"] if select else ""

    @staticmethod
    def _extract_date(prop: Optional[Dict]) -> str:
        """Extract date from Notion property"""
        if not prop or prop["type"] != "date":
            return ""
        date = prop.get("date")
        return date["start"] if date else ""
