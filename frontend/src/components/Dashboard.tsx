import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Category, Email, EmailDetail, GmailAccount, categoriesAPI, emailsAPI, accountsAPI, authAPI } from '../api';
import CategoryModal from './CategoryModal';
import EmailDetailView from './EmailDetailView';

function Dashboard() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmails, setSelectedEmails] = useState<Set<number>>(new Set());
  const [accounts, setAccounts] = useState<GmailAccount[]>([]);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<EmailDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  
  const loadCategories = useCallback(async () => {
    try {
      const data = await categoriesAPI.list();
      setCategories(data);
      if (data.length > 0 && !selectedCategory) {
        setSelectedCategory(data[0]);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading categories:', error);
      setLoading(false);
    }
  }, [selectedCategory]);
  
  const loadEmails = useCallback(async (categoryId: number) => {
    try {
      const data = await emailsAPI.listByCategory(categoryId);
      setEmails(data);
      setSelectedEmails(new Set());
    } catch (error) {
      console.error('Error loading emails:', error);
    }
  }, []);
  
  const loadAccounts = useCallback(async () => {
    try {
      const data = await accountsAPI.list();
      setAccounts(data);
    } catch (error) {
      console.error('Error loading accounts:', error);
    }
  }, []);
  
  useEffect(() => {
    loadCategories();
    loadAccounts();
  }, [loadCategories, loadAccounts]);
  
  useEffect(() => {
    if (selectedCategory) {
      loadEmails(selectedCategory.id);
    }
  }, [selectedCategory, loadEmails]);
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };
  
  const handleAddCategory = async (name: string, description: string) => {
    try {
      await categoriesAPI.create({ name, description });
      await loadCategories();
      setShowCategoryModal(false);
    } catch (error) {
      console.error('Error creating category:', error);
      alert('Failed to create category');
    }
  };
  
  const handleEditCategory = async (name: string, description: string) => {
    if (!editingCategory) return;
    
    try {
      await categoriesAPI.update(editingCategory.id, { name, description });
      await loadCategories();
      setEditingCategory(null);
      setShowCategoryModal(false);
      // Update selected category if it was the one being edited
      if (selectedCategory?.id === editingCategory.id) {
        const updated = await categoriesAPI.list();
        const updatedCategory = updated.find(c => c.id === editingCategory.id);
        if (updatedCategory) {
          setSelectedCategory(updatedCategory);
        }
      }
    } catch (error) {
      console.error('Error updating category:', error);
      alert('Failed to update category');
    }
  };
  
  const handleDeleteCategory = async (categoryId: number) => {
    if (!window.confirm('Delete this category? All emails in this category will remain in your account.')) {
      return;
    }
    
    try {
      await categoriesAPI.delete(categoryId);
      await loadCategories();
      // Clear selection if deleted category was selected
      if (selectedCategory?.id === categoryId) {
        const remaining = categories.filter(c => c.id !== categoryId);
        setSelectedCategory(remaining.length > 0 ? remaining[0] : null);
      }
    } catch (error) {
      console.error('Error deleting category:', error);
      alert('Failed to delete category');
    }
  };
  
  const openEditModal = (category: Category, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent category selection
    setEditingCategory(category);
    setShowCategoryModal(true);
  };
  
  const closeModal = () => {
    setShowCategoryModal(false);
    setEditingCategory(null);
  };
  
  const handleSync = async () => {
    setSyncing(true);
    try {
      await emailsAPI.sync();
      alert('Email sync started! This may take a few moments.');
      // Reload after a delay
      setTimeout(() => {
        if (selectedCategory) {
          loadEmails(selectedCategory.id);
        }
        loadCategories();
        setSyncing(false);
      }, 5000);
    } catch (error) {
      console.error('Error syncing emails:', error);
      alert('Failed to start sync');
      setSyncing(false);
    }
  };
  
  const toggleEmailSelection = (emailId: number) => {
    const newSelection = new Set(selectedEmails);
    if (newSelection.has(emailId)) {
      newSelection.delete(emailId);
    } else {
      newSelection.add(emailId);
    }
    setSelectedEmails(newSelection);
  };
  
  const toggleSelectAll = () => {
    if (selectedEmails.size === emails.length) {
      setSelectedEmails(new Set());
    } else {
      setSelectedEmails(new Set(emails.map(e => e.id)));
    }
  };
  
  const handleBulkDelete = async () => {
    if (selectedEmails.size === 0) return;
    
    if (!window.confirm(`Delete ${selectedEmails.size} email(s)?`)) return;
    
    try {
      await emailsAPI.bulkAction(Array.from(selectedEmails), 'delete');
      if (selectedCategory) {
        await loadEmails(selectedCategory.id);
      }
      await loadCategories();
    } catch (error) {
      console.error('Error deleting emails:', error);
      alert('Failed to delete emails');
    }
  };
  
  const handleBulkUnsubscribe = async () => {
    if (selectedEmails.size === 0) return;
    
    if (!window.confirm(`Unsubscribe from ${selectedEmails.size} email(s)? This will attempt to automatically unsubscribe you.`)) return;
    
    try {
      await emailsAPI.bulkAction(Array.from(selectedEmails), 'unsubscribe');
      alert('Unsubscribe process started. This may take a few moments.');
      // Reload after delay
      setTimeout(() => {
        if (selectedCategory) {
          loadEmails(selectedCategory.id);
        }
        loadCategories();
      }, 3000);
    } catch (error) {
      console.error('Error unsubscribing:', error);
      alert('Failed to start unsubscribe process');
    }
  };
  
  const handleEmailClick = async (email: Email) => {
    try {
      const detail = await emailsAPI.get(email.id);
      setSelectedEmail(detail);
    } catch (error) {
      console.error('Error loading email detail:', error);
      alert('Failed to load email');
    }
  };
  
  const handleConnectAccount = async () => {
    try {
      const data = await authAPI.login();
      window.open(data.authorization_url, '_blank');
    } catch (error) {
      console.error('Error connecting account:', error);
    }
  };
  
  const handleDisconnectAccount = async (accountId: number) => {
    if (!window.confirm('Disconnect this account?')) return;
    
    try {
      await accountsAPI.disconnect(accountId);
      await loadAccounts();
    } catch (error: any) {
      console.error('Error disconnecting account:', error);
      alert(error.response?.data?.detail || 'Failed to disconnect account');
    }
  };
  
  if (loading) {
    return (
      <div className="loading">
        <p>Loading...</p>
      </div>
    );
  }
  
  if (selectedEmail) {
    return (
      <EmailDetailView
        email={selectedEmail}
        onBack={() => setSelectedEmail(null)}
      />
    );
  }
  
  return (
    <div className="container">
      <div className="header">
        <h1>AI Email Sorter</h1>
        <button onClick={handleLogout}>Logout</button>
      </div>
      
      <div className="dashboard">
        <aside className="sidebar">
          <div>
            <h2>Categories</h2>
            <ul className="category-list">
              {categories.map(category => (
                <li
                  key={category.id}
                  className={`category-item ${selectedCategory?.id === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category)}
                >
                  <div className="category-info">
                    <span className="category-name">{category.name}</span>
                    <span className="email-count">{category.email_count}</span>
                  </div>
                  <div className="category-actions">
                    <button
                      className="edit-category-btn"
                      onClick={(e) => openEditModal(category, e)}
                      title="Edit category"
                    >
                      ✏️
                    </button>
                    <button
                      className="delete-category-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteCategory(category.id);
                      }}
                      title="Delete category"
                    >
                      🗑️
                    </button>
                  </div>
                </li>
              ))}
            </ul>
            <button className="add-category-btn" onClick={() => setShowCategoryModal(true)}>
              + Add Category
            </button>
          </div>
          
          <div className="accounts-section">
            <h2>Gmail Accounts</h2>
            <ul className="account-list">
              {accounts.map(account => (
                <li key={account.id} className="account-item">
                  <span>{account.email}</span>
                  {accounts.length > 1 && (
                    <button
                      className="remove-account-btn"
                      onClick={() => handleDisconnectAccount(account.id)}
                    >
                      Remove
                    </button>
                  )}
                </li>
              ))}
            </ul>
            <button className="add-category-btn" onClick={handleConnectAccount}>
              + Connect Account
            </button>
            <button className="sync-btn" onClick={handleSync} disabled={syncing}>
              {syncing ? 'Syncing...' : 'Sync Emails'}
            </button>
          </div>
        </aside>
        
        <main className="main-content">
          {selectedCategory ? (
            <>
              <div className="content-header">
                <h2>{selectedCategory.name}</h2>
                {selectedEmails.size > 0 && (
                  <div className="bulk-actions">
                    <button className="delete-btn" onClick={handleBulkDelete}>
                      Delete ({selectedEmails.size})
                    </button>
                    <button className="unsubscribe-btn" onClick={handleBulkUnsubscribe}>
                      Unsubscribe ({selectedEmails.size})
                    </button>
                  </div>
                )}
              </div>
              
              {emails.length > 0 ? (
                <>
                  <div style={{ marginBottom: '15px' }}>
                    <label>
                      <input
                        type="checkbox"
                        className="select-all-checkbox"
                        checked={selectedEmails.size === emails.length && emails.length > 0}
                        onChange={toggleSelectAll}
                      />
                      Select All
                    </label>
                  </div>
                  
                  <ul className="email-list">
                    {emails.map(email => (
                      <li
                        key={email.id}
                        className={`email-item ${selectedEmails.has(email.id) ? 'selected' : ''}`}
                      >
                        <div className="email-header">
                          <input
                            type="checkbox"
                            className="email-checkbox"
                            checked={selectedEmails.has(email.id)}
                            onChange={() => toggleEmailSelection(email.id)}
                            onClick={(e) => e.stopPropagation()}
                          />
                          <div style={{ flex: 1 }} onClick={() => handleEmailClick(email)}>
                            <div className="email-subject">{email.subject}</div>
                            <div className="email-sender">From: {email.sender}</div>
                            <div className="email-summary">{email.ai_summary}</div>
                          </div>
                          <div className="email-date">
                            {new Date(email.received_at).toLocaleDateString()}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <div className="empty-state">
                  <h3>No emails yet</h3>
                  <p>Click "Sync Emails" to import new emails into this category.</p>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <h3>No categories yet</h3>
              <p>Create a category to start organizing your emails.</p>
            </div>
          )}
        </main>
      </div>
      
      {showCategoryModal && (
        <CategoryModal
          category={editingCategory}
          onSave={editingCategory ? handleEditCategory : handleAddCategory}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

export default Dashboard;

