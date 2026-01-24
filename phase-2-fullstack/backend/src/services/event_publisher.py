"""
Event publisher service for Kafka integration via Dapr.
[Task]: T-C-001 (Event Publisher Service), T-D-006 (Dapr Integration)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3, Section 6.1,
        specs/005-phase-v-cloud/phase5-cloud.plan.md Section 5.1-5.2,
        specs/005-phase-v-cloud/phase5-cloud.tasks.md Section D.6
"""

import json
import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from sqlmodel import Session
from src.models.event_log import EventLog
from src.config import settings


class EventPublisher:
    """
    Event publisher for publishing task events to Kafka.
    
    In development (without Kafka), events are logged to the database.
    In production (with Kafka), events are published to Kafka topics.
    
    [Task]: T-C-001
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3.1-3.3
    """
    
    # Event types
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_SENT = "reminder.sent"
    
    # Topics
    TOPIC_TASK_EVENTS = "task-events"
    TOPIC_REMINDERS = "reminders"
    TOPIC_TASK_UPDATES = "task-updates"
    
    def __init__(self):
        """Initialize event publisher with Dapr support."""
        self.kafka_enabled = settings.KAFKA_ENABLED.lower() == "true"
        self.dapr_http_endpoint = settings.DAPR_HTTP_ENDPOINT
        self.kafka_bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        
        # HTTP client for Dapr API calls
        self.http_client = httpx.AsyncClient(timeout=10.0)
        
        if self.kafka_enabled:
            try:
                from kafka import KafkaProducer
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_bootstrap_servers.split(","),
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
                print(f"✅ Kafka producer initialized: {self.kafka_bootstrap_servers}")
            except ImportError:
                print("⚠️  kafka-python not installed. Install with: pip install kafka-python")
                self.kafka_enabled = False
            except Exception as e:
                print(f"⚠️  Kafka connection failed: {e}")
                self.kafka_enabled = False
    
    async def _publish_via_dapr(
        self,
        topic: str,
        event_payload: Dict[str, Any]
    ) -> bool:
        """
        Publish event to Kafka via Dapr Pub/Sub API.
        
        Dapr Endpoint: POST /v1.0/publish/{pubsubname}/{topic}
        
        [Task]: T-D-006
        [From]: specs/005-phase-v-cloud/phase5-cloud.tasks.md Section D.6
        """
        try:
            url = f"{self.dapr_http_endpoint}/v1.0/publish/kafka-pubsub/{topic}"
            response = await self.http_client.post(
                url,
                json=event_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ Event published via Dapr: {topic}")
                return True
            else:
                print(f"⚠️  Dapr publish failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"⚠️  Dapr publish error: {e}")
            return False
    
    def publish(
        self,
        event_type: str,
        topic: str,
        payload: Dict[str, Any],
        task_id: Optional[int] = None,
        user_id: Optional[str] = None,
        session: Optional[Session] = None
    ) -> str:
        """
        Publish event to Kafka (or log to database if Kafka unavailable).
        
        Args:
            event_type: Type of event (e.g., "task.created")
            topic: Kafka topic name
            payload: Event payload (will be JSON serialized)
            task_id: Optional task ID reference
            user_id: Optional user ID reference
            session: Database session for logging
        
        Returns:
            event_id: UUID of the published event
        
        [Task]: T-C-001
        [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md Section 5.1
        """
        event_id = str(uuid4())
        
        # Enrich payload with metadata
        event_payload = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Try publishing via Dapr first (if Kafka enabled)
        if self.kafka_enabled:
            try:
                # Use asyncio to run async Dapr publish
                import asyncio
                success = asyncio.run(self._publish_via_dapr(topic, event_payload))
                if success:
                    return event_id
            except Exception as e:
                print(f"⚠️  Dapr publish failed: {e}")
        
        # Fallback: Publish to Kafka directly if enabled and Dapr failed
        if self.kafka_enabled and self.producer:
            try:
                future = self.producer.send(
                    topic,
                    key=str(task_id) if task_id else event_id,
                    value=event_payload
                )
                # Wait for confirmation (with timeout)
                record_metadata = future.get(timeout=10)
                print(f"✅ Event published to Kafka: {topic} (partition {record_metadata.partition}, offset {record_metadata.offset})")
            except Exception as e:
                print(f"⚠️  Kafka publish failed: {e}")
                # Fall back to database logging
                self._log_to_database(event_id, event_type, topic, task_id, user_id, event_payload, session)
        else:
            # Log to database (development mode)
            self._log_to_database(event_id, event_type, topic, task_id, user_id, event_payload, session)
        
        return event_id
    
    def _log_to_database(
        self,
        event_id: str,
        event_type: str,
        topic: str,
        task_id: Optional[int],
        user_id: Optional[str],
        payload: Dict[str, Any],
        session: Optional[Session]
    ) -> None:
        """
        Log event to database (fallback when Kafka unavailable).
        
        [Task]: T-C-001
        [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md Section 5.1.2
        """
        if not session:
            print("⚠️  No database session provided, event not logged")
            return
        
        try:
            event_log = EventLog(
                event_id=event_id,
                event_type=event_type,
                topic=topic,
                task_id=task_id,
                user_id=user_id,
                payload=payload,
                processed=False
            )
            session.add(event_log)
            session.commit()
            print(f"📝 Event logged to database: {event_type} (ID: {event_id})")
        except Exception as e:
            print(f"❌ Failed to log event to database: {e}")
    
    def publish_task_created(
        self,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any],
        session: Optional[Session] = None
    ) -> str:
        """
        Publish task.created event.
        
        [Task]: T-C-002
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3.1.1
        """
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "priority": task_data.get("priority"),
            "due_date": task_data.get("due_date"),
            "reminder_time": task_data.get("reminder_time"),
            "is_recurring": task_data.get("is_recurring", False),
            "recurrence_pattern": task_data.get("recurrence_pattern"),
            "tags": task_data.get("tags", [])
        }
        return self.publish(
            event_type=self.TASK_CREATED,
            topic=self.TOPIC_TASK_EVENTS,
            payload=payload,
            task_id=task_id,
            user_id=user_id,
            session=session
        )
    
    def publish_task_updated(
        self,
        task_id: int,
        user_id: str,
        changes: Dict[str, Any],
        session: Optional[Session] = None
    ) -> str:
        """
        Publish task.updated event.
        
        [Task]: T-C-003
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3.1.2
        """
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "changes": changes,
            "updated_at": datetime.utcnow().isoformat()
        }
        return self.publish(
            event_type=self.TASK_UPDATED,
            topic=self.TOPIC_TASK_UPDATES,
            payload=payload,
            task_id=task_id,
            user_id=user_id,
            session=session
        )
    
    def publish_task_completed(
        self,
        task_id: int,
        user_id: str,
        completed: bool,
        session: Optional[Session] = None
    ) -> str:
        """
        Publish task.completed event.
        
        [Task]: T-C-004
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3.1.3
        """
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "completed": completed,
            "completed_at": datetime.utcnow().isoformat()
        }
        return self.publish(
            event_type=self.TASK_COMPLETED,
            topic=self.TOPIC_TASK_EVENTS,
            payload=payload,
            task_id=task_id,
            user_id=user_id,
            session=session
        )
    
    def publish_task_deleted(
        self,
        task_id: int,
        user_id: str,
        session: Optional[Session] = None
    ) -> str:
        """
        Publish task.deleted event.
        
        [Task]: T-C-001
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3.1.4
        """
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        return self.publish(
            event_type=self.TASK_DELETED,
            topic=self.TOPIC_TASK_EVENTS,
            payload=payload,
            task_id=task_id,
            user_id=user_id,
            session=session
        )
    
    def publish_reminder_scheduled(
        self,
        task_id: int,
        user_id: str,
        reminder_time: str,
        session: Optional[Session] = None
    ) -> str:
        """
        Publish reminder.scheduled event.
        
        [Task]: T-C-009
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md Section 3.2.1
        """
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "reminder_time": reminder_time,
            "scheduled_at": datetime.utcnow().isoformat()
        }
        return self.publish(
            event_type=self.REMINDER_SCHEDULED,
            topic=self.TOPIC_REMINDERS,
            payload=payload,
            task_id=task_id,
            user_id=user_id,
            session=session
        )
    
    def close(self):
        """Close Kafka producer connection."""
        if self.kafka_enabled and hasattr(self, 'producer'):
            self.producer.close()
            print("✅ Kafka producer closed")


# Global event publisher instance
_event_publisher = None


def get_event_publisher() -> EventPublisher:
    """
    Get singleton event publisher instance.
    
    [Task]: T-C-001
    [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md Section 5.1.3
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
