import React from 'react'
import { Search, Filter, RefreshCw } from 'lucide-react'

const FilterBar = ({ filters, onFilterChange, onRefresh }) => {
  const handleFieldChange = (field) => {
    onFilterChange({ field: field === 'All' ? '' : field })
  }

  const handleLocationChange = (e) => {
    onFilterChange({ location: e.target.value })
  }

  const handleSearchChange = (e) => {
    onFilterChange({ search: e.target.value })
  }

  const clearFilters = () => {
    onFilterChange({ field: '', location: '', search: '' })
  }

  const hasActiveFilters = filters.field || filters.location || filters.search

  return (
    <div className="filter-bar">
      <div className="filter-section">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search internships, companies..."
            value={filters.search}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>

        <div className="field-filters">
          <button
            className={`field-filter ${!filters.field ? 'active' : ''}`}
            onClick={() => handleFieldChange('All')}
          >
            All Fields
          </button>
          <button
            className={`field-filter ${filters.field === 'Cybersecurity' ? 'active' : ''}`}
            onClick={() => handleFieldChange('Cybersecurity')}
          >
            🔒 Cybersecurity
          </button>
          <button
            className={`field-filter ${filters.field === 'IT' ? 'active' : ''}`}
            onClick={() => handleFieldChange('IT')}
          >
            💻 IT
          </button>
          <button
            className={`field-filter ${filters.field === 'Neuroscience' ? 'active' : ''}`}
            onClick={() => handleFieldChange('Neuroscience')}
          >
            🧠 Neuroscience
          </button>
        </div>

        <div className="location-filter">
          <input
            type="text"
            placeholder="Filter by location..."
            value={filters.location}
            onChange={handleLocationChange}
            className="location-input"
          />
        </div>
      </div>

      <div className="filter-actions">
        {hasActiveFilters && (
          <button 
            className="clear-filters-btn"
            onClick={clearFilters}
          >
            <Filter size={16} />
            Clear Filters
          </button>
        )}
        
        <button 
          className="refresh-btn"
          onClick={onRefresh}
          title="Refresh internships"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
    </div>
  )
}

export default FilterBar

