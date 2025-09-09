import React, { useState } from 'react';

const Department = () => {
  const departments = ['Security', 'Police', 'Fire', 'Medical'];
  const [selectedDept, setSelectedDept] = useState('Police');
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('All');

  const policeMembers = [
    { name: 'Smith', rank: 'Sergeant', location: 'Downtown', status: 'InActive' },
    { name: 'Johnson', rank: 'Officer', location: 'North District', status: 'On Patrol' },
    { name: 'Brown', rank: 'Lieutenant', location: 'East Side', status: 'Available' },
  ];

  const fireMembers = [
    { name: 'Firefighter Davis', unit: 'Engine 1', availability: 'Available',status: 'Active' },
    { name: 'Firefighter Wilson', unit: 'Ladder 2', availability: 'On Call' ,status: 'InActive'},
    { name: 'Firefighter Garcia', unit: 'Rescue 3', availability: 'Responding',status: 'Active' },
  ];

  const medicalMembers = [
    { name: 'Dr. Lee', role: 'Doctor', availability: 'Available',status: 'Active' },
    { name: 'Paramedic Patel', role: 'Paramedic', availability: 'On Duty',status: 'Active' },
    { name: 'Nurse Kim', role: 'Nurse', availability: 'Available',status: 'InActive' },
  ];

  const securityMembers = [
    { name: 'Guard Adams', location: 'Main Gate', status: 'Active' },
    { name: 'Guard Taylor', location: 'Parking Lot', status: 'Patrolling' },
  ];

  // Normalize all statuses into Active / Inactive
  const normalizeStatus = (member) => {
    const activeStatuses = [
      'active', 'available', 'on patrol', 'patrolling', 'on call', 'responding', 'on duty'
    ];
    let statusValue = member.status || member.availability || '';
    statusValue = statusValue.toLowerCase();
    return activeStatuses.includes(statusValue) ? 'Active' : 'Inactive';
  };

  const getMembers = () => {
    switch (selectedDept) {
      case 'Police': return policeMembers;
      case 'Fire': return fireMembers;
      case 'Medical': return medicalMembers;
      case 'Security': return securityMembers;
      default: return [];
    }
  };

  const filteredMembers = getMembers().filter(member =>
    member.name.toLowerCase().includes(search.toLowerCase())
  ).filter(member => {
    if (filter === 'All') return true;
    return normalizeStatus(member) === filter;
  });

  return (
    <div className="dept-layout">
      {/* Top Bar */}
      <div className="dept-top-bar">
        <input
          type="text"
          placeholder="Search team members or units..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="dept-search"
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="dept-filter"
        >
          <option value="All">All</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </select>
      </div>

      <div className="dept-main">
        {/* Sidebar */}
        <div className="dept-sidebar">
          <h3 className="dept-title">Department List</h3>
          <ul>
            {departments.map((dept) => (
              <li
                key={dept}
                className={selectedDept === dept ? 'active' : ''}
                onClick={() => setSelectedDept(dept)}
              >
                {dept}
              </li>
            ))}
          </ul>
        </div>

        {/* Content */}
        <div className="dept-content">
          <div className={`dept-card ${selectedDept.toLowerCase()}-card`}>
            <h4>{selectedDept} Team</h4>
            <div className="dept-list">
              {filteredMembers.length > 0 ? (
                filteredMembers.map((member, i) => {
                  const status = normalizeStatus(member);
                  return (
                    <div key={i} className="dept-member-row">
                      <div className="member-name">{member.name}</div>
                      <div className="member-role">{member.rank || member.role || member.unit || '-'}</div>
                      <div className="member-location">📍 {member.location || member.availability || '-'}</div>
                      <div className={`member-status ${status.toLowerCase()}`}>{status}</div>
                    </div>
                  );
                })
              ) : (
                <p className="no-results">No members found.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Department;
