import os
from dataclasses import dataclass, field
from typing import Optional, Protocol

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


class Notifier(Protocol):
    """
    Protocol for sending notifications.

    This protocol defines the interface for notifiers. Implementations
    should provide a method `send_confirmation` that sends a confirmation
    to the customer.
    """
    def send_confirmation(self, customer_data: CustomerData):
        """Send a confirmation notification to the customer.

        :param customer_data: Data about the customer to notify.
        :type customer_data: CustomerData
        """
        raise NotImplemented("Method not implemented")


class EmailNotifier(Notifier):
    def send_confirmation(self, customer_data: CustomerData):
        from email.mime.text import MIMEText
        msg = MIMEText("Thank you for your payment")
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data.contact_info.email or ""
        
        print("Email sent to", customer_data.contact_info.email)


@dataclass
class SMSNotifier(Notifier):
    sms_gateway: str
    
    def send_confirmation(self, customer_data: CustomerData):
        phone_number = customer_data.contact_info.phone
        print(f"send the sms using {self.sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."


@dataclass
class TransactionLogger:
    log_file: str = "transactions.log"
    
    def log(self, customer_data: CustomerData, payment_data: PaymentData, charge: Charge):
        with open(self.log_file, "a") as log_file:
            log_file.write(f"{customer_data.name} paid {payment_data.amount}\n")
            log_file.write(f"Payment status: {charge.status}\n")


class PaymentProcessor(Protocol):
    """
    Protocol for processing payments.

    This protocol defines the interface for payment processors. Implementations
    should provide a method `process_transaction` that takes customer data and payment data,
    and returns a Stripe Charge object.
    """
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData) -> Charge:
        """Process a transaction for the given customer and payment data.

        :param customer_data: Data about the customer making the payment.
        :type customer_data: CustomerData
        :param payment_data: Data about the payment to be processed.
        :type payment_data: PaymentData
        :return: The result of the payment processing.
        :rtype: Charge
        """
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
                description=f"Payment from {customer_data.name}",
            )
            return charge
        except StripeError as e:
            print(f"Stripe error: {e}")
            raise ValueError("Payment processing failed")


@dataclass
class PaymentService:
    customer_validator = CustomerValidator()
    payment_validator = PaymentDataValidator()
    payment_processor: PaymentProcessor = field(default_factory=StripePaymentProcessor)
    notifier: Notifier = field(default_factory=EmailNotifier)
    logger = TransactionLogger()
    
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData):
        self.customer_validator.validate(customer_data=customer_data)
        self.payment_validator.validate(payment_data=payment_data)
        
        try:
            charge = self.payment_processor.process_transaction(customer_data=customer_data, payment_data=payment_data)
        except StripeError as e:
            raise e
        self.notifier.send_confirmation(customer_data=customer_data)
        self.logger.log(customer_data=customer_data, payment_data=payment_data, charge=charge)
        return charge


if __name__ == "__main__":
    sms_notifier = SMSNotifier(sms_gateway="Twilio")
    payment_service = PaymentService()
    payment_service_sms_notifier = PaymentService(notifier=sms_notifier)
    
    customer_data_with_email = CustomerData(
        name="Alice",
        contact_info=ContactInfo(email="alice@example.com")
    )
    
    customer_data_with_phone = CustomerData(
        name="Bob",
        contact_info=ContactInfo(phone="+1234567890")
    )
    
    payment_data = PaymentData(amount=100, source="tok_visa")
    
    payment_service_sms_notifier.process_transaction(customer_data=customer_data_with_email, payment_data=payment_data)
    payment_service.process_transaction(customer_data=customer_data_with_phone, payment_data=payment_data)
    try:
        error_payment_data = PaymentData(amount=0, source="tok_radarBlock")
        payment_service.process_transaction(customer_data=customer_data_with_email, payment_data=error_payment_data)
    except Exception as e:
        print(f"Payment failed and PaymentProcessor raise and exception:{e}")
