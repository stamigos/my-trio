class InvoiceStatus:
        New = 1
        Waiting = 2
        Success = 3
        Rejected = 4
        PsCreatingError = 5


class ControllerResult:
        Ok = "ok"
        Error = "error"


class ValidationStatus:
        Ok = 1
        ProviderUnavailable = 2
        Unknown = 3


class WithdrawAmountType:
        PsAmount = "ps_amount"
        ShopAmount = "shop_amount"


class WithdrawStatus:
        New = 1
        WaitingManualConfirmation = 2
        PsProcessing = 3
        PsProcessingError = 4
        Success = 5
        Rejected = 6


class OperationType:
        Registration = 1
        Login = 2
        Logout = 3
        Index = 4
