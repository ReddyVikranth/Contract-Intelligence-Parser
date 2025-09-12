import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { uploadContract } from '../services/api';

const ContractUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      toast.error('Only PDF files are supported');
      return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB');
      return;
    }

    setUploadedFile(file);
    setUploading(true);

    try {
      const response = await uploadContract(file);
      toast.success('Contract uploaded successfully! Processing started.');
      
      // Navigate to contract detail page
      navigate(`/contracts/${response.contract_id}`);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload contract. Please try again.');
      setUploadedFile(null);
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: uploading
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Contract for Analysis
        </h1>
        <p className="text-lg text-gray-600">
          Upload your PDF contract to extract key information, financial details, and generate confidence scores
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : uploading
              ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
              : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
          }`}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="text-lg font-medium text-gray-700">
                  Uploading and processing...
                </p>
                <p className="text-sm text-gray-500">
                  This may take a few moments
                </p>
              </>
            ) : uploadedFile ? (
              <>
                <CheckCircle className="w-12 h-12 text-green-600" />
                <p className="text-lg font-medium text-gray-700">
                  {uploadedFile.name}
                </p>
                <p className="text-sm text-gray-500">
                  File ready for processing
                </p>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400" />
                <p className="text-lg font-medium text-gray-700">
                  {isDragActive
                    ? 'Drop your contract here'
                    : 'Drag & drop your contract here, or click to select'}
                </p>
                <p className="text-sm text-gray-500">
                  PDF files only, up to 50MB
                </p>
              </>
            )}
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start space-x-3">
            <FileText className="w-6 h-6 text-blue-600 mt-1" />
            <div>
              <h3 className="font-medium text-gray-900">Smart Extraction</h3>
              <p className="text-sm text-gray-600">
                Automatically extract parties, financial details, and payment terms
              </p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600 mt-1" />
            <div>
              <h3 className="font-medium text-gray-900">Confidence Scoring</h3>
              <p className="text-sm text-gray-600">
                Get reliability scores for extracted data with gap analysis
              </p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-orange-600 mt-1" />
            <div>
              <h3 className="font-medium text-gray-900">Gap Analysis</h3>
              <p className="text-sm text-gray-600">
                Identify missing information and get recommendations
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContractUpload;