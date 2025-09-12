import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContractParser:
    """Contract parsing and analysis service"""
    
    def __init__(self):
        self.financial_keywords = [
            'total', 'amount', 'price', 'cost', 'fee', 'payment', 'invoice',
            'billing', 'charge', 'rate', 'sum', 'value', '$', 'usd', 'dollar'
        ]
        
        self.party_keywords = [
            'party', 'parties', 'client', 'customer', 'vendor', 'supplier',
            'contractor', 'company', 'corporation', 'llc', 'inc', 'ltd'
        ]
        
        self.payment_terms_keywords = [
            'net 30', 'net 60', 'net 90', 'payment terms', 'due date',
            'payment schedule', 'billing cycle', 'monthly', 'quarterly', 'annually'
        ]
        
        self.sla_keywords = [
            'service level', 'sla', 'performance', 'uptime', 'availability',
            'response time', 'resolution time', 'penalty', 'remedies'
        ]
    
    def parse_contract(self, text_content: str) -> Dict[str, Any]:
        """Parse contract text and extract structured data"""
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text_content)
            
            # Extract different sections
            extracted_data = {
                "party_identification": self._extract_party_info(cleaned_text),
                "account_information": self._extract_account_info(cleaned_text),
                "financial_details": self._extract_financial_details(cleaned_text),
                "payment_structure": self._extract_payment_structure(cleaned_text),
                "revenue_classification": self._extract_revenue_classification(cleaned_text),
                "service_level_agreements": self._extract_sla_info(cleaned_text)
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing contract: {str(e)}")
            return self._get_empty_extracted_data()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _extract_party_info(self, text: str) -> Dict[str, Any]:
        """Extract party identification information"""
        party_info = {
            "name": None,
            "legal_entity": None,
            "registration_details": None,
            "signatories": [],
            "roles": []
        }
        
        # Extract company names (basic pattern matching)
        company_patterns = [
            r'([A-Z][a-zA-Z\s]+(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.|Limited))',
            r'("([^"]+(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.|Limited))")',
        ]
        
        companies = []
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    companies.append(match[0] if match[0] else match[1])
                else:
                    companies.append(match)
        
        if companies:
            party_info["name"] = companies[0]
            party_info["legal_entity"] = companies[0]
        
        # Extract signatories (basic pattern)
        signatory_patterns = [
            r'signed by:?\s*([A-Z][a-zA-Z\s]+)',
            r'signature:?\s*([A-Z][a-zA-Z\s]+)',
            r'authorized by:?\s*([A-Z][a-zA-Z\s]+)'
        ]
        
        signatories = []
        for pattern in signatory_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signatories.extend(matches)
        
        party_info["signatories"] = list(set(signatories))[:5]  # Limit to 5
        
        return party_info
    
    def _extract_account_info(self, text: str) -> Dict[str, Any]:
        """Extract account information"""
        account_info = {
            "billing_details": None,
            "account_numbers": [],
            "contact_info": {}
        }
        
        # Extract account numbers
        account_patterns = [
            r'account\s*(?:number|#):?\s*([A-Z0-9\-]+)',
            r'customer\s*(?:id|number):?\s*([A-Z0-9\-]+)',
            r'reference\s*(?:number|#):?\s*([A-Z0-9\-]+)'
        ]
        
        account_numbers = []
        for pattern in account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            account_numbers.extend(matches)
        
        account_info["account_numbers"] = list(set(account_numbers))
        
        # Extract contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        if emails:
            account_info["contact_info"]["email"] = emails[0]
        
        if phones:
            account_info["contact_info"]["phone"] = f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
        
        return account_info
    
    def _extract_financial_details(self, text: str) -> Dict[str, Any]:
        """Extract financial details"""
        financial_details = {
            "line_items": [],
            "total_value": None,
            "currency": "USD",
            "tax_info": {},
            "additional_fees": []
        }
        
        # Extract monetary amounts
        money_patterns = [
            r'\$\s*([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*(?:dollars?|usd)',
            r'total:?\s*\$?\s*([0-9,]+\.?[0-9]*)',
            r'amount:?\s*\$?\s*([0-9,]+\.?[0-9]*)'
        ]
        
        amounts = []
        for pattern in money_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue
        
        if amounts:
            financial_details["total_value"] = max(amounts)  # Assume largest amount is total
        
        # Extract currency
        currency_pattern = r'\b(USD|EUR|GBP|CAD|AUD)\b'
        currency_match = re.search(currency_pattern, text, re.IGNORECASE)
        if currency_match:
            financial_details["currency"] = currency_match.group(1).upper()
        
        return financial_details
    
    def _extract_payment_structure(self, text: str) -> Dict[str, Any]:
        """Extract payment structure information"""
        payment_structure = {
            "payment_terms": None,
            "due_dates": [],
            "payment_methods": [],
            "banking_details": {}
        }
        
        # Extract payment terms
        payment_terms_patterns = [
            r'net\s*(\d+)',
            r'payment\s*terms?:?\s*([^.\n]+)',
            r'due\s*(?:in|within):?\s*(\d+\s*days?)'
        ]
        
        for pattern in payment_terms_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                payment_structure["payment_terms"] = match.group(0)
                break
        
        # Extract payment methods
        payment_methods_patterns = [
            r'(?:payment\s*(?:by|via|through):?\s*)?(?:check|cheque|wire\s*transfer|ach|credit\s*card|bank\s*transfer)',
        ]
        
        methods = []
        for pattern in payment_methods_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            methods.extend(matches)
        
        payment_structure["payment_methods"] = list(set(methods))
        
        return payment_structure
    
    def _extract_revenue_classification(self, text: str) -> Dict[str, Any]:
        """Extract revenue classification"""
        revenue_classification = {
            "payment_type": None,
            "billing_cycle": None,
            "renewal_terms": None,
            "auto_renewal": None
        }
        
        # Determine payment type
        recurring_keywords = ['monthly', 'quarterly', 'annually', 'subscription', 'recurring']
        one_time_keywords = ['one-time', 'lump sum', 'upfront', 'single payment']
        
        text_lower = text.lower()
        
        has_recurring = any(keyword in text_lower for keyword in recurring_keywords)
        has_one_time = any(keyword in text_lower for keyword in one_time_keywords)
        
        if has_recurring and has_one_time:
            revenue_classification["payment_type"] = "both"
        elif has_recurring:
            revenue_classification["payment_type"] = "recurring"
        elif has_one_time:
            revenue_classification["payment_type"] = "one-time"
        
        # Extract billing cycle
        billing_cycle_pattern = r'\b(monthly|quarterly|annually|yearly|weekly)\b'
        cycle_match = re.search(billing_cycle_pattern, text, re.IGNORECASE)
        if cycle_match:
            revenue_classification["billing_cycle"] = cycle_match.group(1).lower()
        
        # Check for auto-renewal
        auto_renewal_keywords = ['auto-renew', 'automatically renew', 'auto renewal']
        revenue_classification["auto_renewal"] = any(
            keyword in text_lower for keyword in auto_renewal_keywords
        )
        
        return revenue_classification
    
    def _extract_sla_info(self, text: str) -> Dict[str, Any]:
        """Extract service level agreement information"""
        sla_info = {
            "performance_metrics": [],
            "penalty_clauses": [],
            "support_terms": None,
            "maintenance_terms": None
        }
        
        # Extract performance metrics
        performance_patterns = [
            r'(\d+%?\s*uptime)',
            r'(\d+\s*(?:hours?|minutes?|seconds?)\s*response\s*time)',
            r'(availability:?\s*\d+%?)'
        ]
        
        metrics = []
        for pattern in performance_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend(matches)
        
        sla_info["performance_metrics"] = metrics
        
        # Extract penalty information
        penalty_patterns = [
            r'(penalty:?\s*[^.\n]+)',
            r'(liquidated\s*damages:?\s*[^.\n]+)',
            r'(service\s*credits?:?\s*[^.\n]+)'
        ]
        
        penalties = []
        for pattern in penalty_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            penalties.extend(matches)
        
        sla_info["penalty_clauses"] = penalties
        
        return sla_info
    
    def calculate_confidence_scores(self, extracted_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for extracted data"""
        scores = {
            "financial_completeness": 0.0,
            "party_identification": 0.0,
            "payment_terms_clarity": 0.0,
            "sla_definition": 0.0,
            "contact_information": 0.0,
            "overall_score": 0.0
        }
        
        # Financial completeness (30 points)
        financial = extracted_data.get("financial_details", {})
        if financial.get("total_value"):
            scores["financial_completeness"] += 15
        if financial.get("currency"):
            scores["financial_completeness"] += 5
        if financial.get("line_items"):
            scores["financial_completeness"] += 10
        
        # Party identification (25 points)
        party = extracted_data.get("party_identification", {})
        if party.get("name"):
            scores["party_identification"] += 10
        if party.get("legal_entity"):
            scores["party_identification"] += 8
        if party.get("signatories"):
            scores["party_identification"] += 7
        
        # Payment terms clarity (20 points)
        payment = extracted_data.get("payment_structure", {})
        if payment.get("payment_terms"):
            scores["payment_terms_clarity"] += 10
        if payment.get("payment_methods"):
            scores["payment_terms_clarity"] += 5
        if payment.get("due_dates"):
            scores["payment_terms_clarity"] += 5
        
        # SLA definition (15 points)
        sla = extracted_data.get("service_level_agreements", {})
        if sla.get("performance_metrics"):
            scores["sla_definition"] += 8
        if sla.get("penalty_clauses"):
            scores["sla_definition"] += 4
        if sla.get("support_terms"):
            scores["sla_definition"] += 3
        
        # Contact information (10 points)
        account = extracted_data.get("account_information", {})
        contact_info = account.get("contact_info", {}) if account else {}
        if contact_info.get("email"):
            scores["contact_information"] += 5
        if contact_info.get("phone"):
            scores["contact_information"] += 3
        if account and account.get("account_numbers"):
            scores["contact_information"] += 2
        
        # Calculate overall score
        scores["overall_score"] = sum(scores.values()) - scores["overall_score"]
        
        return scores
    
    def perform_gap_analysis(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform gap analysis to identify missing information"""
        missing_fields = []
        incomplete_sections = []
        recommendations = []
        
        # Check financial details
        financial = extracted_data.get("financial_details", {})
        if not financial.get("total_value"):
            missing_fields.append("Total contract value")
        if not financial.get("line_items"):
            missing_fields.append("Detailed line items")
        if not financial.get("tax_info"):
            incomplete_sections.append("Tax information")
        
        # Check party identification
        party = extracted_data.get("party_identification", {})
        if not party.get("name"):
            missing_fields.append("Party names")
        if not party.get("signatories"):
            missing_fields.append("Authorized signatories")
        
        # Check payment structure
        payment = extracted_data.get("payment_structure", {})
        if not payment.get("payment_terms"):
            missing_fields.append("Payment terms")
        if not payment.get("payment_methods"):
            missing_fields.append("Payment methods")
        
        # Check SLA
        sla = extracted_data.get("service_level_agreements", {})
        if not sla.get("performance_metrics"):
            missing_fields.append("Performance metrics")
        
        # Check contact information
        account = extracted_data.get("account_information", {})
        if not account or not account.get("contact_info"):
            missing_fields.append("Contact information")
        
        # Generate recommendations
        if missing_fields:
            recommendations.append("Request additional contract documentation to fill missing fields")
        
        if len(missing_fields) > 5:
            recommendations.append("Consider manual review due to significant missing information")
        
        if not financial.get("total_value"):
            recommendations.append("Verify contract value with client before processing payments")
        
        return {
            "missing_fields": missing_fields,
            "incomplete_sections": incomplete_sections,
            "recommendations": recommendations
        }
    
    def _get_empty_extracted_data(self) -> Dict[str, Any]:
        """Return empty extracted data structure"""
        return {
            "party_identification": {},
            "account_information": {},
            "financial_details": {},
            "payment_structure": {},
            "revenue_classification": {},
            "service_level_agreements": {}
        }