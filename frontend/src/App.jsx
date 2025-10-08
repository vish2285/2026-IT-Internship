import React, { useState, useEffect } from 'react'
import { Search, Filter, ExternalLink, MapPin, Calendar, Building2 } from 'lucide-react'
import InternshipCard from './components/InternshipCard'
import FilterBar from './components/FilterBar'
import { fetchInternships } from './api/internshipAPI'
import './App.css'

function App() {
  const [internships, setInternships] = useState([])
  const [filteredInternships, setFilteredInternships] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    field: '',
    location: '',
    search: ''
  })

  useEffect(() => {
    loadInternships()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [internships, filters])

  const loadInternships = async () => {
    try {
      setLoading(true)
      const data = await fetchInternships()
      setInternships(data)
      setError(null)
    } catch (err) {
      console.error('Error loading internships:', err)
      setError('Failed to load internships. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...internships]

    if (filters.field) {
      filtered = filtered.filter(internship => 
        internship.field.toLowerCase() === filters.field.toLowerCase()
      )
    }

    if (filters.location) {
      filtered = filtered.filter(internship => 
        internship.location.toLowerCase().includes(filters.location.toLowerCase())
      )
    }

    if (filters.search) {
      filtered = filtered.filter(internship => 
        internship.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        internship.company.toLowerCase().includes(filters.search.toLowerCase()) ||
        (internship.description && internship.description.toLowerCase().includes(filters.search.toLowerCase()))
      )
    }

    setFilteredInternships(filtered)
  }

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
  }

  const handleStatusUpdate = (internshipId, newStatus) => {
    setInternships(prev => 
      prev.map(internship => 
        internship.id === internshipId 
          ? { ...internship, application_status: newStatus }
          : internship
      )
    )
  }


  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading internship opportunities...</p>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <h1>Internship Hub</h1>
              <p>Cybersecurity • IT • Neuroscience</p>
            </div>
          </div>
        </div>
      </header>
      

      <main className="main">
        <div className="container">
          <FilterBar 
            filters={filters}
            onFilterChange={handleFilterChange}
            onRefresh={loadInternships}
          />

          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={loadInternships} className="retry-button">
                Try Again
              </button>
            </div>
          )}

          {filteredInternships.length === 0 && !loading && !error && (
            <div className="no-results">
              <p>No internships found matching your criteria.</p>
              <button onClick={() => setFilters({ field: '', location: '', search: '' })}>
                Clear Filters
              </button>
            </div>
          )}

          <div className="internships-grid">
            {filteredInternships.length > 0 ? (
              filteredInternships.map(internship => (
                <InternshipCard 
                  key={internship.id} 
                  internship={internship}
                  onStatusUpdate={handleStatusUpdate}
                />
              ))
            ) : (
              <div className="no-results">
                <div className="no-results-content">
                  <h3>No internships found</h3>
                  <p>Try adjusting your search criteria or filters</p>
                  <button 
                    onClick={() => setFilters({ field: '', location: '', search: '' })}
                    className="clear-filters-btn"
                  >
                    Clear All Filters
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>Auto-updated internship listings • Last updated: {new Date().toLocaleDateString()}</p>
          <p>Built with React & FastAPI • Deployed on Vercel & Railway</p>
        </div>
      </footer>
    </div>
  )
}

export default App
