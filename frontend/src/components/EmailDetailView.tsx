import React from 'react';
import { EmailDetail } from '../api';

interface EmailDetailViewProps {
  email: EmailDetail;
  onBack: () => void;
}

function EmailDetailView({ email, onBack }: EmailDetailViewProps) {
  return (
    <div className="container">
      <div className="header">
        <h1>AI Email Sorter</h1>
      </div>
      
      <div className="main-content">
        <button className="back-btn" onClick={onBack}>
          ← Back to Emails
        </button>
        
        <div className="email-detail">
          <div className="email-detail-header">
            <h1 className="email-detail-subject">{email.subject}</h1>
            <div className="email-meta">
              <div><strong>From:</strong> {email.sender} &lt;{email.sender_email}&gt;</div>
              <div><strong>To:</strong> {email.recipient}</div>
              <div><strong>Date:</strong> {new Date(email.received_at).toLocaleString()}</div>
            </div>
            <div style={{ marginTop: '15px', padding: '15px', background: '#f8f9ff', borderRadius: '8px' }}>
              <strong>AI Summary:</strong>
              <p style={{ marginTop: '8px' }}>{email.ai_summary}</p>
            </div>
          </div>
          
          <div className="email-body">
            {email.body_html ? (
              <div dangerouslySetInnerHTML={{ __html: email.body_html }} />
            ) : (
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                {email.body_text}
              </pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmailDetailView;

