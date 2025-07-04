"""
Flask API routes for Compliance RAG Agent
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
import werkzeug
from flask_cors import CORS

from config import Config
from agent import ComplianceRAGAgent
from utils import allowed_file, handle_agent_error


def create_app(config: Config = None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for frontend integration
    
    # Use provided config or create default
    if config is None:
        config = Config()
    
    # Configure Flask app
    app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
    app.config['UPLOAD_FOLDER'] = config.upload_folder
    app.secret_key = config.secret_key
    
    # Global variables
    global_agent = None
    uploaded_file_paths = []
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'Compliance RAG Agent API',
            'agent_initialized': global_agent is not None
        })
    
    @app.route('/upload', methods=['POST'])
    def upload_files():
        """Handle file uploads."""
        nonlocal uploaded_file_paths
        
        try:
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            print(f"DEBUG: Upload folder: {app.config['UPLOAD_FOLDER']}")
            
            print(f"DEBUG: Request files: {list(request.files.keys())}")
            print(f"DEBUG: Request form: {list(request.form.keys())}")
            
            if 'files' not in request.files:
                print(f"DEBUG: No 'files' in request.files")
                return jsonify({'success': False, 'error': 'No files provided'})
            
            files = request.files.getlist('files')
            print(f"DEBUG: Number of files received: {len(files)}")
            
            uploaded_files = []
            
            for file in files:
                print(f"DEBUG: Processing file: {file.filename}")
                if file.filename == '':
                    print(f"DEBUG: Empty filename, skipping")
                    continue
                    
                if file and allowed_file(file.filename, config.allowed_extensions):
                    # Secure the filename
                    filename = werkzeug.utils.secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    print(f"DEBUG: Saving file to: {filepath}")
                    
                    # Save the file
                    file.save(filepath)
                    uploaded_files.append(filename)
                    uploaded_file_paths.append(filepath)
                    print(f"DEBUG: Successfully saved: {filename}")
                else:
                    print(f"DEBUG: File not allowed or invalid: {file.filename}")
            
            print(f"DEBUG: Total uploaded: {len(uploaded_files)}")
            return jsonify({
                'success': True, 
                'files': uploaded_files,
                'message': f'Successfully uploaded {len(uploaded_files)} files'
            })
            
        except Exception as e:
            print(f"DEBUG: Upload error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/setup_ingestion', methods=['POST'])
    def setup_ingestion():
        """Setup document ingestion with company description."""
        nonlocal global_agent
        
        try:
            data = request.get_json()
            company_description = data.get('company_description', '')
            
            if not company_description:
                return jsonify({'success': False, 'error': 'Company description is required'})
            
            # Initialize the agent if not already done
            if global_agent is None:
                global_agent = ComplianceRAGAgent(config)
            
            # Try agent invocation first, fallback to direct tool call
            try:
                result = global_agent.invoke(f"Set up document ingestion for {company_description}")
                output = result.get('output', 'Document ingestion setup complete')
                if isinstance(output, dict):
                    output = output.get('action_input', 'Document ingestion setup complete')
            except Exception as agent_error:
                # Fallback to direct tool invocation
                result = global_agent.invoke_direct("ingest_company_documents", company_description)
                output = result.get('output', 'Document ingestion setup complete')
            
            return jsonify({
                'success': True,
                'message': output
            })
            
        except Exception as e:
            error_message = handle_agent_error(e, 'setup ingestion')
            return jsonify({'success': False, 'error': error_message})

    @app.route('/process_files', methods=['POST'])
    def process_files():
        """Process uploaded files."""
        nonlocal global_agent, uploaded_file_paths
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized. Please setup ingestion first.'})
            
            if not uploaded_file_paths:
                return jsonify({'success': False, 'error': 'No files uploaded. Please upload files first.'})
            
            # Process files using the agent's method
            chunks_processed = global_agent.process_uploaded_files_sync(uploaded_file_paths)
            
            return jsonify({
                'success': True,
                'chunks': chunks_processed,
                'message': f'Successfully processed {chunks_processed} document chunks'
            })
            
        except Exception as e:
            error_message = handle_agent_error(e, 'file processing')
            return jsonify({'success': False, 'error': error_message})

    @app.route('/analyze/<regulation_type>', methods=['POST'])
    def analyze_regulation(regulation_type):
        """Analyze compliance against a specific regulation."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized.'})
            
            # Validate regulation type
            valid_regulations = ['GDPR', 'NIST', 'HIPAA', 'ISO27001']
            regulation_upper = regulation_type.upper()
            
            if regulation_upper not in valid_regulations:
                return jsonify({
                    'success': False, 
                    'error': f'Invalid regulation type. Must be one of: {", ".join(valid_regulations)}'
                })
            
            # Try agent invocation first, fallback to direct tool call
            try:
                result = global_agent.invoke(f"Analyze against {regulation_upper}")
                output = result.get('output', f'{regulation_upper} analysis completed')
                if isinstance(output, dict):
                    output = output.get('action_input', f'{regulation_upper} analysis completed')
            except Exception as agent_error:
                # Fallback to direct tool invocation
                result = global_agent.invoke_direct("compliance_gap_analysis", regulation_upper)
                output = result.get('output', f'{regulation_upper} analysis completed')
            
            return jsonify({
                'success': True,
                'regulation': regulation_upper,
                'message': output
            })
            
        except Exception as e:
            error_message = handle_agent_error(e, f'{regulation_type} analysis')
            return jsonify({'success': False, 'error': error_message})

    @app.route('/analyze_gdpr', methods=['POST'])
    def analyze_gdpr():
        """Analyze GDPR compliance (backward compatibility endpoint)."""
        return analyze_regulation('GDPR')

    @app.route('/generate_report', methods=['POST'])
    def generate_report():
        """Generate compliance report."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized.'})
            
            # Try agent invocation first, fallback to direct tool call
            try:
                result = global_agent.invoke("Generate comprehensive compliance report")
                output = result.get('output', 'Report generation completed')
                if isinstance(output, dict):
                    output = output.get('action_input', 'Report generation completed')
            except Exception as agent_error:
                # Fallback to direct tool invocation
                result = global_agent.invoke_direct("generate_compliance_report", "")
                output = result.get('output', 'Report generation completed')
            
            return jsonify({
                'success': True,
                'report': output
            })
            
        except Exception as e:
            error_message = handle_agent_error(e, 'report generation')
            return jsonify({'success': False, 'error': error_message})

    @app.route('/status', methods=['GET'])
    def get_status():
        """Get current compliance analysis status."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({
                    'success': True,
                    'agent_initialized': False,
                    'message': 'Agent not initialized'
                })
            
            return jsonify({
                'success': True,
                'agent_initialized': True,
                'company_description': global_agent.company_context.get('description', 'Not set'),
                'files_processed': global_agent.uploaded_files_processed,
                'document_chunks': len(global_agent.company_documents),
                'regulations_analyzed': list(global_agent.compliance_findings.keys()),
                'ready_for_report': bool(global_agent.compliance_findings)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/compliance_summary', methods=['GET'])
    def get_compliance_summary():
        """Get compliance summary data for the dashboard."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized'})
            
            # Debug print to trace compliance findings
            print('DEBUG: compliance_findings:', global_agent.compliance_findings)
            # Calculate summary from compliance findings
            total_requirements = 0
            total_compliant = 0
            total_warnings = 0
            total_failures = 0
            severity_breakdown = {
                'Critical': 0,
                'High': 0,
                'Medium': 0,
                'Low': 0
            }
            
            all_issues = []
            
            for regulation, analysis in global_agent.compliance_findings.items():
                if isinstance(analysis, dict):
                    total_requirements += analysis.get('total_requirements', 0)
                    total_compliant += analysis.get('compliant_count', 0)
                    total_warnings += analysis.get('warnings_count', 0)
                    total_failures += analysis.get('non_compliant_count', 0)
                    
                    # Process issues for severity breakdown
                    for issue in analysis.get('issues', []):
                        severity = issue.get('severity', 'medium').title()
                        if severity in severity_breakdown:
                            severity_breakdown[severity] += 1
                        all_issues.append(issue)
            
            return jsonify({
                'success': True,
                'summary': {
                    'rules_checked': total_requirements,
                    'passed': total_compliant,
                    'warnings': total_warnings,
                    'failures': total_failures
                },
                'severity_data': [
                    {'name': 'Critical', 'value': severity_breakdown['Critical'], 'color': '#EF4444'},
                    {'name': 'High', 'value': severity_breakdown['High'], 'color': '#F59E0B'},
                    {'name': 'Medium', 'value': severity_breakdown['Medium'], 'color': '#3B82F6'},
                    {'name': 'Low', 'value': severity_breakdown['Low'], 'color': '#10B981'}
                ],
                'total_issues': len(all_issues)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/risk_analysis', methods=['GET'])
    def get_risk_analysis():
        """Get risk analysis data for the dashboard."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized'})
            
            risks = []
            risk_id = 1
            
            for regulation, analysis in global_agent.compliance_findings.items():
                if isinstance(analysis, dict):
                    for issue in analysis.get('issues', []):
                        if issue.get('status') in ['warning', 'error']:
                            risks.append({
                                'id': risk_id,
                                'title': issue.get('title', 'Compliance Issue'),
                                'description': issue.get('description', 'No description available'),
                                'severity': issue.get('severity', 'medium'),
                                'regulation': f"{regulation} {issue.get('section', '')}",
                                'recommendation': issue.get('suggestion', 'Review and address the identified compliance gap.')
                            })
                            risk_id += 1
            
            return jsonify({
                'success': True,
                'risks': risks,
                'total_issues': len(risks)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/project_overview', methods=['GET'])
    def get_project_overview():
        """Get project overview data for the dashboard."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized'})
            
            # Determine overall compliance status
            overall_status = 'Compliant'
            if global_agent.compliance_findings:
                has_errors = any(
                    isinstance(analysis, dict) and analysis.get('non_compliant_count', 0) > 0
                    for analysis in global_agent.compliance_findings.values()
                )
                if has_errors:
                    overall_status = 'Non-Compliant'
                elif any(
                    isinstance(analysis, dict) and analysis.get('warnings_count', 0) > 0
                    for analysis in global_agent.compliance_findings.values()
                ):
                    overall_status = 'Partial'
            
            return jsonify({
                'success': True,
                'overview': {
                    'project_name': global_agent.company_context.get('description', 'Unknown Project'),
                    'project_id': f"PRJ-{datetime.now().strftime('%Y%m%d')}",
                    'analysis_date': datetime.now().strftime('%B %d, %Y'),
                    'scanned_by': 'ComplianceAI Agent #C-4321',
                    'documents_evaluated': ', '.join(global_agent.company_context.get('processed_files', [])),
                    'compliance_status': overall_status,
                    'key_regulations': list(global_agent.compliance_findings.keys())
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/compliance_issues', methods=['GET'])
    def get_compliance_issues():
        """Get detailed compliance issues for the compliance tab."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized'})
            
            all_issues = []
            issue_id = 1
            
            for regulation, analysis in global_agent.compliance_findings.items():
                if isinstance(analysis, dict):
                    for issue in analysis.get('issues', []):
                        all_issues.append({
                            'id': issue_id,
                            'title': issue.get('title', 'Compliance Issue'),
                            'status': issue.get('status', 'warning'),
                            'description': issue.get('description', 'No description available'),
                            'suggestion': issue.get('suggestion', 'Review and address the identified compliance gap.'),
                            'regulation': regulation,
                            'section': issue.get('section', 'General')
                        })
                        issue_id += 1
            
            return jsonify({
                'success': True,
                'issues': all_issues,
                'total_requirements': sum(
                    analysis.get('total_requirements', 0) 
                    for analysis in global_agent.compliance_findings.values() 
                    if isinstance(analysis, dict)
                ),
                'compliant_count': sum(
                    analysis.get('compliant_count', 0) 
                    for analysis in global_agent.compliance_findings.values() 
                    if isinstance(analysis, dict)
                ),
                'non_compliant_count': sum(
                    analysis.get('non_compliant_count', 0) 
                    for analysis in global_agent.compliance_findings.values() 
                    if isinstance(analysis, dict)
                )
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/uploaded_files', methods=['GET'])
    def get_uploaded_files():
        """Get information about uploaded files."""
        nonlocal global_agent, uploaded_file_paths
        
        try:
            if global_agent is None:
                return jsonify({
                    'success': True,
                    'files': [],
                    'message': 'No agent initialized'
                })
            
            files_info = []
            for i, filepath in enumerate(uploaded_file_paths):
                try:
                    filename = os.path.basename(filepath)
                    file_size = os.path.getsize(filepath)
                    upload_time = os.path.getctime(filepath)
                    
                    # Determine status based on agent state
                    status = 'processed' if global_agent.uploaded_files_processed else 'uploaded'
                    
                    files_info.append({
                        'id': i + 1,
                        'name': filename,
                        'size': f"{file_size / (1024*1024):.1f} MB",
                        'upload_date': datetime.fromtimestamp(upload_time).isoformat(),
                        'status': status,
                        'issues': 0  # This would be calculated from compliance analysis
                    })
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
                    continue
            
            return jsonify({
                'success': True,
                'files': files_info,
                'total_files': len(files_info)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/reset', methods=['POST'])
    def reset_session():
        """Reset compliance analysis session."""
        nonlocal global_agent, uploaded_file_paths
        
        try:
            if global_agent is not None:
                global_agent.reset_compliance_session()
            
            # Clear uploaded files
            uploaded_file_paths = []
            
            return jsonify({
                'success': True,
                'message': 'Compliance session reset successfully'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/test_agent', methods=['GET'])
    def test_agent():
        """Test if the agent is working properly."""
        nonlocal global_agent
        
        try:
            if global_agent is None:
                return jsonify({'success': False, 'error': 'Agent not initialized'})
            
            # Test with a simple direct tool call
            test_result = global_agent.tools[0].invoke("Test company - A technology company")
            
            return jsonify({
                'success': True,
                'message': 'Agent is working properly',
                'test_result': str(test_result)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/available_regulations', methods=['GET'])
    def get_available_regulations():
        """Get list of available regulations for analysis."""
        return jsonify({
            'success': True,
            'regulations': [
                {
                    'code': 'GDPR',
                    'name': 'General Data Protection Regulation',
                    'description': 'European data protection and privacy regulation'
                },
                {
                    'code': 'NIST',
                    'name': 'NIST Cybersecurity Framework',
                    'description': 'US cybersecurity framework for critical infrastructure'
                },
                {
                    'code': 'HIPAA',
                    'name': 'Health Insurance Portability and Accountability Act',
                    'description': 'US healthcare data protection regulation'
                },
                {
                    'code': 'ISO27001',
                    'name': 'ISO/IEC 27001',
                    'description': 'International information security management standard'
                }
            ]
        })

    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'success': False, 'error': 'File too large. Maximum size is 50MB.'}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    return app
