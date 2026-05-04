from pydantic import BaseModel
from typing import Optional, Any, List

class ExtractedField(BaseModel):
    value: Optional[Any] = None
    confidence: Optional[float] = None

class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None

class LineItemsField(BaseModel):
    value: Optional[List[LineItem]] = None
    confidence: Optional[float] = None

class InvoiceData(BaseModel):
    doc_type: str
    classification_confidence: Optional[float] = None
    classification_reasoning: Optional[str] = None
    invoice_number: ExtractedField
    invoice_date: ExtractedField
    due_date: ExtractedField
    vendor_name: ExtractedField
    vendor_address: ExtractedField
    vendor_email: ExtractedField
    bill_to_name: ExtractedField
    bill_to_address: ExtractedField
    po_number: ExtractedField
    currency: ExtractedField
    line_items: LineItemsField
    subtotal: ExtractedField
    tax_rate: ExtractedField
    tax_amount: ExtractedField
    discount_amount: ExtractedField
    total_amount: ExtractedField

class Transaction(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    running_balance: Optional[float] = None

class TransactionsField(BaseModel):
    value: Optional[List[Transaction]] = None
    confidence: Optional[float] = None

class BankStatementData(BaseModel):
    doc_type: str
    classification_confidence: Optional[float] = None
    classification_reasoning: Optional[str] = None
    account_holder_name: ExtractedField
    account_number_last4: ExtractedField
    account_type: ExtractedField
    bank_name: ExtractedField
    statement_start_date: ExtractedField
    statement_end_date: ExtractedField
    currency: ExtractedField
    opening_balance: ExtractedField
    closing_balance: ExtractedField
    total_credits: ExtractedField
    total_debits: ExtractedField
    transactions: TransactionsField

class LoanApplicationData(BaseModel):
    doc_type: str
    classification_confidence: Optional[float] = None
    classification_reasoning: Optional[str] = None
    full_name: ExtractedField
    date_of_birth: ExtractedField
    sin_last3: ExtractedField
    address: ExtractedField
    phone: ExtractedField
    email: ExtractedField
    employment_status: ExtractedField
    employer_name: ExtractedField
    job_title: ExtractedField
    years_employed: ExtractedField
    annual_income: ExtractedField
    loan_amount_requested: ExtractedField
    loan_purpose: ExtractedField
    loan_term_months: ExtractedField
    collateral: ExtractedField
    monthly_expenses: ExtractedField
    existing_monthly_debt: ExtractedField
    self_reported_credit_score: ExtractedField
    number_of_dependents: ExtractedField
    has_co_applicant: ExtractedField
    co_applicant_name: ExtractedField
    co_applicant_annual_income: ExtractedField

MODEL_MAP = {
    "invoice": InvoiceData,
    "bank_statement": BankStatementData,
    "loan_application": LoanApplicationData
}

def get_model(doc_type: str):
    if doc_type not in MODEL_MAP:
        raise ValueError(f"No model for doc type: {doc_type}")
    return MODEL_MAP[doc_type]