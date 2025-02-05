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

class StripePaymentProcessor(PaymentProcessorProtocol, RefundPyamentProtocol, RecurringPaymentProtocol):
    
    def process_transaction(
        self, customer_data: CustomerData, payment_data: PaymentDataD
    ) -> PaymentResponse:
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        try:
            charge = stripe.Charge.create(
                amount=payment_data.amount,
                currency="usd",
                source=payment_data.source,
                description="Charge for " + customer_data.name,
            )
            print("Payment Successful")
            return PaymentResponse(
                status=charge["status"],
                amount=charge["amount"],
                transaction_id=charge["id"],
                message="Payment Successful",
            )
        except StripeError as e:
            print("Payment Failed:", e)
            return PaymentResponse(
                status="failed",
                amount=payment_data.amount,
                transaction_id=None,
                message=str(e),
            )
    
    def refund_payment(self, transaction_id: str) -> PaymentResponse:
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        try:
            refund = stripe.Refund.create(charge=transaction_id)
            print("Refund Succesful")
            return PaymentResponse(
                status=refund["status"],
                amount=refund["amount"],
                transaction_id=refund["id"],
                message="Refund Succesful",
            )
        except StripeError as e:
            print("Refund failed:", e)
            return PaymentResponse(
                status="failed",
                amount=0,
                transaction_id=None,
                message=str(e)
            )
    
    def recurring_payment(
        self, customer_data: CustomerData, payment_data: PaymentData
    ) -> PaymentResponse:
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        price_id = os.getenv("STRIPE_PRICE_ID")
        try:
            customer = self._get_or_create_customer(customer_data)
            
            payment_method = self._attach_payment_method(
                customer.id, payment_data.source
            )
            
            self._set_default_payment_method(customer.id, payment_method.id)
            
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items = [
                    {"price": price_id}
                ],
                expand=["latest_invoice.payment_intent"]
            )
            print("Recurring payment setup succesusful")
            amount = subscription["items"]["data"][0]["price"]["unit_amount"]
            return PaymentResponse(
                status=subscription["status"],
                amount=amount,
                transaction_id=subscription["id"],
                message="Recurring payment setup successful",
            )
        except StripeError as e:
            print("Recurring payment setup failed:", e)
            return PaymentResponse(
                status="Failed",
                amount=0,
                transaction_id=None,
                message=str(e),
            )
            
    def _get_or_create_customer(self, customer_data: CustomerData) -> stripe.Customer:
        pass
