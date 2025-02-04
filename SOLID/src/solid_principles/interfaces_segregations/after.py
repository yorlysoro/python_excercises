import os
from dataclasses import dataclass, field
from typing import Optional, Protocol
import uuid
import stripe
from dotenv import load_dotenv
from pydantic import BaseModel
from stripe.error import StripeError

_ = load_dotenv()

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo
    customer_id: Optional[str] = None

class PaymentData(BaseModel):
    amount: int
    source: str

class PaymentResponse(BaseModel):
    status: str
    amount: int
    transaction_id: Optional[str] = None
    message: Optional[str] = None

class PaymentProcessorProtocol(Protocol):
    def process_transaction(
        self, customer_data: CustomerData, payment_data: PaymentData
    ) -> PaymentResponse:
        pass

class RefundPyamentProtocol(Protocol):
    def refund_payment(self, transaction_id: str) -> PaymentResponse:
        pass

class RecurringPaymentProtocol(Protocol):
    def process_recurring_payment(
        self, customer_data: CustomerData, payment_data: PaymentData
    ) -> PaymentResponse:
        pass

class 