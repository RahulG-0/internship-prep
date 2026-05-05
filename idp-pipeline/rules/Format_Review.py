from config import APPROVAL_THRESHOLD, CONFIDENCE_THRESHOLD, DTI_THRESHOLD

class RulesEngine:
    
    def apply(self, validated: dict, doc_type: str) -> dict:
        data = validated["data"]
        flags = {}
        needs_review = False

        if not validated.get("valid", False):
            flags = {"validation_errors": validated.get("errors", [])}
            if doc_type == "unknown":
                flags["unsupported_document_type"] = True
            return {
                **validated,
                "flags": flags,
                "needs_review": True
            }

        if doc_type == "invoice":
            flags, needs_review = self._apply_invoice_rules(data)
        elif doc_type == "bank_statement":
            flags, needs_review = self._apply_bank_statement_rules(data)
        elif doc_type == "loan_application":
            flags, needs_review = self._apply_loan_application_rules(data)

        low_confidence_fields = self._check_confidence(data)
        if low_confidence_fields:
            flags["low_confidence_fields"] = low_confidence_fields
            needs_review = True

        return {
            **validated,
            "flags": flags,
            "needs_review": needs_review
        }

    def _apply_invoice_rules(self, data) -> tuple:
        flags = {}
        needs_review = False

        try:
            line_items = data.line_items.value or []
            calculated_subtotal = sum(
                item.line_total for item in line_items
                if item.line_total is not None
            )
            stated_subtotal = data.subtotal.value or 0
            flags["line_items_match_subtotal"] = (
                abs(calculated_subtotal - stated_subtotal) < 0.01
            )
            if not flags["line_items_match_subtotal"]:
                needs_review = True
        except Exception:
            flags["line_items_match_subtotal"] = False
            needs_review = True

        try:
            total = data.total_amount.value or 0
            flags["exceeds_approval_threshold"] = total > APPROVAL_THRESHOLD
            if flags["exceeds_approval_threshold"]:
                needs_review = True
        except Exception:
            flags["exceeds_approval_threshold"] = False

        try:
            from datetime import date
            due_date_str = data.due_date.value
            if due_date_str:
                due_date = date.fromisoformat(due_date_str)
                flags["is_overdue"] = due_date < date.today()
                if flags["is_overdue"]:
                    needs_review = True
            else:
                flags["is_overdue"] = False
        except Exception:
            flags["is_overdue"] = False

        return flags, needs_review

    def _apply_bank_statement_rules(self, data) -> tuple:
        flags = {}
        needs_review = False

        try:
            opening = data.opening_balance.value or 0
            closing = data.closing_balance.value or 0
            credits = data.total_credits.value or 0
            debits = data.total_debits.value or 0
            expected_closing = opening + credits - debits
            flags["balances_reconcile"] = abs(expected_closing - closing) < 0.01
            if not flags["balances_reconcile"]:
                needs_review = True
        except Exception:
            flags["balances_reconcile"] = False
            needs_review = True

        try:
            transactions = data.transactions.value or []
            large_transactions = [
                t for t in transactions
                if t.amount and t.amount > APPROVAL_THRESHOLD
            ]
            flags["has_large_transactions"] = len(large_transactions) > 0
            if flags["has_large_transactions"]:
                needs_review = True
        except Exception:
            flags["has_large_transactions"] = False

        try:
            transactions = data.transactions.value or []
            dates = [t.date for t in transactions if t.date]
            flags["dates_are_sequential"] = dates == sorted(dates)
            if not flags["dates_are_sequential"]:
                needs_review = True
        except Exception:
            flags["dates_are_sequential"] = False

        return flags, needs_review

    def _apply_loan_application_rules(self, data) -> tuple:
        flags = {}
        needs_review = False

        try:
            monthly_income = (data.annual_income.value or 0) / 12
            monthly_debt = data.existing_monthly_debt.value or 0
            dti = monthly_debt / monthly_income if monthly_income > 0 else 1.0
            flags["debt_to_income_ratio"] = round(dti, 4)
            flags["dti_exceeds_threshold"] = dti > DTI_THRESHOLD
            if flags["dti_exceeds_threshold"]:
                needs_review = True
        except Exception:
            flags["debt_to_income_ratio"] = None
            flags["dti_exceeds_threshold"] = True
            needs_review = True

        try:
            from datetime import date
            dob_str = data.date_of_birth.value
            if dob_str:
                dob = date.fromisoformat(dob_str)
                age = (date.today() - dob).days // 365
                flags["age_meets_minimum"] = age >= 18
                if not flags["age_meets_minimum"]:
                    needs_review = True
            else:
                flags["age_meets_minimum"] = False
                needs_review = True
        except Exception:
            flags["age_meets_minimum"] = False
            needs_review = True

        required_fields = [
            "full_name", "date_of_birth", "address",
            "annual_income", "loan_amount_requested", "employment_status"
        ]
        missing = [
            f for f in required_fields
            if getattr(data, f).value is None
        ]
        flags["missing_required_fields"] = missing
        if missing:
            needs_review = True

        try:
            monthly_income = (data.annual_income.value or 0) / 12
            loan_amount = data.loan_amount_requested.value or 0
            term = data.loan_term_months.value or 12
            monthly_payment_estimate = loan_amount / term
            flags["income_supports_loan"] = monthly_income > (monthly_payment_estimate * 3)
            if not flags["income_supports_loan"]:
                needs_review = True
        except Exception:
            flags["income_supports_loan"] = False
            needs_review = True

        return flags, needs_review

    def _check_confidence(self, data) -> list:
        low_confidence = []
        if hasattr(data, "model_fields"):
            items = (
                (field_name, getattr(data, field_name))
                for field_name in type(data).model_fields
            )
        elif isinstance(data, dict):
            items = data.items()
        else:
            return low_confidence

        for field_name, field_value in items:
            if hasattr(field_value, "confidence"):
                if (
                    field_value.confidence is not None
                    and field_value.confidence < CONFIDENCE_THRESHOLD
                ):
                    low_confidence.append(field_name)
            elif isinstance(field_value, dict):
                confidence = field_value.get("confidence")
                if confidence is not None and confidence < CONFIDENCE_THRESHOLD:
                    low_confidence.append(field_name)
        return low_confidence
