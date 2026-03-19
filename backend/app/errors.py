class DomainError(Exception):
    """Base class for all domain-level errors."""

    error_code = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidSplit(DomainError):
    """Split amounts do not satisfy the required constraint."""
    error_code = "INVALID_SPLIT"


class MemberNotInGroup(DomainError):
    """Referenced member does not belong to the group."""
    error_code = "MEMBER_NOT_IN_GROUP"


class GroupNotSettled(DomainError):
    """Group has outstanding balances and cannot be deleted."""
    error_code = "GROUP_NOT_SETTLED"


class InsufficientBalance(DomainError):
    """Settlement amount exceeds the outstanding balance."""
    error_code = "INSUFFICIENT_BALANCE"


class ResourceNotFound(DomainError):
    """Requested resource does not exist."""
    error_code = "NOT_FOUND"
    status_code = 404
