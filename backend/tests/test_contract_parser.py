import pytest
from app.services.contract_parser import ContractParser

class TestContractParser:
    
    @pytest.fixture
    def parser(self):
        """Contract parser fixture"""
        return ContractParser()
    
    @pytest.fixture
    def sample_contract_text(self):
        """Sample contract text for testing"""
        return """
        SERVICE AGREEMENT
        
        This agreement is between ABC Corporation Inc. and XYZ Services LLC.
        
        Total contract value: $50,000 USD
        Payment terms: Net 30 days
        
        Contact: john.doe@abccorp.com
        Phone: (555) 123-4567
        Account Number: ACC-12345
        
        Service Level Agreement:
        - 99.9% uptime guarantee
        - 4 hour response time
        - Monthly billing cycle
        
        Signed by: John Smith, CEO
        """
    
    def test_parse_contract_success(self, parser, sample_contract_text):
        """Test successful contract parsing"""
        result = parser.parse_contract(sample_contract_text)
        
        # Check structure
        assert "party_identification" in result
        assert "account_information" in result
        assert "financial_details" in result
        assert "payment_structure" in result
        assert "revenue_classification" in result
        assert "service_level_agreements" in result
    
    def test_extract_party_info(self, parser, sample_contract_text):
        """Test party information extraction"""
        result = parser.parse_contract(sample_contract_text)
        party_info = result["party_identification"]
        
        assert party_info["name"] is not None
        assert "Corporation" in party_info["name"] or "LLC" in party_info["name"]
        assert len(party_info["signatories"]) > 0
        assert "John Smith" in party_info["signatories"]
    
    def test_extract_financial_details(self, parser, sample_contract_text):
        """Test financial details extraction"""
        result = parser.parse_contract(sample_contract_text)
        financial = result["financial_details"]
        
        assert financial["total_value"] == 50000.0
        assert financial["currency"] == "USD"
    
    def test_extract_account_info(self, parser, sample_contract_text):
        """Test account information extraction"""
        result = parser.parse_contract(sample_contract_text)
        account = result["account_information"]
        
        assert "ACC-12345" in account["account_numbers"]
        assert account["contact_info"]["email"] == "john.doe@abccorp.com"
        assert account["contact_info"]["phone"] == "(555) 123-4567"
    
    def test_extract_payment_structure(self, parser, sample_contract_text):
        """Test payment structure extraction"""
        result = parser.parse_contract(sample_contract_text)
        payment = result["payment_structure"]
        
        assert "net 30" in payment["payment_terms"].lower()
    
    def test_extract_revenue_classification(self, parser, sample_contract_text):
        """Test revenue classification extraction"""
        result = parser.parse_contract(sample_contract_text)
        revenue = result["revenue_classification"]
        
        assert revenue["billing_cycle"] == "monthly"
    
    def test_extract_sla_info(self, parser, sample_contract_text):
        """Test SLA information extraction"""
        result = parser.parse_contract(sample_contract_text)
        sla = result["service_level_agreements"]
        
        assert len(sla["performance_metrics"]) > 0
        assert any("99.9%" in metric for metric in sla["performance_metrics"])
    
    def test_calculate_confidence_scores(self, parser, sample_contract_text):
        """Test confidence score calculation"""
        extracted_data = parser.parse_contract(sample_contract_text)
        scores = parser.calculate_confidence_scores(extracted_data)
        
        # Check score structure
        assert "financial_completeness" in scores
        assert "party_identification" in scores
        assert "payment_terms_clarity" in scores
        assert "sla_definition" in scores
        assert "contact_information" in scores
        assert "overall_score" in scores
        
        # Check score ranges
        for key, score in scores.items():
            assert 0 <= score <= 100
        
        # Overall score should be sum of others
        expected_overall = sum(v for k, v in scores.items() if k != "overall_score")
        assert scores["overall_score"] == expected_overall
    
    def test_perform_gap_analysis(self, parser):
        """Test gap analysis functionality"""
        # Test with minimal data
        minimal_data = {
            "party_identification": {},
            "account_information": {},
            "financial_details": {},
            "payment_structure": {},
            "revenue_classification": {},
            "service_level_agreements": {}
        }
        
        gap_analysis = parser.perform_gap_analysis(minimal_data)
        
        # Check structure
        assert "missing_fields" in gap_analysis
        assert "incomplete_sections" in gap_analysis
        assert "recommendations" in gap_analysis
        
        # Should have many missing fields
        assert len(gap_analysis["missing_fields"]) > 0
        assert len(gap_analysis["recommendations"]) > 0
    
    def test_clean_text(self, parser):
        """Test text cleaning functionality"""
        messy_text = "  This   is    messy\n\n\ntext   with   extra   spaces  "
        cleaned = parser._clean_text(messy_text)
        
        assert cleaned == "This is messy text with extra spaces"
    
    def test_empty_contract_parsing(self, parser):
        """Test parsing empty or invalid contract"""
        result = parser.parse_contract("")
        
        # Should return empty structure without errors
        assert isinstance(result, dict)
        assert "party_identification" in result
    
    def test_confidence_scores_with_complete_data(self, parser):
        """Test confidence scores with complete data"""
        complete_data = {
            "party_identification": {
                "name": "Test Corp",
                "legal_entity": "Test Corp Inc.",
                "signatories": ["John Doe"]
            },
            "account_information": {
                "account_numbers": ["ACC-123"],
                "contact_info": {"email": "test@test.com", "phone": "555-1234"}
            },
            "financial_details": {
                "total_value": 10000,
                "currency": "USD",
                "line_items": [{"item": "service", "amount": 10000}]
            },
            "payment_structure": {
                "payment_terms": "Net 30",
                "payment_methods": ["check"],
                "due_dates": ["2024-01-01"]
            },
            "service_level_agreements": {
                "performance_metrics": ["99% uptime"],
                "penalty_clauses": ["5% penalty"],
                "support_terms": "24/7 support"
            }
        }
        
        scores = parser.calculate_confidence_scores(complete_data)
        
        # Should have high scores for complete data
        assert scores["financial_completeness"] > 20
        assert scores["party_identification"] > 15
        assert scores["payment_terms_clarity"] > 10
        assert scores["sla_definition"] > 10
        assert scores["contact_information"] > 5