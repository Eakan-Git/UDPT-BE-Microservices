from fastapi import APIRouter, HTTPException, Request
from schemas.ticket_schema import TicketCreate, TicketRead, TicketUpdate
from controllers.ticket_controller import create_ticket, get_tickets_by_user_id, update_ticket, get_ticket_by_id, get_tickets_with_filter
from enums import Role

router = APIRouter()

@router.post("/tickets/", response_model=TicketRead)
async def create_ticket_endpoint(ticket: TicketCreate):
    ticket_data = ticket.dict()
    try:
        new_ticket = await create_ticket(ticket_data)
        return new_ticket
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tickets/", response_model=dict)
async def get_tickets_with_filter_endpoint(request: Request, page: int = 1, limit: int = 10, type: str = None, status: str = None):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    tickets = await get_tickets_with_filter(page, limit, type, status)
    return tickets

@router.get("/tickets/me/", response_model=dict)
async def get_my_tickets_endpoint(request: Request, page: int = 1, limit: int = 10, type: str = None, status: str = None):
    current_user_id = request.state.user.get("user_id")
    tickets = await get_tickets_by_user_id(current_user_id, page, limit, type, status)
    return tickets

@router.get("/tickets/{ticket_id}", response_model=TicketRead)
async def get_ticket_by_id_endpoint(ticket_id: int, request: Request):
    ticket = await get_ticket_by_id(ticket_id)
    if ticket.user_id != request.state.user.get("user_id") or not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    return ticket

@router.get("/tickets/users/{user_id}", response_model=dict)
async def get_tickets_by_user_id_endpoint(request: Request, user_id: int, page: int = 1, limit: int = 10):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    tickets = await get_tickets_by_user_id(user_id, page, limit)
    return tickets

@router.patch("/tickets/{ticket_id}", response_model=TicketRead)
async def update_ticket_endpoint(ticket_id: int, ticket: TicketUpdate, request: Request):
    ticket_data = ticket.dict()
    if ticket.type:
        ticket_data["type"] = ticket.type.lower()
    if ticket.status:
        ticket_data["status"] = ticket.status.lower()
    updated_ticket = await update_ticket(ticket_id, ticket_data, request.state.user.get("user_id"))
    if updated_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated_ticket