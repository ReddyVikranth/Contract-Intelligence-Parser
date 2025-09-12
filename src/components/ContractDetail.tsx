import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Download,
  Users,
  DollarSign,
  CreditCard,
  Repeat,
  Shield,
  Phone,
  Mail,
  Building,
  Calendar
} from 'lucide-react';
import { getContract, getContractStatus, downloadContract } from '../services/api';
import { Contract } from '../types/contract';
import toast from 'react-hot-toast';

const ContractDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [contract, setContract] = useState<Contract | null>(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (id) {
      fetchContract();
    }
  }, [id]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (contract && (contract.status === 'pending' || contract.status === 'processing')) {
      setPolling(true);
      interval = setInterval(async () => {
        try {
          const status = await getContractStatus(contract.contract_id);
          setContract(prev => prev ? { ...prev, ...status } : null);
          
          if (status.status === 'completed' || status.status === 'failed') {
            setPolling(false);
            if (status.status === 'completed') {
              // Fetch full contract data
              fetchContract();
            }
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
      setPolling(false);
    };
  }, [contract?.status, contract?.contract_id]);

  const fetchContract = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const contractData = await getContract(id);
      setContract(contractData);
    } catch (error: any) {
      console.error('Error fetching contract:', error);
      if (error.response?.status === 400) {
        // Contract not ready yet, fetch status instead
        try {
          const status = await getContractStatus(id);
          setContract({
            contract_id: id,
            filename: 'Loading...',
            file_size: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            ...status
          } as Contract);
        } catch (statusError) {
          toast.error('Contract not found');
        }
      } else {
        toast.error('Failed to load contract');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!contract) return;
    
    try {
      await downloadContract(contract.contract_id, contract.filename);
      toast.success('Contract downloaded successfully');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download contract');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'processing':
        return <AlertCircle className="w-5 h-5 text-blue-600" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="text-center py-12">
        <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Contract not found</h3>
        <Link to="/contracts" className="text-blue-600 hover:text-blue-800">
          Back to contracts
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Link
            to="/contracts"
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to contracts</span>
          </Link>
        </div>
        
        <button
          onClick={handleDownload}
          className="flex items-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Download</span>
        </button>
      </div>

      {/* Contract Info */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <FileText className="w-12 h-12 text-blue-600 mt-1" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {contract.filename}
              </h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>{formatFileSize(contract.file_size)}</span>
                <span>•</span>
                <span>Uploaded {formatDate(contract.created_at)}</span>
                {contract.updated_at !== contract.created_at && (
                  <>
                    <span>•</span>
                    <span>Updated {formatDate(contract.updated_at)}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {getStatusIcon(contract.status)}
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(contract.status)}`}>
              {contract.status}
            </span>
            {contract.status === 'processing' && (
              <span className="text-sm text-gray-500">
                {contract.progress_percentage}%
              </span>
            )}
          </div>
        </div>

        {/* Progress Bar for Processing */}
        {contract.status === 'processing' && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${contract.progress_percentage}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Processing contract... {polling && '(Auto-refreshing)'}
            </p>
          </div>
        )}

        {/* Error Message */}
        {contract.status === 'failed' && contract.error_message && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <XCircle className="w-5 h-5 text-red-600" />
              <span className="font-medium text-red-800">Processing Failed</span>
            </div>
            <p className="text-red-700 mt-1">{contract.error_message}</p>
          </div>
        )}
      </div>

      {/* Contract Data - Only show if completed */}
      {contract.status === 'completed' && contract.extracted_data && (
        <>
          {/* Confidence Scores */}
          {contract.confidence_scores && (
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Confidence Scores</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {Math.round(contract.confidence_scores.overall_score)}%
                  </div>
                  <div className="text-sm font-medium text-gray-700">Overall Score</div>
                </div>
                
                {Object.entries(contract.confidence_scores)
                  .filter(([key]) => key !== 'overall_score')
                  .map(([key, value]) => (
                    <div key={key}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="text-sm text-gray-600">
                          {Math.round(value)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${value}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Extracted Data */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Party Identification */}
            {contract.extracted_data.party_identification && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Users className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Party Identification</h3>
                </div>
                
                <div className="space-y-3">
                  {contract.extracted_data.party_identification.name && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Name:</span>
                      <p className="text-gray-900">{contract.extracted_data.party_identification.name}</p>
                    </div>
                  )}
                  
                  {contract.extracted_data.party_identification.legal_entity && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Legal Entity:</span>
                      <p className="text-gray-900">{contract.extracted_data.party_identification.legal_entity}</p>
                    </div>
                  )}
                  
                  {contract.extracted_data.party_identification.signatories && 
                   contract.extracted_data.party_identification.signatories.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Signatories:</span>
                      <ul className="text-gray-900 list-disc list-inside">
                        {contract.extracted_data.party_identification.signatories.map((signatory, index) => (
                          <li key={index}>{signatory}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Financial Details */}
            {contract.extracted_data.financial_details && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Financial Details</h3>
                </div>
                
                <div className="space-y-3">
                  {contract.extracted_data.financial_details.total_value && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Total Value:</span>
                      <p className="text-gray-900 text-lg font-semibold">
                        {contract.extracted_data.financial_details.currency || 'USD'} {contract.extracted_data.financial_details.total_value.toLocaleString()}
                      </p>
                    </div>
                  )}
                  
                  {contract.extracted_data.financial_details.currency && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Currency:</span>
                      <p className="text-gray-900">{contract.extracted_data.financial_details.currency}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Payment Structure */}
            {contract.extracted_data.payment_structure && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <CreditCard className="w-5 h-5 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Payment Structure</h3>
                </div>
                
                <div className="space-y-3">
                  {contract.extracted_data.payment_structure.payment_terms && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Payment Terms:</span>
                      <p className="text-gray-900">{contract.extracted_data.payment_structure.payment_terms}</p>
                    </div>
                  )}
                  
                  {contract.extracted_data.payment_structure.payment_methods && 
                   contract.extracted_data.payment_structure.payment_methods.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Payment Methods:</span>
                      <ul className="text-gray-900 list-disc list-inside">
                        {contract.extracted_data.payment_structure.payment_methods.map((method, index) => (
                          <li key={index}>{method}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Revenue Classification */}
            {contract.extracted_data.revenue_classification && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Repeat className="w-5 h-5 text-orange-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Revenue Classification</h3>
                </div>
                
                <div className="space-y-3">
                  {contract.extracted_data.revenue_classification.payment_type && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Payment Type:</span>
                      <p className="text-gray-900 capitalize">{contract.extracted_data.revenue_classification.payment_type}</p>
                    </div>
                  )}
                  
                  {contract.extracted_data.revenue_classification.billing_cycle && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Billing Cycle:</span>
                      <p className="text-gray-900 capitalize">{contract.extracted_data.revenue_classification.billing_cycle}</p>
                    </div>
                  )}
                  
                  {contract.extracted_data.revenue_classification.auto_renewal !== null && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Auto Renewal:</span>
                      <p className="text-gray-900">
                        {contract.extracted_data.revenue_classification.auto_renewal ? 'Yes' : 'No'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Account Information */}
            {contract.extracted_data.account_information && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Building className="w-5 h-5 text-indigo-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Account Information</h3>
                </div>
                
                <div className="space-y-3">
                  {contract.extracted_data.account_information.account_numbers && 
                   contract.extracted_data.account_information.account_numbers.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Account Numbers:</span>
                      <ul className="text-gray-900 list-disc list-inside">
                        {contract.extracted_data.account_information.account_numbers.map((number, index) => (
                          <li key={index}>{number}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {contract.extracted_data.account_information.contact_info && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Contact Information:</span>
                      <div className="mt-2 space-y-2">
                        {contract.extracted_data.account_information.contact_info.email && (
                          <div className="flex items-center space-x-2">
                            <Mail className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-900">{contract.extracted_data.account_information.contact_info.email}</span>
                          </div>
                        )}
                        {contract.extracted_data.account_information.contact_info.phone && (
                          <div className="flex items-center space-x-2">
                            <Phone className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-900">{contract.extracted_data.account_information.contact_info.phone}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Service Level Agreements */}
            {contract.extracted_data.service_level_agreements && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Shield className="w-5 h-5 text-red-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Service Level Agreements</h3>
                </div>
                
                <div className="space-y-3">
                  {contract.extracted_data.service_level_agreements.performance_metrics && 
                   contract.extracted_data.service_level_agreements.performance_metrics.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Performance Metrics:</span>
                      <ul className="text-gray-900 list-disc list-inside">
                        {contract.extracted_data.service_level_agreements.performance_metrics.map((metric, index) => (
                          <li key={index}>{metric}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {contract.extracted_data.service_level_agreements.penalty_clauses && 
                   contract.extracted_data.service_level_agreements.penalty_clauses.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Penalty Clauses:</span>
                      <ul className="text-gray-900 list-disc list-inside">
                        {contract.extracted_data.service_level_agreements.penalty_clauses.map((clause, index) => (
                          <li key={index}>{clause}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Gap Analysis */}
          {contract.gap_analysis && (
            <div className="bg-white rounded-lg shadow-sm p-6 mt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Gap Analysis</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {contract.gap_analysis.missing_fields && contract.gap_analysis.missing_fields.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-800 mb-2">Missing Fields</h4>
                    <ul className="text-sm text-red-700 space-y-1">
                      {contract.gap_analysis.missing_fields.map((field, index) => (
                        <li key={index}>• {field}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {contract.gap_analysis.incomplete_sections && contract.gap_analysis.incomplete_sections.length > 0 && (
                  <div>
                    <h4 className="font-medium text-yellow-800 mb-2">Incomplete Sections</h4>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      {contract.gap_analysis.incomplete_sections.map((section, index) => (
                        <li key={index}>• {section}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {contract.gap_analysis.recommendations && contract.gap_analysis.recommendations.length > 0 && (
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">Recommendations</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      {contract.gap_analysis.recommendations.map((recommendation, index) => (
                        <li key={index}>• {recommendation}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ContractDetail;