from typing import Any, Protocol

from app.client import ExtensionClient, InstallationClient


class AutomationClient(Protocol):
    async def get_helpdesk_case(self, case_id: str) -> dict[str, Any]: ...
    async def update_helpdesk_case(self, case_id: str, payload: dict[str, Any]) -> dict[str, Any]: ...
    async def process_helpdesk_case(self, case_id: str) -> dict[str, Any] | None: ...
    async def get_contact_by_email(self, email: str) -> dict[str, Any] | None: ...
    async def get_helpdesk_chat_participants(self, chat_id: str) -> list[dict[str, Any]]: ...
    async def add_helpdesk_chat_participant(
        self, chat_id: str, payload: list[dict[str, Any]]
    ) -> dict[str, Any] | list[dict[str, Any]]: ...
    async def get_helpdesk_parameters_by_external_ids(
        self, external_ids: list[str]
    ) -> list[dict[str, Any]]: ...
    async def create_helpdesk_chat_message(
        self, chat_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]: ...


class AutomationError(RuntimeError):
    """Raised when the automation cannot complete due to missing helpdesk data."""


class PlatformAutomationClient:
    def __init__(self, client: InstallationClient, ext_client: ExtensionClient) -> None:
        self.client = client
        self.ext_client = ext_client

    # case methods
    async def get_helpdesk_case(self, case_id: str) -> dict[str, Any]:
        return await self.client.get(
            "helpdesk/cases",
            case_id,
            "id,chat,queue,parameters,audit,status,account,reporter,assignee".split(","),
        )

    async def update_helpdesk_case(self, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.update("helpdesk/cases", case_id, payload)

    async def process_helpdesk_case(self, case_id: str) -> dict[str, Any]:
        return await self.client.run_object_action("helpdesk/cases", case_id, "process")

    # contact methods
    async def get_contact_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.client.get_first(
            "notifications/contacts",
            query=f"eq(email,{email})",
            select=["id", "email", "name"],
        )

    # chat methods
    async def get_helpdesk_chat_participants(self, chat_id: str) -> list[dict[str, Any]]:
        page = await self.client.get_collection(
            f"helpdesk/chats/{chat_id}/participants",
            query="",
            select=["id", "contact", "account", "status", "identity"],
        )
        return page["data"]

    async def add_helpdesk_chat_participant(
        self, chat_id: str, payload: list[dict[str, Any]]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        return await self.client.create(f"helpdesk/chats/{chat_id}/participants", payload)

    async def get_helpdesk_parameters_by_external_ids(
        self, external_ids: list[str]
    ) -> list[dict[str, Any]]:
        joined_ids = ",".join(external_ids)
        page = await self.client.get_collection(
            "helpdesk/parameters",
            query=f'eq(scope,"case"),in(externalId,({joined_ids}))',
            select=["id", "name", "externalId", "type", "multiple", "constraints", "displayOrder"],
        )
        return page["data"]

    async def create_helpdesk_chat_message(
        self, chat_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.client.create(f"helpdesk/chats/{chat_id}/messages", payload)

