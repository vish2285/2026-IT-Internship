import React, { useState } from 'react'
import { ExternalLink, MapPin, Calendar, Building2, Clock, CheckCircle, PlayCircle, XCircle } from 'lucide-react'
import { updateApplicationStatus } from '../api/internshipAPI'

const InternshipCard = ({ internship, onStatusUpdate }) => {
  const [isUpdating, setIsUpdating] = useState(false)
  
  const handleApply = () => {
    if (internship.apply_url && internship.apply_url !== '') {
      window.open(internship.apply_url, '_blank', 'noopener,noreferrer')
    } else {
      alert('Application link not available for this position')
    }
  }

  const handleStatusUpdate = async (newStatus) => {
    if (isUpdating) return
    
    try {
      setIsUpdating(true)
      await updateApplicationStatus(internship.id, newStatus)
      if (onStatusUpdate) {
        onStatusUpdate(internship.id, newStatus)
      }
    } catch (error) {
      console.error('Error updating status:', error)
      alert('Failed to update application status')
    } finally {
      setIsUpdating(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return null
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getFieldColor = (field) => {
    switch (field) {
      case 'Cybersecurity':
        return 'field-cybersecurity'
      case 'IT':
        return 'field-it'
      case 'Neuroscience':
        return 'field-neuroscience'
      default:
        return 'field-default'
    }
  }

  const isDeadlineSoon = (deadline) => {
    if (!deadline) return false
    const deadlineDate = new Date(deadline)
    const today = new Date()
    const diffTime = deadlineDate - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays <= 7 && diffDays >= 0
  }

  const getDateLabel = (postedDate) => {
    if (!postedDate) return null
    
    const posted = new Date(postedDate)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const lastWeek = new Date(today)
    lastWeek.setDate(lastWeek.getDate() - 7)
    
    // Reset time to compare dates only
    posted.setHours(0, 0, 0, 0)
    today.setHours(0, 0, 0, 0)
    yesterday.setHours(0, 0, 0, 0)
    lastWeek.setHours(0, 0, 0, 0)
    
    if (posted.getTime() === today.getTime()) {
      return { text: 'Today', color: 'green' }
    } else if (posted.getTime() === yesterday.getTime()) {
      return { text: 'Yesterday', color: 'yellow' }
    } else if (posted >= lastWeek) {
      return { text: 'This Week', color: 'gray' }
    } else {
      return { text: 'Older', color: 'muted' }
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'applied':
        return <CheckCircle className="w-4 h-4" />
      case 'started':
        return <PlayCircle className="w-4 h-4" />
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      default:
        return <XCircle className="w-4 h-4" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'applied':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'started':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusClass = (status) => {
    const statusMap = {
      'applied': 'status-applied',
      'started': 'status-started', 
      'completed': 'status-completed',
      'not_applied': 'status-not-applied'
    }
    return statusMap[status] || 'status-not-applied'
  }

  return (
    <div className={`internship-card ${getStatusClass(internship.application_status || 'not_applied')}`}>
      <div className="card-header">
        <div className="field-badge">
          <span className={`field-tag ${getFieldColor(internship.field)}`}>
            {internship.field}
          </span>
        </div>
        <div className="header-badges">
          {getDateLabel(internship.posted_date) && (
            <div className={`date-label date-label-${getDateLabel(internship.posted_date).color}`}>
              {getDateLabel(internship.posted_date).text}
            </div>
          )}
          {internship.deadline && isDeadlineSoon(internship.deadline) && (
            <div className="urgent-badge">
              <Clock size={14} />
              <span>Deadline Soon</span>
            </div>
          )}
        </div>
      </div>

      <div className="card-content">
        <h3 className="internship-title">{internship.title}</h3>
        
        <div className="company-info">
          <Building2 size={16} />
          <span className="company-name">{internship.company}</span>
        </div>

        <div className="location-info">
          <MapPin size={16} />
          <span className="location">{internship.location}</span>
        </div>

        {internship.description && (
          <p className="description">
            {internship.description.length > 150 
              ? `${internship.description.substring(0, 150)}...`
              : internship.description
            }
          </p>
        )}

        <div className="date-info">
          <div className="posted-date">
            <Calendar size={14} />
            <span>Posted: {formatDate(internship.posted_date)}</span>
          </div>
          
          {internship.deadline && (
            <div className={`deadline ${isDeadlineSoon(internship.deadline) ? 'deadline-urgent' : ''}`}>
              <Clock size={14} />
              <span>Deadline: {formatDate(internship.deadline)}</span>
            </div>
          )}
        </div>

        {/* Application Status Section */}
        <div className="application-status-section">
          <div className="current-status">
            <span className="status-label">Status:</span>
            <div className={`status-badge ${getStatusColor(internship.application_status || 'not_applied')}`}>
              {getStatusIcon(internship.application_status || 'not_applied')}
              <span className="capitalize">
                {(internship.application_status || 'not_applied').replace('_', ' ')}
              </span>
            </div>
          </div>
          
          <div className="status-buttons">
            <button
              className={`status-btn ${(internship.application_status || 'not_applied') === 'not_applied' ? 'active' : ''}`}
              onClick={() => handleStatusUpdate('not_applied')}
              disabled={isUpdating}
            >
              <XCircle size={14} />
              Not Applied
            </button>
            <button
              className={`status-btn ${(internship.application_status || 'not_applied') === 'applied' ? 'active' : ''}`}
              onClick={() => handleStatusUpdate('applied')}
              disabled={isUpdating}
            >
              <CheckCircle size={14} />
              Applied
            </button>
            <button
              className={`status-btn ${(internship.application_status || 'not_applied') === 'started' ? 'active' : ''}`}
              onClick={() => handleStatusUpdate('started')}
              disabled={isUpdating}
            >
              <PlayCircle size={14} />
              Started
            </button>
          </div>
        </div>
      </div>

      <div className="card-footer">
        <button 
          className="apply-button"
          onClick={handleApply}
        >
          <ExternalLink size={16} />
          Apply Now
        </button>
      </div>
    </div>
  )
}

export default InternshipCard
