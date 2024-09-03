from enum import Enum

class TicketType(Enum):
    WFH = "wfh"
    LEAVE = "leave"
    UPDATE_TIME_SHEET = "update_time_sheet"

    @classmethod
    def get_all(cls):
        return [ticket_type.value for ticket_type in cls]

    @classmethod
    def is_valid(cls, value):
        return value in cls.get_all()

# Enum for ticket status
class TicketStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    @classmethod
    def get_all(cls):
        return [ticket_status.value for ticket_status in cls]
    
    @classmethod
    def is_valid(cls, value):
        return value in cls.get_all()

class Role(Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"

    @classmethod
    def get_all(cls):
        return [role.value for role in cls]
    
    @classmethod
    def is_valid(cls, value):
        return value in cls.get_all()
    
    @classmethod
    def is_granted(cls, role):
        return role in [cls.ADMIN.value, cls.MANAGER.value]
    
class ActivityType(Enum):
    WALK = "walk"

    @classmethod
    def get_all(cls):
        return [activity_type.value for activity_type in cls]
    
    @classmethod
    def is_valid(cls, value):
        return value in cls.get_all()
    
class VoucherProvider(Enum):
    URBOX = "urbox"

    @classmethod
    def get_all(cls):
        return [voucher_provider.value for voucher_provider in cls]
    
    @classmethod
    def is_valid(cls, value):
        return value in cls.get_all()

class TimeSheetStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    @classmethod
    def get_all(cls):
        return [time_sheet_status.value for time_sheet_status in cls]
    
    @classmethod
    def is_valid(cls, value):
        return value in cls.get_all() 
class TimeSheet():
    DEFAULT = {
        "monday": {
            "is_leave": False
        },
        "tuesday": {
            "is_leave": False
        },
        "wednesday": {
            "is_leave": False
        },
        "thursday": {
            "is_leave": False
        },
        "friday": {
            "is_leave": False
        },
        "saturday": {
            "is_leave": True
        },
        "sunday": {
            "is_leave": True
        }
    }

    @classmethod
    def get_default(cls):
        return cls.DEFAULT.copy()
    
    @classmethod
    def is_valid_value(cls, given_value: dict):
        # given_value = given_value.get("current_value")
        if set(given_value.keys()) != set(cls.DEFAULT.keys()):
            return False
        
        for day, data in given_value.items():
            if not isinstance(data, dict):
                return False
            if "is_leave" not in data:
                return False
            if not isinstance(data["is_leave"], bool):
                return False
        return True
    
    @classmethod
    def is_empty(cls, time_sheet):
        return time_sheet == cls.DEFAULT