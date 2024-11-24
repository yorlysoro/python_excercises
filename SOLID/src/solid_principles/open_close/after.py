import os
from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod
import stripe
from dotenv import load_dotenv
from pydantic import BaseModel
from stripe import Charge
from stripe.error import StripeError

_ = load_dotenv()


class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo


class PaymentData(BaseModel):
    amount: int
    source: str


@dataclass
class CustomerValidator:
    def validate(self, customer_data: CustomerData):
        if not customer_data.name:
            print("Invalid customer data: missing name")
            raise ValueError("Invalid customer data: missing name")
        if not customer_data.contact_info:
            print("Invalid customer data: missing contact info")
            raise ValueError("Invalid customer data: missing contact_info")
        if not (customer_data.contact_info.email or customer_data.contact_info.phone):
            print("Invalid customer data: missing email and phone")
            raise ValueError("Invalid customer data: missing email and phone")


@dataclass
class PaymentDataValidator:
    def validate(self, payment_data: PaymentData):
        if not payment_data.source:
            print("Invalid payment data")
            raise ValueError("Invalid payment data")
        if payment_data.amount <= 0:
            print("Invalid payment data: amount must be greater than 0")
            raise ValueError("Invalid payment data: amount must be greater than 0")


class Notifier(ABC):
    @abstractmethod
    def send_confirmation(self, customer_data: CustomerData):
        raise NotImplemented("Method not implemented")


class EmailNotifier(Notifier):
    def send_confirmation(self, customer_data: CustomerData):
        from email.mime.text import MIMEText
        msg = MIMEText("Thank you for your payment")
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data.contact_info.email or ""
        print("Email sent to", customer_data.contact_info.email)


class SMSNotifier(Notifier):
    def send_confirmation(self, customer_data: CustomerData):
        phone_number = customer_data.contact_info.phone
        sms_gateway = "the custom SMS Gateway"
        print(f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment.")


@dataclass
class TransactionLogger:
    def log(self, customer_data: CustomerData, payment_data: PaymentData, charge: Charge):
        with open("transactions.log", "a") as log_file:
            log_file.write(f"{customer_data.name} paid {payment_data.amount}\n")
            log_file.write(f"Payment status: {charge.status}\n")


class PaymentProcessor(ABC):
    @abstractmethod
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData) -> Charge:
        raise NotImplemented("Method not implemented")


@dataclass
class StripePaymentProcessor(PaymentProcessor):
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData) -> Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        try:
            charge = stripe.Charge.create(
                amount=payment_data.amount,
                currency="usd",
                source=payment_data.source,
            )
            return charge
        except StripeError as e:
            print("Payment failed:", str(e))
            raise ValueError("Payment failed")


@dataclass
class PaymentService:
    customer_validator = CustomerValidator()
    payment_validator = PaymentDataValidator()
    payment_processor: PaymentProcessor = field(default_factory=StripePaymentProcessor)
    notifier: Notifier = field(default_factory=EmailNotifier)
    logger = TransactionLogger()
    
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData):
        try:
            self.customer_validator.validate(customer_data=customer_data)
        except ValueError as e:
            raise e
        
        try:
            self.payment_validator.validate(payment_data=payment_data)
        except ValueError as e:
            raise e
        try:
            charge = self.payment_processor.process_transaction(customer_data=customer_data, payment_data=payment_data)
            self.notifier.send_confirmation(customer_data=customer_data)
            self.logger.log(customer_data=customer_data, payment_data=payment_data, charge=charge)
            return charge
        except StripeError as e:
            raise e


if __name__ == "__main__":
    sms_notifier = SMSNotifier()
    payment_processor = PaymentService()
    
    customer_data_with_email = CustomerData(
        name="Jhon Doe",
        contact_info=ContactInfo(email="jhon@example.com")
    )
    
    customer_data_with_phone = CustomerData(
        name="Jane Doe",
        contact_info=ContactInfo(phone="123456789")
    )
    payment_data = PaymentData(amount=100, source="tok_visa")
    
    payment_processor.process_transaction(customer_data=customer_data_with_email, payment_data=payment_data)
    payment_processor.process_transaction(customer_data=customer_data_with_phone, payment_data=payment_data)
    
    try:
        error_payment_data = PaymentData(amount=0, source="tok_visa")
        payment_processor.process_transaction(customer_data=customer_data_with_email, payment_data=error_payment_data)
    except Exception as e:
        print(f"Payment failed and PaymentProcessor raise an exception: {e}")
