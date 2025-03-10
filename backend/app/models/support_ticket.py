# app/models/support_ticket.py

class SupportTicket:
    def __init__(self, ticket_id, user_id, message, status):
        self.ticket_id = ticket_id
        self.user_id = user_id
        self.message = message
        self.status = status
