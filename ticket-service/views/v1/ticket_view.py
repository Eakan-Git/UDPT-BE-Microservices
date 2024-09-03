from fastapi import APIRouter, HTTPException, Query
from schemas.ticket_schema import TicketCreate, TicketRead, TicketUpdate
from controllers.ticket_controller import create_ticket, get_tickets_by_user_id, update_ticket, get_tickets_paginate, get_ticket_by_id, get_tickets_with_filter
from controllers.user_controller import user_dependency
from enums import Role

router = APIRouter()

@router.post("/tickets/", response_model=TicketRead)
async def create_ticket_endpoint(ticket: TicketCreate, current_user: user_dependency):
    ticket_data = ticket.dict()
    try:
        new_ticket = await create_ticket(ticket_data)
        return new_ticket
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tickets/", response_model=dict)
async def get_tickets_with_filter_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10, type: str = None, status: str = None):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Permission denied")
    tickets = await get_tickets_with_filter(page, limit, type, status)
    return tickets

@router.get("/tickets/me/", response_model=dict)
async def get_my_tickets_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10, type: str = None, status: str = None):
    tickets = await get_tickets_by_user_id(current_user.id, page, limit, type, status)
    return tickets

@router.get("/tickets/{ticket_id}", response_model=TicketRead)
async def get_ticket_by_id_endpoint(ticket_id: int, current_user: user_dependency):
    ticket = await get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("/tickets/users/{user_id}", response_model=dict)
async def get_tickets_by_user_id_endpoint(current_user: user_dependency, user_id: int, page: int = 1, limit: int = 10):
    tickets = await get_tickets_by_user_id(user_id, page, limit)
    return tickets

@router.patch("/tickets/{ticket_id}", response_model=TicketRead)
async def update_ticket_endpoint(ticket_id: int, ticket: TicketUpdate, current_user: user_dependency):
    ticket_data = ticket.dict()
    if ticket.type:
        ticket_data["type"] = ticket.type.lower()
    if ticket.status:
        ticket_data["status"] = ticket.status.lower()
    updated_ticket = await update_ticket(ticket_id, ticket_data)
    if updated_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated_ticket