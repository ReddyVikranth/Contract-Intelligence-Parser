export type ContractStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface PartyInfo {
  name?: string;
  legal_entity?: string;
  registration_details?: string;
  signatories?: string[];
  roles?: string[];
}

export interface AccountInfo {
  billing_details?: string;
  account_numbers?: string[];
  contact_info?: {
    email?: string;
    phone?: string;
    [key: string]: string | undefined;
  };
}

export interface FinancialDetails {
  line_items?: any[];
  total_value?: number;
  currency?: string;
  tax_info?: any;
  additional_fees?: any[];
}

export interface PaymentStructure {
  payment_terms?: string;
  due_dates?: string[];
  payment_methods?: string[];
  banking_details?: { [key: string]: string };
}

export interface RevenueClassification {
  payment_type?: string;
  billing_cycle?: string;
  renewal_terms?: string;
  auto_renewal?: boolean;
}

export interface ServiceLevelAgreement {
  performance_metrics?: string[];
  penalty_clauses?: string[];
  support_terms?: string;
  maintenance_terms?: string;
}

export interface ExtractedData {
  party_identification?: PartyInfo;
  account_information?: AccountInfo;
  financial_details?: FinancialDetails;
  payment_structure?: PaymentStructure;
  revenue_classification?: RevenueClassification;
  service_level_agreements?: ServiceLevelAgreement;
}

export interface ConfidenceScores {
  financial_completeness: number;
  party_identification: number;
  payment_terms_clarity: number;
  sla_definition: number;
  contact_information: number;
  overall_score: number;
}

export interface GapAnalysis {
  missing_fields: string[];
  incomplete_sections: string[];
  recommendations: string[];
}

export interface Contract {
  contract_id: string;
  filename: string;
  file_size: number;
  status: ContractStatus;
  created_at: string;
  updated_at: string;
  progress_percentage: number;
  error_message?: string;
  extracted_data?: ExtractedData;
  confidence_scores?: ConfidenceScores;
  gap_analysis?: GapAnalysis;
}