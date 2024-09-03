from fastapi import HTTPException
from models.mongo import engine
from models.ticket import Ticket
from controllers.user_controller import get_user_by_id
from datetime import datetime
from enums import TicketType, TicketStatus
from typing import Optional

async def get_ticket_by_id(ticket_id: int) -> Ticket:
    if not isinstance(ticket_id, int) or ticket_id < 1:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    ticket = await engine.find_one(Ticket, Ticket.id == ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket

async def get_tickets_with_filter(page: int, limit: int, ticket_type: Optional[str] = None, status: Optional[str] = None) -> dict:
    query = {}
    if ticket_type:
        query["type"] = ticket_type.lower()
    if status:
        query["status"] = status.lower()
    
    tickets = await engine.find(Ticket, query, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/tickets?page={page - 1}&limit={limit}&type={ticket_type}&status={status}' if page > 1 else None
    next_url = f'/tickets?page={page + 1}&limit={limit}&type={ticket_type}&status={status}' if len(tickets) == limit else None
    
    total = await engine.count(Ticket, query)
    total_pages = (total + limit - 1) // limit
    
    res = {
        "data": [ticket.dict() for ticket in tickets],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def create_ticket(ticket_data: dict) -> Ticket:
    given_user_id = ticket_data.get("user_id")
    if not isinstance(given_user_id, int) or given_user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id")

    if not await get_user_by_id(given_user_id):
        raise HTTPException(status_code=400, detail="User not found")
    
    given_ticket_type = ticket_data.get("type").lower()
    
    if not TicketType.is_valid(given_ticket_type):
        raise HTTPException(status_code=400, detail="Invalid ticket type")
    
    given_from_date = ticket_data.get("from_date").date()
    given_to_date = ticket_data.get("to_date").date()

    current_time = datetime.utcnow().date()
    
    if given_from_date and given_to_date:
        if given_from_date > given_to_date:
            raise HTTPException(status_code=400, detail="Invalid date range")
        if current_time > given_from_date:
            raise HTTPException(status_code=400, detail="Invalid from date")
        if current_time > given_to_date:
            raise HTTPException(status_code=400, detail="Invalid to date")

    ticket_id = await get_next_ticket_id()
    ticket_data["id"] = ticket_id
    ticket = Ticket(**ticket_data)
    await engine.save(ticket)
    return ticket

async def get_next_ticket_id() -> int:
    last_ticket = await engine.find_one(Ticket, sort=Ticket.id.desc())
    return last_ticket.id + 1 if last_ticket else 1

async def get_tickets_paginate(page: int, limit: int) -> dict:
    tickets = await engine.find(Ticket, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/tickets?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/tickets?page={page + 1}&limit={limit}' if len(tickets) == limit else None
    
    total = await engine.count(Ticket)
    total_pages = total // limit + 1 if total % limit else total // limit

    res = {
        "data": [ticket.dict() for ticket in tickets],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def get_tickets_by_user_id(user_id: int, page: int, limit: int, ticket_type: Optional[str] = None, status: Optional[str] = None) -> dict:
    if not isinstance(user_id, int) or user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    query = {"user_id": user_id}
    if ticket_type:
        query["type"] = ticket_type.lower()
    if status:
        query["status"] = status.lower()
    
    if ticket_type and not TicketType.is_valid(ticket_type):
        raise HTTPException(status_code=400, detail="Invalid ticket type")
    
    if status and not TicketStatus.is_valid(status):
        raise HTTPException(status_code=400, detail="Invalid ticket status")
    
    tickets = await engine.find(Ticket, query, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/tickets/users/{user_id}?page={page - 1}&limit={limit}&type={ticket_type}&status={status}' if page > 1 else None
    next_url = f'/tickets/users/{user_id}?page={page + 1}&limit={limit}&type={ticket_type}&status={status}' if len(tickets) == limit else None
    
    total = await engine.count(Ticket, query)
    total_pages = (total + limit - 1) // limit
    
    res = {
        "data": [ticket.dict() for ticket in tickets],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def update_ticket(ticket_id: int, ticket_data: dict) -> Ticket:
    ticket = await engine.find_one(Ticket, Ticket.id == ticket_id)
    if ticket:
        for key, value in ticket_data.items():
            if hasattr(ticket, key) and value is not None:
                setattr(ticket, key, value)
        await engine.save(ticket)
        return ticket
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")